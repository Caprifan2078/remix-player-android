from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'VocalConditioning.kt'
s=p.read_text()
old='    class Measure{'
new='''    /** Only boost a quiet, non-silent Whisper window. Keep sample count and offsets exact;
     * normal/loud input is unchanged and isolated transients limit the gain. */
    fun prepareWhisper(block:FloatArray,n:Int):FloatArray? {
        require(n in 1..block.size)
        var sum=0.0;var peak=0.0
        for(i in 0 until n){
            if(i%8192==0)check(!Thread.currentThread().isInterrupted){"Отменено"}
            val x=block[i].toDouble();require(x.isFinite()&&abs(x)<=1.0){"Некорректный сигнал Whisper"}
            sum+=x*x;peak=max(peak,abs(x))
        }
        val rms=sqrt(sum/n)
        if(rms<=.001)return null
        val gain=minOf(4.0,.025/rms,.90/peak).coerceAtLeast(1.0)
        val result=block.copyOf(n)
        if(gain>1.0)for(i in result.indices){
            if(i%8192==0)check(!Thread.currentThread().isInterrupted){"Отменено"}
            result[i]=(result[i]*gain).toFloat()
        }
        check(!Thread.currentThread().isInterrupted){"Отменено"}
        return result
    }
    class Measure{'''
assert s.count(old)==1
p.write_text(s.replace(old,new))
p=src/'WhisperLocal.kt';s=p.read_text()
old='''if(ms>=250){var sum=0.0;for(i in 0 until n)sum+=block[i].toDouble()*block[i];val offset=start*1000/16000
                    val segments=if(sqrt(sum/n)>.001){val out=recognize(handle,block.copyOf(n),language,Runtime.getRuntime().availableProcessors().coerceIn(1,4))'''
new='''if(ms>=250){val prepared=VocalConditioning.prepareWhisper(block,n);val offset=start*1000/16000
                    val segments=if(prepared!=null){val out=recognize(handle,prepared,language,Runtime.getRuntime().availableProcessors().coerceIn(1,4))'''
assert s.count(old)==1
p.write_text(s.replace(old,new).replace('import kotlin.math.sqrt\n',''))
print('PASS: silence-aware quiet-window preparation for Whisper')
