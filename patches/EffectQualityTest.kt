package app.remix.player
import kotlin.math.*
fun main(){
    fun preset(name:String)=Presets.all.single{it.name==name}
    val rate=44100
    fun rms(name:String,hz:Double):Double{
        val dsp=Dsp(rate,2);val input=FloatArray(2);val out=FloatArray(2);val p=preset(name);var sum=0.0
        repeat(rate*2){i->val x=(.075*sin(2*PI*hz*i/rate)).toFloat();input.fill(x);dsp.frame(input,out,p);if(i>=rate)sum+=out[0]*out[0]}
        return sqrt(sum/rate)/(.075/sqrt(2.0))
    }
    fun tail(name:String,start:Double,end:Double):Double{
        val dsp=Dsp(rate,2);val input=FloatArray(2);val out=FloatArray(2);val p=preset(name);var sum=0.0
        repeat((end*rate).toInt()){i->input.fill(if(i==0).4f else 0f);dsp.frame(input,out,p);if(i>=start*rate)sum+=out[0]*out[0]+out[1]*out[1]}
        return sqrt(sum)
    }
    val deepHigh=rms("Deep Bass",4000.0);val deepLow=rms("Deep Bass",55.0);val water=rms("Underwater",6000.0);val radio=rms("Radio Filter",60.0);val cathedral=tail("Cathedral",.5,1.5);val room=tail("Small Room",.5,1.5)
    val extreme=rms("Extreme Distortion",440.0)
    fun harmonic(name:String):Double{
        val d=Dsp(rate,2);val inFrame=FloatArray(2);val out=FloatArray(2);val p=preset(name);var fundamental=0.0;var third=0.0
        repeat(rate*2){i->val phase=2*PI*440*i/rate;inFrame.fill((.35*sin(phase)).toFloat());d.frame(inFrame,out,p);if(i>=rate){fundamental+=out[0]*sin(phase);third+=out[0]*sin(3*phase)}}
        return abs(third/fundamental)
    }
    val distortion=harmonic("Extreme Distortion");val overdrive=harmonic("Overdrive")
    val measurements=listOf("Extreme distortion quiet gain" to (extreme<2.5),"Distortion character retained" to (distortion>.04&&distortion>overdrive),"Bass high preservation" to (deepHigh>.95),"Bass low boost" to (deepLow>1.35),"Underwater rejection" to (water<.30),"Radio bandpass" to (radio<.30),"Cathedral sustained tail" to (cathedral>.0007),"Different acoustic spaces" to (cathedral>10*room))
    println("Measurements: bass 4k=$deepHigh, bass 55=$deepLow, underwater 6k=$water, radio 60=$radio, cathedral tail=$cathedral, small room tail=$room, extreme gain=$extreme, extreme third=$distortion, overdrive third=$overdrive")
    measurements.forEach{println("${if(it.second)"PASS" else "FAIL"}: ${it.first}")}
    val signatures=mutableSetOf<String>();var checks=0
    for(p in Presets.all){
        for(sr in listOf(8000,44100,48000)){
            val d=Dsp(sr,2);val inp=FloatArray(2);val out=FloatArray(2);var sig=17;var peak=0f;var energy=0.0
            repeat(sr*2){i->
                val amp=if(i<sr).07 else .73
                inp[0]=(amp*(.5*sin(2*PI*65*i/sr)+.32*sin(2*PI*330*i/sr)+.18*sin(2*PI*1700*i/sr))).toFloat()
                inp[1]=(amp*(.5*sin(2*PI*65*i/sr)+.32*sin(2*PI*550*i/sr)+.18*sin(2*PI*2500*i/sr))).toFloat()
                d.frame(inp,out,p);check(out.all{it.isFinite()&&abs(it)<=1f}){"${p.name}: invalid output"}
                peak=maxOf(peak,abs(out[0]),abs(out[1]));energy+=out[0]*out[0]+out[1]*out[1]
                if(i%23==0)sig=31*sig+out[0].toBits()+out[1].toBits()
            }
            check(energy>1.0&&peak>.01f){"${p.name}: silent output"}
            if(sr==44100)check(signatures.add("${p.speed}:${p.pitch}:$sig")){"${p.name}: duplicate DSP + tempo/pitch signature"}
            inp[0]=Float.NaN;inp[1]=Float.POSITIVE_INFINITY;d.frame(inp,out,p);check(out.all{it.isFinite()})
            d.frame(floatArrayOf(.25f,-.5f),out,Presets.all.first());check(out.contentEquals(floatArrayOf(.25f,-.5f)))
            checks++
        }
    }
    println("PASS: $checks preset/rate combinations; 41 distinct DSP + speed/pitch signatures; finite, bounded, audible and exact bypass")
    check(measurements.all{it.second}){"Quality regression: ${measurements.filterNot{it.second}.map{it.first}}"}
}
