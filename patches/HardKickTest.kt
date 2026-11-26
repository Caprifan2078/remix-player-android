package app.remix.player
import kotlin.math.*
fun main(){
 val names=listOf("Hardstyle","Euphoric Hardstyle","Rawstyle","Xtra Raw","Hardcore","Uptempo Hardcore","Frenchcore","Hardtekk")
 val curves=names.map{HardKick.curve(it,44100)!!}
 check(curves.map{it.contentHashCode()}.distinct().size==8)
 check(curves.all{c->c.all{it.isFinite()&&abs(it)<=.65}})
 check(curves.all{it.first()==0.0&&abs(it.last())<.002})
 check(curves[5].size<curves[4].size&&curves[4].size<curves[0].size)
 check(curves.all{c->c.maxOf{abs(it)}>.15})
 check(HardKick.curve("House",44100)==null)
 check(HardKick.sample(HardKick.profile("Hardstyle")!!,Double.NaN,.36)==0.0)
 check(curves[0].contentEquals(HardKick.curve("Hardstyle",44100)))
 fun ratio(hz:Double,kick:Float,enabled:Boolean):Double {
  val mixer=HardMixSpace(48000);var raw=0.0;var output=0.0
  repeat(48000){i->val x=(.3*sin(2*PI*hz*i/48000)).toFloat();mixer.frame(x,-x,kick,enabled);check(abs(mixer.left+mixer.right)<1e-6);if(i>=12000){raw+=x*x;output+=mixer.left*mixer.left}}
  return sqrt(output/raw)
 }
 val bass=ratio(55.0,1f,true);val highs=ratio(3000.0,1f,true)
 check(bass<.50&&bass>.25)
 check(highs>.95)
 check(abs(ratio(55.0,0f,true)-1)<1e-6)
 check(abs(ratio(55.0,1f,false)-1)<1e-6)
 val mix=HardMixSpace(48000);repeat(4800){mix.frame(.3f,-.3f,1f,true)};check(abs(mix.left)<.15f);repeat(48000){mix.frame(.3f,-.3f,0f,true)};check(abs(mix.left-.3f)<.001f)
 check(names.all{HardKick.mixDrumGain(it)==.54f})
 check(HardKick.mixDrumGain("House")==.38f&&HardKick.sidechainDecay("House")==.065)
 check(names.all{HardKick.sidechainDecay(it) in .065.. .135})
 check(HardKick.sidechainDecay("Hardstyle")>HardKick.sidechainDecay("Uptempo Hardcore"))
 val previous=exp(-.12/.065);val current=exp(-.12/HardKick.sidechainDecay("Hardstyle"));check(current>previous*2)
 println("PASS: 19 hard kick and mix checks; bass ratio=$bass, high ratio=$highs; hardstyle duck envelope at 120ms $previous -> $current")
}
