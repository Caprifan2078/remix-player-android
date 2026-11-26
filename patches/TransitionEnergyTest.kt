package app.remix.player
import java.io.File
import kotlin.math.*
fun main(){
 val dir=kotlin.io.path.createTempDirectory("transition-energy").toFile()
 try{
 val n=44100*4
 fun signal(name:String,frequency:Double,amp:Double,phase:Double=0.0)=File(dir,name).apply{outputStream().buffered().use{out->repeat(n){i->val v=(amp*sin(2*PI*frequency*i/44100+phase)).roundToInt().toShort();StemCore.writeShort(out,v);StemCore.writeShort(out,v)}}}
 fun test(label:String,a:File,b:File,reference:Double,minimum:Double){
  val out=File(dir,"mix.wav");val len=TransitionMix.render(a,b,out,2)
  check(len==264600L&&out.length()==44+4*len)
  var power=0.0;var max=0;var count=0
  out.inputStream().buffered().use{r->check(r.skip(44)==44L);repeat(len.toInt()){i->val l=StemCore.readShort(r).toInt();val rr=StemCore.readShort(r).toInt();check(l==rr);max=max(max,abs(l));if(i in 132300-2205 until 132300+2205){power+=l.toDouble()*l;count++}}}
  val db=20*log10(sqrt(power/count)/reference)
  println("$label: midpoint $db dB, peak $max")
  check(db>=minimum&&db<=.4){"midpoint level outside tolerance: $db dB"}
 }
 val a=signal("a.pcm",440.0,10000.0);val b=signal("b.pcm",733.0,10000.0)
 test("Independent tones",a,b,10000/sqrt(2.0),-.3)
 test("Identical tones",a,a,10000/sqrt(2.0),-.3)
 val loudA=signal("loud-a.pcm",440.0,32760.0);val loudB=signal("loud-b.pcm",733.0,32760.0)
 test("Full-scale independent tones",loudA,loudB,32760/sqrt(2.0),-3.2)
 val inverted=signal("inverted.pcm",440.0,10000.0,PI)
 val invOut=File(dir,"inverted.wav");TransitionMix.render(a,inverted,invOut,2)
 java.io.RandomAccessFile(invOut,"r").use{r->r.seek(44+132300L*4);val mid=java.lang.Short.reverseBytes(r.readShort()).toInt();check(abs(mid)<=2)}
 val stereo=File(dir,"stereo.pcm").apply{outputStream().buffered().use{w->repeat(n){i->val v=(12000*sin(2*PI*300*i/44100)).roundToInt().toShort();StemCore.writeShort(w,v);StemCore.writeShort(w,(-v).toShort())}}}
 val originalA=stereo.readBytes();val originalB=b.readBytes();val stereoOut=File(dir,"stereo.wav");TransitionMix.render(stereo,b,stereoOut,2)
 val payload=stereoOut.readBytes().copyOfRange(44,stereoOut.length().toInt())
 check(payload.copyOfRange(0,88200*4).contentEquals(originalA.copyOfRange(0,88200*4)))
 check(payload.takeLast(88200*4).toByteArray().contentEquals(originalB.copyOfRange(88200*4,n*4)))
 check(stereo.readBytes().contentEquals(originalA)&&b.readBytes().contentEquals(originalB))
 val silent=File(dir,"silent.pcm").apply{writeBytes(ByteArray(n*4))}
 val out=File(dir,"silent-mix.wav");TransitionMix.render(silent,silent,out,2);check(out.readBytes().drop(44).all{it==0.toByte()})
 Thread.currentThread().interrupt();try{check(runCatching{TransitionMix.render(a,b,File(dir,"cancel.wav"),2)}.isFailure);check(!File(dir,"cancel.wav").exists())}finally{Thread.interrupted()}
 val preserved=File(dir,"preserved.wav").apply{writeText("previous result")}
 val before=preserved.readBytes()
 check(runCatching{TransitionMix.render(a,b,preserved,2){if(it>=10)error("Injected render failure")}}.isFailure)
 check(preserved.readBytes().contentEquals(before))
 check(dir.listFiles()!!.none{it.name.startsWith(".transition-")})
 val finalProgress=mutableListOf<Int>()
 TransitionMix.render(a,b,preserved,2){finalProgress.add(it)}
 check(finalProgress.last()==100&&preserved.length()==44+264600L*4)
 println("PASS: independent and identical signals, full-scale protection, opposite phase, stereo endpoints, source integrity, silence and cancellation")
 }finally{dir.deleteRecursively()}
}
