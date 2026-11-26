package app.remix.player
import kotlin.math.*
import java.io.File
fun main(){
 val r=kotlin.random.Random(42);var count=0
 for(g in 30..31)for(slot in 0..15)repeat(100){val base=DoubleArray(9){.01+r.nextDouble()};val sum=base.sum();for(i in base.indices)base[i]/=sum;val before=base.copyOf();val out=ExtendedPhrase.adapt(g,slot,base);check(out.all{it.isFinite()&&it>0}&&abs(out.sum()-1)<1e-12);check(out.contentEquals(ExtendedPhrase.adapt(g,slot,base)));check(base.contentEquals(before));count++}
 val base=DoubleArray(9){1.0/9};check(ExtendedPhrase.parent(30)==8&&ExtendedPhrase.parent(31)==0);check(ExtendedPhrase.adapt(30,1,base)[0]>ExtendedPhrase.adapt(30,0,base)[0]);check(ExtendedPhrase.adapt(31,0,base)[5]>ExtendedPhrase.adapt(31,1,base)[5]);check(ExtendedPhrase.adapt(30,0,base).toList()!=ExtendedPhrase.adapt(31,0,base).toList());check(runCatching{ExtendedPhrase.adapt(32,0,base)}.isFailure)
 println("PASS: $count probability adaptations; deterministic, finite, normalized, source unchanged, genre-specific accents")
 val dir=kotlin.io.path.createTempDirectory("new-remixes").toFile()
 try{
   val raw=File(dir,"source.pcm");val frames=44100L*4;raw.outputStream().buffered().use{w->for(i in 0 until frames){val t=i/44100.0;StemCore.writeShort(w,StemCore.pcm((.12*sin(2*PI*220*t)).toFloat()));StemCore.writeShort(w,StemCore.pcm((.08*sin(2*PI*330*t)).toFloat()))}}
   val before=raw.readBytes();val hashes=mutableSetOf<Int>()
   for(i in listOf(0,8,30,31)){
     val style=GenreEngine.styles[i];val bpm=style.target.toDouble();val f=File(dir,"$i.wav")
     val chords=List(10){Harmony.Chord(it*.4,0,true,.9)}
     GenreEngine.renderFromMix(raw,f,style,bpm,0.0,chords,listOf(.15),sections=listOf(Arrangement.Section(0.0,4.0,Arrangement.Part.DROP)))
     check(f.length()==44+frames*4)
     val stats=Mastering.measure(f);check(stats.peak in .01..1.0&&stats.rms>.005)
     hashes.add(f.readBytes().contentHashCode())
     if(i>=30){
       val s=NeuralInstrumental.Settings(GenrePhrase.family(i),style.target,0,true,2,5703,genre=i);val out=File(dir,"neural-$i.wav");val n=NeuralInstrumental.render(out,s);check(n>0&&out.length()==44+n*4)
       val again=File(dir,"neural-again-$i.wav");NeuralInstrumental.render(again,s);check(out.readBytes().contentEquals(again.readBytes()))
     }
   }
   check(hashes.size==4&&raw.readBytes().contentEquals(before))
   println("PASS: 4 distinct full mix renders and both deterministic neural backing renders")
 }finally{dir.deleteRecursively()}
}
