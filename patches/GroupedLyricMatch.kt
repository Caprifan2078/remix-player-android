package app.remix.player

/** Exact, bounded matching of a reference line across up to three measured ASR segments.
 * Return a result only when the complete ordered alignment is unique. */
object GroupedLyricMatch {
    data class Segment(val ms:Long,val text:String)
    private val token=Regex("[\\p{L}\\p{N}]+")
    private fun words(text:String)=token.findAll(java.text.Normalizer.normalize(text,java.text.Normalizer.Form.NFKC).lowercase(java.util.Locale.ROOT).replace('ё','е')).map{it.value}.take(65).toList()
    fun align(source:List<Segment>,reference:List<String>):List<Long>?{
        if(source.size !in 1..500||reference.size !in 1..300||source.size<reference.size||source.any{it.ms<0}||source.zipWithNext().any{(a,b)->a.ms>b.ms})return null
        val heard=source.map{words(it.text)};val wanted=reference.map(::words)
        if(wanted.any{it.isEmpty()||it.size>64})return null
        val n=source.size
        val starts=Array(reference.size){IntArray(n){-1}}
        val parents=Array(reference.size){IntArray(n){-1}}
        var prior=IntArray(n)
        for(i in wanted.indices){
            check(!Thread.currentThread().isInterrupted){"Cancelled"}
            val next=IntArray(n);var count=0;var unique=-1
            for(start in 0 until n){
                if(i>0&&start>0&&prior[start-1]>0){unique=if(count==0&&prior[start-1]==1)start-1 else -1;count=minOf(2,count+prior[start-1])}
                val ways=if(i==0)1 else count
                if(ways==0)continue
                val combined=ArrayList<String>(64)
                for(end in start until minOf(n,start+3)){
                    if(heard[end].isEmpty()||heard[end].size>64||source[end].ms-source[start].ms>12000||end>start&&source[end].ms<=source[end-1].ms)break
                    combined.addAll(heard[end]);if(combined.size>wanted[i].size)break
                    if(combined.indices.any{combined[it]!=wanted[i][it]})break
                    if(combined.size==wanted[i].size){
                        if(next[end]==0&&ways==1){starts[i][end]=start;parents[i][end]=unique}else{starts[i][end]=-1;parents[i][end]=-1}
                        next[end]=minOf(2,next[end]+ways);break
                    }
                }
            }
            if(next.none{it>0})return null
            prior=next
        }
        if(prior.sum()!=1)return null
        var end=prior.indexOfFirst{it==1};val times=LongArray(reference.size);var grouped=false
        for(i in reference.indices.reversed()){
            val start=starts[i][end];if(start<0)return null
            if(start<end)grouped=true
            times[i]=source[start].ms;end=parents[i][end]
        }
        if(!grouped||(1 until times.size).any{times[it]<=times[it-1]})return null
        return times.toList()
    }
}
