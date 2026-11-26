package app.remix.player

/** Re-decode a bounded phrase only to recover missing measured word timings.
 * Never replace the recognized words or merge ambiguous repeated phrases. */
object PhraseTimingRetry {
    data class Span(val start:Long,val end:Long,val text:String,val words:List<Long>)
    private val pattern=Regex("\\S+")
    private fun identity(s:String)=java.text.Normalizer.normalize(s,java.text.Normalizer.Form.NFKC).lowercase(java.util.Locale.ROOT).trim().replace(Regex("\\s+")," ")
    fun eligible(s:Span)=s.words.isEmpty()&&s.end-s.start in 350..12000&&pattern.findAll(s.text).count() in 1..80
    fun select(original:Span,candidates:List<Span>):List<Long>?{
        if(!eligible(original))return null
        val same=candidates.filter{identity(it.text)==identity(original.text)&&kotlin.math.abs(it.start-original.start)<=500&&kotlin.math.abs(it.end-original.end)<=900}
        val c=same.singleOrNull()?:return null
        val n=pattern.findAll(original.text).count()
        if(c.words.size!=n||c.words.zipWithNext().any{(a,b)->a>=b}||c.words.any{it<original.start||it>=original.end})return null
        return c.words
    }
}
