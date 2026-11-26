#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt'
s=p.read_text()
anchor='    private fun calibrateLyrics(t:Track,raw:String){'
assert s.count(anchor)==1
helper=r'''    private fun searchableLyricLines(raw:String):List<LyricLineSearch.Line>{
        val timed=Lrc.parse(raw).mapNotNull{line->WordLyrics.parse(line).text.trim().takeIf{it.isNotEmpty()}?.let{LyricLineSearch.Line(it,line.ms)}}
        return timed.ifEmpty{LyricDocument.plain(raw).lineSequence().map{it.trim()}.filter{it.isNotEmpty()}.map{LyricLineSearch.Line(it)}.toList()}
    }
    private fun jumpFoundLyric(t:Track,raw:String,ms:Long?){
        if(ms==null){toast("У строки нет временной метки");return}
        if(current()?.uri!=t.uri||rawLyrics(t)!=raw){toast("Песня или текст изменились");return}
        if(MixerSession.active){
            if(MixerSession.request?.source!=t.uri){toast("Откройте нужную песню");return}
        }else if(controller?.currentMediaItem?.mediaId!=t.uri){toast("Включите нужную песню");return}
        seekLyrics(ms)
    }
    private fun findLyricLine(t:Track,raw:String){
        val lines=searchableLyricLines(raw)
        actionSheet("Поиск по тексту",480){dialog,panel->
            val search=EditText(this).apply{hint="Введите слова песни";setSingleLine(true);setTextColor(PremiumChrome.TEXT);setHintTextColor(muted);filters=arrayOf(android.text.InputFilter.LengthFilter(200))}
            panel.addView(search,LinearLayout.LayoutParams(-1,dp(52)))
            val results=column();panel.addView(results)
            fun fill(q:String){
                results.removeAllViews()
                if(q.isBlank()){results.addView(label("Поиск работает без интернета",14,muted));return}
                val found=LyricLineSearch.find(lines,q)
                results.addView(label(if(found.isEmpty())"Совпадений нет" else if(found.size==LyricLineSearch.MAX_RESULTS)"Первые 80 совпадений" else "Найдено: "+found.size,14,muted))
                found.forEach{line->sheetAction(results,line.text,line.ms?.let{fmt(it)}?:"Без тайминга"){
                    if(line.ms!=null){dialog.dismiss();jumpFoundLyric(t,raw,line.ms)}
                    else toast("Для перехода нужна синхронизация текста")
                }}
            }
            fill("")
            search.addTextChangedListener(object:android.text.TextWatcher{override fun beforeTextChanged(s:CharSequence?,start:Int,count:Int,after:Int){};override fun onTextChanged(s:CharSequence?,start:Int,before:Int,count:Int){fill(s?.toString().orEmpty())};override fun afterTextChanged(s:android.text.Editable?) {}})
        }
    }
    private fun bilingualLyrics(t:Track,raw:String){
        val lines=searchableLyricLines(raw)
        if(lines.isEmpty()){toast("Нет текста");return}
        val prefs=getSharedPreferences("bilingual_lyrics_v1",MODE_PRIVATE)
        val id=scanKey(t.uri);val stamp=scanKey(raw)
        val saved=if(prefs.getString(id+"_revision",null)==stamp)prefs.getString(id,"").orEmpty()else ""
        val paired=LyricLineSearch.pair(lines,saved)
        actionSheet("Оригинал и перевод",500){dialog,panel->
            panel.addView(label("Локальный перевод · "+lines.size+" строк. Вставьте готовый перевод в том же порядке. Автоперевод не используется.",14,muted))
            sheetAction(panel,"Добавить / изменить перевод","Одна строка перевода на строку оригинала"){
                dialog.dismiss()
                actionSheet("Редактор перевода",460){editDialog,content->
                    content.addView(label("Нужно непустых строк: "+lines.size,14,muted))
                    val editor=EditText(this).apply{setText(saved);hint="Вставьте перевод";setTextColor(PremiumChrome.TEXT);setHintTextColor(muted);gravity=Gravity.TOP;minLines=6;maxLines=12;filters=arrayOf(android.text.InputFilter.LengthFilter(64000))}
                    content.addView(editor,LinearLayout.LayoutParams(-1,dp(230)))
                    content.addView(btn("Сохранить"){
                        val value=editor.text.toString()
                        if(current()?.uri!=t.uri||rawLyrics(t)!=raw){toast("Песня или текст изменились");return@btn}
                        if(LyricLineSearch.pair(lines,value)==null){toast("Количество строк не совпадает");return@btn}
                        if(!prefs.edit().putString(id,value).putString(id+"_revision",stamp).commit()){toast("Не удалось сохранить перевод");return@btn}
                        editDialog.dismiss();bilingualLyrics(t,raw)
                    })
                    content.addView(btn("Удалить перевод"){
                        if(prefs.edit().remove(id).remove(id+"_revision").commit()){editDialog.dismiss();bilingualLyrics(t,raw)}else toast("Не удалось удалить перевод")
                    })
                }
            }
            if(paired!=null){
                val page=column();panel.addView(page)
                val nav=row();panel.addView(nav)
                var offset=0
                val status=label("",14,muted);panel.addView(status)
                fun fill(){
                    page.removeAllViews()
                    paired.drop(offset).take(40).forEach{line->sheetAction(page,line.original.text,line.translation+(line.original.ms?.let{" · "+fmt(it)}?:"")){
                        if(line.original.ms!=null){dialog.dismiss();jumpFoundLyric(t,raw,line.original.ms)}
                    }}
                    status.text=(offset+1).toString()+"–"+minOf(offset+40,paired.size)+" / "+paired.size
                }
                nav.addView(btn("Назад"){offset=(offset-40).coerceAtLeast(0);fill()},weight())
                nav.addView(btn("Далее"){if(offset+40<paired.size){offset+=40;fill()}},weight())
                fill()
            }
        }
    }
'''
s=s.replace(anchor,helper+anchor)
a='val raw=rawLyrics(t);if(raw.isNotBlank()&&!stemBusy)'
assert s.count(a)==1
s=s.replace(a,'val raw=rawLyrics(t);if(raw.isNotBlank()){val tools=row();tools.addView(btn("Найти строку"){findLyricLine(t,raw)},weight());tools.addView(btn("Перевод"){bilingualLyrics(t,raw)},weight());body.addView(tools)};if(raw.isNotBlank()&&!stemBusy)')
p.write_text(s)
print("PASS: offline lyric line search and local bilingual reader integration")
