package app.remix.player
import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.util.LruCache
import androidx.appcompat.widget.AppCompatSeekBar
import java.util.concurrent.Executors
import java.util.concurrent.Future

/** Native SeekBar retains accessibility, touch target and the original seek listener. */
class WaveSeekBar(context:Context):AppCompatSeekBar(context){
    private val paint=Paint(Paint.ANTI_ALIAS_FLAG)
    private var samples:FloatArray?=null
    fun setEnvelope(v:FloatArray?){samples=v;tag=if(v==null)null else if(v.all{it.isFinite()})"waveform-ready" else "waveform-loading";invalidate()}
    override fun onDraw(canvas:Canvas){
        val bars=samples
        if(bars==null||bars.isEmpty()||layoutDirection==LAYOUT_DIRECTION_RTL){super.onDraw(canvas);return}
        val left=paddingLeft.toFloat();val right=(width-paddingRight).toFloat();val span=right-left
        if(span<=0||height<=0){super.onDraw(canvas);return}
        val center=height/2f;val step=span/bars.size;val half=minOf(step*.32f,2f*resources.displayMetrics.density)
        val ratio=progress.toFloat()/max.coerceAtLeast(1)
        val radius=half
        for(i in bars.indices){
            val x=left+(i+.5f)*step;val measured=bars[i].isFinite()
            val h=if(measured)(height*.38f*bars[i]).coerceAtLeast(resources.displayMetrics.density)else resources.displayMetrics.density*.65f
            paint.color=if(!measured)0xff30343a.toInt() else if((i+.5f)/bars.size<=ratio)0xffc7e8a2.toInt() else 0xff51565d.toInt()
            canvas.drawRoundRect(x-half,center-h,x+half,center+h,radius,radius,paint)
        }
        paint.color=0xffc7e8a2.toInt();paint.strokeWidth=2f*resources.displayMetrics.density
        val x=left+span*ratio;canvas.drawLine(x,height*.08f,x,height*.92f,paint)
    }
}
/** One cancellable background request, bounded session and versioned disk cache, guarded main-thread delivery. */
class WaveformLoader(context:Context){
    private val app=context.applicationContext
    private val worker=Executors.newSingleThreadExecutor()
    private val handler=Handler(Looper.getMainLooper())
    private val cache=LruCache<String,FloatArray>(24)
    private var key:String?=null
    private var future:Future<*>?=null
    private var generation=0L
    private var closed=false
    // Persist only when a provider exposes a file size and modification time.
    private val disk by lazy{java.io.File(app.cacheDir,"waveforms-v1")}
    private fun fingerprint(uri:Uri):String?{
        for(column in listOf("last_modified","date_modified")){
            val version=runCatching{
                app.contentResolver.query(uri,arrayOf("_size",column),null,null,null)?.use{c->
                    val size=c.getColumnIndex("_size");val modified=c.getColumnIndex(column)
                    if(size<0||modified<0||!c.moveToFirst()||c.isNull(size)||c.isNull(modified))null
                    else c.getLong(size).takeIf{it>0}?.let{bytes->c.getLong(modified).takeIf{it>0}?.let{"$bytes:$column:$it"}}
                }
            }.getOrNull()
            if(version!=null){
                val raw=uri.toString()+"|"+version
                return java.security.MessageDigest.getInstance("SHA-256").digest(raw.toByteArray(Charsets.UTF_8)).joinToString(""){(it.toInt() and 255).toString(16).padStart(2,'0')}
            }
        }
        return null
    }
    private fun readDisk(id:String):FloatArray?=runCatching{
        val f=java.io.File(disk,id+".bin")
        require(f.length()==96L*4)
        val data=java.io.DataInputStream(f.inputStream().buffered()).use{input->FloatArray(96){input.readFloat()}}
        require(data.all{it.isFinite()&&it in 0f..1f});f.setLastModified(System.currentTimeMillis());data
    }.getOrNull()
    private fun writeDisk(id:String,data:FloatArray){
        if(data.size!=96||data.any{!it.isFinite()||it !in 0f..1f}||Thread.currentThread().isInterrupted)return
        runCatching{
            check(disk.isDirectory||disk.mkdirs())
            val tmp=java.io.File.createTempFile("wave-",".tmp",disk)
            try{
                java.io.DataOutputStream(tmp.outputStream().buffered()).use{out->data.forEach{out.writeFloat(it)}}
                check(!Thread.currentThread().isInterrupted)
                check(tmp.renameTo(java.io.File(disk,id+".bin")))
            }finally{tmp.delete()}
            disk.listFiles().orEmpty().filter{it.extension=="bin"}.sortedByDescending{it.lastModified()}.drop(128).forEach{it.delete()}
        }
    }
    fun show(uri:String,deliver:(FloatArray?)->Unit){
        if(closed||key==uri)return
        clear();key=uri;val token=generation
        deliver(null)
        future=worker.submit{
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND)
            val source=Uri.parse(uri);val id=fingerprint(source);val cacheKey=id?:uri
            if(Thread.currentThread().isInterrupted)return@submit
            val cached=cache.get(cacheKey)?:id?.let{readDisk(it)}
            val data=cached?:WaveformDecode.scan(app,source){part->
                handler.post{if(!closed&&generation==token&&key==uri)deliver(part)}
            }
            if(Thread.currentThread().isInterrupted)return@submit
            if(data!=null&&cached==null&&id!=null)writeDisk(id,data)
            handler.post{if(!closed&&generation==token&&key==uri){if(data!=null)cache.put(cacheKey,data);deliver(data)}}
        }
    }
    fun clear(){generation++;key=null;future?.cancel(true);future=null}
    fun close(){closed=true;clear();worker.shutdownNow();cache.evictAll()}
}
