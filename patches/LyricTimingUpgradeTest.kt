package app.remix.player
fun main(){
    fun line(t:Long,s:String,vararg words:Long)=LyricTimingUpgrade.Line(t,s,words.toList())
    val before=listOf(line(2000,"Ёлка горит"),line(7000,"Все поют"))
    val after=listOf(line(1900,"Ёлка горит",1900,3100),line(7200,"Все поют",7200,8100))
    fun accepts(a:List<LyricTimingUpgrade.Line>)=LyricTimingUpgrade.accept(before,a)
    val tests=listOf(
        "line only eligible" to LyricTimingUpgrade.eligible(before),
        "valid complete upgrade" to accepts(after),
        "empty rejected" to !LyricTimingUpgrade.eligible(emptyList()),
        "already enhanced preserved" to !LyricTimingUpgrade.eligible(after),
        "mixed preserved" to !LyricTimingUpgrade.eligible(listOf(before[0],after[1])),
        "duplicate time rejected" to !LyricTimingUpgrade.eligible(listOf(before[0],before[1].copy(start=2000))),
        "wrong text rejected" to !accepts(listOf(after[0].copy(text="Елка горит"),after[1])),
        "missing line rejected" to !accepts(after.take(1)),
        "missing markers rejected" to !accepts(listOf(after[0],after[1].copy(words=emptyList()))),
        "wrong occurrence rejected" to !accepts(listOf(after[0].copy(start=3000,words=listOf(3000,3500)),after[1])),
        "equal word times rejected" to !accepts(listOf(after[0].copy(words=listOf(1900,1900)),after[1])),
        "word before line rejected" to !accepts(listOf(after[0].copy(words=listOf(1800,3100)),after[1])),
        "cross next original line rejected" to !accepts(listOf(after[0].copy(words=listOf(1900,7000)),after[1])),
        "cross next new line rejected" to !accepts(listOf(after[0].copy(words=listOf(1900,6800)),after[1].copy(start=6600,words=listOf(6600,8000)))),
        "late first word rejected" to !accepts(listOf(after[0].copy(words=listOf(2900,3500)),after[1])),
        "one-word line eligible" to LyricTimingUpgrade.accept(listOf(line(1000,"Да")),listOf(line(1000,"Да",1000)))
    )
    tests.forEach{(name,ok)->check(ok){name};println("PASS: $name")}
    println("PASS: ${tests.size} lyric timing upgrade cases")
}
