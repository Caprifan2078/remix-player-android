package app.remix.player
fun main(){
    val lines=listOf(LyricLineSearch.Line("Всё, что было",1000),LyricLineSearch.Line("Café déjà vu",2500),LyricLineSearch.Line("Всё, что было",4000),LyricLineSearch.Line("Unmarked"))
    check(LyricLineSearch.find(lines,"все что").map{it.ms}==listOf(1000L,4000L))
    check(LyricLineSearch.find(lines,"CAFE DEJA").single().ms==2500L)
    check(LyricLineSearch.find(lines,"unmarked").single().ms==null)
    check(LyricLineSearch.find(lines,"???").isEmpty())
    check(LyricLineSearch.find(lines,"missing").isEmpty())
    check(LyricLineSearch.find(List(1000){LyricLineSearch.Line("match",it.toLong())},"match").size==80)
    check(LyricLineSearch.pair(lines,"One\nTwo\nThree\nFour")?.get(1)?.original?.ms==2500L)
    check(LyricLineSearch.pair(lines,"One\nTwo")==null)
    check(LyricLineSearch.pair(lines,"One\n\nTwo\nThree\nFour")?.size==4)
    check(LyricLineSearch.pair(lines,"x".repeat(64001))==null)
    println("PASS: 10 lyric search and translation pairing checks")
}
