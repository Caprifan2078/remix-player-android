#!/usr/bin/env python3
"""Keep everyday playback and remixing visible; opt into specialist controls."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt'
s=p.read_text()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:120],s.count(a))
    s=s.replace(a,b)
anchor='    private fun compactSection(key:String,title:String,views:List<View>,at:Int){'
rep(anchor,'''    private fun proMode()=getSharedPreferences("interface_mode",MODE_PRIVATE).getBoolean("pro",false)
    private fun togglePro(){
        val enabled=!proMode()
        if(!getSharedPreferences("interface_mode",MODE_PRIVATE).edit().putBoolean("pro",enabled).commit()){
            toast("Не удалось сохранить настройки");return
        }
        if(!enabled)expandedSections.clear()
        render()
    }
    private fun proButton(title:String,action:()->Unit)=btn(title,action).apply{
        if(!proMode())visibility=View.GONE
    }
    private fun proCard(title:String,subtitle:String,action:()->Unit){
        if(proMode())card(title,subtitle,action)
    }
'''+anchor)
# The named studio cards are explicitly classified, not removed by a generic substring filter.
rep('card("Инструментал","Создать музыку с нуля · экспериментально")','proCard("Инструментал","Создать музыку с нуля · экспериментально")')
rep('card("Сведение","Совместить песню с инструменталом")','proCard("Сведение","Совместить песню с инструменталом")')
rep('btn("Vosk · эксперимент")','proButton("Vosk · эксперимент")')
rep('btn("Речевые модели Vosk")','proButton("Речевые модели Vosk")')
rep('btn("Пакет эффектов…")','proButton("Пакет эффектов…")')
# Keep the studio and useful model manager intact. Only advanced actions disappear.
# The setting is deliberately outside every collapsed settings section.
rep('val backupStart=body.childCount;','body.addView(btn(if(proMode())"PRO-инструменты: вкл." else "PRO-инструменты: выкл."){togglePro()});body.addView(label("Дополнительные инструменты. Музыка, ремиксы и тексты остаются доступны в обоих режимах.",13,muted));val backupStart=body.childCount;')
# Filter the optional player actions by stable operation IDs, not index in the filtered menu.
a='android.app.AlertDialog.Builder(this).setTitle("Композиция").setItems(arrayOf("Версии","Микшер","Студия","Таймер и переходы","Повтор A/B","Вырезать фрагмент","Эквалайзер")){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(i)'
b='val actions=listOf("Версии","Микшер","Студия","Таймер и переходы","Повтор A/B","Вырезать фрагмент","Эквалайзер");val visible=actions.indices.filter{proMode()||it!=4&&it!=5};android.app.AlertDialog.Builder(this).setTitle("Композиция").setItems(visible.map{actions[it]}.toTypedArray()){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(visible[i])'
rep(a,b)
# Bulk ASR is expensive and remains opt-in; single-track Whisper is still available.
rep('panel.addView(search);panel.addView(analyze);panel.addView(local);panel.addView(align)','panel.addView(search);panel.addView(analyze);if(proMode()){panel.addView(local);panel.addView(align)}')
rep('val useLocal=local.isEnabled&&local.isChecked;val useAlign=align.isEnabled&&align.isChecked','val useLocal=proMode()&&local.isEnabled&&local.isChecked;val useAlign=proMode()&&align.isEnabled&&align.isChecked')
# Hide advanced controls in the library without disabling importing, playlists, or local discovery.
rep('val libraryTools=bodyChildren().filter','val libraryTools=bodyChildren().filter') if False else None
# Omit an empty disclosure when all of its actual controls are hidden by simple mode.
rep('if(views.isEmpty())return','if(views.isEmpty())return\n        if(views.all{it.visibility==View.GONE}){views.forEach{v->(v.parent as? ViewGroup)?.removeView(v)};return}')

# One primary lyric entry; keep the existing editable lookup available as the manual source.
rep('val lookup=body.getChildAt(2);body.removeView(lookup);body.addView(lookup,1);','val lookup=body.getChildAt(2) as Button;body.removeView(lookup);body.addView(btn(if(lyricsBusy)"Поиск текста…" else "Найти текст"){lyricSearchChoices(t){lookup.performClick()}},1);body.getChildAt(2).visibility=View.GONE;')
anchor='    private fun compactSection(key:String,title:String,views:List<View>,at:Int){'
rep(anchor,'''    private fun lyricSearchChoices(t:Track,manual:()->Unit){
        if(stemBusy||lyricsBusy){toast("Дождитесь завершения обработки");return}
        val original=if(t.tempoRatio!=null)libraryIndex.get(t.group)?:t else t
        fun scan(online:Boolean,deep:Boolean){
            if(original.uri!=original.group){manual();return}
            val live=libraryIndex.get(original.uri)?:run{toast("Песня недоступна");return}
            if(lyricsBusy||stemBusy)return
            scanLibrary(listOf(ScanItem(live.uri,live.title,live.artist,live.lyrics)),online,false,deep,deep)
        }
        actionSheet("Найти текст",490){dialog,panel->
            sheetAction(panel,"Автоматически","Из файла и интернета · безопасное сохранение"){dialog.dismiss();scan(true,false)}
            sheetAction(panel,"По вокалу → найти оригинал","Whisper + поиск в интернете"){dialog.dismiss();recognizeAndReview(t)}
            sheetAction(panel,"Поиск в браузере","По названию и исполнителю"){dialog.dismiss();lyricWebSearch(t)}
            sheetAction(panel,"Вставить и синхронизировать","Готовые слова → автоматические субтитры"){dialog.dismiss();pasteAndSync(t)}
            sheetAction(panel,"Вся медиатека","Один запуск для всех песен"){dialog.dismiss();batchLyrics()}
            sheetAction(panel,"Другие источники","Метаданные, браузер, распознавание"){dialog.dismiss()
                actionSheet("Источники текста",420){sources,content->
                    sheetAction(content,"Импортировать текст","LRC или TXT"){sources.dismiss();lyricTarget=t.uri;lyricRevision=lyricRevision(t);lyricPicker.launch(arrayOf("*/*"))}
                    sheetAction(content,"Только из аудиофайла","Офлайн · встроенный текст"){sources.dismiss();scan(false,false)}
                    sheetAction(content,"Уточнить название и исполнителя","Онлайн-поиск с выбором результата"){sources.dismiss();manual()}
                    val raw=rawLyrics(t)
                    if(raw.isNotBlank())sheetAction(content,"Уточнить время текста","Whisper · слова сохраняются"){sources.dismiss();alignKnownLyrics(t,raw)}
                }
            }
        }
    }
'''+anchor)
# Replace the checkbox-heavy bulk dialog with a default action and a secondary mode sheet.
a=s.index('        actionSheet("Сканирование библиотеки",390)')
b=s.index('    private fun scanKey(',a)
s=s[:a]+'''        val ready=WhisperLocal.available&&WhisperLocal.installed(this)!=null
        val songs=tracks.filter{it.uri==it.group}
        val states=songs.associate{it.uri to lyricState(it)}
        val done=states.values.count{it==LyricScanState.State.WORDS||it==LyricScanState.State.LINES}
        val pendingSmart=songs.filter{LyricScanState.pending(states.getValue(it.uri),lyricAttempt(it)!=null,false)}
        val retry=songs.filter{LyricScanState.pending(states.getValue(it.uri),lyricAttempt(it)!=null,true)}
        fun launch(items:List<Track>){
            if(!ready){whisperModelDialog();return}
            if(items.isEmpty()){lyricScanLog();return}
            scanLibrary(items.map{ScanItem(it.uri,it.title,it.artist,it.lyrics)},true,false,true,true,true)
        }
        actionSheet("Тексты медиатеки",430){dialog,panel->
            panel.addView(label("С субтитрами: "+done+" / "+songs.size,20,PremiumChrome.TEXT,true))
            panel.addView(label("Нужно проверить: "+states.values.count(LyricScanState::needsReview)+" · Не обработано: "+pendingSmart.size,14,muted))
            sheetAction(panel,if(pendingSmart.isEmpty())"Все новые песни проверены" else "Умное сканирование · "+pendingSmart.size,
                if(ready)"Метаданные, интернет, локальный Whisper · продолжение с оставшихся" else "Нужна локальная модель Whisper"){
                dialog.dismiss();launch(pendingSmart)
            }
            sheetAction(panel,"Журнал и фильтры","Все песни · готовые, без текста и с ошибками"){dialog.dismiss();lyricScanLog()}
            if(retry.isNotEmpty())sheetAction(panel,"Повторить неполные · "+retry.size,"Проверить снова без готовых пословных текстов"){dialog.dismiss();launch(retry)}
            sheetAction(panel,"Другие режимы","Быстрый поиск, офлайн и анализ музыки"){dialog.dismiss()
                actionSheet("Режим сканирования",350){options,content->
                    sheetAction(content,"Быстрый поиск","Метаданные + интернет, без Whisper"){options.dismiss();scanLibrary(pending,true,false,false,false)}
                    sheetAction(content,"Только метаданные","Без интернета"){options.dismiss();scanLibrary(pending,false,false,false,false)}
                    sheetAction(content,"Анализ музыки","Темп, тональность, подборки"){options.dismiss();scanLibrary(pending,false,true,false,false)}
                }
            }
        }
    }
'''+s[b:]
# Move per-track overflow into the existing row; native 3-dot icon and common custom sheet.
a=s.index('        body.addView(btn("Ещё"){val actions=')
b=s.index('\n',a)
s=s[:a]+'''        for(j in 0 until modes.childCount){
            val control=modes.getChildAt(j) as? Button?:continue
            control.background=PremiumChrome.ripple(0xff252930.toInt(),dp(12).toFloat())
            control.setTextColor(PremiumChrome.TEXT)
            control.minHeight=dp(48);control.minimumHeight=dp(48)
            val lp=control.layoutParams as LinearLayout.LayoutParams
            lp.marginEnd=dp(6);control.layoutParams=lp
        }
        val overflow=btn("⋮"){
            if(current()?.uri!=t.uri){toast("Композиция изменилась");return@btn}
            actionSheet("Композиция",if(proMode())450 else 320){dialog,panel->
                fun action(name:String,run:()->Unit){
                    sheetAction(panel,name){
                        dialog.dismiss()
                        if(current()?.uri!=t.uri){toast("Композиция изменилась");return@sheetAction}
                        run()
                    }
                }
                action("Версии"){screen="Версии";render()}
                action("Микшер"){screen="Микшер";render()}
                action("Студия"){screen="Студия";render()}
                action("Таймер и переходы"){playbackOptionsDialog()}
                if(proMode()){action("Повтор A/B"){loopDialog()};action("Вырезать фрагмент"){clipDialog(t)}}
                action("Эквалайзер"){screen="Эквалайзер";render()}
            }
        }.apply{contentDescription="Другие действия с композицией";background=PremiumChrome.ripple(Color.TRANSPARENT,dp(12).toFloat());setTextColor(PremiumChrome.TEXT)}
        modes.addView(overflow,LinearLayout.LayoutParams(dp(48),dp(48)))'''+s[b:]

rep('body.addView(whisperButton,3)','body.addView(whisperButton,3);whisperButton.visibility=View.GONE')
# A transcript is a draft; compare against candidates before the user accepts it.
(Path(sys.argv[1])/'app/src/main/java/app/remix/player/TranscriptMatch.kt').write_bytes((Path(__file__).parent/'TranscriptMatch.kt').read_bytes())
(Path(sys.argv[1])/'app/src/main/java/app/remix/player/LyricScanState.kt').write_bytes((Path(__file__).parent/'LyricScanState.kt').read_bytes())
(Path(sys.argv[1])/'app/src/main/java/app/remix/player/BrowserLyricImport.kt').write_bytes((Path(__file__).parent/'BrowserLyricImport.kt').read_bytes())
assets=Path(sys.argv[1])/'app/src/main/assets';assets.mkdir(parents=True,exist_ok=True)
(assets/'lyrics-extract.js').write_bytes((Path(__file__).parent/'lyrics-extract.js').read_bytes())
anchor='    private fun scanDraftReview(){'
rep(anchor,r'''    private fun lyricAttempt(t:Track):String? {
        val raw=getSharedPreferences("lyric_scan_v1",MODE_PRIVATE).getString(scanKey(t.uri),null)?:return null
        val prefix=lyricRevision(t)+":"
        return raw.takeIf{it.startsWith(prefix)}?.substring(prefix.length)
    }
    private fun recordLyricAttempt(t:Track,outcome:String){
        val ok=getSharedPreferences("lyric_scan_v1",MODE_PRIVATE).edit().putString(scanKey(t.uri),lyricRevision(t)+":"+outcome).commit()
        if(!ok)android.util.Log.w("RemixLyrics","Could not persist scan status")
    }
    private fun lyricState(t:Track):LyricScanState.State {
        val raw=rawLyrics(t);val lines=Lrc.parse(raw)
        return LyricScanState.classify(raw.isNotBlank(),lines.isNotEmpty(),lines.isNotEmpty()&&lines.all{WordLyrics.parse(it).words.isNotEmpty()},scanDraftFile(t.uri).isFile,lyricAttempt(t))
    }
    private fun lyricScanLog(filter:Int=0,page:Int=0){
        if(stemBusy||lyricsBusy){toast("Дождитесь завершения обработки");return}
        val rows=tracks.filter{it.uri==it.group}.map{it to lyricState(it)}
        val filters=listOf("Нужна проверка","Все песни","С субтитрами","Без текста","Не проверено")
        val selected=filter.coerceIn(filters.indices)
        val filtered=rows.filter{(_,state)->when(selected){
            0->LyricScanState.needsReview(state)
            2->state==LyricScanState.State.WORDS||state==LyricScanState.State.LINES
            3->state in setOf(LyricScanState.State.REVIEW,LyricScanState.State.ERROR,LyricScanState.State.MISSING,LyricScanState.State.NEW)
            4->state==LyricScanState.State.NEW
            else->true
        }}
        val pageStart=(page.coerceAtLeast(0)*30).coerceAtMost(((filtered.size-1).coerceAtLeast(0)/30)*30)
        actionSheet("Журнал текстов",500){dialog,panel->
            panel.addView(btn(filters[selected]+" · "+filtered.size){
                android.app.AlertDialog.Builder(this).setTitle("Фильтр песен").setItems(filters.toTypedArray()){_,i->dialog.dismiss();lyricScanLog(i)}.show()
            })
            if(filtered.isEmpty())panel.addView(label("В этом разделе нет песен",15,muted))
            filtered.drop(pageStart).take(30).forEach{(t,state)->sheetAction(panel,t.title,state.label+" · "+t.artist){
                dialog.dismiss()
                actionSheet(t.title,350){song,actions->
                    actions.addView(label(state.label+" · "+t.artist,14,muted))
                    sheetAction(actions,"Воспроизвести"){song.dismiss();start(t)}
                    if(scanDraftFile(t.uri).isFile)sheetAction(actions,"Проверить черновик"){song.dismiss();recognizeAndReview(t)}
                    sheetAction(actions,"Найти в браузере"){song.dismiss();lyricWebSearch(t)}
                    sheetAction(actions,"Вставить и синхронизировать"){song.dismiss();pasteAndSync(t)}
                    if(rawLyrics(t).isNotBlank())sheetAction(actions,"Уточнить субтитры"){song.dismiss();syncPastedLyrics(t,rawLyrics(t))}
                }
            }}
            if(filtered.size>30){
                val nav=row()
                if(pageStart>0)nav.addView(btn("←"){dialog.dismiss();lyricScanLog(selected,pageStart/30-1)},weight())
                nav.addView(label((pageStart+1).toString()+"–"+minOf(pageStart+30,filtered.size)+" / "+filtered.size,14,muted),weight())
                if(pageStart+30<filtered.size)nav.addView(btn("→"){dialog.dismiss();lyricScanLog(selected,pageStart/30+1)},weight())
                panel.addView(nav)
            }
        }
    }
    private fun pasteAndSync(t:Track,initial:String=""){
        if(stemBusy||lyricsBusy){toast("Дождитесь завершения обработки");return}
        val source=libraryIndex.get(t.group)?:t
        val revision=lyricRevision(source)
        actionSheet("Вставить текст песни",460){dialog,panel->
            panel.addView(label("Вставьте правильные слова. Whisper сам попробует определить время строк и слов на оригинальной записи.",14,muted))
            val editor=EditText(this).apply{
                hint="Слова песни";setText(initial);setTextColor(PremiumChrome.TEXT);setHintTextColor(muted)
                gravity=android.view.Gravity.TOP;minLines=5;maxLines=9
                filters=arrayOf(android.text.InputFilter.LengthFilter(LyricDocument.MAX_CHARS))
                inputType=android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE
            }
            panel.addView(editor,LinearLayout.LayoutParams(-1,dp(170)))
            sheetAction(panel,"Вставить из буфера"){
                val clipboard=getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                val raw=clipboard.primaryClip?.takeIf{it.itemCount>0}?.getItemAt(0)?.text?.toString().orEmpty()
                val clean=BrowserLyricImport.candidate(raw)
                if(clean==null)toast("В буфере нет подходящего текста")else editor.setText(clean)
            }
            sheetAction(panel,"Синхронизировать и проверить","Метки только из распознавания вокала"){
                val clean=BrowserLyricImport.candidate(editor.text.toString())
                if(clean==null){toast("Введите слова песни, а не ссылку");return@sheetAction}
                val live=libraryIndex.get(source.uri)
                if(live==null||lyricRevision(live)!=revision){toast("Песня или текст изменились");dialog.dismiss();return@sheetAction}
                dialog.dismiss();syncPastedLyrics(live,clean)
            }
        }
    }
    private fun syncPastedLyrics(t:Track,input:String,knownDraft:String?=null){
        if(stemBusy||lyricsBusy)return
        val source=libraryIndex.get(t.group)?:t
        val id=source.uri;val revision=lyricRevision(source)
        val clean=BrowserLyricImport.candidate(input)?:run{toast("Не удалось прочитать текст");return}
        val reference=LyricDocument.plain(clean).trim()
        if(reference.isBlank()){toast("Нет слов песни");return}
        val previous=rawLyrics(source)
        val cached=knownDraft?:runCatching{val f=scanDraftFile(id);require(f.length() in 1..262144);f.readText()}.getOrNull()
        val modelReady=WhisperLocal.available&&WhisperLocal.installed(this)!=null
        stemWork("Подгоняем субтитры по вокалу…",{
            // Reuse real timing when available; do not repeat inference unnecessarily.
            var best:KnownLyricAlignment.Result?=null
            for(heard in listOfNotNull(cached,previous).distinct()){
                if(Lrc.parse(heard).isEmpty())continue
                val result=KnownLyricAlignment.align(heard,reference)
                if(result?.wordLevel==true){best=result;break}
                if(best==null&&result!=null)best=result
            }
            if(best?.wordLevel!=true&&modelReady){
                val heard=try{scanRecognize(Uri.parse(id),id,reference)}catch(e:Exception){
                    if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e
                    ""
                }
                if(heard.isNotBlank()){
                    val result=KnownLyricAlignment.align(heard,reference)
                    if(result?.wordLevel==true||best==null)best=result
                }
            }
            check(!Thread.currentThread().isInterrupted)
            best
        }){aligned->
            val target=libraryIndex.get(id)
            if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@stemWork}
            val status=when{
                aligned?.wordLevel==true->"Синхронизация по словам"
                aligned!=null->"Синхронизация по строкам"
                !modelReady->"Нет модели Whisper · текст без времени"
                else->"Нет надёжного совпадения · текст без времени"
            }
            actionSheet("Проверить субтитры",300){dialog,panel->
                panel.addView(label(status,16,PremiumChrome.TEXT,true))
                if(aligned==null)panel.addView(label("Существующие метки не меняются без вашего подтверждения. Можно сохранить слова без времени или вернуться.",14,muted))
                else panel.addView(label("Слова сохранены в исходном написании. Проверьте найденные временные метки.",14,muted))
                sheetAction(panel,if(aligned==null)"Проверить обычный текст" else "Проверить и сохранить"){
                    dialog.dismiss()
                    reviewTranscript(status,aligned?.lrc?:reference){accepted->
                        val live=libraryIndex.get(id)
                        if(live==null||lyricRevision(live)!=revision){toast("Песня или текст изменились");return@reviewTranscript}
                        val before=live.lyrics;live.lyrics=accepted
                        if(saveLibrary(true)){scanDraftFile(id).delete();render();toast("Текст сохранён для офлайн-просмотра")}
                        else{live.lyrics=before;reindex();toast("Не удалось сохранить текст")}
                    }
                }
                if(!modelReady&&aligned==null)sheetAction(panel,"Установить Whisper"){dialog.dismiss();whisperModelDialog()}
                sheetAction(panel,"Вернуться к тексту"){dialog.dismiss();pasteAndSync(source,reference)}
            }
        }
    }
    @android.annotation.SuppressLint("SetJavaScriptEnabled")
    private fun lyricWebSearch(t:Track,phrase:String?=null,knownDraft:String?=null){
        if(stemBusy||lyricsBusy)return
        val source=libraryIndex.get(t.group)?:t
        val revision=lyricRevision(source)
        val url=BrowserLyricImport.url(source.title,source.artist,phrase)
        val script=runCatching{assets.open("lyrics-extract.js").bufferedReader().use{it.readText()}}.getOrNull()
        if(script==null){openLyricBrowser(BrowserLyricImport.query(source.title,source.artist,phrase));return}
        val dialog=android.app.Dialog(this)
        dialog.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE)
        val panel=column()
        val info=label("Поиск текста · выберите результат",14,muted)
        panel.addView(info)
        val web=android.webkit.WebView(this)
        panel.addView(web,LinearLayout.LayoutParams(-1,0,1f))
        var candidate:String?=null
        var generation=0
        var disposed=false
        val actions=row()
        val importButton=btn("Импортировать найденный текст"){
            val text=candidate?:return@btn
            val live=libraryIndex.get(source.uri)
            if(live==null||lyricRevision(live)!=revision){toast("Песня или текст изменились");dialog.dismiss();return@btn}
            dialog.dismiss();syncPastedLyrics(live,text,knownDraft)
        }.apply{isEnabled=false}
        panel.addView(importButton)
        fun extract(){
            if(disposed||web.url?.startsWith("https://")!=true)return
            val token=generation;val page=web.url
            web.evaluateJavascript(script){json->
                if(disposed||generation!=token||web.url!=page)return@evaluateJavascript
                val value=runCatching{org.json.JSONTokener(json?:"null").nextValue() as? String}.getOrNull()
                candidate=value?.let(BrowserLyricImport::candidate)
                importButton.isEnabled=candidate!=null
                info.text=if(candidate!=null)"Текст найден · можно импортировать и синхронизировать" else "Готового блока слов не найдено · откройте результат или повторите проверку"
            }
        }
        actions.addView(btn("Назад"){if(web.canGoBack())web.goBack()else dialog.dismiss()},weight())
        actions.addView(btn("Проверить страницу"){extract()},weight())
        panel.addView(actions)
        panel.addView(btn("Вставить текст вручную"){dialog.dismiss();pasteAndSync(source)})
        panel.addView(btn("Открыть обычный браузер"){
            val link=web.url?.takeIf{it.startsWith("https://")}?:url
            dialog.dismiss();pasteAndSync(source)
            runCatching{startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW,Uri.parse(link)))}.onFailure{toast("Браузер недоступен")}
        })
        web.settings.apply{
            javaScriptEnabled=true
            allowFileAccess=false;allowContentAccess=false
            setAllowFileAccessFromFileURLs(false);setAllowUniversalAccessFromFileURLs(false)
            mixedContentMode=android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            safeBrowsingEnabled=true
            setGeolocationEnabled(false);setSupportMultipleWindows(false)
            javaScriptCanOpenWindowsAutomatically=false
        }
        android.webkit.CookieManager.getInstance().setAcceptThirdPartyCookies(web,false)
        web.webViewClient=object:android.webkit.WebViewClient(){
            override fun shouldOverrideUrlLoading(view:android.webkit.WebView,request:android.webkit.WebResourceRequest):Boolean =
                request.url.scheme!="https"
            override fun onPageStarted(view:android.webkit.WebView,url:String?,favicon:android.graphics.Bitmap?){
                generation++;candidate=null;importButton.isEnabled=false;info.text="Загрузка страницы…"
            }
            override fun onPageFinished(view:android.webkit.WebView,url:String?){if(url==view.url)extract()}
        }
        dialog.setContentView(panel)
        dialog.setOnDismissListener{
            disposed=true;web.stopLoading();(web.parent as? ViewGroup)?.removeView(web);web.destroy()
        }
        dialog.show()
        dialog.window?.setLayout(-1,-1)
        web.loadUrl(url)
    }
    private fun recognizeAndReview(t:Track){
        if(stemBusy||lyricsBusy)return
        val original=libraryIndex.get(t.group)?:t
        val id=original.uri;val revision=lyricRevision(original)
        val draft=scanDraftFile(id)
        val cached=runCatching{require(draft.length() in 1..262144);draft.readText()}.getOrNull()
        if(!cached.isNullOrBlank()){transcriptChoices(original,cached,revision,true);return}
        if(!WhisperLocal.available||WhisperLocal.installed(this)==null){whisperModelDialog();return}
        stemWork("Whisper · распознавание вокала…",{scanRecognize(Uri.parse(id),id)}){raw->
            val target=libraryIndex.get(id)
            if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@stemWork}
            if(!saveScanDraft(id,raw))toast("Не удалось записать черновик на диск")
            transcriptChoices(target,raw,revision,true)
        }
    }
    private fun transcriptChoices(source:Track,raw:String,revision:String,autoSearch:Boolean=false){
        val id=source.uri
        val heard=LyricDocument.plain(raw)
        val phrase=TranscriptMatch.query(heard)
        fun accept(candidate:String,verify:Boolean){
            if(verify){
                val target=libraryIndex.get(id)
                if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return}
                syncPastedLyrics(target,candidate,raw);return
            }
            val clean=runCatching{LyricDocument.decode(candidate.toByteArray(Charsets.UTF_8))}.getOrElse{toast(it.message?:"Некорректный текст");return}
            val text=LyricDocument.plain(clean)
            if(text.isBlank()){toast("Нет текста");return}
            // A raw draft is kept with its measured timing, pending explicit confirmation.
            val prepared=clean
            if(prepared.toByteArray(Charsets.UTF_8).size>LyricDocument.MAX_BYTES){toast("Текст слишком большой");return}
            reviewTranscript("Whisper · черновик",prepared){accepted->
                val target=libraryIndex.get(id)
                if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@reviewTranscript}
                val before=target.lyrics;target.lyrics=accepted
                if(saveLibrary(true)){scanDraftFile(id).delete();render();toast("Текст сохранён для офлайн-просмотра")}
                else{target.lyrics=before;reindex();toast("Не удалось сохранить текст")}
            }
        }
        fun findOriginal(){
                if(stemBusy||lyricsBusy)return
                val title=source.title;val artist=source.artist
                stemWork("Ищем оригинальный текст…",{
                    val found=try{TrackLyricSource.search(this,Uri.parse(id),title,artist,null).first}catch(e:Exception){
                        if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e
                        emptyList()
                    }
                    found.mapNotNull{item->
                        val text=LyricDocument.plain(item.plain?:item.synced?:return@mapNotNull null)
                        val score=TranscriptMatch.score(heard,text)
                        if(score.plausible)Triple(item,text,score)else null
                    }.sortedWith(compareByDescending<Triple<LyricsMatch.Candidate,String,TranscriptMatch.Score>>{it.third.fraction}.thenByDescending{it.third.matching}).take(5)
                }){matches->
                    val target=libraryIndex.get(id)
                    if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@stemWork}
                    actionSheet("Варианты оригинала",440){results,content->
                        if(matches.isEmpty())content.addView(label("Каталог недоступен или надёжных совпадений нет. Черновик сохранён.",14,muted))
                        matches.forEach{(item,text,score)->
                            sheetAction(content,item.title+" · "+item.artist,"Совпало фраз: "+score.matching+" / "+score.total){results.dismiss();actionSheet("Сравнить тексты",460){compare,preview->
                                preview.addView(label("Распознано Whisper",14,muted,true));preview.addView(label(heard.take(420),15,PremiumChrome.TEXT))
                                preview.addView(label("Найденный вариант",14,muted,true));preview.addView(label(text.take(420),15,PremiumChrome.TEXT))
                                sheetAction(preview,"Проверить и сохранить","Полный текст и проверка временных меток"){compare.dismiss();accept(text,true)}
                                sheetAction(preview,"Назад"){compare.dismiss();transcriptChoices(source,raw,revision)}
                            }}
                        }
                        sheetAction(content,"Поиск по фразе в браузере","Открыть результат и импортировать найденный текст"){results.dismiss();lyricWebSearch(source,phrase,raw)}
                        sheetAction(content,"Назад к черновику"){results.dismiss();transcriptChoices(source,raw,revision)}
                    }
                }
        }
        if(autoSearch&&!stemBusy&&!lyricsBusy){findOriginal();return}
        actionSheet("Распознанный текст",460){dialog,panel->
            panel.addView(label(heard.take(700),14,PremiumChrome.TEXT))
            sheetAction(panel,"Найти оригинал","Интернет в фоне · сверка с распознанными словами"){dialog.dismiss();findOriginal()}
            sheetAction(panel,"Поиск по фразе в браузере","Найденные слова можно импортировать автоматически"){dialog.dismiss();lyricWebSearch(source,phrase,raw)}
            sheetAction(panel,"Вставить текст из браузера","Скопируйте слова песни, затем нажмите здесь"){
                val clipboard=getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                val value=clipboard.primaryClip?.takeIf{it.itemCount>0}?.getItemAt(0)?.text?.toString().orEmpty()
                if(value.isBlank()||value.toByteArray(Charsets.UTF_8).size>LyricDocument.MAX_BYTES){toast("Скопируйте текст песни, не ссылку");return@sheetAction}
                if(value.trim().startsWith("https://")||value.trim().startsWith("http://")){toast("Нужны слова песни, а не ссылка");return@sheetAction}
                val score=TranscriptMatch.score(heard,LyricDocument.plain(value))
                if(!score.plausible){
                    android.app.AlertDialog.Builder(this).setTitle("Слабое совпадение").setMessage("Скопированный текст мало похож на распознанный вокал. Проверьте, что это та же песня.").setNegativeButton("Отмена",null).setPositiveButton("Проверить вручную"){_,_->dialog.dismiss();accept(value,true)}.show()
                }else{dialog.dismiss();accept(value,true)}
            }
            sheetAction(panel,"Проверить черновик Whisper","Оставить локально распознанные слова"){dialog.dismiss();accept(raw,false)}
        }
    }
'''+anchor)
a=s.index('                reviewTranscript("Whisper",raw){accepted->',s.index('    private fun scanDraftReview(){'))
b=s.index('            }}',a)
s=s[:a]+'''                transcriptChoices(t,raw,lyricRevision(t))
'''+s[b:]
rep('if(tracks.isNotEmpty())body.addView(btn("Настроение и подборки"){moodDiscoveryDialog()});val tools=row();tools.addView(filter,weight());','if(tracks.isNotEmpty()){val quick=row();quick.addView(btn("Подборки"){moodDiscoveryDialog()},weight());quick.addView(btn("Тексты"){batchLyrics()},weight());body.addView(quick)};val tools=row();tools.addView(filter,weight());')
# System-managed automatic scan. The active library remains owned by the Activity.
import re
for filename in ('AutoLyricsJob.kt','TrackIdentityFix.kt'):
    (p.parent/filename).write_bytes((Path(__file__).parent/filename).read_bytes())
manifest=Path(sys.argv[1])/'app/src/main/AndroidManifest.xml'
xml=manifest.read_text()
assert xml.count('</application>')==1
xml=xml.replace('</application>','    <service android:name=".AutoLyricsJob" android:permission="android.permission.BIND_JOB_SERVICE" android:exported="false"/>\n    </application>')
if 'android.permission.RECEIVE_BOOT_COMPLETED' not in xml:
    xml=xml.replace('<application ','<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />\n    <application ',1)
manifest.write_text(xml)
# Prevent two native Whisper sessions from competing for phone memory.
whisper=p.parent/'WhisperLocal.kt'
w=whisper.read_text()
anchor='fun transcribe(c:Context,uri:Uri,stem:StemEngine.Bundle?,language:String,status:(String)->Unit):String{'
assert w.count(anchor)==1
whisper.write_text(w.replace(anchor,'@Synchronized '+anchor+'\n        check(!Thread.currentThread().isInterrupted)'))
rep('    private fun lyricAttempt(t:Track):String? {',r'''    private fun mergeAutomaticLyrics():Boolean{
        if(stemBusy||lyricsBusy)return false
        data class Pending(val file:java.io.File,val entry:JSONObject,val index:Int,val before:Track,val after:Track)
        val pending=mutableListOf<Pending>()
        for(file in AutoLyrics.staged(this)){
            val result=AutoLyrics.read(file)?:continue
            val id=result.optString("uri")
            val current=libraryIndex.get(id)?.takeIf{it.uri==it.group}
            if(current==null){file.delete();continue}
            val revision=AutoLyrics.revision(id,current.title,current.artist,current.lyrics)
            if(result.optString("revision")!=revision){file.delete();continue}
            val index=tracks.indexOfFirst{it.uri==id};if(index<0)continue
            val text=if(result.isNull("raw"))current.lyrics else result.optString("raw").takeIf{it.length<=LyricDocument.MAX_CHARS&&it.isNotBlank()}?:current.lyrics
            val title=result.optString("title").takeIf{it.isNotBlank()&&it.length<=300}?:current.title
            val artist=result.optString("artist").takeIf{it.isNotBlank()&&it.length<=200}?:current.artist
            val after=current.copy(title=title,artist=artist,lyrics=text)
            pending.add(Pending(file,result,index,current,after))
        }
        if(pending.isEmpty())return false
        val changed=pending.any{it.before!=it.after}
        if(changed){
            pending.forEach{tracks[it.index]=it.after}
            if(!saveLibrary(true)){pending.forEach{tracks[it.index]=it.before};reindex();return false}
        }
        for(entry in pending){
            val t=entry.after;val result=entry.entry
            val draft=result.optString("draft").takeIf{!result.isNull("draft")&&it.isNotBlank()}
            val stored=draft==null||saveScanDraft(t.uri,draft)
            if(!stored){recordLyricAttempt(t,"error");continue}
            val outcome=result.optString("outcome")
            if(outcome!="waiting")recordLyricAttempt(t,if(outcome=="error")"error" else "done")
            val rev=AutoLyrics.revision(t.uri,t.title,t.artist,t.lyrics)
            if(AutoLyrics.mark(this,t.uri,rev,outcome)&&AutoLyrics.read(entry.file)?.optString("revision")==result.optString("revision"))entry.file.delete()
        }
        return changed
    }
    private fun automaticLyricsSettings(){
        val enabled=AutoLyrics.enabled(this)
        actionSheet("Автоматические тексты",330){dialog,panel->
            panel.addView(label(if(enabled)"Автоматическая обработка включена" else "Автоматическая обработка выключена",16,PremiumChrome.TEXT,true))
            panel.addView(label("Android запускает задачи при зарядке, достаточной памяти и неметрируемой сети. Экран может быть выключен. Готовые тексты и подтверждённые данные сохраняются отдельно, спорные — в журнале. Аудио остаётся на телефоне.",14,muted))
            sheetAction(panel,if(enabled)"Выключить автосканирование" else "Включить автосканирование"){
                dialog.dismiss()
                if(!AutoLyrics.setEnabled(this,!enabled)){toast("Не удалось изменить режим");return@sheetAction}
                toast(if(enabled)"Автосканирование выключено" else "Автосканирование включено")
                batchLyrics()
            }
            if(!enabled&&(!WhisperLocal.available||WhisperLocal.installed(this)==null))sheetAction(panel,"Установить Whisper","Для локальной синхронизации"){dialog.dismiss();whisperModelDialog()}
        }
    }
    private fun lyricAttempt(t:Track):String? {''')
rep('    private fun batchLyrics(){','    private fun batchLyrics(){\n        mergeAutomaticLyrics()')
rep('            sheetAction(panel,"Журнал и фильтры","Все песни · готовые, без текста и с ошибками")','            sheetAction(panel,if(AutoLyrics.enabled(this))"Автосканирование: включено" else "Автосканирование: выключено","При зарядке и Wi-Fi · без открытого экрана"){dialog.dismiss();automaticLyricsSettings()}\n            sheetAction(panel,"Журнал и фильтры","Все песни · готовые, без текста и с ошибками")')
rep('actionSheet("Тексты медиатеки",430)','actionSheet("Тексты медиатеки",480)')
rep('val filters=listOf("Нужна проверка","Все песни","С субтитрами","Без текста","Не проверено")','val filters=listOf("Нужна проверка","Все песни","С субтитрами","Без текста","Не проверено","Без исполнителя")')
rep('val filtered=rows.filter{(_,state)->when(selected){','val filtered=rows.filter{(track,state)->when(selected){')
rep('            4->state==LyricScanState.State.NEW','            4->state==LyricScanState.State.NEW\n            5->!TrackIdentityFix.knownArtist(track.artist)')
# Apply staged results after Activity initialization, not while loading an incomplete library.
resume=re.search(r'override\s+fun\s+onResume\s*\(\s*\)\s*\{',s)
if resume:
    i=resume.end()
    assert s[i:].lstrip().startswith('super.onResume()')
    j=s.index('super.onResume()',i)+len('super.onResume()')
    s=s[:j]+';AutoLyrics.schedule(this);if(mergeAutomaticLyrics())render();'+s[j:]
else:
    anchor='override fun onDestroy(){'
    assert s.count(anchor)==1
    s=s.replace(anchor,'override fun onResume(){super.onResume();AutoLyrics.schedule(this);if(mergeAutomaticLyrics())render()}\n    '+anchor)
# Reuse existing translation storage/backup format, validate exact line identity and stale results.
a=s.index('    private fun translateLyrics(t:Track,raw:String,source:String,target:String,download:Boolean){')
b=s.index('\n',a)
s=s[:a]+'''    private fun translateLyrics(t:Track,raw:String,source:String,target:String,download:Boolean){
        if(translationBusy||stemBusy)return
        val timed=Lrc.parse(raw)
        val reference=if(timed.isNotEmpty())timed.map{WordLyrics.parse(it).text}else searchableLyricLines(raw).map{it.text}
        if(reference.isEmpty()||reference.size>2000){toast("Неподдерживаемое количество строк");return}
        val id=t.uri;val revision=lyricRevision(t)
        translationBusy=true;render()
        io.execute{
            val result=runCatching{LyricTranslation.translate(reference,source,target,download)}
            runOnUiThread{
                if(!isDestroyed){
                    translationBusy=false
                    result.onSuccess{values->
                        val live=libraryIndex.get(id)
                        if(live==null||lyricRevision(live)!=revision){toast("Песня или текст изменились; перевод не сохранён")}
                        else if(values.size!=reference.size||values.indices.any{i->values[i].length>4000||(reference[i].isNotBlank()&&values[i].isBlank())}||values.sumOf{it.length}>256000){toast("Перевод неполный")}
                        else if(getSharedPreferences("translations",MODE_PRIVATE).edit().putString(translationKey(live,raw),JSONArray(values).toString()).commit()){toast("Перевод сохранён")}
                        else toast("Не удалось сохранить перевод")
                    }.onFailure{toast("Перевод не выполнен: "+(it.message?:"ошибка"))}
                    render()
                }
            }
        }
    }'''+s[b:]
# Manual and automatic translations now share the renderer. Legacy manual entries are read only if the lyric revision matches.
rep('private fun translated(t:Track,raw:String):List<String> = runCatching{val a=JSONArray(getSharedPreferences("translations",MODE_PRIVATE).getString(translationKey(t,raw),"[]"));(0 until a.length()).map{a.getString(it)}}.getOrDefault(emptyList())', '''private fun translated(t:Track,raw:String):List<String>{
        fun stored(track:Track,value:String):List<String>{
            val prefs=getSharedPreferences("translations",MODE_PRIVATE)
            val key=translationKey(track,value)
            if(prefs.contains(key))return runCatching{val a=JSONArray(prefs.getString(key,"[]"));(0 until a.length()).map{a.getString(it)}}.getOrDefault(emptyList())
            val old=getSharedPreferences("bilingual_lyrics_v1",MODE_PRIVATE)
            val id=scanKey(track.uri)
            return if(old.getString(id+"_revision",null)==scanKey(value))LyricLineSearch.pair(searchableLyricLines(value),old.getString(id,"").orEmpty())?.map{it.translation}.orEmpty()else emptyList()
        }
        val own=stored(t,raw)
        if(own.isNotEmpty()||getSharedPreferences("translations",MODE_PRIVATE).contains(translationKey(t,raw)))return own
        val original=libraryIndex.get(t.group)
        if(original!=null&&original.uri!=t.uri&&t.tempoRatio!=null&&searchableLyricLines(raw).map{it.text}==searchableLyricLines(original.lyrics).map{it.text})return stored(original,original.lyrics)
        return emptyList()
    }''')
rep('body.addView(btn(if(translationBusy)"Перевод…" else "Перевести текст"){chooseTranslation(t,raw)});','')
rep('getSharedPreferences("translations",MODE_PRIVATE).edit().remove(translationKey(t,raw)).apply();render()','getSharedPreferences("translations",MODE_PRIVATE).edit().putString(translationKey(t,raw),"[]").apply();render()')
# Untimed lyrics can be translated as paired text, without pretending they are synchronized.
rep('val plain=label(raw,20,Color.WHITE);plain.setTextIsSelectable(true);body.addView(plain)','''val pairs=translated(t,raw)
                    val originals=searchableLyricLines(raw)
                    if(pairs.size==originals.size&&pairs.isNotEmpty()){
                        originals.forEachIndexed{idx,line->body.addView(label(line.text,20,PremiumChrome.TEXT,true));body.addView(label(pairs[idx],15,muted).apply{setPadding(0,dp(2),0,dp(12))})}
                    }else{val plain=label(raw,20,Color.WHITE);plain.setTextIsSelectable(true);body.addView(plain)}''')
rep('val tr=label(visibleTranslation[idx],15,muted);tr.setOnClickListener','val tr=label(visibleTranslation[idx],17,muted).apply{setPadding(0,dp(2),0,dp(14))};tr.setOnClickListener')
# Bounded second inference pass: try only incomplete phrases, retain the same words and observed timing.
(p.parent/'PhraseTimingRetry.kt').write_bytes((Path(__file__).parent/'PhraseTimingRetry.kt').read_bytes())
whisper=p.parent/'WhisperLocal.kt';w=whisper.read_text()
old='var start=0L;var fresh=0;val filter=VocalConditioning.Filter()'
assert w.count(old)==1
w=w.replace(old,old+';var retryBudget=8')
old='result.add(WhisperSegments.Window(offset,offset+ms,segments))'
assert w.count(old)==1
w=w.replace(old,'''val refined=if(prepared==null||retryBudget<=0)segments else segments.map{seg->
                        val span=PhraseTimingRetry.Span(seg.startMs,seg.endMs,seg.text,seg.wordStarts)
                        if(retryBudget<=0||!PhraseTimingRetry.eligible(span))seg else{
                            val from=((seg.startMs-offset-350).coerceAtLeast(0)*16).toInt().coerceIn(0,prepared.size)
                            val until=((seg.endMs-offset+350).coerceAtLeast(0)*16).toInt().coerceIn(from,prepared.size)
                            if(until-from<5600)seg else{
                                retryBudget--
                                check(!Thread.currentThread().isInterrupted)
                                val retryOffset=offset+from/16
                                val retryDuration=(until-from)/16L
                                val data=recognize(handle,prepared.copyOfRange(from,until),language,Runtime.getRuntime().availableProcessors().coerceIn(1,4),beam)
                                check(!Thread.currentThread().isInterrupted)
                                val alternatives=if(data==null)emptyList()else WhisperSegments.parse(data.toString(Charsets.UTF_8),retryOffset,retryDuration)
                                val recovered=PhraseTimingRetry.select(span,alternatives.map{PhraseTimingRetry.Span(it.startMs,it.endMs,it.text,it.wordStarts)})
                                if(recovered==null)seg else seg.copy(wordStarts=recovered)
                            }
                        }
                    }
                    result.add(WhisperSegments.Window(offset,offset+ms,refined))''')
whisper.write_text(w)
# Simultaneous words do not qualify as reliable per-word alignment.
align=p.parent/'LyricAlign.kt';al=align.read_text()
old='heard[b].second-heard[a].second in 0..3500'
assert al.count(old)==1
align.write_text(al.replace(old,'heard[b].second-heard[a].second in 1..3500'))
p.write_text(s)
print("PASS: persistent default-off PRO controls; core player unchanged")
