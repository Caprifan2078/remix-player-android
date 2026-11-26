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
 val ref="Hello bright stars shine tonight\nWe walk slowly down the street"
 val heard="[00:02.000]Hello bright scars shine tonight\n[00:07.000]We walk slowly round the street"
 fun noisy(h:String,r:String)=KnownLyricAlignment.alignNoisyPhrases(h,r)
 val n=noisy(heard,ref)!!
 check(!n.wordLevel)
 check(LyricDocument.plain(n.lrc)==ref)
 check(Lrc.parse(n.lrc).map{it.ms}==listOf(2000L,7000L))
 check(noisy(heard,"Goodbye bright stars shine tonight\nWe walk slowly down the street")==null)
 check(noisy(heard,"Hello wrong words not tonight\nWe walk slowly down the street")==null)
 check(noisy(heard,"We walk slowly down the street\nHello bright stars shine tonight")==null)
 check(noisy(heard+"\n[00:10.000]We walk slowly down the street",ref)==null)
 check(noisy("[00:02.000]Hello bright scars shine tonight\n[00:02.000]We walk slowly round the street",ref)==null)
 check(noisy("[00:02.000]Hello bright scars shine tonight\n[00:04.000]Noise between phrases\n[00:07.000]We walk slowly round the street",ref)?.lrc==n.lrc)
 check(noisy("[00:02.000]One two","One three")==null)
 check(noisy("[00:02.000]One two","One two")!=null)
 check(noisy("",ref)==null)
 Thread.currentThread().interrupt()
 val stopped=try{runCatching{noisy(heard,ref)}.isFailure}finally{Thread.interrupted()}
 check(stopped)
 check(noisy("[00:02.000]"+"word ".repeat(66),"word ".repeat(66))==null)
 val split="[00:02.000]Снова светит\n[00:04.000]яркая луна\n[00:08.000]Иду домой"
 val splitRef="Снова светит яркая луна\nИду домой"
 val grouped=KnownLyricAlignment.alignGroupedPhrases(split,splitRef)!!
 check(!grouped.wordLevel&&LyricDocument.plain(grouped.lrc)==splitRef)
 check(Lrc.parse(grouped.lrc).map{it.ms}==listOf(2000L,8000L))
 check(KnownLyricAlignment.align(split,splitRef)?.lrc==grouped.lrc)
 println("PASS: 24 known lyric alignment cases, including split and noisy phrase recovery")
}
