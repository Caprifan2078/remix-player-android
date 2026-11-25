package app.remix.player
import kotlin.math.abs
fun main(){
    val line=WordLyrics.parse(Lyric(1000,"<00:01.000>Первое <00:02.000>второе <00:03.000>третье"))
    check(WordLyrics.highlight(line,WordLyrics.current(line,999))==null)
    val a=WordLyrics.highlight(line,WordLyrics.current(line,1000))!!;check(a.completedEnd==0&&line.text.substring(a.activeStart,a.activeEnd)=="Первое ")
    val b=WordLyrics.highlight(line,WordLyrics.current(line,2500))!!;check(b.completedEnd==a.activeEnd&&line.text.substring(b.activeStart,b.activeEnd)=="второе ")
    val c=WordLyrics.highlight(line,WordLyrics.current(line,3500))!!;check(c.completedEnd==b.activeEnd)
    check(WordLyrics.highlight(line,WordLyrics.current(line,1000))==a)
    check(WordLyrics.highlight(WordLyrics.parse(Lyric(0,"no word timing")),0)==null)
    println("PASS: timed-word cumulative highlighting, backward seek, no fake timing")
    val w=OverlapCore.window(12000,12000,3000)!!
    var checked=0
    for(late in 0L..3000L){
        val actual=OverlapCore.startWindow(w,w.start+late)
        if(late>2500){check(actual==null);continue}
        check(actual!=null&&actual.duration==3000-late&&actual.start==9000+late)
        for(p in listOf(0L,50L,250L,500L,1000L,3000L)){
            for(delay in listOf(0L,100L,400L,800L,1200L)){
                val incoming=(p-delay).coerceAtLeast(0)
                val elapsed=OverlapCore.synchronizedElapsed(p,incoming,actual.duration)
                check(elapsed<=incoming&&elapsed in 0..actual.duration)
                val g=OverlapCore.gains(elapsed,actual.duration)
                check(g.outgoing in 0f..1f&&g.incoming in 0f..1f&&abs(g.outgoing+g.incoming-1f)<.000001f)
                if(incoming==0L)check(g.outgoing==1f&&g.incoming==0f)
                checked++
            }
        }
    }
    println("PASS: 3001 late decoder start cases; $checked synchronized gain cases, bounded sum and no fade before incoming audio")
}
