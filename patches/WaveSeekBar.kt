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
/** One cancellable background request, session-only cache, guarded main-thread delivery. */
class WaveformLoader(context:Context){
    private val app=context.applicationContext
    private val worker=Executors.newSingleThreadExecutor()
    private val handler=Handler(Looper.getMainLooper())
    private val cache=LruCache<String,FloatArray>(24)
    private var key:String?=null
    private var future:Future<*>?=null
    private var generation=0L
    private var closed=false
    fun show(uri:String,deliver:(FloatArray?)->Unit){
        if(closed||key==uri)return
        clear();key=uri;val token=generation
        val cached=cache.get(uri)
        if(cached!=null){deliver(cached);return}
        deliver(null)
        future=worker.submit{
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND)
            val data=WaveformDecode.scan(app,Uri.parse(uri)){part->
                handler.post{if(!closed&&generation==token&&key==uri)deliver(part)}
            }
            handler.post{if(!closed&&generation==token&&key==uri){if(data!=null)cache.put(uri,data);deliver(data)}}
        }
    }
    fun clear(){generation++;key=null;future?.cancel(true);future=null}
    fun close(){closed=true;clear();worker.shutdownNow();cache.evictAll()}
}
