package app.remix.player

import android.app.job.JobInfo
import android.app.job.JobParameters
import android.app.job.JobScheduler
import android.app.job.JobService
import android.content.ComponentName
import android.content.Context
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import java.util.concurrent.Executors
import java.util.concurrent.Future

/** System-managed, opt-in charging/Wi-Fi job. The worker never edits the active library.
 * Results are atomically staged per track and applied by the Activity with a revision check.
 */
object AutoLyrics {
    private const val JOB_ID=66126
    private const val PREF="auto_lyrics_v1"
    fun translateEnabled(c:Context)=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getBoolean("translate",false)
    fun setTranslate(c:Context,value:Boolean)=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putBoolean("translate",value).commit()
    fun needsTranslation(c:Context,id:String,raw:String):Boolean{
        val key=AutoTranslationPolicy.key(id,raw)
        return AutoTranslationPolicy.pending(translateEnabled(c),raw,c.getSharedPreferences("translations",Context.MODE_PRIVATE).contains(key),c.getSharedPreferences(PREF,Context.MODE_PRIVATE).contains("tr_"+key))
    }
    fun markTranslation(c:Context,key:String)=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putBoolean("tr_"+key,true).commit()
    fun enabled(c:Context)=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getBoolean("enabled",false)
    fun setEnabled(c:Context,enabled:Boolean):Boolean{
        if(!c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putBoolean("enabled",enabled).commit())return false
        schedule(c)
        return true
    }
    fun schedule(c:Context){
        val scheduler=c.getSystemService(Context.JOB_SCHEDULER_SERVICE) as JobScheduler
        if(!enabled(c)){scheduler.cancel(JOB_ID);return}
        if(scheduler.getPendingJob(JOB_ID)!=null)return
        scheduler.schedule(JobInfo.Builder(JOB_ID,ComponentName(c,AutoLyricsJob::class.java))
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_UNMETERED)
            .setRequiresCharging(true).setRequiresBatteryNotLow(true).setRequiresStorageNotLow(true)
            .setPersisted(true).setPeriodic(15*60*1000L).build())
    }
    fun key(uri:String)=MessageDigest.getInstance("SHA-256").digest(uri.toByteArray(Charsets.UTF_8)).joinToString(""){"%02x".format(it)}
    fun revision(uri:String,title:String,artist:String,lyrics:String)=LyricDocument.revision(uri,null,title+"\u0000"+artist+"\u0000"+lyrics)
    fun directory(c:Context)=File(c.filesDir,"auto-lyric-results")
    fun file(c:Context,uri:String)=File(directory(c),key(uri)+".json")
    fun completed(c:Context,uri:String,revision:String,modelReady:Boolean):Boolean{
        val value=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getString("done_"+key(uri),null)
        return value==revision+":done"||value==revision+":waiting"&&!modelReady
    }
    fun mark(c:Context,uri:String,revision:String,outcome:String)=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit()
        .putString("done_"+key(uri),revision+":"+if(outcome=="waiting")"waiting"else "done").commit()
    fun read(file:File):JSONObject?=runCatching{require(file.length() in 1..(2*1024*1024));JSONObject(file.readText())}.getOrNull()
    fun write(c:Context,uri:String,result:JSONObject):Boolean{
        val d=directory(c);val target=file(c,uri)
        return runCatching{
            check(d.isDirectory||d.mkdirs())
            val bytes=result.toString().toByteArray(Charsets.UTF_8)
            require(bytes.size in 1..(2*1024*1024))
            val occupied=d.listFiles().orEmpty().sumOf{it.length()}-target.length()
            require(occupied+bytes.size<=64L*1024*1024)
            val tmp=File.createTempFile("auto-",".part",d)
            try{java.io.FileOutputStream(tmp).use{it.write(bytes);it.fd.sync()};check(tmp.renameTo(target))}finally{tmp.delete()}
            true
        }.getOrDefault(false)
    }
    fun staged(c:Context)=directory(c).listFiles().orEmpty().filter{it.name.matches(Regex("[a-f0-9]{64}\\.json"))}
}
class AutoLyricsJob:JobService(){
    private val worker=Executors.newSingleThreadExecutor()
    private var task:Future<*>?=null
    private var generation=0
    override fun onStartJob(params:JobParameters):Boolean{
        if(!AutoLyrics.enabled(this))return false
        val token=++generation
        task=worker.submit{
            try{android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);process()}
            catch(e:Exception){if(e is InterruptedException)Thread.currentThread().interrupt()}
            finally{Handler(Looper.getMainLooper()).post{if(token==generation){task=null;jobFinished(params,false)}}}
        }
        return true
    }
    override fun onStopJob(params:JobParameters):Boolean{generation++;task?.cancel(true);task=null;return AutoLyrics.enabled(this)}
    override fun onDestroy(){generation++;task?.cancel(true);worker.shutdownNow();super.onDestroy()}
    private fun checkRunning(){if(Thread.currentThread().isInterrupted||!AutoLyrics.enabled(this))throw InterruptedException()}
    private fun process(){
        val prefs=getSharedPreferences("library",MODE_PRIVATE)
        val entries=JSONArray(prefs.getString("tracks","[]")?:"[]")
        val modelReady=WhisperLocal.available&&WhisperLocal.installed(this)!=null
        val end=SystemClock.elapsedRealtime()+6*60*1000L
        for(i in 0 until entries.length()){
            checkRunning()
            if(SystemClock.elapsedRealtime()>end)return
            val row=entries.optJSONObject(i)?:continue
            val id=row.optString("uri");if(id.isBlank()||row.optString("group",id)!=id||Uri.parse(id).scheme!="content")continue
            val oldTitle=row.optString("title");val oldArtist=row.optString("artist");val old=row.optString("lyrics")
            val rev=AutoLyrics.revision(id,oldTitle,oldArtist,old)
            val lyricsDone=AutoLyrics.completed(this,id,rev,modelReady)
            if(lyricsDone&&!AutoLyrics.needsTranslation(this,id,old))continue
            val existing=AutoLyrics.file(this,id)
            if(AutoLyrics.read(existing)?.optString("revision")==rev)continue
            val uri=Uri.parse(id)
            var identity=TrackIdentityFix.Identity(oldTitle,oldArtist)
            var raw:String?=null;var draft:String?=null;var outcome=if(lyricsDone&&!modelReady)"waiting" else "done"
            if(!lyricsDone)try{
                val info=TrackLyricSource.metadata(this,uri,oldTitle,oldArtist,null)
                identity=TrackIdentityFix.fromTags(identity,info.tagTitle,info.tagArtist)
                raw=try{TrackLyricSource.automatic(this,uri,identity.title,identity.artist,old,true)}catch(e:Exception){
                    if(e is InterruptedException||Thread.currentThread().isInterrupted)throw InterruptedException()
                    outcome="error"
                    TrackLyricSource.automatic(this,uri,identity.title,identity.artist,old,false)
                }
                checkRunning()
                val reference=raw?:old
                val timed=Lrc.parse(reference)
                val upgrade=timed.isNotEmpty()&&KnownLyricAlignment.canUpgradeTiming(reference)
                val missing=reference.isBlank()
                val needs=missing||timed.isEmpty()||upgrade
                // Unknown performer may require content verification even when a text already exists.
                val wantArtist=!TrackIdentityFix.knownArtist(identity.artist)
                if((needs||wantArtist)&&modelReady){
                    val stem=runCatching{getSharedPreferences("stem_cache",MODE_PRIVATE).getString(id,null)?.let{StemEngine.load(this,it)}}.getOrNull()
                    val heard=try{WhisperLocal.transcribe(this,uri,stem,"auto"){checkRunning()}}catch(e:Exception){
                        if(e is InterruptedException||Thread.currentThread().isInterrupted||stem==null)throw e
                        WhisperLocal.transcribe(this,uri,null,"auto"){checkRunning()}
                    }
                    checkRunning()
                    if(reference.isNotBlank()&&needs){
                        val result=KnownLyricAlignment.align(heard,LyricDocument.plain(reference))
                        if(result!=null&&(timed.isEmpty()||KnownLyricAlignment.acceptsTimingUpgrade(reference,result)))raw=result.lrc
                    }
                    if(missing||wantArtist){
                        val recognized=LyricDocument.plain(heard)
                        val candidates=try{TrackLyricSource.search(this,uri,identity.title,identity.artist,info.seconds).first}catch(e:Exception){if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e;emptyList()}
                        val matches=candidates.mapNotNull{candidate->
                            val text=LyricDocument.plain(candidate.plain?:candidate.synced?:return@mapNotNull null).trim()
                            val score=TranscriptMatch.score(recognized,text)
                            if(score.matching<5||score.fraction<.55)return@mapNotNull null
                            val aligned=KnownLyricAlignment.align(heard,text)
                            candidate to LyricScanState.Match(text,score.matching,score.total,aligned?.lrc)
                        }
                        val chosen=LyricScanState.choose(matches.map{it.second})
                        if(chosen!=null){
                            if(missing){raw=chosen;outcome="done"}
                            identity=identity.copy(artist=TrackIdentityFix.verifiedArtist(identity.artist,matches.filter{it.second.aligned==chosen&&it.first.id>=0}.map{it.first.artist}))
                        }else if(missing)draft=heard.takeIf{it.toByteArray(Charsets.UTF_8).size<=262144}
                    }
                }else if((needs||wantArtist)&&!modelReady)outcome="waiting"
            }catch(e:Exception){
                if(e is InterruptedException||Thread.currentThread().isInterrupted)throw InterruptedException()
                outcome="error"
            }
            checkRunning()
            val finalRaw=raw?:old
            var translation:List<String>?=null
            var translationKey:String?=null
            if(AutoLyrics.needsTranslation(this,id,finalRaw)){
                val lines=LocalLyricLanguage.lines(finalRaw)
                try{
                    val lang=LocalLyricLanguage.detect(lines)
                    if(lang!=null&&lang!="ru"){
                        val result=LyricTranslation.translate(lines,lang,"ru",true)
                        if(AutoTranslationPolicy.valid(lines,result))translation=result
                    }
                    translationKey=AutoTranslationPolicy.key(id,finalRaw)
                }catch(e:Exception){
                    if(e is InterruptedException||Thread.currentThread().isInterrupted)throw InterruptedException()
                    // Retain the original and retry transient download/translation errors on a later job.
                }
            }
            checkRunning()
            if(!AutoLyrics.write(this,id,JSONObject().put("uri",id).put("revision",rev).put("title",identity.title).put("artist",identity.artist)
                .put("raw",raw?:JSONObject.NULL).put("draft",draft?:JSONObject.NULL).put("outcome",outcome).put("translationKey",translationKey?:JSONObject.NULL).put("translation",translation?.let{JSONArray(it)}?:JSONObject.NULL)))return
            Thread.sleep(1100)
        }
    }
}
