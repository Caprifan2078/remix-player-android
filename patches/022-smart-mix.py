from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'MainActivity.kt'
s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,(old,s.count(old))
    s=s.replace(old,new)
replace('"Сравнить песни по звуку…")){_,i->if(!stemBusy)when(i){0->chooseGenreBatch();1->chooseMoodBatch();2->suggestVersions();3->fingerprintDialog()}}','"Сравнить песни по звуку…","Умные плейлисты · Mix / Радио")){_,i->if(!stemBusy)when(i){0->chooseGenreBatch();1->chooseMoodBatch();2->suggestVersions();3->fingerprintDialog();4->chooseSmartMix()}}')
replace('    private fun chooseGenreBatch(){',r'''    private fun chooseSmartMix(){
        if(stemBusy)return
        val candidates=visibleSongs().take(200)
        if(candidates.size<2)return toast("Нужны хотя бы две песни в текущем фильтре")
        android.app.AlertDialog.Builder(this).setTitle("Умные плейлисты · офлайн").setItems(arrayOf("Smart Mix · совместимые переходы","Радио · похожие на первую выбранную песню")){_,mode->
            val checked=BooleanArray(candidates.size)
            android.app.AlertDialog.Builder(this).setTitle("Выберите 2–20 песен").setMultiChoiceItems(candidates.map{"${it.title} · ${it.artist}"}.toTypedArray(),checked){_,i,v->checked[i]=v}
                .setNegativeButton("Отмена",null).setNeutralButton("Первые 20"){_,_->runSmartMix(candidates.take(20),mode==1)}
                .setPositiveButton("Анализировать"){_,_->val chosen=candidates.filterIndexed{i,_->checked[i]};if(chosen.size in 2..20)runSmartMix(chosen,mode==1)else toast("Выберите 2–20 песен")}.show()
        }.setNegativeButton("Отмена",null).show()
    }
    private fun runSmartMix(songs:List<Track>,radio:Boolean){
        if(stemBusy||songs.size !in 2..20)return
        val snapshot=songs.map{it.uri to reports[it.uri]}
        val titles=songs.associate{it.uri to it.title}
        val seed=songs.first().uri
        stemWork("Анализ для умного плейлиста…",{
            val entries=snapshot.map{(id,cached)->
                check(!Thread.currentThread().isInterrupted){"Отменено"}
                val r=cached?:try{TrackAnalyzer.report(this,Uri.parse(id))}catch(e:Exception){if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e;null}
                SmartMix.Entry(id,r?.tempo?.takeIf{it.confidence>=.30}?.bpm,r?.key?.takeIf{(r.keyConfidence>.025)},r?.rms)
            }
            SmartMix.arrange(entries,seed,radio)
        }){rows->
            if(rows.size<2){toast("Недостаточно измеренных данных: выберите другую первую песню")}
            else{
                val measured=rows.count{SmartMix.measured(it)}
                val kind=if(radio)"Радио" else "Smart Mix"
                val preview=rows.mapIndexed{i,e->"${i+1}. ${titles[e.id].orEmpty()} · ${e.bpm?.toInt()?.let{"$it BPM"}?:"BPM ?"} · ${e.key?:"тональность ?"}"}.joinToString("\n")
                val field=EditText(this).apply{setSingleLine();setText("$kind · ${titles[seed].orEmpty().take(54)}");selectAll()}
                val panel=column();panel.addView(label("Измерено $measured из ${songs.size}. Офлайн-оценка темпа, тональности и уровня; не автоматический beatmatch. Исходная очередь не изменится.",14,muted));panel.addView(label(preview,14,Color.WHITE));panel.addView(field)
                val scroll=ScrollView(this);scroll.addView(panel)
                android.app.AlertDialog.Builder(this).setTitle("Новый умный плейлист").setView(scroll).setNegativeButton("Отмена",null).setPositiveButton("Сохранить"){_,_->
                    val name=field.text.toString().trim()
                    if(name.isBlank()||name.length>80||name in playlists)toast("Название пустое или уже используется")
                    else if(rows.any{e->libraryIndex.get(e.id)?.let{it.group==it.uri}!=true})toast("Библиотека изменилась; повторите анализ")
                    else{playlists[name]=rows.map{it.id}.toCollection(linkedSetOf());savePlaylists();toast("Плейлист сохранён: ${rows.size} песен");render()}
                }.show()
            }
        }
    }
    private fun chooseGenreBatch(){''')
p.write_text(s)
(src/'SmartMix.kt').write_text(r'''package app.remix.player
import kotlin.math.*
/** Local similarity heuristic. Unknown features never pretend to be a match. */
object SmartMix {
    data class Entry(val id:String,val bpm:Double?,val key:String?,val rms:Double?)
    private val notes=listOf("C","C♯","D","D♯","E","F","F♯","G","G♯","A","A♯","B")
    private fun tempo(x:Double?)=x?.takeIf{it.isFinite()&&it in 50.0..220.0}
    private fun loud(x:Double?)=x?.takeIf{it.isFinite()&&it in .005..1.0}
    private fun key(x:String?):Pair<Int,Boolean>? {
        val p=x?.split(' ')?:return null
        if(p.size!=2||p[1] !in listOf("major","minor"))return null
        val n=notes.indexOf(p[0]);return if(n<0)null else n to (p[1]=="minor")
    }
    fun measured(x:Entry)=tempo(x.bpm)!=null||key(x.key)!=null||loud(x.rms)!=null
    fun distance(a:Entry,b:Entry):Double {
        val x=tempo(a.bpm);val y=tempo(b.bpm)
        val beat=if(x!=null&&y!=null) minOf(abs(ln(x/y)),abs(ln(2*x/y))+.10,abs(ln(x/(2*y)))+.10).coerceAtMost(1.0) else .50
        val k=key(a.key);val l=key(b.key)
        val harmonic=if(k==null||l==null).55 else {
            val diff=Math.floorMod(l.first-k.first,12)
            when {k==l->0.0;k.second==l.second&&diff in listOf(5,7)->.20;k.second!=l.second&&diff==(if(k.second)3 else 9)->.20;else->.85}
        }
        val ar=loud(a.rms);val br=loud(b.rms)
        val level=if(ar!=null&&br!=null)(abs(20*log10(ar/br))/24).coerceAtMost(1.0) else .50
        return .55*beat+.30*harmonic+.15*level
    }
    fun arrange(entries:List<Entry>,seedId:String,radio:Boolean):List<Entry>{
        require(entries.size in 1..200&&entries.map{it.id}.distinct().size==entries.size)
        val seed=entries.firstOrNull{it.id==seedId&&measured(it)}?:return emptyList()
        val rest=entries.filter{it.id!=seed.id&&measured(it)}.toMutableList()
        val result=mutableListOf(seed)
        while(rest.isNotEmpty()){
            val anchor=if(radio)seed else result.last()
            val i=rest.indices.minByOrNull{distance(anchor,rest[it])}!!
            result.add(rest.removeAt(i))
        }
        if(!radio)result.addAll(entries.filterNot(::measured))
        return result
    }
}
''')
print('PASS: Smart Mix integrated in existing library tools')
