package app.remix.player
import kotlin.math.*
fun main(){
 val original=Presets.all.first();val bass=Presets.all.single{it.name=="Deep Bass"}
 var cases=0
 for(rate in listOf(8000,44100,48000)){
  val d=LiveEffectSwitch(rate,2);val x=FloatArray(2);val y=FloatArray(2);val reference=Dsp(rate,2);val wet=FloatArray(2);var sample=0
  fun tone(){x[0]=(.25*sin(2*PI*55*sample++/rate)).toFloat();x[1]=-x[0]}
  check(d.canBypass(original));d.frame(x,y,original);check(y.contentEquals(x));repeat(rate){tone();d.frame(x,y,bass);reference.frame(x,wet,bass)};check(!d.canBypass(original))
  val before=y[0];var last=before;var maximum=0f
  repeat(rate/10){i->tone();reference.frame(x,wet,bass);d.frame(x,y,original);val mix=(i.toFloat()/(rate*24/1000).coerceAtLeast(1)).coerceAtMost(1f);check(abs(y[0]-(wet[0]+(x[0]-wet[0])*mix))<1e-6);maximum=max(maximum,abs(y[0]-last));last=y[0];check(y.all{it.isFinite()&&abs(it)<=1f});check(abs(y[0]+y[1])<1e-5)}
  check(maximum<.03f);check(y.contentEquals(x));check(d.canBypass(original));println("$rate Hz: direct jump avoided; max step=$maximum")
  cases+=7
  val modes=Presets.all;repeat(2){for(p in modes){repeat(7){d.frame(x,y,p);check(y.all{it.isFinite()&&abs(it)<=1f})}}}
  repeat(rate/10){d.frame(x,y,original)};check(y.contentEquals(x));cases+=2
 }
 println("PASS: $cases switching checks including rapid requests and exact original recovery")
}
