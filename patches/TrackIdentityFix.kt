package app.remix.player
import java.util.Locale
object TrackIdentityFix {
    data class Identity(val title:String,val artist:String)
    fun knownArtist(value:String)=value.trim().lowercase(Locale.ROOT) !in setOf("","unknown","unknown artist","неизвестный исполнитель","неизвестно","<unknown>","n/a","unknown artists","various artists","разные исполнители")
    private val versions=Regex("(?iu)(?:remix|remaster|remastered|nightcore|daycore|sped[ -]?up|speed[ -]?up|slowed|reverb|hardstyle|bootleg|mashup|cover|live|edit|ремикс|ускоренн|замедленн|кавер)")
    fun fromTags(current:Identity,tagTitle:String?,tagArtist:String?):Identity{
        val title=current.title
        val clean=title.replace(Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus|aac)$"),"").trim()
        val tag=tagTitle?.trim()?.takeIf{it.isNotBlank()&&it.length<=300}
        val placeholder=clean.isBlank()||Regex("(?i)(?:track|audio|song|трек)[ _-]*\\d+").matches(clean)
        val chosen=when{
            versions.containsMatchIn(title)->clean.ifBlank{title}
            tag!=null&&(placeholder||title!=clean&&clean.equals(tag,true))->tag
            else->clean.ifBlank{title}
        }
        val artist=if(!knownArtist(current.artist)&&tagArtist!=null&&knownArtist(tagArtist)&&tagArtist.length<=200)tagArtist.trim()else current.artist
        return Identity(chosen,artist)
    }
    fun verifiedArtist(current:String,artists:List<String>):String{
        if(knownArtist(current))return current
        val known=artists.map{it.trim()}.filter{knownArtist(it)&&it.length<=200}.distinctBy{it.lowercase(Locale.ROOT)}
        return known.singleOrNull()?:current
    }
}
