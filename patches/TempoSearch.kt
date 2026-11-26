package app.remix.player
import kotlin.math.abs
internal object TempoSearch {
    enum class Kind { BPM, RATIO }
    data class Range(val kind:Kind,val low:Double,val high:Double){
        init{val bounds=if(kind==Kind.BPM)30.0..300.0 else .4..1.8;require(low in bounds&&high in bounds&&low<=high)}
        fun contains(v:Double?)=v!=null&&v.isFinite()&&v in low..high
    }
    data class Entry(val id:String,val bpm:Double?,val ratio:Double?)
    fun parse(text:String,kind:Kind):Range?=runCatching{
        val clean=text.trim().replace(',','.').replace('–','-').replace('—','-').replace(Regex("(?i)bpm|[×xх]"),"").trim()
        val parts=clean.split('-').map{it.trim()};require(parts.size in 1..2)
        val a=parts[0].toDouble();val b=parts.getOrNull(1)?.toDouble()
        val bounds=if(kind==Kind.BPM)30.0..300.0 else .4..1.8;require(a in bounds)
        val tolerance=if(kind==Kind.BPM)3.0 else .005
        if(b==null)Range(kind,(a-tolerance).coerceAtLeast(bounds.start),(a+tolerance).coerceAtMost(bounds.endInclusive))else Range(kind,a,b)
    }.getOrNull()
    fun measured(bpm:Double?,confidence:Double?):Double?=bpm?.takeIf{it.isFinite()&&it in 30.0..300.0&&confidence!=null&&confidence.isFinite()&&confidence>=.30&&confidence<=1.0}
    fun value(e:Entry,kind:Kind)=if(kind==Kind.BPM)e.bpm else e.ratio
    fun find(entries:List<Entry>,range:Range):List<Entry>{val center=(range.low+range.high)/2;return entries.filter{range.contains(value(it,range.kind))}.distinctBy{it.id}.sortedWith(compareBy<Entry>{abs(value(it,range.kind)!!-center)}.thenBy{it.id})}
}
