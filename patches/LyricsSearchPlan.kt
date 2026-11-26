package app.remix.player
import java.net.URLEncoder
import java.util.Locale

/** Broader discovery without treating a remix or mashup as a verified original. */
object LyricsSearchPlan {
    private val format=Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus|aac|webm|mp4)$")
    private val extra=Regex("(?i)\\s*[\\[(]\\s*(?:official(?:\\s+(?:music\\s+video|video|audio|lyrics?))?|lyrics?|lyric\\s+video|visualizer|audio|video|sped\\s*up|slowed(?:\\s*(?:\\+|and|&)\\s*reverb)?|reverb|nightcore|daycore|bass\\s*boost|(?:[^\\]\\)]+\\s+)?(?:remix|mashup))\\s*[\\])]\\s*")
    private val suffix=Regex("(?i)\\s+(?:[-–—|]\\s*)?(?:sped\\s*up|slowed(?:\\s*(?:\\+|and|&)\\s*reverb)?|nightcore|daycore|bass\\s*boost|official\\s+(?:music\\s+)?video|lyrics?|mashup|remix)\\s*$")
    private val mash=Regex("(?i)\\s+(?:x|×|vs\\.?|versus)\\s+")
    private val artistTitle=Regex("\\s+[-–—]\\s+")
    fun clean(input:String):String {
        var s=input.trim().replace(format,"").replace('_',' ').replace(Regex("^\\s*\\d{1,3}[.)-]\\s+"),"")
        repeat(3){s=s.replace(extra," ").replace(suffix,"").trim()}
        return s.replace(Regex("\\s+")," ").trim()
    }
    fun components(title:String)=clean(title).split(mash).map{it.trim()}.filter{it.length>=3}.take(3)
    fun isComposite(title:String)=components(title).size>1
    fun artistKnown(artist:String)=artist.isNotBlank()&&LyricsMatch.normalize(artist) !in setOf("unknown","unknown artist","неизвестный исполнитель","неизвестно","без исполнителя")
    fun alternatives(title:String):List<String>{
        val full=clean(title)
        val pair=full.split(artistTitle,limit=2)
        return (listOf(title.trim(),full)+components(title)+if(pair.size==2)listOf(pair[1].trim())else emptyList()).filter{it.length>=2}.distinct()
    }
    private fun enc(s:String)=URLEncoder.encode(s,"UTF-8")
    fun queries(title:String,artist:String,expanded:Boolean=true):List<String>{
        val t=title.trim().take(300);val a=artist.trim().take(200);val clean=clean(t)
        val out=linkedSetOf<String>()
        fun track(s:String,who:String=""){if(s.isNotBlank())out.add("track_name="+enc(s)+if(who.isNotBlank())"&artist_name="+enc(who)else "")}
        fun q(s:String){if(s.isNotBlank())out.add("q="+enc(s))}
        if(artistKnown(a)){track(t,a);if(expanded&&clean!=t)track(clean,a)}
        track(t)
        if(!expanded)return out.take(2)
        val parts=components(t)
        if(parts.size>1)parts.forEach{track(it)}
        val pair=clean.split(artistTitle,limit=2)
        if(pair.size==2){track(pair[1],pair[0]);track(pair[1])}
        track(clean);q(clean)
        if(artistKnown(a))q("$clean $a")
        return out.take(7)
    }
    /** Keep the user's corrected query first; use file tags only as an alternative. */
    fun metadataTitles(entered:String,tag:String?):List<String> =
        listOfNotNull(entered,tag).map{it.trim().take(300)}.filter{it.isNotBlank()}.distinctBy{LyricsMatch.normalize(it)}
    /** A short editable snippet, not the entire recognized song. */
    fun transcriptHint(lines:List<String>):String {
        val candidates=lines.asSequence().take(100).map{line->
            Regex("[\\p{L}\\p{N}]+(?:['’][\\p{L}]+)?").findAll(line.take(500)).map{it.value}.take(10).toList()
        }.filter{it.size>=3}.toList()
        val words=candidates.maxWithOrNull(compareBy<List<String>>{it.map{w->w.lowercase(Locale.ROOT)}.distinct().size}.thenBy{it.size})?:return ""
        return words.joinToString(" ").take(120)
    }
    fun browserUrl(query:String):String? {
        val q=query.trim().replace(Regex("\\s+")," ").take(180)
        if(q.isBlank())return null
        return "https://www.google.com/search?q="+enc("$q lyrics")
    }
    fun exact(title:String,artist:String,seconds:Long?,candidate:LyricsMatch.Candidate):Boolean =
        artistKnown(artist)&&LyricsMatch.normalize(artist).isNotBlank()&&LyricsMatch.normalize(title).isNotBlank()&&!isComposite(title)&&LyricsMatch.normalize(title)==LyricsMatch.normalize(candidate.title)&&LyricsMatch.normalize(artist)==LyricsMatch.normalize(candidate.artist)&&seconds!=null&&seconds>0&&candidate.duration!=null&&candidate.duration>0&&kotlin.math.abs(seconds-candidate.duration)<=3&&!candidate.synced.isNullOrBlank()
}
