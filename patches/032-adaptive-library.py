#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'GenreMix.kt';p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'ProducerAdaptation.kt').read_text().split('\n',1)[1])
p=src/'GenreCheckpoint.kt';s=p.read_text();assert s.count('genre-render-v8')==1;p.write_text(s.replace('genre-render-v8','genre-render-v11'))
p=src/'MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b)
rep('val sections=SectionArrangement.plan(report,frames/44100.0)','val sections=SectionArrangement.plan(report,frames/44100.0);val adapted=ProducerAdaptation.adapt(controls,ProducerAdaptation.factors(report.rms,report.energy,report.keyConfidence,stems!=null))')
rep('report.chords,report.energy,groove,controls,sections,update)','report.chords,report.energy,groove,adapted,sections,update)') if False else None
assert s.count('report.chords,report.energy,groove,controls,sections,update)')==2
s=s.replace('report.chords,report.energy,groove,controls,sections,update)','report.chords,report.energy,groove,adapted,sections,update)')
rep('30 шаблонов · умное сведение баса и разные тембры','40 направлений · адаптивная аранжировка')
# Only hard-dance renders use the neural note estimate; ambiguous results keep the preset.
rep('val files=GenreCheckpoint.render(raw,inputs,dir,job.plan,bpm,','''val pitch=if(styles.any{HardKick.profile(it.name)!=null}){
                    status("Basic Pitch · анализ низких нот…")
                    try{BasicPitchModel.estimate(this,raw)}catch(e:Exception){if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e;null}
                }else null
                val tuned=styles.map{style->
                    val profile=HardKick.profile(style.name)
                    val hz=if(pitch!=null&&profile!=null)BasicPitchHint.frequencyNear(pitch,profile.hz)else null
                    style.copy(kickHz=hz)
                }
                val renderPlan=job.plan.copy(styles=tuned)
                val files=GenreCheckpoint.render(raw,inputs,dir,renderPlan,bpm,''')
