package app.remix.player
import kotlin.math.abs
import kotlin.math.sqrt
/** Fixed-size, time-indexed peak envelope. Empty bins are not treated as silence. */
class WaveEnvelope(private val durationUs:Long,private val bins:Int=96){
    init{require(durationUs in 1..900000000L&&bins in 24..256)}
    private val peaks=FloatArray(bins)
    private val counts=LongArray(bins)
    fun frame(timeUs:Long,peak:Float){
        if(timeUs !in 0 until durationUs||!peak.isFinite())return
        val i=(timeUs*bins/durationUs).toInt().coerceIn(0,bins-1)
        peaks[i]=maxOf(peaks[i],abs(peak).coerceAtMost(1f));counts[i]++
    }
    /** Measured bins only. NaN means not decoded, not a silent passage. */
    fun preview(sampleRate:Int):FloatArray?{
        require(sampleRate in 8000..384000)
        val expected=durationUs.toDouble()*sampleRate/1000000/bins
        val ready=BooleanArray(bins){counts[it]>=expected*.55}
        if(ready.none{it})return null
        val max=peaks.indices.filter{ready[it]}.maxOf{peaks[it]}
        return FloatArray(bins){if(!ready[it])Float.NaN else if(max<=0f)0f else sqrt((peaks[it]/max).coerceIn(0f,1f))}
    }
    fun finish(sampleRate:Int):FloatArray?{
        require(sampleRate in 8000..384000)
        val expected=durationUs.toDouble()*sampleRate/1000000/bins
        if(counts.any{it<expected*.55})return null
        val max=peaks.maxOrNull()?:return null
        if(max<=0f)return FloatArray(bins)
        return FloatArray(bins){sqrt((peaks[it]/max).coerceIn(0f,1f))}
    }
}
