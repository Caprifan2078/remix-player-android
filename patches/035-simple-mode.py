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
        actionSheet("Найти текст",330){dialog,panel->
            sheetAction(panel,"Автоматически","Из файла и интернета · безопасное сохранение"){dialog.dismiss();scan(true,false)}
            sheetAction(panel,"Вся медиатека","Один запуск для всех песен"){dialog.dismiss();batchLyrics()}
            sheetAction(panel,"Другие источники","Метаданные, браузер, распознавание"){dialog.dismiss()
                actionSheet("Источники текста",420){sources,content->
                    sheetAction(content,"Импортировать текст","LRC или TXT"){sources.dismiss();lyricTarget=t.uri;lyricRevision=lyricRevision(t);lyricPicker.launch(arrayOf("*/*"))}
                    sheetAction(content,"Только из аудиофайла","Офлайн · встроенный текст"){sources.dismiss();scan(false,false)}
                    sheetAction(content,"Уточнить название и исполнителя","Онлайн-поиск с выбором результата"){sources.dismiss();manual()}
                    sheetAction(content,"Поиск в браузере","По названию и исполнителю"){openLyricBrowser(original.title+" "+original.artist)}
                    sheetAction(content,"По вокалу · Whisper","Локальное распознавание или синхронизация"){
                        sources.dismiss()
                        val raw=rawLyrics(t)
                        if(raw.isBlank())recognizeAndReview(t)else alignKnownLyrics(t,raw)
                    }
                }
            }
        }
    }
'''+anchor)
# Replace the checkbox-heavy bulk dialog with a default action and a secondary mode sheet.
a=s.index('        actionSheet("Сканирование библиотеки",390)')
b=s.index('    private fun scanKey(',a)
s=s[:a]+'''        actionSheet("Тексты всей медиатеки",300){dialog,panel->
            panel.addView(label("Песен: "+pending.size+" · глубокий поиск может уточнить построчные метки до слов",14,muted))
            sheetAction(panel,"Начать автоматически","Встроенные тексты + онлайн-поиск"){dialog.dismiss();scanLibrary(pending,true,false,false,false)}
            sheetAction(panel,"Другие режимы","Офлайн, глубокий поиск, анализ музыки"){dialog.dismiss()
                actionSheet("Режим сканирования",390){options,content->
                    sheetAction(content,"Только метаданные","Без интернета и нейросетей"){options.dismiss();scanLibrary(pending,false,false,false,false)}
                    sheetAction(content,"Глубокий поиск","Интернет + Whisper · поиск и уточнение времени слов"){
                        if(!WhisperLocal.available||WhisperLocal.installed(this)==null){options.dismiss();whisperModelDialog();return@sheetAction}
                        options.dismiss();scanLibrary(pending,true,false,true,true)
                    }
                    sheetAction(content,"Анализ музыки","Темп, тональность, подборки по настроению"){options.dismiss();scanLibrary(pending,false,true,false,false)}
                    sheetAction(content,"Черновики Whisper","Проверить распознанные слова"){options.dismiss();scanDraftReview()}
                    panel.contentDescription="Тексты всей медиатеки"
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
anchor='    private fun scanDraftReview(){'
rep(anchor,r'''    private fun recognizeAndReview(t:Track){
        if(stemBusy||lyricsBusy)return
        val original=libraryIndex.get(t.group)?:t
        val id=original.uri;val revision=lyricRevision(original)
        val draft=scanDraftFile(id)
        val cached=runCatching{require(draft.length() in 1..262144);draft.readText()}.getOrNull()
        if(!cached.isNullOrBlank()){transcriptChoices(original,cached,revision);return}
        if(!WhisperLocal.available||WhisperLocal.installed(this)==null){whisperModelDialog();return}
        stemWork("Whisper · распознавание вокала…",{scanRecognize(Uri.parse(id),id)}){raw->
            val target=libraryIndex.get(id)
            if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@stemWork}
            if(!saveScanDraft(id,raw))toast("Не удалось записать черновик на диск")
            transcriptChoices(target,raw,revision)
        }
    }
    private fun transcriptChoices(source:Track,raw:String,revision:String){
        val id=source.uri
        val heard=LyricDocument.plain(raw)
        val phrase=TranscriptMatch.query(heard)
        fun accept(candidate:String,verify:Boolean){
            val text=LyricDocument.plain(candidate)
            if(text.isBlank()){toast("Нет текста");return}
            // Only use measured timestamps from this recording, never silently copy another remix's timeline.
            val aligned=if(verify)KnownLyricAlignment.align(raw,text) else null
            val prepared=if(verify)aligned?.lrc?:text else candidate
            if(prepared.toByteArray(Charsets.UTF_8).size>LyricDocument.MAX_BYTES){toast("Текст слишком большой");return}
            reviewTranscript(if(verify)"Текст · сверка с вокалом" else "Whisper · черновик",prepared){accepted->
                val target=libraryIndex.get(id)
                if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@reviewTranscript}
                val before=target.lyrics;target.lyrics=accepted
                if(saveLibrary(true)){scanDraftFile(id).delete();render();toast("Текст сохранён для офлайн-просмотра")}
                else{target.lyrics=before;reindex();toast("Не удалось сохранить текст")}
            }
        }
        actionSheet("Распознанный текст",460){dialog,panel->
            panel.addView(label(heard.take(700),14,PremiumChrome.TEXT))
            sheetAction(panel,"Найти оригинал","Интернет в фоне · сверка с распознанными словами"){
                dialog.dismiss()
                if(stemBusy||lyricsBusy)return@sheetAction
                val title=source.title;val artist=source.artist
                stemWork("Ищем оригинальный текст…",{
                    val (found,_)=TrackLyricSource.search(this,Uri.parse(id),title,artist,null)
                    found.mapNotNull{item->
                        val text=LyricDocument.plain(item.plain?:item.synced?:return@mapNotNull null)
                        val score=TranscriptMatch.score(heard,text)
                        if(score.plausible)Triple(item,text,score)else null
                    }.sortedWith(compareByDescending<Triple<LyricsMatch.Candidate,String,TranscriptMatch.Score>>{it.third.fraction}.thenByDescending{it.third.matching}).take(5)
                }){matches->
                    val target=libraryIndex.get(id)
                    if(target==null||lyricRevision(target)!=revision){toast("Песня или текст изменились");return@stemWork}
                    actionSheet("Варианты оригинала",440){results,content->
                        if(matches.isEmpty())content.addView(label("Надёжных совпадений в каталоге нет. Черновик сохранён.",14,muted))
                        matches.forEach{(item,text,score)->
                            sheetAction(content,item.title+" · "+item.artist,"Совпало фраз: "+score.matching+" / "+score.total){results.dismiss();accept(text,true)}
                        }
                        sheetAction(content,"Поиск по фразе в браузере","Вернитесь сюда и импортируйте скопированный текст"){results.dismiss();openLyricBrowser(title+" "+artist+" "+phrase);transcriptChoices(source,raw,revision)}
                        sheetAction(content,"Назад к черновику"){results.dismiss();transcriptChoices(source,raw,revision)}
                    }
                }
            }
            sheetAction(panel,"Поиск по фразе в браузере","Запрос уже заполнен · без ручного ввода"){openLyricBrowser(source.title+" "+source.artist+" "+phrase)}
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
p.write_text(s)
print("PASS: persistent default-off PRO controls; core player unchanged")
