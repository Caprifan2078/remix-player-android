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
    /** Accept plain lyrics only for the same unambiguous recording. */
    fun chooseAutomatic(items:List<LyricsMatch.Candidate>,title:String,artist:String,seconds:Long?):String? {
        if(seconds==null||seconds<=0||!LyricsSearchPlan.artistKnown(artist)||LyricsSearchPlan.isComposite(title))return null
        val name=LyricsMatch.normalize(title.replace(Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus|aac)$"),""))
        val who=LyricsMatch.normalize(artist)
        if(name.isBlank()||who.isBlank())return null
        val exact=items.filter{LyricsMatch.normalize(it.title)==name&&LyricsMatch.normalize(it.artist)==who&&it.duration!=null&&it.duration>0&&abs(it.duration-seconds)<=3}
        val timed=exact.mapNotNull{it.synced?.trim()?.takeIf{v->v.isNotBlank()}}.distinct()
        if(timed.isNotEmpty())return timed.singleOrNull()
        return exact.mapNotNull{it.plain?.trim()?.takeIf{v->v.isNotBlank()}}.distinct().singleOrNull()
    }
    /** Upgrade untimed lyrics only when the words agree; never silently replace a timed text. */
    fun merge(known:String?,candidate:String?,isTimed:(String)->Boolean,plainText:(String)->String):String? {
        val base=known?.takeIf{it.isNotBlank()};val next=candidate?.takeIf{it.isNotBlank()}
        if(base==null)return next
        if(next==null||isTimed(base)||!isTimed(next))return base
        val words=LyricsMatch.normalize(plainText(base))
        return if(words.isNotBlank()&&words==LyricsMatch.normalize(plainText(next)))next else base
    }
}
