package app.remix.player

import java.net.URLEncoder

/** Only search terms are transmitted; never attach audio or the complete transcript. */
object BrowserLyricImport {
    fun query(title:String,artist:String,phrase:String?=null):String {
        val p=phrase?.trim()?.take(180).orEmpty()
        val terms=if(p.isNotBlank()) p else listOf(title.trim().take(200),artist.trim().take(120)).filter{it.isNotBlank()}.joinToString(" ")
        return (terms+" lyrics текст песни").trim()
    }
    fun url(title:String,artist:String,phrase:String?=null):String =
        "https://www.google.com/search?q="+URLEncoder.encode(query(title,artist,phrase),"UTF-8")
    /** Reject links, empty pages, accidental menus and oversized clipboard data. */
    fun candidate(raw:String):String? {
        if(raw.length>500000)return null
        val s=raw.replace("\r\n","\n").replace('\r','\n').trim().trimStart('\uFEFF').trim()
        if(s.isBlank()||s.any{it.isISOControl()&&it !in "\n\t"}||s.toByteArray(Charsets.UTF_8).size>1024*1024)return null
        if(Regex("(?i)^https?://\\S+$").matches(s)||s.startsWith("<!DOCTYPE",true)||s.startsWith("<html",true))return null
        return s.takeIf{it.any(Char::isLetter)}
    }
}
