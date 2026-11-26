from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text()
    assert s.count(old)==1,(name,old)
    p.write_text(s.replace(old,new))
replace('AudioCore.kt','    private val guard=LinkedPeakGuard(rate)','    private val guard=LinkedPeakGuard(rate)\n    private val orbit=if(channels==2)SpatialOrbit(rate)else null\n    private var orbitHz=.19')
replace('AudioCore.kt',';guard.reset() }',';guard.reset();orbit?.reset();orbitHz=when(p.name){"Slow Stereo Orbit"->.12;"Fast Stereo Orbit"->.32;else->.19} }')
replace('AudioCore.kt','            if(channels==2 && p.pan>0) y *= if(c==0) sqrt((1-sweep).coerceAtLeast(0f))*.75f else sqrt((1+sweep).coerceAtLeast(0f))*.75f\n','')
replace('AudioCore.kt','        if(processed)guard.apply(out)','        if(p.pan>0)orbit?.frame(out,sweep)\n        if(processed)guard.apply(out)')
replace('AudioCore.kt','phase += 2*PI*.19/rate','phase += 2*PI*orbitHz/rate')
p=src/'AudioCore.kt'
p.write_text(p.read_text()+'\n'+'''/** Approximate headphone spatial motion: fractional interaural delay and far-ear
 * high-frequency attenuation. Not an HRTF or personalized binaural renderer. */
internal class SpatialOrbit(private val rate:Int){
    init{require(rate>0)}
    private val left=FloatArray((rate*.00065).toInt()+3)
    private val right=FloatArray(left.size)
    private val shadowAlpha=(1-exp(-2*PI*2200/rate)).toFloat()
    private var cursor=0
    private var shadowL=0f;private var shadowR=0f
    fun reset(){left.fill(0f);right.fill(0f);cursor=0;shadowL=0f;shadowR=0f}
    private fun tap(buffer:FloatArray,delay:Float):Float{
        val whole=delay.toInt();val frac=delay-whole
        val a=(cursor-whole+buffer.size)%buffer.size
        val b=(a+buffer.size-1)%buffer.size
        return buffer[a]+(buffer[b]-buffer[a])*frac
    }
    fun frame(out:FloatArray,position:Float){
        val p=(position.takeIf{it.isFinite()}?:0f).coerceIn(-1f,1f)
        val l=(out[0].takeIf{it.isFinite()}?:0f).coerceIn(-4f,4f)
        val r=(out[1].takeIf{it.isFinite()}?:0f).coerceIn(-4f,4f)
        left[cursor]=l;right[cursor]=r
        val farL=max(0f,p);val farR=max(0f,-p)
        val delayedL=tap(left,farL*rate*.0006f);val delayedR=tap(right,farR*rate*.0006f)
        shadowL+=shadowAlpha*(delayedL-shadowL);shadowR+=shadowAlpha*(delayedR-shadowR)
        val mixL=farL*.65f;val mixR=farR*.65f
        val spatialL=delayedL+(shadowL-delayedL)*mixL
        val spatialR=delayedR+(shadowR-delayedR)*mixR
        out[0]=(l+(spatialL-l)*farL*.85f)*(1f-.48f*farL)
        out[1]=(r+(spatialR-r)*farR*.85f)*(1f-.48f*farR)
        cursor=(cursor+1)%left.size
    }
}
''')
replace('EffectCheckpoint.kt','dsp-peak-guard-v60','dsp-spatial-orbit-v67')
# Reject oversized or malformed translations before persistent storage, while keeping
# the existing original/translation line alignment and offline model workflow.
replace('MainActivity.kt','val result=runCatching{LyricTranslation.translate(Lrc.parse(raw).map{WordLyrics.parse(it).text},source,target,download)}','val result=runCatching{LyricTranslation.translate(Lrc.parse(raw).map{WordLyrics.parse(it).text},source,target,download).also{require(PortableSettings.validateTranslation(raw,it)){"Некорректный перевод"}}}')
replace('MainActivity.kt','translated(t,raw).takeIf{it.size==activeLyrics.size}.orEmpty()','translated(t,raw).takeIf{PortableSettings.validateTranslation(raw,it)}.orEmpty()')
print('PASS: spatial orbit, effect cache version and translation validation overlay')
