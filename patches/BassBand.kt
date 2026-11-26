package app.remix.player
import kotlin.math.*

/** Band-limited bass boost: do not amplify DC or subsonic rumble. Dry signal is untouched. */
class BassBand(private val rate:Int,channels:Int){
    init{require(rate in 8000..384000&&channels>0)}
    private val dc1=FloatArray(channels);private val dc2=FloatArray(channels)
    private val low1=FloatArray(channels);private val low2=FloatArray(channels)
    private val highPass=(1-exp(-2*PI*18/rate)).toFloat()
    private var lowPass=0f
    fun reset(cutoff:Double){
        require(cutoff.isFinite()&&cutoff in 40.0..250.0)
        lowPass=(1-exp(-2*PI*cutoff/rate)).toFloat()
        dc1.fill(0f);dc2.fill(0f);low1.fill(0f);low2.fill(0f)
    }
    fun sample(c:Int,x:Float):Float{
        val clean=if(x.isFinite())x else 0f
        dc1[c]+=highPass*(clean-dc1[c]);val a=clean-dc1[c]
        dc2[c]+=highPass*(a-dc2[c]);val b=a-dc2[c]
        low1[c]+=lowPass*(b-low1[c]);low2[c]+=lowPass*(low1[c]-low2[c])
        return low2[c]
    }
}
