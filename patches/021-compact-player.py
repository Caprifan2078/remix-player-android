#!/usr/bin/env python3
"""UI hierarchy changes after the phone recording. Keep underlying operations and IDs."""
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'MainActivity.kt';s=p.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1, (a[:180],s.count(a))
 s=s.replace(a,b)
# Compact neutral visual system and typography. Internal preset names remain stable.
replace('Color.rgb(12,14,20); private val surface=Color.rgb(29,33,45); private val accent=Color.rgb(192,176,255); private val muted=Color.rgb(174,181,200)','Color.rgb(12,13,17); private val surface=Color.rgb(24,26,33); private val accent=Color.rgb(200,188,255); private val muted=Color.rgb(170,175,188)')
replace('setPadding(dp(6),dp(8),dp(6),dp(8))','setPadding(dp(6),dp(5),dp(6),dp(5))')
replace('setTextColor(accent);background=android.graphics.drawable.RippleDrawable','setTextColor(Color.rgb(226,221,242));background=android.graphics.drawable.RippleDrawable')
replace('bar.setPadding(dp(12),dp(9),dp(12),dp(8))','bar.setPadding(dp(8),dp(3),dp(8),dp(3))')
# Move timestamp to the title row; preserve 48dp touch targets and seek.
replace('now=label("Выберите композицию",16,Color.WHITE,true);bar.addView(now);','val nowRow=row();bar.addView(nowRow);now=label("Выберите композицию",15,Color.WHITE,true).apply{maxLines=1;ellipsize=android.text.TextUtils.TruncateAt.END};nowRow.addView(now,weight());')
replace('time=label("0:00 / 0:00",12,muted);bar.addView(time)','time=label("0:00 / 0:00",11,muted).apply{setSingleLine()};nowRow.addView(time)')
replace('c.addView(label(title,17,Color.WHITE,true));c.addView(label(sub,13,muted))','c.addView(label(title,17,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END});c.addView(label(sub,13,muted))')
replace('col.addView(label(t.title,17,Color.WHITE,true));col.addView(label("${t.artist} · ${libraryIndex.versions(t.uri).size} файл(ов)",12,muted))','col.addView(label(t.title,16,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END});col.addView(label(t.artist+if(libraryIndex.versions(t.uri).size>1)" · ${libraryIndex.versions(t.uri).size} версии" else "",12,muted).apply{maxLines=1;ellipsize=android.text.TextUtils.TruncateAt.END})')
replace('r.background=rounded(surface,14);r.addView(col,weight())','r.background=rounded(bg,8);r.addView(col,weight())')
# Progressive disclosure. Move actual existing views, including listeners, not a duplicate menu.
helper='''    private val expandedSections=mutableSetOf<String>()
    private fun compactSection(key:String,title:String,views:List<View>,at:Int){
        if(views.isEmpty())return
        val panel=column()
        views.forEach{v->(v.parent as? ViewGroup)?.removeView(v);panel.addView(v)}
        val toggle=btn(title){}
        fun update(){val expanded=key in expandedSections;panel.visibility=if(expanded)View.VISIBLE else View.GONE;toggle.text=title+(if(expanded)"  ▴" else "  ▾");toggle.contentDescription=title+(if(expanded)", свернуть" else ", раскрыть")}
        toggle.setOnClickListener{if(!expandedSections.add(key))expandedSections.remove(key);update()}
        val index=at.coerceIn(0,body.childCount);body.addView(toggle,index);body.addView(panel,index+1);update()
    }
    private fun bodyChildren()=(0 until body.childCount).map{body.getChildAt(it)}
    private fun effectPicker(){
        val groups=EffectMenu.groups(Presets.all)
        android.app.AlertDialog.Builder(this).setTitle("Эффекты").setItems(groups.keys.toTypedArray()){_,i->
            val entries=groups.values.elementAt(i)
            android.app.AlertDialog.Builder(this).setTitle(groups.keys.elementAt(i)).setItems(entries.map{(if(it==Presets.active)"✓ " else "")+EffectMenu.title(it.name)}.toTypedArray()){_,j->applyPreset(entries[j]);render()}.setNegativeButton("Назад"){_,_->effectPicker()}.show()
        }.setNegativeButton("Закрыть",null).show()
    }
    private fun reviewTranscript(engine:String,raw:String,commit:()->Unit){
        val lines=Lrc.parse(raw).map{WordLyrics.parse(it).text}.filter{it.isNotBlank()}
        if(lines.isEmpty()){toast("Не удалось распознать текст");return}
        actionSheet("Проверка распознавания",490){dialog,panel->
            panel.addView(label("Черновик · "+engine+". Проверьте слова. Для поиска правильного текста можно открыть браузер с коротким фрагментом.",14,muted))
            val query=EditText(this).apply{setText(LyricsSearchPlan.transcriptHint(lines));hint="Несколько услышанных слов";setTextColor(PremiumChrome.TEXT);setHintTextColor(muted);setSingleLine(true);filters=arrayOf(android.text.InputFilter.LengthFilter(180))}
            panel.addView(query,LinearLayout.LayoutParams(-1,dp(50)))
            sheetAction(panel,"Найти слова в браузере","Будет отправлен только выбранный фрагмент"){openLyricBrowser(query.text.toString())}
            sheetAction(panel,"Сохранить черновик","Слова могут содержать ошибки"){dialog.dismiss();commit();render()}
            sheetAction(panel,"Не сохранять"){dialog.dismiss()}
            panel.addView(label(lines.take(18).joinToString("\\n")+if(lines.size>18)"\\n…"else "",16,PremiumChrome.TEXT))
        }
    }
    private fun openLyricBrowser(query:String){
        val url=LyricsSearchPlan.browserUrl(query)
        if(url==null){toast("Введите несколько слов");return}
        runCatching{startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW,Uri.parse(url)))}.onFailure{toast("Не удалось открыть браузер")}
    }
'''
# ViewGroup is imported by android.view.* in the app.
replace('    private val screenScroll=mutableMapOf<String,Int>()',helper+'    private val screenScroll=mutableMapOf<String,Int>()')
# Library: search first; keep everyday filters and collapse batch tools/history/scan.
replace('body.addView(list)\n        fun fill()', '''body.addView(list)
        body.removeView(search);body.addView(search,1)
        val libraryTools=bodyChildren().filter{v->v is Button&&(
            v.text.toString().startsWith("Инструменты библиотеки")||
            v.text.toString().startsWith("Случайные версии")||
            v.text.toString().startsWith("Добавить найденные")||
            (tracks.isNotEmpty()&&v.text.toString()=="Найти музыку на телефоне")
        )||v===extras}
        compactSection("library","Ещё",libraryTools,body.indexOfChild(list)-libraryTools.size)
        fun fill()''')
