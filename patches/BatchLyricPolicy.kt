package app.remix.player
import kotlin.math.abs
/** Batch mode is deliberately more conservative than interactive search. */
object BatchLyricPolicy {
    fun choose(items:List<LyricsMatch.Candidate>,title:String,artist:String,seconds:Long?):String? {
        if(seconds==null||seconds<=0||title.isBlank()||artist.isBlank())return null
        val who=LyricsMatch.normalize(artist)
        if(who in setOf("неизвестный исполнитель","unknown","unknown artist","неизвестно"))return null
        // Do not strip remix, live or speed tags in automatic mode.
        val name=LyricsMatch.normalize(title.replace(Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus|aac)$"),""))
        val exact=items.filter{LyricsMatch.normalize(it.title)==name&&LyricsMatch.normalize(it.artist)==who&&it.duration!=null&&abs(it.duration-seconds)<=3&&!it.synced.isNullOrBlank()}
        val texts=exact.mapNotNull{it.synced?.trim()}.distinct()
        return texts.singleOrNull()
    }
}
