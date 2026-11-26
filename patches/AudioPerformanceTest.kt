package app.remix.player
import java.io.*
import kotlin.math.*
fun main(){
    val rng=kotlin.random.Random(42)
    fun baseline(re:DoubleArray,im:DoubleArray,lo:Int,hi:Int,rate:Int):DoubleArray{
        val result=DoubleArray(12)
        fun mag(i:Int)=hypot(re[i],im[i])
        for(i in lo..hi){val a=mag(i-1);val b=mag(i);val c=mag(i+1);if(b>a&&b>=c&&b>.025){val d=(.5*(a-c)/(a-2*b+c)).coerceIn(-.5,.5);val hz=(i+d)*rate/re.size;val midi=(69+12*ln(hz/440)/ln(2.0)).roundToInt();result[Math.floorMod(midi,12)]+=sqrt(b)}}
        return result
    }
    fun actual(re:DoubleArray,im:DoubleArray,lo:Int,hi:Int,rate:Int):DoubleArray{
        val result=DoubleArray(12)
        SpectralPeaks.each(re,im,lo,hi){i,a,b,c->val d=(.5*(a-c)/(a-2*b+c)).coerceIn(-.5,.5);val hz=(i+d)*rate/re.size;val midi=(69+12*ln(hz/440)/ln(2.0)).roundToInt();result[Math.floorMod(midi,12)]+=sqrt(b)}
        return result
    }
    for(n in listOf(2048,4096,8192,16384))repeat(250){
        val re=DoubleArray(n){rng.nextDouble(-10.0,10.0)};val im=DoubleArray(n){rng.nextDouble(-10.0,10.0)}
        val lo=2+rng.nextInt(10);val hi=lo+rng.nextInt(n/2-lo-1)
        check(baseline(re,im,lo,hi,44100).contentEquals(actual(re,im,lo,hi,44100)))
    }
    val silent=DoubleArray(2048);check(actual(silent,silent,2,500,8000).all{it==0.0});check(actual(silent,silent,4,3,8000).all{it==0.0})
    val dir=kotlin.io.path.createTempDirectory("mastering-perf").toFile()
    try{
        for(frames in listOf(1,2,4095,4096,4097,8192,16385,220500)){
            val wav=File(dir,"source.wav")
            wav.outputStream().buffered().use{out->StemCore.header(out,frames.toLong());repeat(frames*2){StemCore.writeShort(out,rng.nextInt(-32768,32768).toShort())}}
            var peak=0.0;var sum=0.0
            wav.inputStream().buffered().use{r->DataInputStream(r).readFully(ByteArray(44));repeat(frames*2){val v=StemCore.readShort(r)/32768.0;peak=max(peak,abs(v));sum+=v*v}}
            val before=wav.readBytes()
            val actual=Mastering.measure(wav)
            check(actual==Mastering.Stats(peak,sqrt(sum/(frames*2)),frames*2L))
            check(wav.readBytes().contentEquals(before))
            Thread.currentThread().interrupt()
            try{check(runCatching{Mastering.measure(wav)}.isFailure)}finally{Thread.interrupted()}
            RandomAccessFile(wav,"rw").use{it.setLength(it.length()-4)}
            check(runCatching{Mastering.measure(wav)}.isFailure)
        }
    }finally{dir.deleteRecursively()}
    println("PASS: 1000 bit-identical chroma cases, exact PCM peak/RMS, block boundaries, source identity, invalid WAV and cancellation")
}
