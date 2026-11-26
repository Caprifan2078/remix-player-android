from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text();assert s.count(old)==1,(name,old,s.count(old));p.write_text(s.replace(old,new))
replace('MusicAnalysis.kt','fun mag(i:Int):Double { return hypot(re[i],im[i]) };for(i in low..high){val a=mag(i-1);val b=mag(i);val c=mag(i+1);if(b>a&&b>=c&&b>0.025){','SpectralPeaks.each(re,im,low,high){i,a,b,c->')
replace('MusicAnalysis.kt','segmentChroma[pc]+=sqrt(b)}};Harmony.detect','segmentChroma[pc]+=sqrt(b)};Harmony.detect')
p=src/'MusicAnalysis.kt'
p.write_text(p.read_text()+'\n'+'''/** Reuse adjacent magnitudes without changing their values or the order of peak callbacks. */
internal object SpectralPeaks {
    inline fun each(re:DoubleArray,im:DoubleArray,low:Int,high:Int,visit:(Int,Double,Double,Double)->Unit){
        if(low>high)return
        var a=hypot(re[low-1],im[low-1]);var b=hypot(re[low],im[low])
        for(i in low..high){val c=hypot(re[i+1],im[i+1]);if(b>a&&b>=c&&b>0.025)visit(i,a,b,c);a=b;b=c}
    }
}
''')
replace('Mastering.kt','repeatLoop@ while(count<samples){if(count%8192==0L)check(!Thread.currentThread().isInterrupted);val v=StemCore.readShort(input)/32768.0;peak=max(peak,abs(v));sum+=v*v;count++}','''val bytes=ByteArray(16384);val data=DataInputStream(input)
            while(count<samples){
                check(!Thread.currentThread().isInterrupted)
                val n=minOf(bytes.size.toLong()/2,samples-count).toInt()*2
                data.readFully(bytes,0,n)
                for(i in 0 until n step 2){val v=((bytes[i].toInt() and 255) or (bytes[i+1].toInt() shl 8)).toShort()/32768.0;peak=max(peak,abs(v));sum+=v*v}
                count+=n/2
            }''')
print('PASS: reuse adjacent spectrum magnitudes and read mastering PCM in bounded blocks')
