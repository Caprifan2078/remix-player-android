package app.remix.player
import kotlin.math.*

/** Estimate spectral balance from actual stereo PCM, with slow control and bounded gains.
 * This is not source separation or a change to the chosen tempo/pitch.
 */
class SourceEffectBalance(rate:Int,channels:Int){
    init{require(rate in 8000..384000&&channels>0)}
    private val low=FloatArray(channels)
    private val smooth=FloatArray(channels)
    private val lowA=(1-exp(-2*PI*170/rate)).toFloat()
    private val highA=(1-exp(-2*PI*3000.coerceAtMost(rate/3)/rate)).toFloat()
    private val avg=(1-exp(-1.0/(.45*rate))).toFloat()
    private val blend=(1-exp(-1.0/(.18*rate))).toFloat()
    private var energy=0f;private var lowEnergy=0f;private var highEnergy=0f
    private var fastEnergy=0f
    private val fastBlend=(1-exp(-1.0/(.012*rate))).toFloat()
    private val protectAttack=(1-exp(-1.0/(.006*rate))).toFloat()
    private val protectRelease=(1-exp(-1.0/(.15*rate))).toFloat()
    private var transientTarget=1f
    var transient=1f;private set
    private var targetBass=1f;private var targetDrive=1f;private var targetRoom=1f
    private var tick=0
    private val interval=(rate/100).coerceAtLeast(1)
    var bass=1f;private set
    var drive=1f;private set
    var room=1f;private set
    fun reset(){
        low.fill(0f);smooth.fill(0f);energy=0f;lowEnergy=0f;highEnergy=0f;tick=0
        targetBass=1f;targetDrive=1f;targetRoom=1f;bass=1f;drive=1f;room=1f;fastEnergy=0f;transientTarget=1f;transient=1f
    }
    fun frame(input:FloatArray){
        var e=0f;var l=0f;var h=0f
        for(c in low.indices){
            val x=input.getOrNull(c)?.takeIf{it.isFinite()}?.coerceIn(-1f,1f)?:0f
            low[c]+=lowA*(x-low[c]);smooth[c]+=highA*(x-smooth[c])
            e+=x*x;l+=low[c]*low[c];val high=x-smooth[c];h+=high*high
        }
        fastEnergy+=(e/low.size-fastEnergy)*fastBlend
        energy+=(e/low.size-energy)*avg;lowEnergy+=(l/low.size-lowEnergy)*avg;highEnergy+=(h/low.size-highEnergy)*avg
        if(tick==0){
            if(energy>0.0004f){
                val bottom=(lowEnergy/energy).coerceIn(0f,1f)
                val top=(highEnergy/energy).coerceIn(0f,1f)
                targetBass=(1.10f-.48f*bottom).coerceIn(.62f,1.10f)
                targetDrive=(1.02f-.48f*top).coerceIn(.54f,1.02f)
                targetRoom=(1.04f-.28f*bottom-.17f*top).coerceIn(.68f,1.04f)
            }else{targetBass=1f;targetDrive=1f;targetRoom=1f}
            // Preserve percussive attacks and syllable onsets; never compress the dry path.
            val crest=if(energy>.0004f&&fastEnergy>.002f)(fastEnergy/energy).coerceIn(1f,6f) else 1f
            transientTarget=(1f-.10f*(crest-1f)).coerceIn(.50f,1f)
            tick=interval
        }
        tick--
        transient+=(transientTarget-transient)*(if(transientTarget<transient)protectAttack else protectRelease)
        bass+=(targetBass-bass)*blend;drive+=(targetDrive-drive)*blend;room+=(targetRoom-room)*blend
    }
}
