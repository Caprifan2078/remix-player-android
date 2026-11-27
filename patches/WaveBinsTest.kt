package app.remix.player
import java.nio.*
import kotlin.math.*
fun main(){
    val rng=kotlin.random.Random(42)
    repeat(500){case->
        val rate=listOf(8000,16000,44100,48000,96000)[case%5];val seconds=1+case%3;val total=rate*seconds;val channels=1+case%2;val floating=case%3==0
        val bins=16+case%145;val collector=WaveBins(seconds*1000000L,rate,bins);val expected=FloatArray(bins);var frame=0
        while(frame<total){val n=minOf(total-frame,1+rng.nextInt(4096));val b=ByteBuffer.allocate(n*channels*(if(floating)4 else 2)).order(ByteOrder.LITTLE_ENDIAN)
            repeat(n){f->repeat(channels){val v=if(floating){val x=rng.nextFloat()*2-1;b.putFloat(x);abs(x)}else{val x=rng.nextInt(-32768,32768);b.putShort(x.toShort());abs(x)/32768f};val k=(frame+f)*bins/total;expected[k]=maxOf(expected[k],v)}}
            b.flip();collector.add(b,channels,floating,(frame*1000000.0/rate).roundToLong());frame+=n
        };check(collector.finish()!!.contentEquals(expected)){"case $case"}
    }
    check(WaveBins(1_000_000,8000).finish()==null)
    val b=ByteBuffer.allocate(16000).order(ByteOrder.LITTLE_ENDIAN);repeat(8000){b.putShort(if(it==0)Short.MIN_VALUE else 0)};b.flip();val wave=WaveBins(1_000_000,8000);wave.add(b,1,false,0);check(wave.finish()!![0]==1f);check(wave.finish()!!.drop(1).all{it==0f})
    // Format changes and nonfinite floats preserve the previous exact peak.
    val mixed=WaveBins(1_000_000,8000,16)
    val floats=ByteBuffer.allocate(4000*4).order(ByteOrder.LITTLE_ENDIAN)
    repeat(4000){floats.putFloat(when(it%5){0->Float.NaN;1->Float.POSITIVE_INFINITY;2->-.6f;else->0f})}
    floats.flip();mixed.add(floats,1,true,0)
    val shorts=ByteBuffer.allocate(4000*2).order(ByteOrder.LITTLE_ENDIAN)
    repeat(4000){shorts.putShort((-16384).toShort())};shorts.flip();mixed.add(shorts,1,false,500_000)
    check(mixed.finish()!!.contentEquals(FloatArray(16){if(it<8).6f else .5f}))
    println("PASS: 500 randomized waveforms exact against per-frame reference, five rates, mono/stereo, float/PCM16, irregular chunks, silence and incomplete input")
}
