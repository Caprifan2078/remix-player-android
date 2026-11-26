package app.remix.player
import java.security.MessageDigest

object AutoTranslationPolicy {
    data class Guess(val language:String,val confidence:Float)
    fun language(text:String,guesses:List<Guess>,supported:Set<String>):String?{
        if(text.count(Char::isLetter)<40)return null
        val ranked=guesses.filter{it.confidence.isFinite()&&it.confidence in 0f..1f}.sortedByDescending{it.confidence}
        val best=ranked.firstOrNull()?:return null
        val other=ranked.firstOrNull{it.language!=best.language}
        if(best.confidence<.80f||(other!=null&&best.confidence-other.confidence<.20f))return null
        return best.language.takeIf{it!="und"&&it in supported}
    }
    fun key(uri:String,raw:String)=MessageDigest.getInstance("SHA-256").digest((uri+"\u0000"+raw).toByteArray(Charsets.UTF_8)).joinToString(""){"%02x".format(it.toInt() and 255)}
    fun valid(source:List<String>,translated:List<String>)=source.isNotEmpty()&&source.size==translated.size&&translated.size<=2000&&translated.sumOf{it.length.toLong()}<=256000&&translated.indices.all{i->translated[i].length<=4000&&(source[i].isBlank()==translated[i].isBlank())}
    fun pending(enabled:Boolean,raw:String,alreadySaved:Boolean,attempted:Boolean)=enabled&&raw.isNotBlank()&&!alreadySaved&&!attempted
}
