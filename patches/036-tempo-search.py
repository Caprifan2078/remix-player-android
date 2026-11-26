from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player'
shutil.copyfile(Path(__file__).parent/'TempoSearch.kt',src/'TempoSearch.kt')
p=src/'MainActivity.kt';s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,("tempo UI anchor",old[:100],s.count(old))
    s=s.replace(old,new)
replace('    private fun library(){',r'''    private val tempoSearchCache=object:LinkedHashMap<String,Double?>(128,.75f,true){
        override fun removeEldestEntry(eldest:MutableMap.MutableEntry<String,Double?>?)=size>4096
    }
    private fun knownTempo(t:Track):Double?{
        val estimate=reports[t.uri]?.tempo?:tempos[t.uri]
        return TempoSearch.measured(estimate?.bpm,estimate?.confidence)?:tempoSearchCache[t.uri]
    }
    private fun tempoSearchDialog(){
        val panel=column()
        val mode=Spinner(this).apply{adapter=android.widget.ArrayAdapter(this@MainActivity,android.R.layout.simple_spinner_dropdown_item,listOf("Темп песни · BPM","Скорость сохранённой версии · ×"))};panel.addView(mode)
        val field=EditText(this).apply{setSingleLine();hint="120–140 BPM или 1,25×";setText("120-140")};panel.addView(field)
        panel.addView(label("Один BPM: допуск ±3. Скорость ×1,25 — относительно оригинала. Поиск работает по всей локальной библиотеке, включая версии. Неизвестные значения не считаются совпадением.",14,muted))
        android.app.AlertDialog.Builder(this).setTitle("Найти по темпу / скорости").setView(panel).setNegativeButton("Отмена",null).setPositiveButton("Найти"){_,_->
            val kind=TempoSearch.Kind.entries[mode.selectedItemPosition];val range=TempoSearch.parse(field.text.toString(),kind)
            if(range==null)toast("Некорректный диапазон: BPM 30–300 или скорость 0,4–1,8×")else showTempoResults(range)
        }.show()
    }
    private fun showTempoResults(range:TempoSearch.Range){
        val rows=tracks.map{t->TempoSearch.Entry(t.uri,knownTempo(t),t.tempoRatio?:if(t.uri==t.group)1.0 else null)}
        val found=TempoSearch.find(rows,range)
        val unknown=rows.count{TempoSearch.value(it,range.kind)==null}
        val visible=found.take(100)
        val choices=visible.map{e->val t=libraryIndex.get(e.id);val v=TempoSearch.value(e,range.kind)!!;val text=if(range.kind==TempoSearch.Kind.BPM)String.format(java.util.Locale.ROOT,"%.1f BPM",v)else String.format(java.util.Locale.ROOT,"×%.2f",v);"$text · ${t?.title.orEmpty()} · ${t?.artist.orEmpty()}"}
        val missing=tracks.filter{knownTempo(it)==null&&!tempoSearchCache.containsKey(it.uri)}.take(20).map{it.uri}
        val title="Найдено ${found.size} · неизвестно $unknown"+if(found.size>100)" · первые 100" else ""
        val dialog=android.app.AlertDialog.Builder(this).setTitle(title).setNegativeButton("Закрыть",null)
        if(choices.isEmpty())dialog.setMessage("Нет совпадений среди известных значений. Для BPM можно измерить следующие 20 треков по запросу.")
        else dialog.setItems(choices.toTypedArray()){_,i->val target=libraryIndex.get(visible[i].id);if(target==null)toast("Композиция удалена")else start(target)}
        if(range.kind==TempoSearch.Kind.BPM&&missing.isNotEmpty()&&!stemBusy)dialog.setNeutralButton("Анализ 20"){_,_->analyzeTempoBatch(missing,range)}
        dialog.show()
    }
    private fun analyzeTempoBatch(ids:List<String>,range:TempoSearch.Range){
        if(stemBusy||ids.isEmpty())return
        stemWork("Измерение BPM…",{
            ids.mapIndexed{i,id->
                check(!Thread.currentThread().isInterrupted){"Отменено"}
                val estimate=try{TrackAnalyzer.report(this,Uri.parse(id))?.tempo}catch(e:Exception){if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e;null}
                updateWork("Измерение BPM: ${i+1}/${ids.size}")
                id to TempoSearch.measured(estimate?.bpm,estimate?.confidence)
            }
        }){result->result.forEach{(id,bpm)->if(libraryIndex.get(id)!=null)tempoSearchCache[id]=bpm};showTempoResults(range)}
    }
    private fun library(){''')
replace('body.addView(search);val filter=btn','body.addView(search);body.addView(btn("Темп / скорость…"){tempoSearchDialog()});val filter=btn')
replace('found.onSuccess{list->reports.clear();completeReports.clear();','found.onSuccess{list->reports.clear();completeReports.clear();tempoSearchCache.clear();tempos.clear();')
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


p.write_text(s)
print('PASS: local BPM and version speed search, bounded on-demand analysis, compact player and grouped version export ported from PR 15')
