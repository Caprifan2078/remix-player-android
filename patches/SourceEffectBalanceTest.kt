package app.remix.player
import kotlin.math.*
fun main(){
 fun run(hz:Double,amp:Float=.3f):SourceEffectBalance{
  val a=SourceEffectBalance(48000,2);val frame=FloatArray(2)
  repeat(144000){i->frame[0]=(amp*sin(2*PI*hz*i/48000)).toFloat();frame[1]=-frame[0];a.frame(frame)}
  return a
 }
 val low=run(55.0);val mid=run(1000.0);val high=run(9000.0)
 check(low.bass<mid.bass-.25f)
 check(high.drive<mid.drive-.15f)
 check(low.room<mid.room)
 check(listOf(low,mid,high).all{it.bass in .61f..1.11f&&it.drive in .53f..1.03f&&it.room in .67f..1.05f})
 val silent=run(1000.0,0f);check(abs(silent.bass-1f)<.001f)
 low.reset();check(low.bass==1f&&low.drive==1f&&low.room==1f)
 repeat(100){low.frame(floatArrayOf(Float.NaN,Float.POSITIVE_INFINITY))}
 check(low.bass.isFinite()&&low.drive.isFinite())
 val attack=SourceEffectBalance(48000,2)
 repeat(48000){attack.frame(floatArrayOf(.03f,-.03f))}
 repeat(2400){attack.frame(floatArrayOf(.8f,-.8f))}
 check(attack.transient<.8f&&attack.transient>=.5f)
 repeat(96000){attack.frame(floatArrayOf(.03f,-.03f))}
 check(attack.transient>.98f)
 attack.reset();check(attack.transient==1f)
 println("PASS: 10 source spectrum and transient effect adaptation checks")
}
