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

# Fail closed if any legacy top-level duplicate survives.
versions=s[s.index("    private fun versions(){"):s.index("    private val customPresets=")]
for duplicate in ('btn("Экспорт WAV в папку…")','btn("Экспорт FLAC без потерь…")','btn("Экспорт MP3…")','btn("Открыть студию эффектов")','listOf("Текст","Микшер","Студия","Очередь")'):
    assert duplicate not in versions, duplicate
assert 'listOf("Текст","Микшер","Студия","Очередь")' not in s
p.write_text(s)
print("PASS: compact player, version actions and bounded studio preset list (source assertions only)")
