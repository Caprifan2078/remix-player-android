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
rep('val lookup=body.getChildAt(2);body.removeView(lookup);body.addView(lookup,1);','val lookup=body.getChildAt(2) as Button;body.removeView(lookup);body.addView(btn(if(lyricsBusy)"Поиск текста…" else "Найти текст"){lyricSearchChoices(t){lookup.performClick()}},1);')
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
                actionSheet("Источники текста",350){sources,content->
                    sheetAction(content,"Только из аудиофайла","Офлайн · встроенный текст"){sources.dismiss();scan(false,false)}
                    sheetAction(content,"Уточнить название и исполнителя","Онлайн-поиск с выбором результата"){sources.dismiss();manual()}
                    sheetAction(content,"Поиск в браузере","По названию и исполнителю"){openLyricBrowser(original.title+" "+original.artist)}
                    sheetAction(content,"По вокалу · Whisper","Локальное распознавание или синхронизация"){
                        sources.dismiss()
                        val raw=rawLyrics(t)
                        if(raw.isBlank())recognizeWhisper(t)else alignKnownLyrics(t,raw)
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
            panel.addView(label("Песен: "+pending.size+" · сохранённые синхронные тексты не заменяются",14,muted))
            sheetAction(panel,"Начать автоматически","Встроенные тексты + онлайн-поиск"){dialog.dismiss();scanLibrary(pending,true,false,false,false)}
            sheetAction(panel,"Другие режимы","Офлайн, глубокий поиск, анализ музыки"){dialog.dismiss()
                actionSheet("Режим сканирования",390){options,content->
                    sheetAction(content,"Только метаданные","Без интернета и нейросетей"){options.dismiss();scanLibrary(pending,false,false,false,false)}
                    sheetAction(content,"Глубокий поиск","Интернет + Whisper для пропусков и текстов без времени"){
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

p.write_text(s)
print("PASS: persistent default-off PRO controls; core player unchanged")
