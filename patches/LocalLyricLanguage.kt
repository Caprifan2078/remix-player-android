package app.remix.player

import com.google.android.gms.tasks.Tasks
import com.google.mlkit.nl.languageid.LanguageIdentification
import com.google.mlkit.nl.languageid.LanguageIdentificationOptions
import java.util.concurrent.TimeUnit

object LocalLyricLanguage {
    fun lines(raw:String):List<String>{
        val timed=Lrc.parse(raw)
        return if(timed.isNotEmpty())timed.map{WordLyrics.parse(it).text}
        else LyricDocument.plain(raw).lines().map{it.trim()}.filter{it.isNotEmpty()}
    }
    fun detect(lines:List<String>):String?{
        val sample=lines.asSequence().filter{it.isNotBlank()}.distinct().joinToString("\n").take(6000)
        val client=LanguageIdentification.getClient(LanguageIdentificationOptions.Builder().setConfidenceThreshold(.05f).build())
        try{
            val guesses=Tasks.await(client.identifyPossibleLanguages(sample),20,TimeUnit.SECONDS)
            return AutoTranslationPolicy.language(sample,guesses.map{AutoTranslationPolicy.Guess(it.languageTag,it.confidence)},LyricTranslation.languages.keys)
        }finally{client.close()}
    }
}
