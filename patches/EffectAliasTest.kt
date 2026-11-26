package app.remix.player
import kotlin.math.*
fun main(){
 val rate=48000;val n=rate;val x=FloatArray(2);val y=FloatArray(2)
 fun measure(name:String,hz:Double):Pair<Double,Double>{
 val p=Presets.all.single{it.name==name};val d=Dsp(rate,2);var a=0.0;var b=0.0;var c=0.0;var e=0.0
 val fold=abs(3*hz-rate)
 repeat(n*2){i->val t=2*PI*i/rate;x.fill((.65*sin(t*hz)).toFloat());d.frame(x,y,p);if(i>=n){a+=y[0]*sin(t*hz);b+=y[0]*cos(t*hz);c+=y[0]*sin(t*fold);e+=y[0]*cos(t*fold)}}
 return hypot(a,b)*2/n to hypot(c,e)/hypot(a,b)
 }
 val values=listOf("Overdrive","Distorted","Extreme Distortion").map{it to measure(it,11000.0)}
 values.forEach{println("${it.first}: fundamental=${it.second.first}, folded third=${it.second.second}")}
 check(values.all{it.second.first>.15&&it.second.second<.055}){"Folded harmonic too strong"}
}
