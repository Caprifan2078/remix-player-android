package app.remix.player
fun main(){
    data class Song(val id:String,val group:String,val title:String)
    val tracks=listOf(Song("a","a","Привет мир"),Song("b","a","Hardstyle"),Song("c","a","Phonk"),Song("d","d","Hello World"),Song("e","d","Slowed"),Song("f","f","ghbdtn exact"),Song("g","g","Ёлка"),Song("h","h","Nightcore"))
    val index=LibrarySearch(tracks,Song::id,Song::group){listOf(it.title)}
    check(index.find("руддщ").keys==setOf("d")){"English song lost under Russian keyboard"}
    check(index.find("ghbdtn").keys==setOf("f")){"exact matches must win"}
    check(index.find("ghbdtn vbh").keys==setOf("a"))
    check(index.find("ghbdtn vbh").getValue("a").originalMatches)
    check(index.find("ghbdtn").keys==setOf("f"))
    check(index.find("руддщ цщкдв").keys==setOf("d"))
    check(index.find("руддщ цщк").keys==setOf("d"))
    check(index.find("`krf").keys==setOf("g"))
    check(index.find("тшпресщку").keys==setOf("h"))
    check(index.find("hardstyle phonk").isEmpty())
    check(index.find("hello slowed").getValue("d").versions.single().id=="e")
    check(index.find("hello привет").isEmpty())
    check(index.find("").size==5)
    val queries=listOf("руддщ", "руддщ ц", "руддщ цщкдв", "руддщ", "ghbdtn", "ghbdtn vbh", "ghbdtn", "hello", "hello slowed", "", "phonk", "hardstyle phonk", "`krf", "тшпресщку")
    for(q in queries)check(index.find(q)==LibrarySearch(tracks,Song::id,Song::group){listOf(it.title)}.find(q)){"incremental result differs: $q"}
    println("PASS: 13 search cases and 14 incremental/cache comparisons")
}
