package app.remix.player
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import org.json.JSONObject
import org.json.JSONArray

/** Explicit opt-in lookup. Only title, artist and optional duration leave the device. */
object LyricsLookup {
    data class Result(val title:String,val artist:String,val seconds:Long,val synced:String?,val plain:String?)
    private fun enc(s:String)=URLEncoder.encode(s.take(200),"UTF-8")
    private fun request(path:String):String?{
        val c=URL("https://lrclib.net/api/"+path).openConnection() as HttpURLConnection
        try{
            c.connectTimeout=7000;c.readTimeout=7000;c.instanceFollowRedirects=false
            c.setRequestProperty("User-Agent","RemixPlayer/0.66 (Android lyrics lookup)");c.setRequestProperty("Accept","application/json")
            val code=c.responseCode;if(code==404)return null;require(code==200){"LRCLIB: HTTP $code"}
            return c.inputStream.use{input->val out=java.io.ByteArrayOutputStream();val b=ByteArray(8192);var total=0;while(true){check(!Thread.currentThread().isInterrupted);val n=input.read(b);if(n<0)break;total+=n;require(total<=2*1024*1024){"Ответ слишком большой"};out.write(b,0,n)};out.toString("UTF-8")}
        }finally{c.disconnect()}
    }
    private fun row(j:JSONObject):Result?{
        if(j.optBoolean("instrumental"))return null
        val title=j.optString("trackName").take(300);val artist=j.optString("artistName").take(300)
        val seconds=j.optDouble("duration",0.0).takeIf{it.isFinite()&&it in 0.0..86400.0}?.toLong()?:0
        fun value(k:String)=if(j.isNull(k))null else j.optString(k).takeIf{it.isNotBlank()&&it.length<=200000}
        val synced=value("syncedLyrics")?.takeIf{Lrc.parse(it).isNotEmpty()}
        val plain=value("plainLyrics")
        if(title.isBlank()||synced==null&&plain==null)return null
        return Result(title,artist,seconds,synced,plain)
    }
    fun search(title:String,artist:String):List<Result>{
        val q=LyricsMatch.query(title,artist);if(q.title.isBlank())return emptyList()
        fun load(path:String):List<Result>{val text=request(path)?:return emptyList();val arr=JSONArray(text);return (0 until minOf(arr.length(),30)).mapNotNull{i->arr.optJSONObject(i)?.let(::row)}}
        val first=load("search?track_name="+enc(q.title)+(if(q.artist.isBlank())"" else "&artist_name="+enc(q.artist)))
        return if(first.isNotEmpty())first else load("search?q="+enc(listOf(q.artist,q.title).filter{it.isNotBlank()}.joinToString(" ")))
    }
    fun fetch(title:String,artist:String,durationSeconds:Long?):String?{
        val q=LyricsMatch.query(title,artist);if(q.title.isBlank())return null
        if(q.artist.isNotBlank()){
            val exact=request("get?track_name="+enc(q.title)+"&artist_name="+enc(q.artist)+(durationSeconds?.takeIf{it>0}?.let{"&duration=$it"}?:""))
            if(exact!=null){val r=row(JSONObject(exact));if(r!=null&&LyricsMatch.choose(q,durationSeconds,listOf(LyricsMatch.Candidate(r.title,r.artist,r.seconds,r.synced!=null)))==0)return r.synced}
        }
        val rows=search(q.title,q.artist)
        val index=LyricsMatch.choose(q,durationSeconds,rows.map{LyricsMatch.Candidate(it.title,it.artist,it.seconds,it.synced!=null)})
        return index?.let{rows[it].synced}
    }
}
