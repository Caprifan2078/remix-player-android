package app.remix.player
import kotlin.math.*
fun main(){
 val original=Presets.all.first();val bass=Presets.all.single{it.name=="Deep Bass"}
 var cases=0
 for(rate in listOf(8000,44100,48000)){
  val d=LiveEffectSwitch(rate,2);val x=floatArrayOf(.25f,-.25f);val y=FloatArray(2)
  check(d.canBypass(original));d.frame(x,y,original);check(y.contentEquals(x));repeat(rate){d.frame(x,y,bass)};check(!d.canBypass(original))
  val before=y[0];var last=before;var maximum=0f
  repeat(rate/10){d.frame(x,y,original);maximum=max(maximum,abs(y[0]-last));last=y[0];check(y.all{it.isFinite()&&abs(it)<=1f});check(abs(y[0]+y[1])<1e-5)}
  check(maximum<.005f);check(y.contentEquals(x));check(d.canBypass(original));println("$rate Hz: direct jump avoided; max step=$maximum")
  cases+=7
  val modes=Presets.all;repeat(2){for(p in modes){repeat(7){d.frame(x,y,p);check(y.all{it.isFinite()&&abs(it)<=1f})}}}
  repeat(rate/10){d.frame(x,y,original)};check(y.contentEquals(x));cases+=2
 }
 println("PASS: $cases switching checks including rapid requests and exact original recovery")
}
