package app.remix.player
import kotlin.math.*
fun main(){
    val rates=listOf(8000,22050,44100,48000,96000,192000)
    var frames=0L
    for(rate in rates){
        val orbit=SpatialOrbit(rate);val out=FloatArray(2)
        fun measure(freq:Double,p:Float):Pair<Double,Double>{
            orbit.reset();var a=0.0;var b=0.0
            repeat(rate/2){i->val x=(.3*sin(2*PI*freq*i/rate)).toFloat();out[0]=x;out[1]=x;orbit.frame(out,p);check(out.all{it.isFinite()&&abs(it)<=.301f});if(i>rate/10){a+=out[0]*out[0];b+=out[1]*out[1]};frames++}
            return sqrt(a) to sqrt(b)
        }
        val center=measure(440.0,0f);check(abs(center.first/center.second-1)<1e-6)
        val right=measure(440.0,1f);val left=measure(440.0,-1f)
        check(right.second/right.first>1.7);check(left.first/left.second>1.7)
        check(abs(right.first-left.second)<1e-6)
        val high=measure(3000.0,1f);check(high.first/high.second<right.first/right.second)
        orbit.reset();out[0]=.3f;out[1]=.3f;orbit.frame(out,1f);check(out[1]==.3f&&out[0]<.1f)
        out[0]=Float.NaN;out[1]=Float.POSITIVE_INFINITY;orbit.frame(out,Float.NaN);check(out.all{it.isFinite()})
        orbit.reset();out.fill(0f);orbit.frame(out,1f);check(out.all{it==0f})
        repeat(rate){i->out[0]=.3f;out[1]=-.3f;orbit.frame(out,sin(i*2*PI/rate).toFloat());check(out.all{it.isFinite()&&abs(it)<=.301f});frames++}
        println("PASS $rate Hz: far-ear ratio ${right.first/right.second}, high ${high.first/high.second}")
    }
    // Integration checks for the shared real-time and offline DSP.
    val d=Dsp(44100,2);val out=FloatArray(2);val input=floatArrayOf(.25f,-.2f)
    d.frame(input,out,Presets.all.first());check(out.contentEquals(input))
    val preset=Presets.all.first{it.name=="8D Audio"}
    repeat(44100){d.frame(input,out,preset);check(out.all{it.isFinite()&&abs(it)<=1f})}
    d.frame(input,out,Presets.all.first());check(out.contentEquals(input))
    val mono=Dsp(44100,1);val m=FloatArray(1);repeat(1000){mono.frame(floatArrayOf(.2f),m,preset);check(m[0].isFinite())}
    println("PASS: $frames signal frames; symmetry, center identity, delay, spectral shadow, reset and invalid input")
}
