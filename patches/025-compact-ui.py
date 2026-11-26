#!/usr/bin/env python3
"""Keep primary playback controls visible; move secondary actions into compact menus."""
from pathlib import Path
import sys

p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/MainActivity.kt"
s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1, ("compact UI anchor",old[:100],s.count(old))
    s=s.replace(old,new)

# A shared menu checks the track before executing a delayed selection.
replace('    private fun versions(){', '''    private fun compactTrackMenu(title:String,t:Track,actions:List<Pair<String,()->Unit>>){
        android.app.AlertDialog.Builder(this).setTitle(title).setItems(actions.map{it.first}.toTypedArray()){_,i->
            if(current()?.uri!=t.uri||libraryIndex.get(t.uri)==null)toast("Композиция изменилась")
            else actions[i].second()
        }.setNegativeButton("Закрыть",null).show()
    }
    private fun versions(){''')

# Player: 4 small tools + one more button becomes one two-button row and one menu.
# Studio is already a top-level navigation destination.
replace('val tools=row();listOf("Текст","Микшер","Студия","Очередь").forEach{name->tools.addView(btn(name){screen=name;render()},weight())};body.addView(tools);body.addView(btn("Дополнительные действия…"){android.app.AlertDialog.Builder(this).setTitle("Плеер").setItems(arrayOf("Таймер сна и переходы","Повтор фрагмента A/B","Вырезать аудиофрагмент","Эквалайзер")){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(i){0->playbackOptionsDialog();1->loopDialog();2->clipDialog(t);3->{screen="Эквалайзер";render()}}}.show()})',
'''val tools=row();listOf("Текст","Очередь").forEach{name->tools.addView(btn(name){screen=name;render()},weight())};body.addView(tools)
        body.addView(btn("Ещё…"){compactTrackMenu("Инструменты плеера",t,listOf<Pair<String,()->Unit>>(
            "Микшер" to {screen="Микшер";render()},
            "Таймер сна и переходы" to {playbackOptionsDialog()},
            "Повтор фрагмента A/B" to {loopDialog()},
            "Вырезать аудиофрагмент" to {clipDialog(t)},
            "Эквалайзер" to {screen="Эквалайзер";render()}
        ))})''')

# Versions: formats grouped, uncommon changes moved behind a single menu.
replace('run{body.addView(btn("Экспорт WAV в папку…"){exportWav(t)});body.addView(btn("Экспорт FLAC без потерь…"){exportWav(t,true)});body.addView(btn("Экспорт MP3…"){exportMp3(t)})};if(t.uri!=t.group){body.addView(btn("Отделить в самостоятельную песню…"){restructureVersion(t,false)});body.addView(btn("Сделать оригиналом группы…"){restructureVersion(t,true)});body.addView(btn("Убрать текущую версию"){removeVersion(t)})};body.addView(btn("Редактировать сведения текущей версии…"){editTrackMetadata(t)});body.addView(btn("Сравнить качество ремиксов"){compareQuality(t)});body.addView(btn("Случайная версия сейчас"){val options=libraryIndex.versions(t.group).filter{it.uri!=t.uri};if(options.isEmpty())toast("Других версий нет")else switchVersion(t,options.random())});body.addView(btn("Сделать текущую версию основной"){choosePreferred(t)});body.addView(btn("＋ Добавить свой ремикс"){addingTo=t.group;picker.launch(arrayOf("audio/*"))});body.addView(btn("Открыть студию эффектов"){screen="Студия";render()})',
'''body.addView(btn("Экспорт…"){compactTrackMenu("Формат экспорта",t,listOf<Pair<String,()->Unit>>(
            "WAV · в папку" to {exportWav(t)},
            "FLAC · без потерь" to {exportWav(t,true)},
            "MP3" to {exportMp3(t)}
        ))})
        body.addView(btn("Управление версией…"){
            val actions=mutableListOf<Pair<String,()->Unit>>(
                "Сделать основной" to {choosePreferred(t)},
                "Редактировать сведения" to {editTrackMetadata(t)},
                "Сравнить техническое качество" to {compareQuality(t)},
                "Случайная версия" to {val options=libraryIndex.versions(t.group).filter{it.uri!=t.uri};if(options.isEmpty())toast("Других версий нет")else switchVersion(t,options.random())}
            )
            if(t.uri!=t.group){
                actions.add("Отделить в самостоятельную песню" to {restructureVersion(t,false)})
                actions.add("Сделать оригиналом группы" to {restructureVersion(t,true)})
                actions.add("Убрать текущую версию" to {removeVersion(t)})
            }
            compactTrackMenu("Управление версией",t,actions)
        })
        body.addView(btn("＋ Добавить свой ремикс"){addingTo=t.group;picker.launch(arrayOf("audio/*"))})''')

