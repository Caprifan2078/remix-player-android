package app.remix.player

import kotlin.math.exp
import kotlin.math.sqrt

/** Streaming, channel-linked effect depth. It changes wet/dry balance, not tempo or pitch. */
class AdaptiveEffectEnvelope(rate:Int) {
    init { require(rate in 8000..384000) }
    private val attack=(1.0-exp(-1.0/(.045*rate))).toFloat()
    private val release=(1.0-exp(-1.0/(.30*rate))).toFloat()
    private val blend=(1.0-exp(-1.0/(.080*rate))).toFloat()
    private val referenceBlend=(1.0-exp(-1.0/(4.0*rate))).toFloat()
    private var reference=0f
    private var power=0f
    private var strength=1f
    fun reset(){power=0f;reference=0f;strength=1f}
    fun frame(input:FloatArray):Float {
        if(input.isEmpty())return strength
        var sum=0f
        for(x in input){if(x.isFinite()){val a=x.coerceIn(-1f,1f);sum+=a*a}}
        val sample=sum/input.size
        power+=(sample-power)*(if(sample>power)attack else release)
        reference+=(power-reference)*referenceBlend
        val rms=sqrt(power.coerceAtLeast(0f))
        val absolute=((rms-.12f)/.35f).coerceIn(0f,1f)
        // Compare to recent track dynamics; ignore relative changes close to silence.
        val relative=if(rms>.09f&&reference>.0004f)((sqrt(power/reference)-1.15f)/.9f).coerceIn(0f,1f) else 0f
        val dense=maxOf(absolute,relative)
        val target=1f-.45f*dense
        strength=(strength+(target-strength)*blend).coerceIn(.55f,1f)
        return strength
    }
}