# The list remains directly below the visible filters; all prior actions retained.
replace('body.addView(btn(if(onlyFavorites)"♥ Избранное" else "Все композиции")','body.addView(btn(if(onlyFavorites)"♥ Избранное" else "Все композиции")') if False else None
# Studio: 41 profiles accessible through grouped picker, no long scroll.
replace('Presets.all.forEach{p->card((if(p==Presets.active)"✓  " else "")+p.name,"Темп ${p.speed}× · тон ${p.pitch}×"){applyPreset(p);render()}}','''body.addView(btn("Выбрать эффект"){effectPicker()})
        if(Presets.active!=Presets.all.first())body.addView(btn("Сбросить эффект"){applyPreset(Presets.all.first());render()})''')
replace('body.addView(label("Эффекты",15,muted,true));body.addView(btn("Пакет эффектов…")','body.addView(label("Эффекты",19,Color.WHITE,true));val effectToolsStart=body.childCount;body.addView(btn("Пакет эффектов…")')
replace('body.addView(btn("Выбрать эффект"){effectPicker()})','''val effectTools=bodyChildren().drop(effectToolsStart)
        body.addView(label("Сейчас: "+EffectMenu.title(Presets.active.name),14,muted),effectToolsStart)
        body.addView(btn("Выбрать эффект"){effectPicker()},effectToolsStart+1)
        compactSection("studio-tools","Настроить и сохранить",effectTools,effectToolsStart+2)''')
replace('card("Нейросетевой инструментал","Создать новый музыкальный материал офлайн")','card("Инструментал","Создать музыку с нуля · экспериментально")')
# use only labels that exist; underlying operations unchanged
replace('card("AI Mixer","Разделить вокал и инструменты")','card("Микшер","Вокал, ударные и другие дорожки")')
replace('card("Сведение с инструменталом","Вокал / оригинал · автоматическая подгонка BPM")','card("Сведение","Совместить песню с инструменталом")')
# Lyrics lookup: place lookup first, let user correct metadata; audio stays local.
replace('else "Найти синхронный текст (онлайн)"','else "Найти текст"')
replace('btn("Импортировать LRC / TXT")','btn("Импорт текста")')
replace('if(!lyricsBusy)android.app.AlertDialog.Builder(this).setTitle("Поиск в LRCLIB").setMessage("Сервису будут переданы название песни, исполнитель и длительность. Сам аудиофайл не отправляется. Найденный текст будет сохранён для офлайн-просмотра.")','''if(!lyricsBusy){val origin=if(t.tempoRatio!=null)tracks.find{it.uri==t.group}?:t else t
        val panel=column();val searchTitle=EditText(this).apply{hint="Название песни";setSingleLine();setText(origin.title)};val searchArtist=EditText(this).apply{hint="Исполнитель";setSingleLine();setText(origin.artist)}
        panel.addView(searchTitle);panel.addView(searchArtist);panel.addView(label("Поиск готового текста по метаданным. Можно исправить название и исполнителя. Аудио не отправляется.",14,muted))
        android.app.AlertDialog.Builder(this).setTitle("Найти текст").setView(panel)''')
