package app.remix.player
fun main(){
 fun m(vararg text:String)=text.mapIndexed{i,s->GroupedLyricMatch.Segment(i*2000L,s)}
 fun a(s:List<GroupedLyricMatch.Segment>,vararg lines:String)=GroupedLyricMatch.align(s,lines.toList())
 val split=m("Снова светит", "яркая луна", "Иду домой")
 check(a(split,"Снова светит яркая луна","Иду домой")==listOf(0L,4000L))
 check(a(m("Снова","светит","яркая луна"),"Снова светит яркая луна")==listOf(0L))
 check(a(m("noise","Снова светит","яркая луна","noise","Иду домой"),"Снова светит яркая луна","Иду домой")==listOf(2000L,8000L))
 check(a(m("Ёлка","горит!"),"елка горит")==listOf(0L))
 check(a(m("Снова светит","яркая луна","Снова светит","яркая луна"),"Снова светит яркая луна")==null)
 check(a(m("Снова светит","яркая луна","Снова светит яркая луна"),"Снова светит яркая луна")==null)
 check(a(split,"Снова светит яркая звезда","Иду домой")==null)
 check(a(split,"Иду домой","Снова светит яркая луна")==null)
 check(a(m("Снова","светит","яркая","луна"),"Снова светит яркая луна")==null)
 check(a(listOf(GroupedLyricMatch.Segment(1,"Снова"),GroupedLyricMatch.Segment(13002,"светит")),"Снова светит")==null)
 check(a(listOf(GroupedLyricMatch.Segment(1,"Снова"),GroupedLyricMatch.Segment(1,"светит")),"Снова светит")==null)
 check(a(m("Снова светит яркая луна","Иду домой"),"Снова светит яркая луна","Иду домой")==null)
 check(a(m("word ".repeat(66),"next"),"word ".repeat(66)+"next")==null)
 Thread.currentThread().interrupt();try{check(runCatching{a(split,"Снова светит яркая луна","Иду домой")}.isFailure)}finally{Thread.interrupted()}
 println("PASS: 14 exact grouped ASR matching cases")
}
