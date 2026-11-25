from pathlib import Path
import sys
root=Path(sys.argv[1]); src=root if (root/'GenreEngine.kt').exists() else root/'app/src/main/java/app/remix/player'
def replace(file,old,new):
 p=src/file;s=p.read_text();assert s.count(old)==1,(file,old);p.write_text(s.replace(old,new))
p=src/'GenreDynamics.kt'
p.write_text(p.read_text()+'''
/** Linked, frequency-selective sidechain: free room for generated kicks without
 * pumping the entire source mix. Two smoothed low-pass stages; O(1) memory. */
class SourceLowEnd(rate:Int=44100){
    init{require(rate in 8000..192000)}
    private val a=(1-exp(-2.0*PI*180/rate)).toFloat()
    private var l1=0f;private var l2=0f;private var r1=0f;private var r2=0f
    var left=0f;private set
    var right=0f;private set
    fun frame(l:Float,r:Float,kickGain:Float){
        l1+=a*(l-l1);l2+=a*(l1-l2);r1+=a*(r-r1);r2+=a*(r1-r2)
        val amount=1f-kickGain.coerceIn(0f,1f)
        left=l-amount*l2;right=r-amount*r2
    }
}
''')
replace('GenreEngine.kt','sourceDrumScale:Float,controls:GenreMix):Float','sourceDrumScale:Float,controls:GenreMix,sourceBassGain:Float=1f):Float')
replace('GenreEngine.kt','samples[1]/32768f*style.bass*controls.source','samples[1]/32768f*style.bass*controls.source*sourceBassGain')
replace('GenreEngine.kt','levels.sourceDrums,controls),sum(right,beat*(.75f+.25f*duck),style,newBass*duck,levels.sourceDrums,controls)','levels.sourceDrums,controls,kickGain),sum(right,beat*(.75f+.25f*duck),style,newBass*duck,levels.sourceDrums,controls,kickGain)')
replace('GenreEngine.kt','val kickSpace=KickSpace()\n        try','val kickSpace=KickSpace();val sourceLow=SourceLowEnd()\n        try')
replace('GenreEngine.kt','val l=StemCore.readShort(r)/32768f*.72f*controls.source+b;val rr=StemCore.readShort(r)/32768f*.72f*controls.source+b;dynamics.frame(l,rr);','val l=StemCore.readShort(r)/32768f*.72f*controls.source;val rr=StemCore.readShort(r)/32768f*.72f*controls.source;sourceLow.frame(l,rr,kickGain);dynamics.frame(sourceLow.left+b,sourceLow.right+b);')
replace('LeadSynth.kt','    private val enabled=','''    // Genre-dependent additive timbres; harmonic amplitudes normalized below.
    private val color=when(style.name){
        "Hardstyle","Rawstyle","Hardcore","Frenchcore","Hardtekk","Hard Techno"->doubleArrayOf(1.0,.64,.47,.26,.19)
        "Drift Phonk","Brazilian Phonk","Montagem","Krushfunk","Automotivo","Memphis Phonk","House Phonk"->doubleArrayOf(.52,1.0,.0,.48,.16)
        "Brazilian Funk","Jersey Club"->doubleArrayOf(1.0,.12,.68,.0,.12)
        "UK Garage","Speed Garage"->doubleArrayOf(1.0,.44,.04,.16,.05)
        "Synthwave","Hypertechno","Hyperflip"->doubleArrayOf(1.0,.28,.35,.15,.23)
        "Amapiano","Afro House"->doubleArrayOf(1.0,.08,.19,.03,.0)
        "Dubstep","Trap"->doubleArrayOf(.78,.7,.1,.56,.23)
        else->doubleArrayOf(1.0,.25,.10,.02,.0)
    }
    private fun tone():Double{
        var sum=0.0;var weights=0.0
        for(i in color.indices){val harmonic=i+1;if(freq*harmonic>=rate*.45)break;val amp=color[i];if(amp==0.0)continue;sum+=amp*sin(oscillator*harmonic);weights+=amp}
        return if(weights>0)sum/weights else 0.0
    }
    private val enabled=''')
replace('LeadSynth.kt','((sin(oscillator)+style.drive*.23*sin(oscillator*3))*gain*.065).toFloat()','(tone()*gain*.075).toFloat()')
if (src/'GenreCheckpoint.kt').exists():replace('GenreCheckpoint.kt','genre-render-v6','genre-render-v7')
if (src/'MainActivity.kt').exists():replace('MainActivity.kt','30 шаблонов · новая аранжировка','30 шаблонов · умное сведение баса и разные тембры')
print('PASS studio upgrade overlay applied')
