#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'GenreMix.kt';p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'ProducerAdaptation.kt').read_text().split('\n',1)[1])
p=src/'GenreCheckpoint.kt';s=p.read_text();assert s.count('genre-render-v8')==1;p.write_text(s.replace('genre-render-v8','genre-render-v9'))
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
# Reuse the existing background job/cancel mechanism. No destructive tag writes or silent ASR downloads.
a=s.index('    private data class BatchLyricsItem')
b=s.index('    // Shared custom bottom sheet',a)
s=s[:a]+'''    private data class ScanItem(val uri:String,val title:String,val artist:String,val before:String)
    private data class ScanUpdate(val item:ScanItem,val raw:String?,val report:MusicAnalysis.Report?,val status:String)
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
            sheetAction(panel,"Начать сканирование","Обработка по одной песне · можно отменить"){
                val useSearch=search.isChecked;val useAnalysis=analyze.isChecked;val useLocal=local.isEnabled&&local.isChecked;val useAlign=align.isEnabled&&align.isChecked
                dialog.dismiss();scanLibrary(pending,useSearch,useAnalysis,useLocal,useAlign)
            }
        }
    }
    private fun scanLibrary(pending:List<ScanItem>,search:Boolean,analyze:Boolean,local:Boolean,align:Boolean){
        var completed=0;var saved=0;var unresolved=0;var errors=0;var analyzed=0
        // Commit each verified track individually on the UI thread. A cancellation keeps completed tracks.
        stemWork("Сканирование библиотеки…",{
            for((i,t) in pending.withIndex()){
                check(!Thread.currentThread().isInterrupted){"Отменено"}
                updateWork("Библиотека: "+(i+1)+"/"+pending.size+" · "+t.title)
                val uri=Uri.parse(t.uri);var raw:String?=null;var report:MusicAnalysis.Report?=null;var status="Пропущено"
                try{
                    if(analyze){report=TrackAnalyzer.report(this,uri,full=true)}
                    if(t.before.isBlank()){
                        raw=TrackLyricSource.embedded(this,uri)
                        if(raw==null&&search){
                            val info=TrackLyricSource.metadata(this,uri,t.title,t.artist,null)
                            if(info.seconds!=null)raw=BatchLyricPolicy.choose(LyricsLookup.search(info.title,info.artist,info.seconds,false),info.title,info.artist,info.seconds)
                            Thread.sleep(1100)
                        }
                        // ASR is explicitly enabled by the user. Store only when the known text can be aligned;
                        // raw recognizer output is a draft requiring individual review, never silently installed.
                        if(raw==null&&local){
                            status="Требуется проверка Whisper"
                        }else status=if(raw!=null)"Текст найден" else "Нет совпадения"
                    }
                    val reference=raw?:t.before
                    if(align&&reference.isNotBlank()&&Lrc.parse(reference).isEmpty()){
                        val heard=WhisperLocal.transcribe(this,uri,null,"auto"){updateWork(it)}
                        val result=KnownLyricAlignment.align(heard,LyricDocument.plain(reference))
                        if(result!=null){raw=result.lrc;status="Синхронизировано"}else if(raw==null)status="Нет уверенной синхронизации"
                    }
                }catch(e:Exception){if(Thread.currentThread().isInterrupted||e is InterruptedException)throw e;status="Ошибка"}
                val update=ScanUpdate(t,raw,report,status)
                val latch=java.util.concurrent.CountDownLatch(1)
                runOnUiThread{
                    try{
                        if(!isDestroyed){
                            val target=libraryIndex.get(update.item.uri)
                            if(target!=null&&target.uri==target.group&&target.lyrics==update.item.before){
                                if(update.report!=null){completeReports[target.uri]=update.report;reports[target.uri]=update.report;analyzed++}
                                val text=update.raw
                                if(text!=null&&text!=target.lyrics){
                                    val previous=target.lyrics;target.lyrics=text
                                    if(saveLibrary(true))saved++ else{target.lyrics=previous;reindex();errors++}
                                }else if(update.status=="Ошибка")errors++
                                else if(update.status!="Пропущено")unresolved++
                            }
                            completed++
                        }
                    }finally{latch.countDown()}
                }
                while(!latch.await(200,java.util.concurrent.TimeUnit.MILLISECONDS))check(!Thread.currentThread().isInterrupted)
            }
            Unit
        }{
            actionSheet("Сканирование завершено",290){dialog,panel->
                panel.addView(label("Проверено: "+completed+" / "+pending.size,20,PremiumChrome.TEXT,true))
                panel.addView(label("Сохранены тексты: "+saved+"\\nПолный анализ: "+analyzed+"\\nНужна проверка: "+unresolved+"\\nОшибки: "+errors,16,muted))
                sheetAction(panel,"Готово"){dialog.dismiss();render()}
            }
        }
    }
'''+s[b:]
# Do not advertise a raw Whisper batch action until its draft queue exists.
s=s.replace('Whisper для песен без найденного текста','Отметить песни без текста для проверки').replace('isEnabled=WhisperLocal.available&&WhisperLocal.installed(this@MainActivity)!=null','isEnabled=true',1).replace('isEnabled=local.isEnabled','isEnabled=WhisperLocal.available&&WhisperLocal.installed(this@MainActivity)!=null')
p.write_text(s)
print("PASS: source-aware remix balance and opt-in library scan")
