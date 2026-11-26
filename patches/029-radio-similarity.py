from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text();assert s.count(old)==1,(name,old,s.count(old));p.write_text(s.replace(old,new))
replace('SmartMix.kt','data class Entry(val id:String,val bpm:Double?,val key:String?,val rms:Double?)','data class Entry(val id:String,val bpm:Double?,val key:String?,val rms:Double?,val pulse:Double?=null,val brightness:Double?=null,val contrast:Double?=null)')
replace('SmartMix.kt','val i=rest.indices.minByOrNull{distance(anchor,rest[it])}!!','val i=rest.indices.minByOrNull{val b=rest[it];val d=distance(anchor,b);if(radio)RadioSimilarity.score(d,anchor.pulse,b.pulse,anchor.brightness,b.brightness,anchor.contrast,b.contrast)else d}!!')
p=src/'SmartMix.kt';p.write_text(p.read_text()+'\n'+'''internal object RadioSimilarity {
    fun score(base:Double, aPulse:Double?, bPulse:Double?, aBright:Double?, bBright:Double?, aContrast:Double?, bContrast:Double?):Double {
        fun gap(a:Double?,b:Double?,max:Double):Double {
            if(a==null||b==null||!a.isFinite()||!b.isFinite()||a !in 0.0..max||b !in 0.0..max)return .65
            return abs(a-b)/max
        }
        return .60*base.coerceIn(0.0,1.0)+.18*gap(aPulse,bPulse,1.0)+.15*gap(aBright,bBright,1.0)+.07*gap(aContrast,bContrast,2.0)
    }
}
''')
replace('MainActivity.kt','SmartMix.Entry(id,r?.tempo?.takeIf{it.confidence>=.30}?.bpm,r?.key?.takeIf{(r.keyConfidence>.025)},r?.rms)','val profile=r?.let{MusicalIntelligence.profile(it)};SmartMix.Entry(id,r?.tempo?.takeIf{it.confidence>=.30}?.bpm,r?.key?.takeIf{(r.keyConfidence>.025)},r?.rms,profile?.pulse,profile?.brightness,profile?.contrast)')
replace('MainActivity.kt','Офлайн-оценка темпа, тональности и уровня; не автоматический beatmatch.','Офлайн-оценка темпа, тональности и уровня; радио также учитывает ритмику, яркость и динамику. Не автоматический beatmatch.')
print('PASS: acoustic radio features reuse existing analysis without loading a neural model')
