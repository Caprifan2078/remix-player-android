package app.remix.player

/** Opt-in upgrade of line-only LRC. Do not move an established timeline to an unrelated occurrence. */
object LyricTimingUpgrade {
    data class Line(val start:Long,val text:String,val words:List<Long> = emptyList())
    fun eligible(lines:List<Line>):Boolean = lines.isNotEmpty() && lines.size<=1000 &&
        lines.all{it.start>=0&&it.text.isNotBlank()&&it.words.isEmpty()} &&
        lines.zipWithNext().all{(a,b)->a.start<b.start}

    fun accept(before:List<Line>,after:List<Line>):Boolean {
        if(!eligible(before)||before.size!=after.size)return false
        // The original line timing is an independent check against wrong verse/chorus alignment.
        for(i in before.indices){
            val a=before[i];val b=after[i]
            if(a.text.trim()!=b.text.trim()||b.start<0||kotlin.math.abs(b.start-a.start)>800)return false
            val next=before.getOrNull(i+1)?.start?:Long.MAX_VALUE
            val nextNew=after.getOrNull(i+1)?.start?:Long.MAX_VALUE
            if(b.words.isEmpty()||b.words.first()<b.start||kotlin.math.abs(b.words.first()-a.start)>800)return false
            if(b.words.zipWithNext().any{(x,y)->x>=y}||b.words.last()>=minOf(next,nextNew))return false
        }
        return true
    }
}
