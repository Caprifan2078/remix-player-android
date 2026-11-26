package app.remix.player
import java.text.Normalizer
import java.util.Locale

/** Local content comparison; never sends the transcript to the metadata service. */
object TranscriptMatch {
    private val words=Regex("[\\p{L}\\p{N}]+")
    private fun tokens(text:String)=words.findAll(Normalizer.normalize(text.take(64000),Normalizer.Form.NFKC).lowercase(Locale.ROOT).replace('ё','е')).take(2500).map{it.value}.toList()
    data class Score(val matching:Int,val total:Int){val fraction get()=if(total==0)0.0 else matching.toDouble()/total;val plausible get()=matching>=3&&fraction>=.22}
    private fun phrases(text:String)=tokens(text).windowed(5).filter{it.toSet().size>=4}.distinct()
    private fun masks(w:List<String>)=(0..4).map{skip->skip.toString()+":"+w.filterIndexed{i,_->i!=skip}.joinToString(" ")}
    fun score(heard:String,reference:String):Score{
        val query=phrases(heard);if(query.isEmpty())return Score(0,0)
        val index=phrases(reference).flatMap(::masks).toHashSet()
        return Score(query.count{w->masks(w).any{it in index}},query.size)
    }
    /** A short distinctive phrase for an explicit browser fallback. */
    fun query(heard:String):String = heard.lineSequence().map{tokens(it).take(10)}.filter{it.size>=5&&it.distinct().size>=4}.maxByOrNull{it.distinct().size}?.joinToString(" ").orEmpty().take(180)
}
