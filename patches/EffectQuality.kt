package app.remix.player

import kotlin.math.*

/** Distinct damped, diffused rooms; delay and decay are in seconds, independent of sample rate. */
private class EffectRoom(rate:Int,channels:Int,p:Preset){
    private data class Profile(val scale:Double,val decay:Double,val damping:Double,val lowCut:Double)
    private val profile=when(p.name){
        "Cathedral"->Profile(1.72,2.8,3200.0,170.0)
        "Concert Hall"->Profile(1.28,1.65,4800.0,150.0)
        "Deep Space"->Profile(1.95,2.35,4200.0,190.0)
        "Small Room"->Profile(.46,.34,6800.0,200.0)
        "Next Room"->Profile(.70,.60,1500.0,150.0)
        "Dreamy","Slow Dream"->Profile(1.45,1.85,3100.0,180.0)
        "Daycore Echo"->Profile(2.05,1.55,3900.0,200.0)
        "8D Audio","Slow Stereo Orbit","Fast Stereo Orbit"->Profile(.86,.90,5500.0,180.0)
        "Slowed + Reverb","Super Slowed + Reverb","Ultra Slowed","Extreme Slowed"->Profile(1.34,1.45,3600.0,180.0)
        "Sped Up","Nightcore","Sped Up + Reverb","Nightcore Reverb"->Profile(.92,1.0,5800.0,200.0)
        else->Profile(1.0,.55+1.2*p.room,4400.0,180.0)
    }
    private class Comb(size:Int,val feedback:Float,val damping:Float){
        private val data=FloatArray(size);private var i=0;private var damp=0f
        fun sample(x:Float):Float{val old=data[i];damp+=damping*(old-damp);data[i]=(x+damp*feedback).coerceIn(-2f,2f);if(++i==data.size)i=0;return old}
    }
    private class Diffuser(size:Int){
        private val data=FloatArray(size);private var i=0
        fun sample(x:Float):Float{val d=data[i];val y=d-.55f*x;data[i]=x+.55f*y;if(++i==data.size)i=0;return y}
    }
    private val lowAlpha=(1-exp(-2*PI*profile.lowCut/rate)).toFloat()
    private val low=FloatArray(channels)
    private val combs=Array(channels){ch->Array(4){i->
        val seconds=(doubleArrayOf(.0297,.0371,.0411,.0533)[i]+(ch%2)*.0019)*profile.scale
        val length=(seconds*rate).roundToInt().coerceAtLeast(1)
        Comb(length,10.0.pow(-3*seconds/profile.decay).toFloat().coerceIn(0f,.94f),(1-exp(-2*PI*profile.damping.coerceAtMost(rate*.45)/rate)).toFloat())
    }}
    private val diffusion=Array(channels){ch->Array(2){i->Diffuser(((if(i==0).0051 else .0017)*rate*profile.scale+(ch%2)*3).roundToInt().coerceAtLeast(1))}}
    fun sample(c:Int,x:Float):Float{
        low[c]+=lowAlpha*(x-low[c]);val high=x-low[c];var wet=0f
        for(line in combs[c])wet+=line.sample(high)
        wet*=.25f
        for(line in diffusion[c])wet=line.sample(wet)
        return wet
    }
}

/** First-order antiderivative antialiasing for the heavy tanh waveshaper.
 * Integrates over the interval between samples; stable for nearly equal samples. */
private class SmoothDrive(channels:Int){
    private val last=DoubleArray(channels)
    private val integral=DoubleArray(channels)
    private val initialized=BooleanArray(channels)
    fun reset(){initialized.fill(false)}
    fun sample(c:Int,x:Float,k:Float,norm:Float):Float{
        val z=x.toDouble()*k
        val a=abs(z);val f=a+ln1p(exp(-2*a))
        val previous=last[c];val delta=z-previous
        val y=if(!initialized[c])tanh(z)else if(abs(delta)<1e-5)tanh((z+previous)*.5)else (f-integral[c])/delta
        last[c]=z;integral[c]=f;initialized[c]=true
        return (y/norm).toFloat()
    }
}

