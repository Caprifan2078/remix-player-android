package app.remix.player
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import org.json.JSONArray
import org.json.JSONObject

/** User-initiated metadata lookup. No audio upload and no automatic application of a match. */
object LyricsLookup {
    private fun enc(s:String)=URLEncoder.encode(s,"UTF-8")
    private fun request(query:String):JSONArray{
        val c=URL("https://lrclib.net/api/search?"+query).openConnection() as HttpURLConnection
        try{
            c.connectTimeout=7000;c.readTimeout=7000;c.instanceFollowRedirects=false
            c.setRequestProperty("User-Agent","RemixPlayer/0.66 (Android lyrics lookup)");c.setRequestProperty("Accept","application/json")
            val code=c.responseCode;if(code==404)return JSONArray();require(code==200){"LRCLIB: HTTP $code"}
            val text=c.inputStream.use{input->val out=java.io.ByteArrayOutputStream();val b=ByteArray(8192);var total=0;while(true){check(!Thread.currentThread().isInterrupted);val n=input.read(b);if(n<0)break;total+=n;require(total<=2*1024*1024){"Ответ слишком большой"};out.write(b,0,n)};out.toString("UTF-8")}
            return JSONArray(text)
        }finally{c.disconnect()}
    }
    fun search(title:String,artist:String,durationSeconds:Long?):List<LyricsMatch.Candidate>{
        val t=title.trim().take(300);val a=artist.trim().take(200);require(t.isNotEmpty())
        val clean=LyricsMatch.titleVariant(t)
        val queries=listOf("track_name="+enc(t)+(if(a.isNotBlank())"&artist_name="+enc(a)else""),"q="+enc("$t $a".trim()),"track_name="+enc(clean),"q="+enc(clean)).distinct()
        val items=mutableListOf<LyricsMatch.Candidate>();var success=false;var failure:Exception?=null
        for(q in queries){if(Thread.currentThread().isInterrupted)throw InterruptedException()
            try{
                val data=request(q);success=true
                for(i in 0 until minOf(40,data.length())){
                    val o=data.optJSONObject(i)?:continue;val id=o.optLong("id",-1);if(id<0||o.optBoolean("instrumental"))continue
                    fun value(key:String)=if(o.isNull(key))null else o.optString(key).takeIf{it.isNotBlank()&&it.length<=256000}
                    val synced=value("syncedLyrics")?.takeIf{Lrc.parse(it).isNotEmpty()}
                    items.add(LyricsMatch.Candidate(id,o.optString("trackName").take(300),o.optString("artistName").take(200),o.optLong("duration",-1).takeIf{it>0},synced,value("plainLyrics")))
                }
                // Avoid unnecessary network requests when a strict metadata query has a strong match.
                if(items.any{LyricsMatch.normalize(it.title)==LyricsMatch.normalize(t)&&LyricsMatch.normalize(it.artist)==LyricsMatch.normalize(a)&&a.isNotBlank()&&it.synced!=null})break
            }catch(e:Exception){failure=e}
        }
        if(!success)throw (failure?:IllegalStateException("Нет ответа от LRCLIB"))
        return LyricsMatch.rank(items,t,a,durationSeconds).take(10)
    }
}
