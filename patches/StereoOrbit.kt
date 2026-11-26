package app.remix.player

import kotlin.math.*

/** Headphone-oriented stereo orbit: fractional interaural delay and shadow, centered low bass. */
class StereoOrbit(private val rate:Int){
    init{require(rate in 8000..384000)}
    private val ring=FloatArray((rate*.0007).toInt()+4)
    private var cursor=0
    private var low=0f
    private var shadowL=0f
    private var shadowR=0f
    private val bassAlpha=(1-exp(-2*PI*160/rate)).toFloat()
    private val shadowAlpha=(1-exp(-2*PI*1800/rate)).toFloat()
    fun reset(){ring.fill(0f);cursor=0;low=0f;shadowL=0f;shadowR=0f}
    private fun delayed(frames:Float):Float{
        val offset=frames.toInt();val frac=frames-offset
        val a=ring[(cursor-offset+ring.size)%ring.size]
        val b=ring[(cursor-offset-1+ring.size)%ring.size]
        return a+(b-a)*frac
    }
    fun apply(frame:FloatArray,position:Float){
        require(frame.size==2)
        val p=if(position.isFinite())position.coerceIn(-1f,1f)else 0f
        val l=frame[0].takeIf{it.isFinite()}?:0f;val r=frame[1].takeIf{it.isFinite()}?:0f
        val mid=(l+r)*.5f;val side=(l-r)*.5f
        low+=bassAlpha*(mid-low)
        ring[cursor]=mid-low
        val dl=delayed(max(0f,p)*rate*.00065f);val dr=delayed(max(0f,-p)*rate*.00065f)
        shadowL+=shadowAlpha*(dl-shadowL);shadowR+=shadowAlpha*(dr-shadowR)
        val farL=max(0f,p);val farR=max(0f,-p)
        val highL=dl+(shadowL-dl)*farL*.72f
        val highR=dr+(shadowR-dr)*farR*.72f
        frame[0]=low+highL*sqrt(1f-.86f*p)+side*.72f
        frame[1]=low+highR*sqrt(1f+.86f*p)-side*.72f
        cursor=(cursor+1)%ring.size
    }
}
