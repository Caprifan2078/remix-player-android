from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text();assert s.count(old)==1,(name,old,s.count(old));p.write_text(s.replace(old,new))
replace('TransitionMix.kt','val peakA:Double,val peakB:Double)','val peakA:Double,val peakB:Double,val rmsA:Double,val rmsB:Double)')
replace('TransitionMix.kt','return Stats(rho,peakA,peakB)','return Stats(rho,peakA,peakB,sqrt(aa/(2.0*frames)),sqrt(bb/(2.0*frames)))')
replace('TransitionMix.kt','first.length()/8,second.length()/8),progress)','first.length()/8,second.length()/8),progress=progress)')
replace('TransitionMix.kt','out:File,overlap:Long,progress:(Int)->Unit={}):Long','out:File,overlap:Long,levelMatch:Boolean=false,progress:(Int)->Unit={}):Long')
replace('TransitionMix.kt','val stats=analyze(first,second,a-overlap,overlap);','val stats=analyze(first,second,a-overlap,overlap);val levels=if(levelMatch)TransitionLevel.match(stats.rmsA,stats.rmsB)else TransitionLevel.Match();')
replace('TransitionMix.kt','val gainA=cos(t*PI/2);val gainB=sin(t*PI/2);','val gainA=cos(t*PI/2)*(if(levelMatch)levels.outgoingAt(t)else 1.0);val gainB=sin(t*PI/2)*(if(levelMatch)levels.incomingAt(t)else 1.0);')
p=src/'TransitionMix.kt';p.write_text(p.read_text()+'\n'+'''/** Conservative RMS balance, not perceptual LUFS normalization. Never boosts either source. */
internal object TransitionLevel {
    data class Match(val outgoing:Double=1.0,val incoming:Double=1.0) {
        fun outgoingAt(t:Double)=outgoing.pow(t.coerceIn(0.0,1.0))
        fun incomingAt(t:Double)=incoming.pow(1-t.coerceIn(0.0,1.0))
    }
    fun match(a:Double,b:Double):Match {
        if(!a.isFinite()||!b.isFinite()||a !in .01..1.0||b !in .01..1.0)return Match()
        val db=20*log10(a/b)
        if(abs(db)<3.0)return Match()
        val gain=10.0.pow(-minOf(abs(db)-3.0,6.0)/20.0)
        return if(db>0)Match(outgoing=gain)else Match(incoming=gain)
    }
}
''')
p=src/'SmartMix.kt';p.write_text(p.read_text()+'\n'+'''/** Small session-only cache. Main-thread owner; background work returns a snapshot. */
internal class MixFeatureCache<T>(private val limit:Int=128,private val ttlMs:Long=300000L){
    init{require(limit in 1..512&&ttlMs>0)}
    private data class Item<T>(val value:T,val at:Long)
    private val rows=object:LinkedHashMap<String,Item<T>>(limit,.75f,true){override fun removeEldestEntry(eldest:MutableMap.MutableEntry<String,Item<T>>?)=size>limit}
    var revision=0L;private set
    fun invalidate(){rows.clear();revision++}
    fun get(id:String,now:Long):T?{val item=rows[id]?:return null;if(now<item.at||now-item.at>=ttlMs){rows.remove(id);return null};return item.value}
    fun put(id:String,value:T,now:Long,expected:Long):Boolean{if(expected!=revision||id.isBlank()||now<0)return false;rows[id]=Item(value,now);return true}
}
''')
replace('MainActivity.kt','private fun reindex(){libraryIndex=LibraryIndex(tracks,Track::uri,Track::group);searchIndex=null}','private fun reindex(){libraryIndex=LibraryIndex(tracks,Track::uri,Track::group);searchIndex=null;mixFeatureCache.invalidate()}')
replace('MainActivity.kt','    private fun chooseSmartMix(){','    private val mixFeatureCache=MixFeatureCache<SmartMix.Entry>()\n    private fun chooseSmartMix(){')
replace('MainActivity.kt','val snapshot=songs.map{it.uri to reports[it.uri]}','val stamp=android.os.SystemClock.elapsedRealtime();val revision=mixFeatureCache.revision\n        val snapshot=songs.map{Triple(it.uri,mixFeatureCache.get(it.uri,stamp),reports[it.uri])}')
replace('MainActivity.kt','val entries=snapshot.map{(id,cached)->','val entries=snapshot.map{(id,features,cached)->')
replace('MainActivity.kt','val r=cached?:try{TrackAnalyzer.report(this,Uri.parse(id))}','if(features!=null)return@map features\n                val r=cached?:try{TrackAnalyzer.report(this,Uri.parse(id))}')
replace('MainActivity.kt','SmartMix.arrange(entries,seed,radio)\n        }){rows->','entries to SmartMix.arrange(entries,seed,radio)\n        }){result->\n            if(mixFeatureCache.revision!=revision){toast("Библиотека изменилась; повторите анализ");return@stemWork}\n            val now=android.os.SystemClock.elapsedRealtime();val previouslyCached=snapshot.filter{it.second!=null}.map{it.first}.toHashSet()\n            result.first.filter{SmartMix.measured(it)&&it.id !in previouslyCached}.forEach{mixFeatureCache.put(it.id,it,now,revision)}\n            val rows=result.second')
# Explicit scan refresh invalidates stale full and quick reports too.
replace('MainActivity.kt','found.onSuccess{list->val known=tracks.map{it.uri}.toHashSet();','found.onSuccess{list->reports.clear();completeReports.clear();val known=tracks.map{it.uri}.toHashSet();')
print('PASS: opt-in transition RMS balance, bounded session feature cache and scan invalidation')
