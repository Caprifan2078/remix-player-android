from pathlib import Path
import sys
root=Path(sys.argv[1])
src=root/'app/src/main/java/app/remix/player'
def replace(p,old,new):
    s=p.read_text();assert s.count(old)==1,(p.name,old,s.count(old));p.write_text(s.replace(old,new))
p=src/'PlayerExtras.kt'
replace(p,'    fun sample(x:Float,c:Int):Float {val clean=if(x.isFinite())x else 0f;if(filters.isEmpty())return clean;var y=clean*headroom;for(f in filters)y=f.next(y,c);return y.coerceIn(-1.0,1.0).toFloat()}','''    private fun raw(x:Float,c:Int):Double {val clean=if(x.isFinite())x else 0f;if(filters.isEmpty())return clean.toDouble();var y=clean*headroom;for(f in filters)y=f.next(y,c);return y}
    fun sample(x:Float,c:Int):Float {val y=raw(x,c);return (if(filters.isEmpty())y else y.coerceIn(-1.0,1.0)).toFloat()}
    private val release=(1-exp(-1.0/(.020*rate))).toFloat()
    private var frameGain=1f
    /** One gain for all channels; preserves stereo ratios during sample-peak overloads. */
    fun frame(samples:FloatArray){
        require(samples.size==channels)
        var peak=0f
        for(c in samples.indices){val v=raw(samples[c],c).toFloat();samples[c]=if(v.isFinite())v else 0f;peak=max(peak,abs(samples[c]))}
        val target=if(peak>1f)1f/peak else 1f
        frameGain=if(target<frameGain)target else min(target,frameGain+(1f-frameGain)*release)
        if(frameGain<1f)for(c in samples.indices)samples[c]*=frameGain
    }''')
p=src/'PlaybackService.kt'
replace(p,'        val d=dsp\n','        val d=dsp;val frameEq=eq?.takeIf{levels.any{it!=0f}}\n')
replace(p,'d.frame(a,b,p); for(c in b.indices) out.putShort(((eq?.sample(b[c],c)?:b[c])*32768).roundToInt().coerceIn(-32768,32767).toShort())','d.frame(a,b,p); frameEq?.frame(b); for(c in b.indices) out.putShort((b[c]*32768).roundToInt().coerceIn(-32768,32767).toShort())')
p=src/'EqRender.kt'
replace(p,'StemCore.header(w,frames);var last=-1','StemCore.header(w,frames);var last=-1;val frame=FloatArray(2)')
replace(p,'for(c in 0..1){val s=StemCore.readShort(r);StemCore.writeShort(w,if(flat)s else StemCore.pcm(eq.sample(s/32768f,c)))}','if(flat){repeat(2){StemCore.writeShort(w,StemCore.readShort(r))}}else{for(c in 0..1)frame[c]=StemCore.readShort(r)/32768f;eq.frame(frame);for(s in frame)StemCore.writeShort(w,StemCore.pcm(s))}')
p=src/'TransitionMix.kt'
replace(p,'fun copy(r:InputStream,n:Long){repeatFrames(n){tick();repeat(2){StemCore.writeShort(w,StemCore.readShort(r))};count++}}','fun copy(r:InputStream,n:Long){count=PcmBlockCopy.copy(r,w,n,count){position->count=position;tick()}}')
p.write_text(p.read_text()+'\n'+'''/** Copy unmodified stereo PCM as bytes, preserving cancellation and progress boundaries. */
internal object PcmBlockCopy {
    fun copy(input:InputStream,output:OutputStream,frames:Long,start:Long,tick:(Long)->Unit):Long {
        require(frames>=0&&start>=0&&frames<=Long.MAX_VALUE-start)
        val buffer=ByteArray(32768);val data=DataInputStream(input);var count=start;val end=start+frames
        while(count<end){check(!Thread.currentThread().isInterrupted){"Отменено"};tick(count);val n=minOf(8192L-count%8192,end-count).toInt();data.readFully(buffer,0,n*4);output.write(buffer,0,n*4);count+=n}
        return count
    }
}
''')
p=root/'tests/EqRenderTest.kt'
replace(p,'    val canceled=File(dir,"cancel.wav");','''    val old=GraphicEq(44100,2,List(10){12f});val next=GraphicEq(44100,2,List(10){12f});val frame=FloatArray(2);var oldErrors=0
    val stereo=File(dir,"eq-overload.pcm");stereo.outputStream().buffered().use{w->
        repeat(44100){i->val x=(.95*sin(2*PI*750*i/44100)).toFloat();val l=old.sample(x,0);val r=old.sample(x*.25f,1);if(abs(l)>=1f&&abs(r-l*.25f)>1e-5)oldErrors++
            frame[0]=x;frame[1]=x*.25f;next.frame(frame);check(abs(frame[1]-frame[0]*.25f)<1e-6);check(frame.all{it.isFinite()&&abs(it)<=1.000001f})
            StemCore.writeShort(w,StemCore.pcm(x));StemCore.writeShort(w,StemCore.pcm(x*.25f))
        }
    };check(oldErrors>0)
    val stereoOut=File(dir,"eq-overload.wav");EqRender.render(stereo,stereoOut,List(10){12f})
    stereoOut.inputStream().buffered().use{r->check(r.skip(44)==44L);repeat(44100){val l=StemCore.readShort(r).toInt();val rr=StemCore.readShort(r).toInt();check(abs(rr-l*.25)<=5.0)}}
    val flatEq=GraphicEq(44100,2,List(10){0f});val rng=kotlin.random.Random(42);repeat(10000){frame[0]=rng.nextFloat()*2-1;frame[1]=rng.nextFloat()*2-1;val before=frame.copyOf();flatEq.frame(frame);check(frame.contentEquals(before))}
    println("PASS: linked EQ peak handling, stereo ratio, real WAV rendering and 10000 exact flat frames; old errors $oldErrors")
    val canceled=File(dir,"cancel.wav");''')
print('PASS: linked equalizer peak protection and bounded PCM block copy')
