package app.remix.player
import kotlin.math.*
/** Stereo low-band exchange. Full-band endpoints stay unchanged. */
class DjBassExchange(rate:Int=44100){
 init{require(rate in 8000..384000)}
 private val alpha=1-exp(-2*PI*160/rate)
 private val a=DoubleArray(2);private val b=DoubleArray(2)
 fun lowGain(t:Double,incoming:Boolean):Double{
  val x=t.coerceIn(0.0,1.0)
  val v=if(incoming)((x-.25)/.50).coerceIn(0.0,1.0) else ((.75-x)/.50).coerceIn(0.0,1.0)
  return v*v*(3-2*v)
 }
 fun sample(ch:Int,l:Double,r:Double,t:Double,ga:Double,gb:Double,norm:Double):Double{
  a[ch]+=alpha*(l-a[ch]);b[ch]+=alpha*(r-b[ch])
  if(t<=0)return l
  if(t>=1)return r
  return (((l-a[ch]*(1-lowGain(t,false)))*ga+(r-b[ch]*(1-lowGain(t,true)))*gb)/norm).coerceIn(-1.0,32767.0/32768)
 }
}
