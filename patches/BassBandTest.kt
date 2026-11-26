package app.remix.player
import kotlin.math.*
fun main(){
    for(rate in listOf(8000,44100,48000)){
        val band=BassBand(rate,2)
        fun measure(hz:Double):Pair<Double,Double>{
            band.reset(115.0);var a=0f;var b=0f;var old=0.0;var fresh=0.0
            val alpha=(1-exp(-2*PI*115/rate)).toFloat()
            repeat(rate*2){i->val x=if(hz==0.0).25f else (.25*sin(2*PI*hz*i/rate)).toFloat();a+=alpha*(x-a);b+=alpha*(a-b);val y=band.sample(0,x);check(band.sample(1,0f)==0f);if(i>=rate){old+=b*b;fresh+=y*y}}
            return sqrt(old/rate) to sqrt(fresh/rate)
        }
        val dc=measure(0.0);val sub=measure(8.0);val bass=measure(55.0);val high=measure(4000.0)
        println("$rate Hz: DC $dc; 8Hz $sub; 55Hz $bass; 4kHz $high")
        check(dc.second<.00001&&dc.first>.24)
        check(sub.second<sub.first*.20)
        check(bass.second>bass.first*.85&&bass.second<bass.first*1.02)
        check(high.second<.001)
        band.reset(115.0);check(band.sample(0,Float.NaN)==0f);check(band.sample(1,Float.POSITIVE_INFINITY)==0f)
    }
    println("PASS: 15 bass band checks at three sample rates")
}
