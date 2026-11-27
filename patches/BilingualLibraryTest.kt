package app.remix.player
fun main(){
 data class Song(val id:String,val group:String,val title:String,val artist:String,val album:String="")
 val songs=listOf(Song("a","a","Группа крови","Кино","Звезда"),Song("b","a","Ночной ремикс",""),Song("c","a","Hardstyle",""),Song("d","d","Kukushka","Polina Gagarina"),Song("e","e","Кукушка","Кино"),Song("f","f","Пачка сигарет","Виктор Цой"),Song("g","g","Pachka sigaret","Viktor Tsoy"))
 val index=LibrarySearch(songs,Song::id,Song::group){listOf(it.title,it.artist,it.album)}
 val cases=mapOf("gruppa krovi" to setOf("a"),"kino группа" to setOf("a"),"кукушка" to setOf("d","e"),"kukushka" to setOf("d","e"),"polina гагарина" to setOf("d"),"звезда" to setOf("a"),"zvezda" to setOf("a"),"kino yjxyjq" to setOf("a"),"hardstyle ремикс" to emptySet(),"пачка сигарет" to setOf("f","g"),"pachka sigaret" to setOf("f","g"),"виктор цой" to setOf("f","g"),"unknown" to emptySet())
 for((q,want) in cases){val got=index.find(q).keys;check(got==want){"$q: $got != $want"}}
 val q=LyricsMatch.Query("Группа крови","Кино")
 check(LyricsMatch.variants(q).any{it.title=="Группа крови"&&it.artist=="kino"})
 check(LyricsMatch.variants(q).any{it.title=="gruppa krovi"&&it.artist=="Кино"})
 check(LyricsMatch.variants(q).any{it.title=="gruppa krovi"&&it.artist=="kino"})
 println("PASS: 16 general bilingual library and independent query variants")
}
