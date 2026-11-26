package app.remix.player
import kotlin.math.*
fun eqHeadroomQualityTests(){
 var failed=0;var frameChecks=0
 for(rate in listOf(8000,44100,48000)){
  val f=if(rate==8000)250.0 else 500.0
  val eq=GraphicEq(rate,2,List(10){12f});var clipped=0;var peak=0f;var err=0.0
  repeat(rate*2){i->val x=(.9*sin(2*PI*f*i/rate)).toFloat();val l=eq.sample(x,0);val r=eq.sample(x*.5f,1);if(i>=rate){if(abs(l)>=.9999f)clipped++;peak=max(peak,abs(l));err=max(err,abs(l-r*2).toDouble())}}
  println("$rate: clipped=$clipped peak=$peak stereo error=$err")
  if(clipped!=0||peak>.98f||err>1e-5)failed++
  val linked=GraphicEq(rate,2,List(10){12f});val v=FloatArray(2)
  repeat(rate){i->val x=if(i%251<20).98f else (.8*sin(2*PI*f*i/rate)).toFloat();v[0]=x;v[1]=x*.5f;linked.frame(v);check(v.all{it.isFinite()&&abs(it)<=.986f});check(abs(v[0]-v[1]*2)<1e-5)}
  frameChecks++
  val flat=GraphicEq(rate,2,List(10){0f});check(flat.sample(.987f,0)==.987f)
  val cut=GraphicEq(rate,2,List(10){if(it==5)-12f else 0f});var sum=0.0;repeat(rate*2){i->val x=(.5*sin(2*PI*1000*i/rate)).toFloat();val y=cut.sample(x,0);if(i>=rate)sum+=y*y};check(sqrt(sum/rate)/(.5/sqrt(2.0)) in .24.. .26)
 }
 check(failed==0){"$failed rate cases failed"}
 println("PASS: 3 sample-rate regression groups and $frameChecks linked transient checks; flat identity and -12 dB cut")
}
