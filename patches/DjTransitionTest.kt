package app.remix.player
import java.io.File
import kotlin.math.*
fun main(){
 fun w(bpm:Double,phase:Double=.1,key:String?="C major",conf:Double=.9)=DjTransition.Window(0,MusicAnalysis.Report(Tempo.Result(bpm,conf),phase,key,.2,.1,16.0,emptyList()))
 val p=DjTransition.plan(w(120.0),w(115.0,key="D major"),true);check(abs(p.speed-120.0/115)<1e-8&&p.semitones==-2)
 check(DjTransition.plan(w(120.0),w(100.0,key="F♯ major"),true).let{it.speed==1.0&&it.semitones==0})
 check(DjTransition.plan(w(120.0),w(115.0,conf=.1),true).speed==1.0)
 check(DjTransition.plan(w(120.0),w(120.0,key="A minor"),true).semitones==0)
 val n=44100L*16;val overlap=DjTransition.overlapFrames(n,n,5,w(120.0,.1),w(120.0,.3));check(overlap==44100L*5+8820)
 check(DjTransition.overlapFrames(n,n,5,w(120.0),w(118.0))==44100L*5)
 val dir=kotlin.io.path.createTempDirectory("dj-align").toFile()
 try{
  fun fixture(name:String,bpm:Double,phase:Double,hz:Double):File=File(dir,name).apply{outputStream().buffered(65536).use{out->repeat(n.toInt()){i->val t=i/44100.0;val beat=((t-phase)%(60/bpm)+60/bpm)%(60/bpm);val v=(sin(2*PI*hz*t)*(.03+.5*exp(-beat*25))*32767).roundToInt().toShort();StemCore.writeShort(out,v);StemCore.writeShort(out,v)}}}
  val a=fixture("a.pcm",120.0,.1,220.0);val b=fixture("b.pcm",115.0,.23,330.0)
  val ra=DjTransition.analyze(a,true);val rb=DjTransition.analyze(b,false);println("Measured BPM ${ra.report.tempo} / ${rb.report.tempo}")
  check(abs(ra.report.tempo!!.bpm-120)<1.5&&abs(rb.report.tempo!!.bpm-115)<1.5)
  val out=File(dir,"out.wav");val bytesA=a.readBytes();val bytesB=b.readBytes();val r=DjTransition.render(a,b,out,5,false)
  println("Rendered result: $r");val speed=DjTransition.plan(ra,rb,false).speed;check(speed in 1.02..1.07&&abs(r.frames-(n+(n/speed).roundToLong()-r.overlap))<=4)
  check(out.length()==44+r.frames*4&&out.readBytes().copyOfRange(44,44+(n-r.overlap).toInt()*4).contentEquals(bytesA.copyOfRange(0,(n-r.overlap).toInt()*4)))
  check(a.readBytes().contentEquals(bytesA)&&b.readBytes().contentEquals(bytesB));check(dir.listFiles()!!.map{it.name}.toSet()==setOf("a.pcm","b.pcm","out.wav"))
  val ordinary=File(dir,"ordinary.wav");check(TransitionMix.render(a,b,ordinary,5)==2*n-44100L*5)
  val cancelled=File(dir,"cancel.wav").apply{writeText("prior export")};Thread.currentThread().interrupt();val failure=try{runCatching{DjTransition.render(a,b,cancelled,5,true)}}finally{Thread.interrupted()};check(failure.isFailure&&cancelled.readText()=="prior export");println("PASS: smart DJ planning, analysis, actual time stretch, WAV render, source integrity, ordinary mode, cancellation")
 }finally{dir.deleteRecursively()}
}