# Custom effects can grow to 100 entries: do not build a long card list.
replace('customPresets.forEach{p->card(p.name,"Свой пресет · применить / изменить / удалить"){customPresetMenu(p)}}',
'''if(customPresets.isNotEmpty())body.addView(btn("Мои эффекты · ${customPresets.size}"){
            val items=customPresets.toList()
            android.app.AlertDialog.Builder(this).setTitle("Мои эффекты").setItems(items.map{it.name}.toTypedArray()){_,i->
                if(customPresets.contains(items[i]))customPresetMenu(items[i])else toast("Эффект изменился")
            }.setNegativeButton("Закрыть",null).show()
        })''')

# Keep six quick effects plus the active effect, with all other presets one tap away.
replace('Presets.all.forEach{p->card((if(p==Presets.active)"✓  " else "")+p.name,"Темп ${p.speed}× · тон ${p.pitch}×"){applyPreset(p);render()}}',
'''val quickPresets=(Presets.all.take(6)+listOf(Presets.active)).distinct()
        quickPresets.forEach{p->card((if(p==Presets.active)"✓  " else "")+p.name,"Темп ${p.speed}× · тон ${p.pitch}×"){applyPreset(p);render()}}
        body.addView(btn("Все эффекты · ${Presets.all.size}"){
            val items=Presets.all.toList()
            android.app.AlertDialog.Builder(this).setTitle("Все эффекты").setItems(items.map{(if(it==Presets.active)"✓  " else "")+it.name}.toTypedArray()){_,i->
                if(current()?.uri!=t.uri)toast("Композиция изменилась")else{applyPreset(items[i]);render()}
            }.setNegativeButton("Закрыть",null).show()
        })''')

# The library should open with search and music, not a dashboard of tools.
replace('    private fun library(){', '''    private var libraryToolsExpanded=false
    private fun library(){''')
replace('body.addView(btn("Инструменты библиотеки…"){android.app.AlertDialog.Builder(this).setTitle("Инструменты библиотеки")',
'''val advanced=column()
        advanced.addView(btn("Инструменты библиотеки…"){android.app.AlertDialog.Builder(this).setTitle("Инструменты библиотеки")''')
replace('body.addView(btn(if(scanBusy)"Сканирование…" else "Найти музыку на телефоне"){requestScan()});val search=EditText(this)',
'''val scan=btn(if(scanBusy)"Сканирование…" else "Найти музыку на телефоне"){requestScan()}
        val search=EditText(this)''')
replace('body.addView(search);val filter=btn', '''body.addView(search)
        if(tracks.isEmpty()||scanBusy)body.addView(scan)else advanced.addView(scan)
        val filter=btn''')
replace('body.addView(filter);val tools=row();tools.addView(btn(selectedPlaylist?:"Плейлисты"){playlistFilter()},weight());tools.addView(btn(listOf(if(selectedPlaylist==null)"По добавлению" else "Порядок плейлиста","По названию","По исполнителю")[sortMode]){sortMode=(sortMode+1)%3;shownSongs=100;render()},weight());body.addView(tools);val extras=row();',
'''val primary=row();primary.addView(filter,weight());primary.addView(btn(selectedPlaylist?:"Плейлисты"){playlistFilter()},weight());body.addView(primary)
        advanced.addView(btn("Сортировка: "+listOf(if(selectedPlaylist==null)"По добавлению" else "Порядок плейлиста","По названию","По исполнителю")[sortMode]){sortMode=(sortMode+1)%3;shownSongs=100;render()})
        val extras=row();''')
