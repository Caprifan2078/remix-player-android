from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text()
    assert s.count(old)==1,(name,old)
    p.write_text(s.replace(old,new))
replace('GenreEngine.kt','private val kicks=DoubleArray(ceil(.36*rate).toInt())','private val kicks=if(GenreKick.supported(style.name))GenreKick.voice(style.name,rate,palette.kickHz.toDouble())else DoubleArray(ceil(.36*rate).toInt())')
p=src/'GenreEngine.kt'
p.write_text(p.read_text()+'\n'+'''/** Deterministic, band-limited additive kick voices; no third-party samples. */
internal object GenreKick {
    fun supported(name:String)=name in setOf("Hardstyle","Rawstyle","Hardcore","Drift Phonk","Brazilian Phonk","Memphis Phonk","House Phonk","Montagem","Krushfunk","Automotivo")
    fun voice(name:String,rate:Int,base:Double):DoubleArray {
        require(supported(name)&&rate>=8000&&base.isFinite()&&base>0)
        val hard=name in setOf("Hardstyle","Rawstyle","Hardcore")
        val raw=name=="Rawstyle"||name=="Krushfunk"
        val hz=base.coerceIn(38.0,68.0)
        val n=ceil(.36*rate).toInt()
        return DoubleArray(n){i->
            val t=i.toDouble()/rate
            val sweep=if(hard) 125.0 else 85.0
            val tau=if(hard) .018 else .012
            val phase=2*PI*(hz*t+sweep*tau*(1-exp(-t/tau)))
            val instant=hz+sweep*exp(-t/tau)
            val body=exp(-t/(if(hard) .19 else .115))
            val harmonics=if(hard) doubleArrayOf(1.0,.38,.27,.14,.09) else doubleArrayOf(1.0,.24,.13,.05)
            var sum=0.0;var weight=0.0
            for(h in harmonics.indices){if(instant*(h+1)>=rate*.42)break;val a=harmonics[h]*(if(raw&&h>0)1.35 else 1.0);sum+=a*sin(phase*(h+1));weight+=a}
            val punch=sin(2*PI*(hz*t+3.2*(1-exp(-t/.009))))*exp(-t/.018)
            val edge=minOf(1.0,t/.002,(.36-t)/.016).coerceAtLeast(0.0)
            (.47*body*sum/max(1.0,weight)+.12*punch)*edge
        }
    }
}
''')
# Share the same synthesized voice with the neural backing generator for selected genres.
replace('NeuralDrums.kt','private val kick=wave(.15){','private val kick=genre?.takeIf{GenreKick.supported(it.name)}?.let{g->GenreKick.voice(g.name,44100,DrumPalette.voice(g).kickHz.toDouble()).map{(it*.65).toFloat()}.toFloatArray()}?:wave(.15){')
replace('GenreCheckpoint.kt','genre-render-v7','genre-render-v8')
print('PASS: differentiated kick voice integration')
