from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'LiveOverlap.kt'
s=p.read_text()
def replace(old,new,count=1):
    global s
    assert s.count(old)==count,(old,s.count(old))
    s=s.replace(old,new)
replace('private var startedAt=0L;', 'private val decoderStall=OverlapStall();')
replace('startedAt=0L;', 'decoderStall.reset();')
replace('startedAt=now;', 'decoderStall.reset();')
replace('now-startedAt>1200', 'decoderStall.expired(now)',2)
replace('        if(OverlapCore.drift(elapsed,p.currentPosition)&&elapsed>400){','        decoderStall.reset()\n        if(OverlapCore.drift(elapsed,p.currentPosition)&&elapsed>400){')
p.write_text(s)
(src/'OverlapStall.kt').write_text('''package app.remix.player
/** Measure consecutive decoder stalls, not time since the overlap began. */
internal class OverlapStall(private val timeoutMs: Long = 1200L) {
    private var since: Long? = null
    fun expired(now: Long): Boolean {
        val start = since ?: now.also { since = it }
        return now - start >= timeoutMs
    }
    fun reset() { since = null }
}
''')
print('PASS: consecutive decoder stall timing overlay')
