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
 val plain=a.copy(synced=null,plain="example")
 fun automatic(items:List<LyricsMatch.Candidate>,title:String="Song",artist:String="Artist",seconds:Long?=200)=BatchLyricPolicy.chooseAutomatic(items,title,artist,seconds)
 val checks=listOf(automatic(listOf(a))==text,automatic(listOf(plain))=="example",automatic(listOf(a,plain))==text,automatic(listOf(plain,plain.copy(id=2)))=="example",automatic(listOf(plain,plain.copy(id=2,plain="other")))==null,automatic(listOf(a,a.copy(id=2,synced="[00:02]example")))==null,automatic(listOf(plain),artist="Unknown artist")==null,automatic(listOf(plain),seconds=204)==null,automatic(listOf(plain),title="Song (Live)")==null,automatic(listOf(plain),title="Song.mp3")=="example",automatic(listOf(plain.copy(duration=0)),seconds=1)==null,automatic(listOf(plain.copy(title="Song x Other")),title="Song x Other")==null)
 fun merge(x:String?,y:String?)=BatchLyricPolicy.merge(x,y,{it.startsWith("[")},{it.substringAfter(']',it)})
 val merges=listOf(merge(null,text)==text,merge("Example!",text)==text,merge("wrong",text)=="wrong",merge(text,"[00:02]example")==text,merge("example",null)=="example",merge("example","other")=="example",merge(null,null)==null)
 (checks+merges).forEachIndexed{i,pass->check(pass){"Automatic lyric case "+(i+1)}}
 println("PASS: 31 conservative selection, automatic lookup and safe merge cases")
}
