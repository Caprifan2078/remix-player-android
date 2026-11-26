package app.remix.player
fun main(){
 val text="[00:01.00]example"
 val a=LyricsMatch.Candidate(1,"Song","Artist",200,text,null)
 fun pick(items:List<LyricsMatch.Candidate>,t:String="Song",artist:String="Artist",d:Long?=200)=BatchLyricPolicy.choose(items,t,artist,d)
 check(pick(listOf(a))==text)
 check(pick(listOf(a,a.copy(id=2)))==text)
 check(pick(listOf(a,a.copy(id=2,synced="[00:02.00]different")))==null)
 check(pick(listOf(a),d=204)==null)
 check(pick(listOf(a),d=203)==text)
 check(pick(listOf(a),artist="Unknown artist")==null)
 check(pick(listOf(a),d=null)==null)
 check(pick(listOf(a),t="Song (Live)")==null)
 check(pick(listOf(a),t="Song (Slowed)")==null)
 check(pick(listOf(a),t="Song.mp3")==text)
 check(pick(listOf(a.copy(synced=null,plain="example")))==null)
 check(pick(listOf(a.copy(artist="Another")))==null)
 println("PASS: 12 conservative batch lyric selection cases")
}