replace('body.addView(extras);body.addView(btn(category?:listOf("Каталог: все песни","Каталог: альбомы","Каталог: папки","Каталог: исполнители")[categoryMode]){chooseCategory()});body.addView(btn(if(randomVersions)',
'''advanced.addView(extras);advanced.addView(btn(category?:listOf("Каталог: все песни","Каталог: альбомы","Каталог: папки","Каталог: исполнители")[categoryMode]){chooseCategory()});advanced.addView(btn(if(randomVersions)''')
replace('val list=column();body.addView(btn("Добавить найденные песни в плейлист…"){bulkPlaylistDialog()});body.addView(btn("Добавить найденные песни в очередь…"){bulkQueueDialog()});body.addView(list)',
'''val list=column()
        advanced.addView(btn("Добавить найденные песни в плейлист…"){bulkPlaylistDialog()})
        advanced.addView(btn("Добавить найденные песни в очередь…"){bulkQueueDialog()})
        val details=mutableListOf<String>()
        if(categoryMode!=0)details.add(category?:listOf("Все песни","Альбомы","Папки","Исполнители")[categoryMode])
        if(sortMode!=0)details.add(listOf("По добавлению","По названию","По исполнителю")[sortMode])
        if(randomVersions)details.add("Случайные версии")
        if(details.isNotEmpty())body.addView(label(details.joinToString(" · "),13,muted))
        val toggle=btn(if(libraryToolsExpanded)"Скрыть инструменты" else "Фильтры и инструменты…"){}
        toggle.setOnClickListener{
            libraryToolsExpanded=!libraryToolsExpanded
            advanced.visibility=if(libraryToolsExpanded)View.VISIBLE else View.GONE
            toggle.text=if(libraryToolsExpanded)"Скрыть инструменты" else "Фильтры и инструменты…"
        }
        body.addView(toggle);advanced.visibility=if(libraryToolsExpanded)View.VISIBLE else View.GONE;body.addView(advanced);body.addView(list)''')

# Untimed or missing lyrics: retain import and online lookup as primary actions,
# but group the editing/model setup buttons just like the synchronized view.
replace('activeLyrics=Lrc.parse(raw);if(activeLyrics.isEmpty()){body.addView(label(',
'''activeLyrics=Lrc.parse(raw);if(activeLyrics.isEmpty()){
        val extra=column()
        while(body.childCount>3){val view=body.getChildAt(3);body.removeViewAt(3);extra.addView(view)}
        val toggle=btn(if(lyricToolsExpanded)"Скрыть инструменты текста" else "Инструменты текста…"){}
        fun updateTools(){
            val expanded=lyricToolsExpanded||stemBusy
            extra.visibility=if(expanded)View.VISIBLE else View.GONE
            toggle.text=if(expanded)"Скрыть инструменты текста" else "Инструменты текста…"
        }
        toggle.setOnClickListener{if(!stemBusy){lyricToolsExpanded=!lyricToolsExpanded;updateTools()}}
        body.addView(toggle);body.addView(extra);updateTools()
        body.addView(label(''')

# Baseline API 35 screenshot: the idle mini-player wastes space and
# neighbouring filled button backgrounds touch. Preserve the 48dp hit areas.
replace('seek.contentDescription="Позиция воспроизведения";bar.addView(seek)',
        'seek.contentDescription="Позиция воспроизведения";seek.visibility=View.GONE;bar.addView(seek)')
replace('time=label("0:00 / 0:00",12,muted);bar.addView(time)',
        'time=label("0:00 / 0:00",12,muted);time.visibility=View.GONE;bar.addView(time)')
replace('setTextChanged(now,title);setTextChanged(play,if(playing)"Ⅱ" else "▶")',
'''val transportDetails=if(controller?.currentMediaItem!=null||MixerSession.active)View.VISIBLE else View.GONE
            if(seek.visibility!=transportDetails)seek.visibility=transportDetails
            if(time.visibility!=transportDetails)time.visibility=transportDetails
            setTextChanged(now,title);setTextChanged(play,if(playing)"Ⅱ" else "▶")''')
replace('background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x30FFFFFF),rounded(surface,12),rounded(Color.WHITE,12));setOnClickListener{action()}',
'''background=android.graphics.drawable.InsetDrawable(android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x30FFFFFF),rounded(surface,12),rounded(Color.WHITE,12)),dp(2));setPadding(dp(8),dp(5),dp(8),dp(5));setOnClickListener{action()}''')

# Fail closed if any legacy top-level duplicate survives.
versions=s[s.index("    private fun versions(){"):s.index("    private val customPresets=")]
for duplicate in ('btn("Экспорт WAV в папку…")','btn("Экспорт FLAC без потерь…")','btn("Экспорт MP3…")','btn("Открыть студию эффектов")','listOf("Текст","Микшер","Студия","Очередь")'):
    assert duplicate not in versions, duplicate
assert 'listOf("Текст","Микшер","Студия","Очередь")' not in s
p.write_text(s)
print("PASS: compact player, version actions and bounded studio preset list (source assertions only)")
