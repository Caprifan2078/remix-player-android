package app.remix.player
import java.text.Normalizer
import java.util.Locale
object LyricLineSearch {
    data class Line(val text:String,val ms:Long?=null)
    const val MAX_RESULTS=80
    private val marks=Regex("\\p{M}+")
    private val separators=Regex("[^\\p{L}\\p{N}]+")
    private val latinMarks=Regex("(?<=\\p{IsLatin})\\p{M}+")
    fun normalize(s:String):String {
        val decomposed=Normalizer.normalize(s.lowercase(Locale.ROOT),Normalizer.Form.NFD)
        val composed=Normalizer.normalize(decomposed.replace(latinMarks,""),Normalizer.Form.NFC)
        return composed.replace('ё','е').replace(marks,"").replace(separators," ").trim()
    }
    data class PairLine(val original:Line,val translation:String)
    fun pair(lines:List<Line>,raw:String):List<PairLine>?{
        if(raw.length>64000)return null
        val translated=raw.lineSequence().map{it.trim()}.filter{it.isNotEmpty()}.toList()
        if(lines.isEmpty()||translated.size!=lines.size)return null
        return lines.zip(translated){line,text->PairLine(line,text)}
    }
    class Index(lines:List<Line>){
        private val entries=lines.mapNotNull{line->normalize(line.text).takeIf{it.isNotBlank()}?.let{line to it}}
        fun find(query:String):List<Line>{
            val q=normalize(query.take(200));if(q.isBlank())return emptyList()
            return entries.asSequence().filter{it.second.contains(q)}.take(MAX_RESULTS).map{it.first}.toList()
        }
    }
    fun find(lines:List<Line>,query:String):List<Line> = Index(lines).find(query)
}
