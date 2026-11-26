package app.remix.player
import java.text.Normalizer
import java.util.Locale
object LyricLineSearch {
    data class Line(val text:String,val ms:Long?=null)
    const val MAX_RESULTS=80
    private val marks=Regex("\\p{M}+")
    private val separators=Regex("[^\\p{L}\\p{N}]+")
    fun normalize(s:String):String=Normalizer.normalize(s.lowercase(Locale.ROOT).replace('ё','е'),Normalizer.Form.NFD).replace(marks,"").replace(separators," ").trim()
    data class PairLine(val original:Line,val translation:String)
    fun pair(lines:List<Line>,raw:String):List<PairLine>?{
        if(raw.length>64000)return null
        val translated=raw.lineSequence().map{it.trim()}.filter{it.isNotEmpty()}.toList()
        if(lines.isEmpty()||translated.size!=lines.size)return null
        return lines.zip(translated){line,text->PairLine(line,text)}
    }
    fun find(lines:List<Line>,query:String):List<Line>{
        val q=normalize(query.take(200));if(q.isBlank())return emptyList()
        return lines.asSequence().filter{it.text.isNotBlank()&&normalize(it.text).contains(q)}.take(MAX_RESULTS).toList()
    }
}
