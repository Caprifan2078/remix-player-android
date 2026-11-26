package app.remix.player
import kotlin.math.abs
import java.util.Locale
/** Local acoustic similarity, not a streaming recommendation service. */
object LocalDiscovery {
 data class Entry(val id:String,val artist:String,val values:List<Double?>){
  init{require(values.size==6&&values.withIndex().all{(i,v)->if(v==null)i==4 else v.isFinite()&&v in 0.0..1.0})}
 }
 enum class Mode { SIMILAR, VARIED }
 private val weights=listOf(.30,.25,.12,.12,.10,.11)
 fun distance(a:Entry,b:Entry):Double{
  var sum=0.0;var mass=0.0
  for(i in weights.indices){val x=a.values[i]?:continue;val y=b.values[i]?:continue;sum+=weights[i]*abs(x-y);mass+=weights[i]}
  return sum/mass
 }
 private fun artist(e:Entry)=e.artist.trim().lowercase(Locale.ROOT)
 fun rank(seed:Entry,entries:List<Entry>,mode:Mode,limit:Int=50,excluded:Set<String> = emptySet()):List<String>{
  require(limit in 1..100)
  val cutoff=if(mode==Mode.SIMILAR).27 else .39
  val pool=entries.asSequence().filter{it.id.isNotBlank()&&it.id!=seed.id&&it.id !in excluded}.distinctBy{it.id}.map{it to distance(seed,it)}.filter{it.second<=cutoff}.sortedWith(compareBy<Pair<Entry,Double>>{it.second}.thenBy{it.first.id}).toMutableList()
  return choose(pool,mode,limit,artist(seed))
 }
 /** Discover against individual liked songs, not an average that erases different tastes. */
 fun favorites(entries:List<Entry>,liked:Set<String>,mode:Mode=Mode.VARIED,limit:Int=50):List<String>{
  require(limit in 1..100)
  val unique=entries.filter{it.id.isNotBlank()}.distinctBy{it.id}
  val known=unique.filter{it.id in liked}.sortedBy{it.id}
  if(known.isEmpty())return emptyList()
  val seeds=if(known.size<=32)known else List(32){i->known[(i.toLong()*(known.size-1)/31).toInt()]}
  val cutoff=if(mode==Mode.SIMILAR).27 else .39
  val pool=unique.asSequence().filter{it.id !in liked}.map{e->
   check(!Thread.currentThread().isInterrupted){"Cancelled"}
   e to seeds.minOf{distance(it,e)}
  }.filter{it.second<=cutoff}.sortedWith(compareBy<Pair<Entry,Double>>{it.second}.thenBy{it.first.id}).toMutableList()
  return choose(pool,mode,limit,"")
 }
 private fun choose(pool:MutableList<Pair<Entry,Double>>,mode:Mode,limit:Int,initialArtist:String):List<String>{
  val result=mutableListOf<String>();val seen=mutableMapOf<String,Int>();var last=initialArtist
  while(pool.isNotEmpty()&&result.size<limit){
   check(!Thread.currentThread().isInterrupted){"Cancelled"}
   val best=pool[0].second;val slack=if(mode==Mode.SIMILAR).035 else .12
   val i=pool.indices.asSequence().takeWhile{pool[it].second<=best+slack}.minWithOrNull(compareBy<Int>{val a=artist(pool[it].first);if(a.isNotBlank()&&a==last)1 else 0}.thenBy{if(mode==Mode.VARIED)seen[artist(pool[it].first)]?:0 else 0}.thenBy{pool[it].second}.thenBy{pool[it].first.id})?:0
   val e=pool.removeAt(i).first;result.add(e.id);last=artist(e);if(last.isNotBlank())seen[last]=(seen[last]?:0)+1
  }
  return result
 }
 fun append(existing:List<String>,suggestions:List<String>,limit:Int=50):List<String>{require(limit in 1..100);val seen=existing.toHashSet();return suggestions.asSequence().filter{it.isNotBlank()&&seen.add(it)}.take(limit).toList()}
 data class QueuePlan(val index:Int,val ids:List<String>)
 /** Next is physical queue order; do not silently disable shuffle. */
 fun queuePlan(existing:List<String>,current:Int,suggestions:List<String>,next:Boolean,shuffle:Boolean,limit:Int=100):QueuePlan?{
  if(next&&(shuffle||current !in existing.indices))return null
  val ids=append(existing,suggestions,limit)
  return QueuePlan(if(next)current+1 else existing.size,ids)
 }
}
