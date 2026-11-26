package app.remix.player
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.drawable.ColorDrawable
import android.widget.SeekBar
/** Native SeekBar keeps accessibility and keyboard controls; only the track is drawn differently. */
internal class WaveSeekBar(context:Context):SeekBar(context){
    private var peaks:FloatArray?=null
    private val normal=progressDrawable
    private val transparent=ColorDrawable(Color.TRANSPARENT)
    private val paint=Paint(Paint.ANTI_ALIAS_FLAG)
    fun setWaveform(value:FloatArray?){
        if(peaks===value)return
        val changed=(peaks==null)!=(value==null);peaks=value
        if(changed)progressDrawable=if(value==null)normal else transparent
        invalidate()
    }
    override fun onDraw(canvas:Canvas){
        val values=peaks
        if(values!=null&&values.isNotEmpty()){
            val w=(width-paddingLeft-paddingRight).toFloat();val h=(height-paddingTop-paddingBottom).toFloat()
            if(w>0&&h>0){
                val count=minOf(values.size,(w/(3*resources.displayMetrics.density)).toInt().coerceAtLeast(1))
                val step=w/count;val y=paddingTop+h/2;val played=progress.toFloat()/max.coerceAtLeast(1)
                for(i in 0 until count){
                    val a=i*values.size/count;val b=(i+1)*values.size/count;var peak=0f
                    for(j in a until b)peak=maxOf(peak,values[j])
                    val height=(h*.38f*peak.coerceIn(0f,1f)).coerceAtLeast(1f)
                    val x=paddingLeft+(i+.5f)*step
                    paint.color=if((i+.5f)/count<=played)0xffc0b0ff.toInt()else 0xff5f586e.toInt()
                    canvas.drawRoundRect(x-step*.31f,y-height,x+step*.31f,y+height,step*.25f,step*.25f,paint)
                }
            }
        }
        super.onDraw(canvas)
    }
}
