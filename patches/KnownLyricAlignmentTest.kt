package app.remix.player
fun main(){
 val enhanced="[00:02.000]<00:02.000>Hello <00:03.000>world\n[00:09.000]<00:09.000>Stay <00:10.000>here"
 val plain="Hello world\nStay here"
 val a=KnownLyricAlignment.align(enhanced,plain)!!
 check(a.wordLevel&&LyricDocument.plain(a.lrc)==plain)
 check(WordLyrics.parse(Lrc.parse(a.lrc)[1]).words.first().ms==9000L)
 val b=KnownLyricAlignment.align("[00:03.000]Hello world\n[00:07.000]Stay here",plain)!!
 check(!b.wordLevel&&Lrc.parse(b.lrc).map{it.ms}==listOf(3000L,7000L))
 check(KnownLyricAlignment.align(enhanced,"Hello world\nMissing line")==null)
 check(KnownLyricAlignment.align("[00:01.000]Hello world\n[00:05.000]Hello world","Hello world")==null)
 check(KnownLyricAlignment.align("",plain)==null)
 check(KnownLyricAlignment.align(enhanced,"")==null)
 println("PASS: 7 known lyric alignment cases")
}
