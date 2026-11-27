package app.remix.player
fun main(){
    fun r(title:String,artist:String,sec:Long=200,synced:Boolean=true)=LyricsMatch.Candidate(title,artist,sec,synced)
    val q=LyricsMatch.query("t.A.T.u. - Нас не догонят [muzfone.com].mp3","Неизвестный исполнитель")
    check(q.title=="Нас не догонят"&&q.artist=="t.A.T.u."){q}
    check(LyricsMatch.query("-- Song_www_lightaudio_ru.mp3","Unknown artist").title=="Song")
    check(LyricsMatch.choose(q,200,listOf(r("Нас не догонят","t.A.T.u."),r("Нас не догонят","Другой артист")))==0)
    check(LyricsMatch.choose(q,200,listOf(r("Нас не догонят (remix)","t.A.T.u.")))==null)
    check(LyricsMatch.choose(q,200,listOf(r("Нас не догонят","t.A.T.u.",220)))==null)
    check(LyricsMatch.choose(q,200,listOf(r("Нас не догонят","t.A.T.u.",200,false)))==null)
    val unknown=LyricsMatch.Query("Нас не догонят","")
    check(LyricsMatch.choose(unknown,200,listOf(r("Нас не догонят","t.A.T.u."),r("Нас не догонят","Другой артист")))==null)
    check(LyricsMatch.choose(unknown,null,listOf(r("Нас не догонят","t.A.T.u.")))==null)
    check(LyricsMatch.choose(q,200,listOf(r("Нас не догонят","t.A.T.u.",199),r("Нас не догонят","t.A.T.u.",201)))==null)
    println("PASS: cleaned filenames, strict recording match, no ambiguous automatic assignment")
}
