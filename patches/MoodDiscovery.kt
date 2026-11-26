package app.remix.player
import kotlin.math.abs
import kotlin.math.sqrt
/** Acoustic estimate, not a prediction of listener emotions. Scores are not probabilities. */
object MoodDiscovery {
 data class Features(val energy:Double,val activity:Double,val brightness:Double,val low:Double,val valence:Double?,val dynamics:Double){
  init{require(listOf(energy,activity,brightness,low,dynamics).all{it.isFinite()&&it in 0.0..1.0});require(valence==null||valence.isFinite()&&valence in 0.0..1.0)}
 }
 data class Profile(val title:String,val detail:String,val energy:Double,val activity:Double,val brightness:Double,val low:Double,val valence:Double?,val dynamics:Double)
 val profiles=listOf(
 Profile("Меланхолия","Мягкое звучание, мало ритмической активности, минорная окраска",.23,.20,.30,.35,.18,.40),
 Profile("Спокойствие","Невысокая энергия, ровное и мягкое звучание",.22,.16,.30,.35,null,.24),
 Profile("Энергия","Быстрый пульс и активное звучание",.80,.85,.56,.52,null,.45),
 Profile("Тренировка","Плотный ритм, выраженная энергия и низ",.87,.88,.50,.72,null,.30),
 Profile("Тёмный драйв","Плотный низ, высокая энергия, минорная окраска",.83,.74,.40,.82,.20,.48),
 Profile("Сосредоточиться","Ровная динамика, умеренная энергия, мягкие высокие частоты",.36,.30,.30,.35,null,.13),
 Profile("Светлое настроение","Яркое активное звучание и мажорная окраска",.63,.62,.65,.35,.82,.42),
 Profile("Атмосфера","Мягкое звучание с контрастными музыкальными фрагментами",.39,.28,.40,.40,null,.72))
 fun from(r:MusicAnalysis.Report):Features? {
  val spec=r.spectrum?:return null
  if(!r.duration.isFinite()||r.duration<8||!r.rms.isFinite()||r.rms<.006||spec.frames<6)return null
  val e=r.energy.filter{it.isFinite()&&it>=0}.sorted();if(e.size<2)return null
  val mid=e[e.size/2];val peak=e[(e.size*9/10).coerceAtMost(e.lastIndex)]
  val dynamics=if(peak>.005)(1-mid/peak).coerceIn(0.0,1.0)else 0.0
  val pulse=r.featureFrames.map{it.onset}.filter{it.isFinite()}.takeIf{it.isNotEmpty()}?.average()?:return null
  val tempo=r.tempo?.takeIf{it.bpm.isFinite()&&it.confidence>=.40}
  val activity=if(tempo!=null).6*pulse.coerceIn(0.0,1.0)+.4*((tempo.bpm-65)/110).coerceIn(0.0,1.0)else pulse.coerceIn(0.0,1.0)
  val valence=if(r.keyConfidence>=.06)when{r.key?.endsWith(" minor")==true->.20;r.key?.endsWith(" major")==true->.80;else->null}else null
  if(!spec.high.isFinite()||!spec.low.isFinite())return null
  return Features((sqrt(r.rms.coerceIn(0.0,1.0))/.58).coerceIn(0.0,1.0),activity,(spec.high*2).coerceIn(0.0,1.0),spec.low.coerceIn(0.0,1.0),valence,dynamics)
 }
 fun score(f:Features,p:Profile):Double?{
  if(p.valence!=null&&f.valence==null)return null
  if(p.valence!=null&&abs(f.valence!!-p.valence)>.45)return null
  val distance=abs(f.energy-p.energy)*.32+abs(f.activity-p.activity)*.26+abs(f.brightness-p.brightness)*.12+abs(f.low-p.low)*.10+abs(f.dynamics-p.dynamics)*.12+(if(p.valence!=null)abs(f.valence!!-p.valence)*.08 else 0.0)
  return (1-distance).takeIf{it>=.69}
 }
 data class Entry(val id:String,val artist:String,val features:Features)
 fun rank(entries:List<Entry>,profile:Profile,limit:Int=100):List<String>{
  require(limit in 1..1000)
  val sorted=entries.distinctBy{it.id}.mapNotNull{e->score(e.features,profile)?.let{e to it}}.sortedWith(compareByDescending<Pair<Entry,Double>>{it.second}.thenBy{it.first.id}).toMutableList()
  val out=mutableListOf<String>();var last=""
  while(sorted.isNotEmpty()&&out.size<limit){
   val best=sorted.first().second
   val i=if(last.isBlank())0 else sorted.indexOfFirst{it.second>=best-.055&&it.first.artist.isNotBlank()&&!it.first.artist.equals(last,true)}.takeIf{it>=0}?:0
   val item=sorted.removeAt(i).first;out.add(item.id);last=item.artist
  }
  return out
 }
}
