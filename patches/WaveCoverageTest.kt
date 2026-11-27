package app.remix.player
import java.nio.*
fun main(){
 fun add(w:WaveBins,start:Int,n:Int){val b=ByteBuffer.allocate(n*2).order(ByteOrder.LITTLE_ENDIAN);repeat(n){b.putShort(1000)};b.flip();w.add(b,1,false,start*125L)}
 val tail=WaveBins(1000000,8000);add(tail,7900,100);check(tail.finish()==null){"False complete waveform from final 100 samples"}
 val hole=WaveBins(1000000,8000);add(hole,0,2000);add(hole,6000,2000);check(hole.finish()==null)
 val duplicates=WaveBins(1000000,8000);repeat(10){add(duplicates,0,1000)};add(duplicates,7000,1000);check(duplicates.finish()==null)
 val overlap=WaveBins(1000000,8000);add(overlap,0,4100);add(overlap,4000,4000);check(overlap.finish()!=null)
 val near=WaveBins(1000000,8000);add(near,0,7800);check(near.finish()==null);check(near.preview()!!.first.takeLast(4).all{it.isNaN()})
 val reversed=WaveBins(1000000,8000);add(reversed,4000,4000);add(reversed,0,4000);check(reversed.finish()==null)
 val progressive=WaveBins(1000000,8000,160);add(progressive,0,2000);check(progressive.preview()?.second==40);check(progressive.finish()==null)
 val missing=WaveBins(1000000,8000,160);add(missing,4000,2000);check(missing.preview()!!.first.take(80).all{it.isNaN()});check(missing.preview()!!.first[80].isFinite())
 add(progressive,2000,6000);check(progressive.preview()?.second==160);check(progressive.finish()!=null)
 val random=kotlin.random.Random(42)
 repeat(5000){val w=WaveBins(1000000,8000);var last=0;var covered=0;repeat(8){val start=(last+random.nextInt(0,900)).coerceAtMost(8000);val end=(start+random.nextInt(1,1700)).coerceAtMost(8000);if(end>start){add(w,start,end-start);covered+=end-start};last=end};check((w.finish()!=null)==(covered==8000))}
 val gap=WaveBins(1000000,8000);add(gap,0,4000);add(gap,4050,3950)
 val partial=gap.preview()!!.first;check(partial[80].isNaN()&&partial[79].isFinite()&&partial[81].isFinite());check(gap.finish()==null)
 val independent=kotlin.random.Random(42)
 repeat(5000){
  val w=WaveBins(1000000,8000);val seen=BooleanArray(8000);var last=0
  repeat(8){val start=(last+independent.nextInt(0,900)).coerceAtMost(8000);val end=(start+independent.nextInt(1,1700)).coerceAtMost(8000);if(end>start){add(w,start,end-start);for(i in start until end)seen[i]=true};last=end}
  val known=BooleanArray(160){b->(b*50 until (b+1)*50).all{seen[it]}}
  check((w.finish()!=null)==known.all{it});val preview=w.preview()?.first
  check((preview!=null)==known.any{it});if(preview!=null)for(i in known.indices)check(preview[i].isFinite()==known[i])
 }
 println("PASS: 5000 randomized gaps, overlaps, duplicates, tail-only data and reversed chunks")
}
