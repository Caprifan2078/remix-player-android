package app.remix.player
fun main(){
 val steady=DoubleArray(48){.25};val tail=DoubleArray(48){if(it<24).25 else .25*(47-it)/24};val quiet=DoubleArray(48){if(it<16).02 else .25}
 val loud=AdaptiveOverlap.plan(steady,steady);val fade=AdaptiveOverlap.plan(tail,steady);val intro=AdaptiveOverlap.plan(steady,quiet)
 check(!loud.naturalOutro&&loud.duration==4000L);check(fade.naturalOutro&&fade.duration>loud.duration);check(intro.quietIntro&&intro.duration>=6500)
 check(AdaptiveOverlap.plan(null,steady).duration==4500L);check(AdaptiveOverlap.plan(DoubleArray(48){Double.NaN},steady).duration==4500L)
 var count=0
 for(p in listOf(loud,fade,intro,AdaptiveOverlap.plan(tail,quiet)))for(d in 500L..8000L step 250)for(i in 0..100){val g=AdaptiveOverlap.gains(d*i/100,d,p);check(g.outgoing in 0f..1f&&g.incoming in 0f..1f&&g.outgoing+g.incoming<=1.000001f);count++}
 println("PASS: loud outro ${loud.duration}ms; natural fade ${fade.duration}ms; quiet intro ${intro.duration}ms; $count safe gain cases")
 fun c(i:Long,t:String,a:String,d:Long,s:String?="[00:01]line",p:String?="line")=LyricsMatch.Candidate(i,t,a,d,s,p)
 val correct=c(1,"Believer","Imagine Dragons",204);val wrong=c(2,"Believer","Other",204);val remix=c(3,"Believer","Imagine Dragons",260);val unrelated=c(4,"Unrelated","Imagine Dragons",204);val plain=c(5,"Believer","Imagine Dragons",204,null)
 val x=LyricsMatch.rank(listOf(wrong,remix,unrelated,plain,correct,correct),"Believer (Official Video).mp3","Imagine Dragons",205)
 check(x.first()==correct);check(x.size==5);check(plain in x);check(x.indexOf(wrong)>x.indexOf(correct));check(LyricsMatch.titleVariant("Song (Live)")=="Song (Live)");check(LyricsMatch.titleVariant("Song (Slowed + Reverb).mp3")=="Song")
 check(LyricsMatch.normalize("Élan — 123")=="élan 123");println("PASS: title cleanup, version preservation, artist/duration ranking, plain lyrics and deduplication")
 check(LyricsSearchPlan.metadataTitles("Bad filename","Real song")==listOf("Bad filename","Real song"))
 check(LyricsSearchPlan.metadataTitles("Real song"," real SONG ")==listOf("Real song"))
 check(LyricsSearchPlan.metadataTitles("","Real song")==listOf("Real song"))
 check(LyricsSearchPlan.transcriptHint(listOf("la la la","one two three four five six seven eight nine ten eleven twelve")).split(' ').size==10)
 check(LyricsSearchPlan.transcriptHint(listOf("a b","???")).isEmpty())
 check(LyricsSearchPlan.browserUrl("  ")==null)
 val browser=java.net.URI(LyricsSearchPlan.browserUrl("слова & more #test")!!)
 check(browser.host=="www.google.com"&&java.net.URLDecoder.decode(browser.rawQuery,"UTF-8")=="q=слова & more #test lyrics")
 println("PASS: 7 fallback metadata and browser query cases")
}
