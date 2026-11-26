package app.remix.player
import java.text.Normalizer
import java.util.Locale
import kotlin.math.abs
object LyricsMatch {
    data class Candidate(val id:Long,val title:String,val artist:String,val duration:Long?,val synced:String?,val plain:String?)
    fun normalize(s:String)=Normalizer.normalize(s,Normalizer.Form.NFKC).lowercase(Locale.ROOT).replace(Regex("[^\\p{L}\\p{N}]+")," ").trim()
    fun titleVariant(s:String)=s.replace(Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus|aac)$"),"").replace(Regex("(?i)\\s*[\\[(](?:official (?:music )?video|official audio|lyrics?|lyric video|sped up|slowed(?: *\\+ *reverb)?|nightcore|daycore)[\\])]\\s*$"),"").trim()
    fun rank(items:List<Candidate>,title:String,artist:String,seconds:Long?):List<Candidate>{
        val names=(listOf(title,titleVariant(title))+LyricsSearchPlan.alternatives(title)).map(::normalize).filter{it.isNotBlank()}.toSet();val who=normalize(artist)
        return items.distinctBy{it.id}.filter{!it.synced.isNullOrBlank()||!it.plain.isNullOrBlank()}.sortedWith(compareByDescending<Candidate>{
            val n=normalize(it.title);val a=normalize(it.artist)
            val name=if(n==normalize(title))125 else if(n in names)100 else if(names.any{q->q.length>=4&&(n.contains(q)||q.contains(n)&&n.length>=4)})35 else 0
            name+(if(who.isNotBlank()&&who==a)60 else 0)+(if(seconds!=null&&it.duration!=null)maxOf(0,20-abs(seconds-it.duration).coerceAtMost(20).toInt())else 0)+(if(!it.synced.isNullOrBlank())5 else 0)
        }.thenBy{it.id})
    }
}
