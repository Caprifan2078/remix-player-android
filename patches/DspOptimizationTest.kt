package app.remix.player
import kotlin.math.*

/** Frozen before-optimization reference algorithms; compare production DSP sample by sample. */
/** Streaming, channel-linked effect depth. It changes wet/dry balance, not tempo or pitch. */
private class ReferenceEnvelope(rate:Int) {
    init { require(rate in 8000..384000) }
    private val attack=(1.0-exp(-1.0/(.045*rate))).toFloat()
    private val release=(1.0-exp(-1.0/(.30*rate))).toFloat()
    private val blend=(1.0-exp(-1.0/(.080*rate))).toFloat()
    private val referenceBlend=(1.0-exp(-1.0/(4.0*rate))).toFloat()
    private var reference=0f
    private var power=0f
    private var strength=1f
    fun reset(){power=0f;reference=0f;strength=1f}
    fun frame(input:FloatArray):Float {
        if(input.isEmpty())return strength
        var sum=0f
        for(x in input){if(x.isFinite()){val a=x.coerceIn(-1f,1f);sum+=a*a}}
        val sample=sum/input.size
        power+=(sample-power)*(if(sample>power)attack else release)
        reference+=(power-reference)*referenceBlend
        val rms=sqrt(power.coerceAtLeast(0f))
        val absolute=((rms-.12f)/.35f).coerceIn(0f,1f)
        // Compare to recent track dynamics; ignore relative changes close to silence.
        val relative=if(rms>.09f&&reference>.0004f)((sqrt(power/reference)-1.15f)/.9f).coerceIn(0f,1f) else 0f
        val dense=maxOf(absolute,relative)
        val target=1f-.45f*dense
        strength=(strength+(target-strength)*blend).coerceIn(.55f,1f)
        return strength
    }
}

/** Headphone-oriented stereo orbit: fractional interaural delay and shadow, centered low bass. */
private class ReferenceOrbit(private val rate:Int){
    init{require(rate in 8000..384000)}
    private val ring=FloatArray((rate*.0007).toInt()+4)
    private var cursor=0
    private var low=0f
    private var shadowL=0f
    private var shadowR=0f
    private val bassAlpha=(1-exp(-2*PI*160/rate)).toFloat()
    private val shadowAlpha=(1-exp(-2*PI*1800/rate)).toFloat()
    fun reset(){ring.fill(0f);cursor=0;low=0f;shadowL=0f;shadowR=0f}
    private fun delayed(frames:Float):Float{
        val offset=frames.toInt();val frac=frames-offset
        val a=ring[(cursor-offset+ring.size)%ring.size]
        val b=ring[(cursor-offset-1+ring.size)%ring.size]
        return a+(b-a)*frac
    }
    fun apply(frame:FloatArray,position:Float){
        require(frame.size==2)
        val p=if(position.isFinite())position.coerceIn(-1f,1f)else 0f
        val l=frame[0].takeIf{it.isFinite()}?:0f;val r=frame[1].takeIf{it.isFinite()}?:0f
        val mid=(l+r)*.5f;val side=(l-r)*.5f
        low+=bassAlpha*(mid-low)
        ring[cursor]=mid-low
        val dl=delayed(max(0f,p)*rate*.00065f);val dr=delayed(max(0f,-p)*rate*.00065f)
        shadowL+=shadowAlpha*(dl-shadowL);shadowR+=shadowAlpha*(dr-shadowR)
        val farL=max(0f,p);val farR=max(0f,-p)
        val highL=dl+(shadowL-dl)*farL*.72f
        val highR=dr+(shadowR-dr)*farR*.72f
        frame[0]=low+highL*sqrt(1f-.86f*p)+side*.72f
        frame[1]=low+highR*sqrt(1f+.86f*p)-side*.72f
        cursor=(cursor+1)%ring.size
    }
}

fun main(){
  var count=0
  for(rate in listOf(8000,22050,44100,48000,96000,192000)){
    val old=ReferenceEnvelope(rate);val new=AdaptiveEffectEnvelope(rate);val f=FloatArray(2);var error=0f;var maxStep=0f;var prev=1f
    repeat(rate*12){i->
      val t=i.toDouble()/rate;val amp=when{t<2->.025;t<3->.85;t<5->.08;t<6->.25;t<7->.001;t<9->.4;else->.08+.45*(.5+.5*sin(t*PI*5))}
      f[0]=(amp*sin(2*PI*440*t)).toFloat();f[1]=(amp*cos(2*PI*67*t)).toFloat()
      if(i%37291==0)f[0]=Float.NaN
      val x=old.frame(f);val y=new.frame(f);error=max(error,abs(x-y));maxStep=max(maxStep,abs(y-prev));prev=y
      check(y.isFinite()&&y in .55f..1f)
    }
    check(error<.006f){"$rate max error $error"};check(maxStep<.001f);new.reset();old.reset();f.fill(.05f);check(new.frame(f)==old.frame(f));count+=3
    println("$rate Hz: max depth error=$error; max step=$maxStep")
  }
  println("PASS: $count control-rate equivalence, smoothness and reset checks")
  count=0
  for(rate in listOf(8000,22050,44100,48000,96000,192000,384000)){
    val old=ReferenceOrbit(rate);val new=StereoOrbit(rate);val a=FloatArray(2);val b=FloatArray(2)
    repeat(rate*3){i->val t=i.toDouble()/rate;a[0]=(.2*sin(t*2*PI*440)+.15*cos(t*2*PI*83)).toFloat();a[1]=(.3*sin(t*2*PI*1500)+.1*cos(t*2*PI*83)).toFloat();if(i%17093==0)a[0]=Float.NaN;b[0]=a[0];b[1]=a[1];val p=when(i%1009){0->-1f;1->1f;2->0f;3->Float.NaN;else->sin(t*2*PI*.19).toFloat()};old.apply(a,p);new.apply(b,p);check(a.contentEquals(b)){"$rate orbit changed at $i"}}
    old.reset();new.reset();a.fill(0f);b.fill(0f);old.apply(a,.95f);new.apply(b,.95f);check(a.contentEquals(b));count+=2;println("$rate Hz: exact orbit sample match")
  }
  println("PASS: $count exact orbit equivalence and reset checks")
}
