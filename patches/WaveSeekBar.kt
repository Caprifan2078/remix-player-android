package app.remix.player
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.drawable.ColorDrawable
import androidx.appcompat.widget.AppCompatSeekBar
/** Native SeekBar keeps accessibility and keyboard controls; only the track is drawn differently. */
internal class WaveSeekBar(context:Context):AppCompatSeekBar(context){
    private var peaks:FloatArray?=null
    private val normal=progressDrawable
    private val transparent=ColorDrawable(Color.TRANSPARENT)
    private val paint=Paint(Paint.ANTI_ALIAS_FLAG)
    private val geometry=Path()
    private var geometryDirty=true
    private var lastWidth=-1;private var lastHeight=-1;private var lastLeft=-1;private var lastRight=-1;private var lastTop=-1;private var lastBottom=-1
    fun setWaveform(value:FloatArray?){
        if(peaks===value)return
        val changed=(peaks==null)!=(value==null);peaks=value
        if(changed)progressDrawable=if(value==null)normal else transparent
        geometryDirty=true;invalidate()
    }
    private fun rebuild(values:FloatArray,w:Float,h:Float){
        geometry.reset()
        val count=minOf(values.size,(w/(3*resources.displayMetrics.density)).toInt().coerceAtLeast(1))
        val step=w/count;val y=paddingTop+h/2
        for(i in 0 until count){
            val a=i*values.size/count;val b=(i+1)*values.size/count;var peak=0f
            for(j in a until b)peak=maxOf(peak,values[j])
            val height=(h*.38f*peak.coerceIn(0f,1f)).coerceAtLeast(1f)
            val x=paddingLeft+(i+.5f)*step
            geometry.addRoundRect(x-step*.31f,y-height,x+step*.31f,y+height,step*.25f,step*.25f,Path.Direction.CW)
        }
        lastWidth=width;lastHeight=height;lastLeft=paddingLeft;lastRight=paddingRight;lastTop=paddingTop;lastBottom=paddingBottom;geometryDirty=false
    }
    override fun onDraw(canvas:Canvas){
        val values=peaks
        if(values!=null&&values.isNotEmpty()){
            val w=(width-paddingLeft-paddingRight).toFloat();val h=(height-paddingTop-paddingBottom).toFloat()
            if(w>0&&h>0){
                if(geometryDirty||lastWidth!=width||lastHeight!=height||lastLeft!=paddingLeft||lastRight!=paddingRight||lastTop!=paddingTop||lastBottom!=paddingBottom)rebuild(values,w,h)
                paint.color=0xff5f586e.toInt();canvas.drawPath(geometry,paint)
                val save=canvas.save()
                val played=progress.toFloat()/max.coerceAtLeast(1)
                canvas.clipRect(paddingLeft.toFloat(),paddingTop.toFloat(),paddingLeft+w*played,height-paddingBottom.toFloat())
                paint.color=0xffc0b0ff.toInt();canvas.drawPath(geometry,paint)
                canvas.restoreToCount(save)
            }
        }
        super.onDraw(canvas)
    }
}