/** Shared realtime/export DSP. Artistic filters retain their character; bass, room and drive adapt separately. */
class Dsp(private val rate:Int,private val channels:Int){
    init{require(rate in 8000..384000&&channels>0)}
    private val bass1=FloatArray(channels);private val bass2=FloatArray(channels)
    private val high1=FloatArray(channels);private val high2=FloatArray(channels)
    private val low1=FloatArray(channels);private val low2=FloatArray(channels)
    private val guard=LinkedPeakGuard(rate);private val adaptiveDepth=AdaptiveEffectEnvelope(rate);private val orbit=StereoOrbit(rate)
    private var previous:Preset?=null;private var room:EffectRoom?=null
    private val smoothDrive=SmoothDrive(channels);private var antiAlias=false
    private var bassAlpha=0f;private var highAlpha=0f;private var lowAlpha=0f;private var colorMix=0f
    private var driveK=1f;private var driveNorm=1f;private var driveMix=1f;private var phase=0.0;private var phaseStep=0.0;private var processed=false;private var bandpass=false
    private fun alpha(hz:Double)=(1-exp(-2*PI*hz.coerceIn(1.0,rate*.45)/rate)).toFloat()
    private fun configure(p:Preset){
        previous=p
        bass1.fill(0f);bass2.fill(0f);high1.fill(0f);high2.fill(0f);low1.fill(0f);low2.fill(0f)
        guard.reset();adaptiveDepth.reset();orbit.reset();phase=0.0
        bassAlpha=alpha(when(p.name){"Sub Bass"->78.0;"Deep Bass"->115.0;"Soft Bass"->145.0;else->165.0})
        val color=when(p.name){
            "Underwater"->Triple(750.0,0.0,.98f)
            "Next Room"->Triple(1100.0,0.0,.97f)
            "Radio Filter"->Triple(3100.0,380.0,1f)
            "Cassette Filter"->Triple(4200.0,95.0,.96f)
            "Lo-Fi Filter"->Triple(5200.0,110.0,.90f)
            "Vintage"->Triple(6500.0,70.0,.74f)
            "Vaporwave effect"->Triple(4700.0,0.0,.64f)
            else->Triple(900.0+(1-p.muffled)*12000,0.0,p.muffled.coerceIn(0f,1f))
        }
        lowAlpha=alpha(color.first);highAlpha=alpha(color.second);bandpass=color.second>0; colorMix=color.third
        driveK=1+p.drive*6
        antiAlias=p.name in setOf("Overdrive","Distorted","Extreme Distortion");smoothDrive.reset()
        driveMix=when(p.name){
            "Sped Up","Nightcore"->.30f
            "Lo-Fi Filter"->.40f
            "Gym Edit","Vintage"->.55f
            "Radio Filter"->.60f
            "Dark Edit","Cassette Filter","Overdrive"->.65f
            "Distorted"->.85f
            "Extreme Distortion"->.95f
            else->1f
        }
        // Compensate named presets' small-signal gain without flattening intentional harmonics.
        driveNorm=tanh(driveK)*(if(driveMix<1f)1f+2.3f*p.drive else 1f)
        room=if(p.room>0f)EffectRoom(rate,channels,p)else null
        phaseStep=2*PI*(when(p.name){"Slow Stereo Orbit"->.10;"Fast Stereo Orbit"->.32;else->.19})/rate
        processed=p.bass!=0f||p.room!=0f||p.pan!=0f||p.drive!=0f||colorMix>0f
    }
    fun frame(input:FloatArray,out:FloatArray,p:Preset){
        if(previous!==p)configure(p)
        if(!processed){for(c in 0 until channels)out[c]=(if(input[c].isFinite())input[c] else 0f).coerceIn(-1f,1f);return}
        val depth=adaptiveDepth.frame(input)
        for(c in 0 until channels){
            val x=if(input[c].isFinite())input[c].coerceIn(-1f,1f)else 0f
            var y=x
            if(p.bass>0){bass1[c]+=bassAlpha*(x-bass1[c]);bass2[c]+=bassAlpha*(bass1[c]-bass2[c]);y+=p.bass*depth*bass2[c]}
            if(colorMix>0){
                var v=y
                if(bandpass){high1[c]+=highAlpha*(v-high1[c]);v-=high1[c];high2[c]+=highAlpha*(v-high2[c]);v-=high2[c]}
                low1[c]+=lowAlpha*(v-low1[c]);low2[c]+=lowAlpha*(low1[c]-low2[c]);y+=(low2[c]-y)*colorMix
            }
            if(p.drive>0){val wet=if(antiAlias)smoothDrive.sample(c,y,driveK,driveNorm)else tanh(y*driveK)/driveNorm;y+=(wet-y)*depth*driveMix}
            room?.let{val amount=p.room*depth;val wet=it.sample(c,y);y=y*(1-.12f*amount)+wet*amount*.72f}
            out[c]=y
        }
        if(channels==2&&p.pan>0){orbit.apply(out,(sin(phase)*p.pan).toFloat());phase+=phaseStep;if(phase>2*PI)phase-=2*PI}
        guard.apply(out)
    }
}
