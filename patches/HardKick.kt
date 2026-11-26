package app.remix.player
import kotlin.math.*

/** Original synthesized kick, distinct punch/body/tail profiles. No third-party samples. */
object HardKick {
    data class Profile(val hz:Double,val sweep:Double,val decay:Double,val drive:Double,val body:Double)
    fun profile(name:String):Profile?=when(name){
        "Hardstyle"->Profile(49.0,190.0,.19,4.8,.70)
        "Euphoric Hardstyle"->Profile(55.0,145.0,.18,3.2,.72)
        "Rawstyle"->Profile(47.0,250.0,.16,7.2,.54)
        "Xtra Raw"->Profile(46.0,330.0,.14,9.0,.48)
        "Hardcore"->Profile(57.0,220.0,.105,6.4,.58)
        "Uptempo Hardcore"->Profile(62.0,295.0,.078,7.0,.52)
        "Frenchcore"->Profile(55.0,180.0,.10,5.3,.65)
        "Hardtekk"->Profile(51.0,270.0,.13,7.5,.55)
        else->null
    }
    /** Keep the tail audible over a source mix and reserve low-frequency headroom until it decays. */
    fun mixDrumGain(name:String):Float=if(profile(name)!=null).54f else .38f
    fun sidechainDecay(name:String):Double=profile(name)?.let{(it.decay*.70).coerceIn(.065,.135)}?:.065
    fun sample(p:Profile,age:Double,length:Double):Double{
        if(!age.isFinite()||!length.isFinite()||age<0||age>=length||length<=0)return 0.0
        val phase=2*PI*(p.hz*age+p.sweep*.018*(1-exp(-age/.018)))
        val sub=sin(phase)
        val punch=sin(phase*1.7)*exp(-age/.019)
        val tail=tanh((sub+.21*sin(phase*3))*p.drive)
        val envelope=exp(-age/p.decay)*minOf(1.0,age/.0015,(length-age)/.012).coerceAtLeast(0.0)
        return ((1-p.body)*punch+p.body*tail)*envelope*.65
    }
    fun curve(name:String,rate:Int,tunedHz:Double?=null):DoubleArray?{
        require(rate in 8000..384000)
        val original=profile(name)?:return null
        val p=tunedHz?.takeIf{it.isFinite()&&it in 40.0..75.0}?.let{original.copy(hz=it)}?:original
        val length=if(name=="Uptempo Hardcore") .22 else if(name=="Hardcore"||name=="Frenchcore") .29 else .36
        return DoubleArray(ceil(length*rate).toInt()){sample(p,it.toDouble()/rate,length)}
    }
}

/** Duck only the original low end around the new kick, not the full mix or vocals. */
class HardMixSpace(rate:Int){
    init{require(rate in 8000..384000)}
    private val alpha=(1-exp(-2*PI*180/rate)).toFloat()
    private val attack=(1-exp(-1.0/(.004*rate))).toFloat()
    private val release=(1-exp(-1.0/(.09*rate))).toFloat()
    private var lowL=0f;private var lowR=0f;private var duck=0f
    var left=0f;private set
    var right=0f;private set
    fun frame(l:Float,r:Float,kick:Float,enabled:Boolean){
        val a=if(l.isFinite())l else 0f;val b=if(r.isFinite())r else 0f
        lowL+=alpha*(a-lowL);lowR+=alpha*(b-lowR)
        val target=if(enabled&&kick.isFinite())kick.coerceIn(0f,1f)*.65f else 0f
        duck+=(target-duck)*(if(target>duck)attack else release)
        left=a-lowL*duck;right=b-lowR*duck
    }
}