# Reuse the existing background job/cancel mechanism. No destructive tag writes or silent ASR downloads.
a=s.index('    private data class BatchLyricsItem')
b=s.index('    // Shared custom bottom sheet',a)
s=s[:a]+'''    private data class ScanItem(val uri:String,val title:String,val artist:String,val before:String)
    private data class ScanUpdate(val item:ScanItem,val raw:String?,val report:MusicAnalysis.Report?,val status:String,val draft:String?)
    private fun batchLyrics(){
        if(stemBusy){toast("Дождитесь завершения обработки");return}
        val pending=tracks.filter{it.uri==it.group}.map{ScanItem(it.uri,it.title,it.artist,it.lyrics)}
        if(pending.isEmpty()){toast("Сначала добавьте музыку");return}
        actionSheet("Сканирование библиотеки",390){dialog,panel->
            panel.addView(label("Композиции: "+pending.size+" · оригиналы не изменяются",15,muted))
            val search=CheckBox(this).apply{text="Поиск готовых текстов в интернете";isChecked=true;setTextColor(PremiumChrome.TEXT)}
            val analyze=CheckBox(this).apply{text="Полный анализ темпа, тональности и структуры";setTextColor(PremiumChrome.TEXT)}
            val local=CheckBox(this).apply{text="Whisper для песен без найденного текста";setTextColor(PremiumChrome.TEXT);isEnabled=WhisperLocal.available&&WhisperLocal.installed(this@MainActivity)!=null}
            val align=CheckBox(this).apply{text="Уточнить время существующих текстов по вокалу";setTextColor(PremiumChrome.TEXT);isEnabled=local.isEnabled}
            panel.addView(search);panel.addView(analyze);panel.addView(local);panel.addView(align)
            panel.addView(label("Встроенные тексты читаются офлайн. Интернету передаются только метаданные. Whisper может занять много времени; сомнительные совпадения не сохраняются.",13,muted))
            sheetAction(panel,"Черновики Whisper","Просмотреть ранее распознанные тексты"){dialog.dismiss();scanDraftReview()}
            sheetAction(panel,"Начать сканирование","Обработка по одной песне · можно отменить"){
                val useSearch=search.isChecked;val useAnalysis=analyze.isChecked;val useLocal=local.isEnabled&&local.isChecked;val useAlign=align.isEnabled&&align.isChecked
                dialog.dismiss();scanLibrary(pending,useSearch,useAnalysis,useLocal,useAlign)
            }
        }
    }
    private fun scanKey(uri:String)=java.security.MessageDigest.getInstance("SHA-256").digest(uri.toByteArray(Charsets.UTF_8)).joinToString(""){(it.toInt() and 255).toString(16).padStart(2,'0')}
    private fun scanDraftFile(uri:String)=java.io.File(java.io.File(filesDir,"lyric-drafts"),scanKey(uri)+".lrc")
    private fun saveScanDraft(uri:String,raw:String):Boolean=runCatching{
        val bytes=raw.toByteArray(Charsets.UTF_8);require(bytes.size in 1..262144)
        val target=scanDraftFile(uri);val dir=requireNotNull(target.parentFile)
        check(dir.isDirectory||dir.mkdirs())
        // Bound the entire draft store; do not delete anyone's unreviewed results.
        require(dir.listFiles().orEmpty().sumOf{it.length()}+bytes.size<=64L*1024*1024)
        val tmp=java.io.File.createTempFile("draft-",".tmp",dir)
        try{tmp.outputStream().use{it.write(bytes)};check(tmp.renameTo(target));true}finally{tmp.delete()}
    }.getOrDefault(false)
    private fun scanFacts(uri:String,report:MusicAnalysis.Report){
        // Compact persistent summary, not full analysis frames; full reports use the existing bounded cache.
        val facts=JSONObject().put("duration",report.duration).put("rms",report.rms)
        report.tempo?.let{facts.put("bpm",it.bpm).put("confidence",it.confidence)}
        report.key?.let{facts.put("key",it).put("keyConfidence",report.keyConfidence)}
        getSharedPreferences("scan_facts",MODE_PRIVATE).edit().putString(scanKey(uri),facts.toString()).apply()
    }
    private fun scanDraftReview(){
        if(stemBusy){toast("Дождитесь завершения обработки");return}
        val items=tracks.filter{it.uri==it.group&&scanDraftFile(it.uri).isFile}
        if(items.isEmpty()){toast("Нет сохранённых черновиков");return}
        actionSheet("Черновики Whisper",480){dialog,panel->
            panel.addView(label("Песен: "+items.size+" · слова и метки требуют проверки",14,muted))
            items.take(100).forEach{t->sheetAction(panel,t.title,t.artist){
                val id=t.uri;val before=t.lyrics;val file=scanDraftFile(id)
                val raw=runCatching{require(file.length() in 1..262144);file.readText()}.getOrNull()
                dialog.dismiss()
                if(raw==null){toast("Черновик недоступен");return@sheetAction}
                reviewTranscript("Whisper",raw){accepted->
                    val target=libraryIndex.get(id)
                    if(target==null||target.lyrics!=before||before.isNotBlank()){toast("Текст уже существует или песня изменилась");return@reviewTranscript}
                    target.lyrics=accepted
                    if(saveLibrary(true)){file.delete();toast("Черновик принят")}else{target.lyrics=before;reindex();toast("Ошибка сохранения")}
                }
            }}
            if(items.size>100)panel.addView(label("Показаны первые 100. После проверки откроются следующие.",13,muted))
        }
    }
    // Prefer already separated vocals. Do not start an expensive separation job implicitly.
    private fun scanRecognize(uri:Uri,id:String):String{
        val stem=getSharedPreferences("stem_cache",MODE_PRIVATE).getString(id,null)?.let{StemEngine.load(this,it)}
        if(stem!=null){
            updateWork("Whisper · выделенный вокал")
            val heard=try{WhisperLocal.transcribe(this,uri,stem,"auto"){updateWork(it)}}catch(e:Exception){
                if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e
                ""
            }
            check(!Thread.currentThread().isInterrupted)
            if(heard.isNotBlank())return heard
        }
        updateWork("Whisper · исходная композиция")
        return WhisperLocal.transcribe(this,uri,null,"auto"){updateWork(it)}
    }
    private fun scanLibrary(pending:List<ScanItem>,search:Boolean,analyze:Boolean,local:Boolean,align:Boolean){
        var completed=0;var saved=0;var unresolved=0;var errors=0;var analyzed=0;var drafts=0
        // Commit each verified track individually on the UI thread. A cancellation keeps completed tracks.
        stemWork("Сканирование библиотеки…",{
            for((i,t) in pending.withIndex()){
                check(!Thread.currentThread().isInterrupted){"Отменено"}
                updateWork("Библиотека: "+(i+1)+"/"+pending.size+" · "+t.title)
                val uri=Uri.parse(t.uri);var raw:String?=null;var report:MusicAnalysis.Report?=null;var status="Пропущено";var draft:String?=null
                try{
                    if(analyze){report=TrackAnalyzer.report(this,uri,full=true)}
                    if(t.before.isBlank()||Lrc.parse(t.before).isEmpty()){
                        raw=try{TrackLyricSource.automatic(this,uri,t.title,t.artist,t.before,search)}catch(e:Exception){if(Thread.currentThread().isInterrupted||e is InterruptedException||!local)throw e;TrackLyricSource.automatic(this,uri,t.title,t.artist,t.before,false)}
                        if(search)Thread.sleep(1100)
                        if(raw.isNullOrBlank()&&local&&!scanDraftFile(t.uri).isFile){
                            draft=scanRecognize(uri,t.uri).takeIf{it.isNotBlank()&&it.length<=256000};status=if(draft!=null)"Черновик Whisper" else "Нет совпадения"
                        }else status=when{raw.isNullOrBlank()->"Нет совпадения";Lrc.parse(raw).isEmpty()->"Только слова";raw==t.before->"Пропущено";else->"Текст найден"}
                    }
                    val reference=raw?:t.before
                    if(align&&reference.isNotBlank()&&Lrc.parse(reference).isEmpty()){
                        val heard=scanRecognize(uri,t.uri)
                        val result=KnownLyricAlignment.align(heard,LyricDocument.plain(reference))
                        if(result!=null){raw=result.lrc;status="Синхронизировано"}else if(raw==null)status="Нет уверенной синхронизации"
                    }
                }catch(e:Exception){if(Thread.currentThread().isInterrupted||e is InterruptedException)throw e;status="Ошибка"}
                val update=ScanUpdate(t,raw,report,status,draft)
                val latch=java.util.concurrent.CountDownLatch(1)
                runOnUiThread{
                    try{
                        if(!isDestroyed&&!isFinishing&&workTicket?.cancelled==false){
                            val target=libraryIndex.get(update.item.uri)
                            if(target!=null&&target.uri==target.group&&target.lyrics==update.item.before){
                                if(update.report!=null){completeReports[target.uri]=update.report;reports[target.uri]=update.report;analyzed++;scanFacts(target.uri,update.report)}
                                val text=update.raw
                                if(text!=null&&text!=target.lyrics){
                                    val previous=target.lyrics;target.lyrics=text
                                    if(saveLibrary(true))saved++ else{target.lyrics=previous;reindex();errors++}
                                }else if(update.draft!=null){if(saveScanDraft(target.uri,update.draft))drafts++ else errors++}
                                else if(update.status=="Ошибка")errors++
                                else if(update.status!="Пропущено")unresolved++
                            }
                            completed++
                        }
                    }finally{latch.countDown()}
                }
                while(!latch.await(200,java.util.concurrent.TimeUnit.MILLISECONDS))check(!Thread.currentThread().isInterrupted)
            }
            Unit
        }){
            actionSheet("Сканирование завершено",290){dialog,panel->
                panel.addView(label("Проверено: "+completed+" / "+pending.size,20,PremiumChrome.TEXT,true))
                panel.addView(label("Сохранены тексты: "+saved+"\\nПолный анализ: "+analyzed+"\\nНужна проверка: "+unresolved+"\\nЧерновики Whisper: "+drafts+"\\nОшибки: "+errors,16,muted))
                sheetAction(panel,"Готово"){dialog.dismiss();render()}
            }
        }
    }
'''+s[b:]
p.write_text(s)
print("PASS: source-aware remix balance and opt-in library scan with saved drafts")
