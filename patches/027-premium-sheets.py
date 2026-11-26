#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b)
a=s.index('    private fun effectPicker(){')
b=s.index('    private fun reviewTranscript(',a)
s=s[:a]+'''    // Shared custom bottom sheet: no platform grey list dialog for common tasks.
    private fun actionSheet(title:String,height:Int,build:(android.app.Dialog,LinearLayout)->Unit){
        val dialog=android.app.Dialog(this)
        dialog.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE)
        val shell=column().apply{
            background=PremiumChrome.shape(0xff1d2025.toInt(),dp(26).toFloat())
            setPadding(dp(20),dp(10),dp(20),dp(14))
        }
        val handle=View(this).apply{background=PremiumChrome.shape(0xff61666d.toInt(),dp(2).toFloat())}
        shell.addView(handle,LinearLayout.LayoutParams(dp(42),dp(4)).apply{gravity=Gravity.CENTER_HORIZONTAL;bottomMargin=dp(12)})
        val head=row()
        head.addView(label(title,25,PremiumChrome.TEXT,true),weight())
        head.addView(btn("×"){dialog.dismiss()}.apply{contentDescription="Закрыть";textSize=24f;background=PremiumChrome.ripple(Color.TRANSPARENT,dp(20).toFloat())},LinearLayout.LayoutParams(dp(48),dp(48)))
        shell.addView(head)
        val content=column();val scroller=ScrollView(this).apply{isFillViewport=false;isVerticalScrollBarEnabled=false;addView(content)}
        val maxHeight=(resources.configuration.screenHeightDp-110).coerceAtLeast(120)
        shell.addView(scroller,LinearLayout.LayoutParams(-1,dp(minOf(height,maxHeight))))
        dialog.setContentView(shell);build(dialog,content);dialog.show()
        dialog.window?.apply{setBackgroundDrawableResource(android.R.color.transparent);setLayout(-1,-2);setGravity(Gravity.BOTTOM);addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);setDimAmount(.62f);setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)}
    }
    private fun sheetAction(panel:LinearLayout,title:String,subtitle:String="",selected:Boolean=false,action:()->Unit){
        val item=row().apply{gravity=Gravity.CENTER_VERTICAL;minimumHeight=dp(58);background=PremiumChrome.ripple(if(selected)0xff303a2b.toInt() else Color.TRANSPARENT,dp(12).toFloat());setPadding(dp(10),dp(2),dp(10),dp(2));isClickable=true;isFocusable=true}
        val words=column();words.addView(label(title,16,if(selected)accent else PremiumChrome.TEXT,true))
        if(subtitle.isNotBlank())words.addView(label(subtitle,12,muted))
        item.addView(words,weight())
        if(selected)item.addView(label("✓",20,accent,true))
        else item.addView(label("›",21,muted))
        item.setOnClickListener{action()};panel.addView(item,LinearLayout.LayoutParams(-1,-2).apply{bottomMargin=dp(3)})
    }
    private fun effectPicker(){
        val popular=QuickEffects.defaults(Presets.all)
        actionSheet("Эффекты",popular.size*61+65){dialog,panel->
            panel.addView(label("Быстрые режимы",12,muted,true))
            popular.forEach{preset->sheetAction(panel,EffectMenu.title(preset.name),QuickEffects.subtitle(preset),preset==Presets.active){applyPreset(preset);dialog.dismiss();render()}}
            sheetAction(panel,"⋮  Все эффекты","Остальные режимы и настройки"){dialog.dismiss();effectCatalog()}
        }
    }
    private fun effectCatalog(){
        actionSheet("Все эффекты",500){dialog,panel->
            val search=EditText(this).apply{hint="Поиск эффекта";setSingleLine(true);setTextColor(PremiumChrome.TEXT);setHintTextColor(muted);textSize=16f;setPadding(dp(12),dp(8),dp(12),dp(8));background=PremiumChrome.shape(bg,dp(12).toFloat())}
            panel.addView(search,LinearLayout.LayoutParams(-1,dp(48)))
            val results=column();panel.addView(results)
            fun fill(q:String){
                results.removeAllViews()
                val terms=q.trim()
                val groups=EffectMenu.groups(Presets.all.filter{terms.isNotBlank()||it in QuickEffects.extra(Presets.all)})
                var count=0
                for((group,items) in groups){
                    val matches=items.filter{terms.isBlank()||it.name.contains(terms,true)||EffectMenu.title(it.name).contains(terms,true)||group.contains(terms,true)}
                    if(matches.isEmpty())continue
                    results.addView(label(group,13,muted,true))
                    matches.forEach{preset->count++;sheetAction(results,EffectMenu.title(preset.name),QuickEffects.subtitle(preset),preset==Presets.active){applyPreset(preset);dialog.dismiss();render()}}
                }
                if(count==0)results.addView(label("Нет подходящих эффектов",14,muted))
            }
            fill("");search.addTextChangedListener(object:android.text.TextWatcher{override fun beforeTextChanged(s:CharSequence?,start:Int,count:Int,after:Int){};override fun onTextChanged(s:CharSequence?,start:Int,before:Int,count:Int){fill(s?.toString().orEmpty())};override fun afterTextChanged(s:android.text.Editable?) {}})
        }
    }
'''+s[b:]
a=s.index('    private fun moreMenu(){');b=s.index('    private data class BatchLyricsItem',a)
s=s[:a]+'''    private fun moreMenu(){
        val names=listOf("Версии","Загрузки","Очередь","История","Эквалайзер","Настройки","Тексты библиотеки")
        actionSheet("Ещё",names.size*61){dialog,panel->names.forEach{ name->sheetAction(panel,name){dialog.dismiss();if(name=="Тексты библиотеки")batchLyrics()else{screen=name;render()}}}}
    }
'''+s[b:]
rep('LyricsLookup.search(t.title,t.artist,seconds),t.title','LyricsLookup.search(t.title,t.artist,seconds,false),t.title')
rep('if(sync!=null&&seconds!=null&&m.duration!=null&&kotlin.math.abs(seconds-m.duration)>3){','if(sync!=null&&(LyricsSearchPlan.isComposite(searchTitleValue)||(seconds!=null&&m.duration!=null&&kotlin.math.abs(seconds-m.duration)>3))){')
rep('У этой версии песни отличаются временные метки. Можно сохранить только слова или использовать метки с ручной настройкой.','Для ремикса или другой версии метки могут не совпадать. Можно сохранить только слова или явно выбрать исходные метки.')
rep('Текст не найден в LRCLIB. Попробуйте название без Remix или исполнителя.','Текст не найден в LRCLIB. Попробуйте исходное название отдельно или распознавание Whisper.')
p.write_text(s)
print("PASS: custom bottom sheets, seven instant modes, searchable catalogue and safer mashup lyrics")
