package app.remix.player
import java.nio.*
fun main(){
 fun add(w:WaveBins,start:Int,n:Int){val b=ByteBuffer.allocate(n*2).order(ByteOrder.LITTLE_ENDIAN);repeat(n){b.putShort(1000)};b.flip();w.add(b,1,false,start*125L)}
 val tail=WaveBins(1000000,8000);add(tail,7900,100);check(tail.finish()==null){"False complete waveform from final 100 samples"}
 val hole=WaveBins(1000000,8000);add(hole,0,2000);add(hole,6000,2000);check(hole.finish()==null)
 val duplicates=WaveBins(1000000,8000);repeat(10){add(duplicates,0,1000)};add(duplicates,7000,1000);check(duplicates.finish()==null)
 val overlap=WaveBins(1000000,8000);add(overlap,0,4100);add(overlap,4000,4000);check(overlap.finish()!=null)
 val near=WaveBins(1000000,8000);add(near,0,7800);check(near.finish()!=null)
 val reversed=WaveBins(1000000,8000);add(reversed,4000,4000);add(reversed,0,4000);check(reversed.finish()==null)
 val random=kotlin.random.Random(42)
 repeat(5000){val w=WaveBins(1000000,8000);var last=0;var covered=0;repeat(8){val start=(last+random.nextInt(0,900)).coerceAtMost(8000);val end=(start+random.nextInt(1,1700)).coerceAtMost(8000);if(end>start){add(w,start,end-start);covered+=end-start};last=end};check((w.finish()!=null)==(covered>=7600))}
 println("PASS: 5000 randomized gaps, overlaps, duplicates, tail-only data and reversed chunks")
}
