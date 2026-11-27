package app.remix.player
import java.nio.ByteBuffer
import kotlin.math.*
/** Exact sample peaks per timeline bin. No FFT, models, or per-frame allocation. */
internal class WaveBins(private val durationUs:Long,private val rate:Int,private val bins:Int=160){
    init{require(durationUs in 1..900_000_000L&&rate in 8000..384000&&bins in 16..512)}
    private val total=(durationUs*rate+999999)/1000000
    private val peaks=FloatArray(bins)
    private var covered=0L
    private var end=0L
    private var previousStart=-1L
    private var ordered=true
    fun add(buffer:ByteBuffer,channels:Int,floatPcm:Boolean,ptsUs:Long){
        require(channels in 1..8&&ptsUs in -900_000_000L..1_000_000_000L)
        val bytes=if(floatPcm)4 else 2
        val frameBytes=channels*bytes
        var frame=(ptsUs.toDouble()*rate/1000000).roundToLong()
        var remaining=buffer.remaining()/frameBytes
        if(frame<0){val skip=minOf(-frame,remaining.toLong()).toInt();buffer.position(buffer.position()+skip*frameBytes);frame+=skip;remaining-=skip}
        if(remaining<=0||frame>=total)return
        if(frame<previousStart)ordered=false
        previousStart=frame
        while(remaining>0&&frame<total){
            val index=(frame*bins/total).toInt().coerceIn(0,bins-1)
            val boundary=((index+1L)*total+bins-1)/bins
            val n=minOf(remaining.toLong(),boundary-frame,total-frame).toInt()
            if(n<=0)break
            var peak=peaks[index]
            if(floatPcm){
                repeat(n*channels){val v=abs(buffer.float);if(v.isFinite()&&v>peak)peak=v.coerceAtMost(1f)}
            }else{
                var pcmPeak=0
                repeat(n*channels){val v=abs(buffer.short.toInt());if(v>pcmPeak)pcmPeak=v}
                peak=maxOf(peak,pcmPeak/32768f)
            }
            peaks[index]=peak;val next=frame+n;covered+=(next-maxOf(end,frame)).coerceAtLeast(0);end=maxOf(end,next);frame=next;remaining-=n
        }
    }
    /** Only advertise complete prefix bins, never present unknown data as silence. */
    fun preview():Pair<FloatArray,Int>?{
        if(!ordered||covered!=end)return null
        val ready=(end*bins/total).toInt().coerceIn(0,bins)
        return if(ready>0)peaks.copyOf() to ready else null
    }
    fun finish():FloatArray?=if(ordered&&covered>=total-total/20)peaks.copyOf()else null
}
