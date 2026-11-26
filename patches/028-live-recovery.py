from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'LiveOverlap.kt';s=p.read_text()
def replace(a,b,count=1):
    global s
    assert s.count(a)==count,(a,s.count(a))
    s=s.replace(a,b)
replace('private val decoderStall=OverlapStall();','private val decoderStall=OverlapStall();private val decoderRecovery=OverlapRecovery();')
replace('fadeWindow=null;decoderStall.reset();','fadeWindow=null;decoderStall.reset();decoderRecovery.reset();')
replace('started=true;decoderStall.reset();','started=true;decoderStall.reset();decoderRecovery.reset();')
replace('main.volume=1f;p.volume=0f;if(decoderStall.expired(now))','decoderRecovery.stall();main.volume=1f;p.volume=0f;if(decoderStall.expired(now))',2)
replace('val g=OverlapCore.gains(audible,w.duration);main.volume=g.outgoing;p.volume=g.incoming','val g=OverlapCore.gains(audible,w.duration);val ramp=decoderRecovery.fraction(now);main.volume=1f+(g.outgoing-1f)*ramp;p.volume=g.incoming*ramp')
p.write_text(s)
p=src/'OverlapStall.kt'
p.write_text(p.read_text()+'\n'+'''internal class OverlapRecovery(private val rampMs:Long=120L){
    init{require(rampMs>0)}
    private var waiting=false
    private var since:Long?=null
    fun stall(){waiting=true;since=null}
    fun reset(){waiting=false;since=null}
    fun fraction(now:Long):Float{
        if(!waiting)return 1f
        val start=since?:now.also{since=it}
        val f=((now-start).coerceAtLeast(0).toDouble()/rampMs).coerceIn(0.0,1.0).toFloat()
        if(f>=1f)reset()
        return f
    }
}
''')
print('PASS: live overlap recovery uses a bounded 120ms gain ramp')
