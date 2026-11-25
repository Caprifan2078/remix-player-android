package app.remix.player
import kotlin.math.*
fun main(){
 val n=16000
 fun tone(a:Double)=FloatArray(n){(a*sin(2*PI*233*it/16000)).toFloat()}
 fun rms(a:FloatArray)=sqrt(a.sumOf{it.toDouble()*it}/a.size)
 fun checkSignal(a:FloatArray, expected:Double){val out=VocalConditioning.prepareWhisper(a,a.size)!!;check(out.size==a.size);val gain=rms(out)/rms(a);println("RMS ${rms(a)} -> ${rms(out)}; gain=$gain");check(abs(gain-expected)<.0001){"Expected gain $expected, actual $gain"};check(out.all{it.isFinite()&&abs(it)<=1f})}
 val quiet=tone(.008);val copy=quiet.copyOf();checkSignal(quiet,4.0);check(copy.contentEquals(quiet))
 checkSignal(tone(.2),1.0)
 checkSignal(tone(.04),1.0)
 val transient=tone(.008);transient[10]=.8f;val out=VocalConditioning.prepareWhisper(transient,n)!!;check(abs(out[10]-.9f)<1e-6);check(out.all{abs(it)<=.900001f})
 check(VocalConditioning.prepareWhisper(FloatArray(n),n)==null);check(VocalConditioning.prepareWhisper(tone(.0008),n)==null)
 check(VocalConditioning.prepareWhisper(tone(.002),n)!=null)
 val longer=tone(.008).copyOf(n+100);longer[n]=Float.NaN;check(VocalConditioning.prepareWhisper(longer,n)!!.size==n)
 val invalid=tone(.008);invalid[1]=Float.NaN;check(runCatching{VocalConditioning.prepareWhisper(invalid,n)}.isFailure)
 invalid[1]=Float.POSITIVE_INFINITY;check(runCatching{VocalConditioning.prepareWhisper(invalid,n)}.isFailure)
 invalid[1]=1.1f;check(runCatching{VocalConditioning.prepareWhisper(invalid,n)}.isFailure)
 Thread.currentThread().interrupt();val cancelled=try{runCatching{VocalConditioning.prepareWhisper(quiet,n)}}finally{Thread.interrupted()};check(cancelled.isFailure)
 println("PASS: quiet signal boost, normal/loud preservation, transient headroom, silence/noise floor, exact sample count, invalid values and cancellation")
}