replace('LyricsLookup.fetch(original.title,original.artist,seconds)','LyricsLookup.fetch(searchTitleValue,searchArtistValue,seconds)')
replace('lyricsBusy=true;render();io.execute{val result=runCatching{LyricsLookup.fetch','val searchTitleValue=searchTitle.text.toString().trim();val searchArtistValue=searchArtist.text.toString().trim();if(searchTitleValue.isBlank()){toast("Укажите название");return@setPositiveButton};lyricsBusy=true;render();io.execute{val result=runCatching{LyricsLookup.fetch')
replace('        }.show()\n    });val raw=rawLyrics(t);','        }.show()}\n    });val lookup=body.getChildAt(2);body.removeView(lookup);body.addView(lookup,1);val raw=rawLyrics(t);')
replace('btn("Модели распознавания · каталог"){showModelCatalog()}','btn("Речевые модели Vosk"){showModelCatalog(ModelCatalog.Kind.SPEECH)}')
replace('btn("Vosk · распознать слова")','btn("Vosk · эксперимент")')
replace('else "Whisper · установить модель"','else "Whisper · установить"')
# Blank lyrics used to expose every tool. Keep search/import/Whisper outside advanced section.
replace('if(activeLyrics.isEmpty()){body.addView(label(','if(activeLyrics.isEmpty()){val whisperButton=bodyChildren().filterIsInstance<Button>().firstOrNull{it.text.toString().startsWith("Whisper ·")};if(whisperButton!=null){body.removeView(whisperButton);body.addView(whisperButton,3)};val advanced=bodyChildren().drop(if(whisperButton==null)3 else 4);if(!stemBusy)compactSection("lyrics-empty","Дополнительно",advanced,if(whisperButton==null)3 else 4);if(raw.isNotBlank()&&!stemBusy){val sync=bodyChildren().flatMap{v->if(v is ViewGroup)(0 until v.childCount).map{v.getChildAt(it)}else listOf(v)}.filterIsInstance<Button>().firstOrNull{it.text.toString()=="Уточнить по вокалу"};if(sync!=null){(sync.parent as? ViewGroup)?.removeView(sync);sync.text="Синхронизировать по вокалу";body.addView(sync,if(whisperButton==null)3 else 4)}};body.addView(label(')
# Existing lyrics retain their original karaoke view and advanced tools.
replace('private fun showModelCatalog(){if(stemBusy)return;val items=ModelCatalog.entries;','private fun showModelCatalog(kind:ModelCatalog.Kind?=null){if(stemBusy)return;val items=ModelCatalog.entries.filter{kind==null||it.kind==kind};')
# Review recognizer output BEFORE mutating tracks, preserving the original concurrency checks.
replace('){raw->if(tracks.contains(original)&&original.lyrics==originalBefore){original.lyrics=raw;','){raw->reviewTranscript("Vosk",raw){if(tracks.contains(original)&&original.lyrics==originalBefore){original.lyrics=raw;')
replace('else toast("Исходный текст или песня изменились. Черновик не сохранён.")}}.show()}','else toast("Исходный текст или песня изменились. Черновик не сохранён.")}}}.show()}')
replace('){raw->if(tracks.contains(original)&&original.lyrics==before){original.lyrics=raw;','){raw->reviewTranscript("Whisper",raw){if(tracks.contains(original)&&original.lyrics==before){original.lyrics=raw;')
replace('else toast("Текст или песня изменились; черновик не сохранён")}}.show()}.show()}','else toast("Текст или песня изменились; черновик не сохранён")}}}.show()}.show()}')
replace('Новый черновик заменит текущий текст, если он не изменился во время обработки.','Сначала покажем черновик. Сохранять его необязательно.')
# Versions, settings and download service options: move secondary actions into collapsible groups.
replace('};run{body.addView(btn("Экспорт WAV в папку…")','};val versionToolsStart=body.childCount;run{body.addView(btn("Экспорт WAV в папку…")')
replace('body.addView(btn("Открыть студию эффектов"){screen="Студия";render()})}','body.addView(btn("Открыть студию эффектов"){screen="Студия";render()});compactSection("versions","Действия с версиями",bodyChildren().drop(versionToolsStart),versionToolsStart)}')
replace('modelManagement();body.addView(btn("Найти неиспользуемые WAV…")','val modelsStart=body.childCount;modelManagement();compactSection("settings-models","Модели ИИ",bodyChildren().drop(modelsStart),modelsStart);body.addView(btn("Найти неиспользуемые WAV…")')
replace('body.addView(btn("Поиск музыки · Jamendo"){catalogDialog()});','val jamendo=btn("Jamendo · внешний каталог"){catalogDialog()};body.addView(jamendo);compactSection("external-catalog","Дополнительные источники",listOf(jamendo),body.indexOfChild(jamendo));')
p.write_text(s)
print("PASS: compact library, grouped effects, transcript review, editable lyric lookup, compact model management")
