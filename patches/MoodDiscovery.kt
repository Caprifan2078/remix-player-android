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
  val weight=if(p.valence==null).92 else 1.0
  return (1-distance/weight).coerceIn(0.0,1.0).takeIf{it>=.69}
 }
 data class Entry(val id:String,val artist:String,val features:Features)
 fun rank(entries:List<Entry>,profile:Profile,limit:Int=100):List<String>{
  require(limit in 1..1000)
  check(!Thread.currentThread().isInterrupted){"Cancelled"}
  val sorted=entries.asSequence().filter{it.id.isNotBlank()}.distinctBy{it.id}.mapNotNull{e->
   check(!Thread.currentThread().isInterrupted){"Cancelled"};score(e.features,profile)?.let{e to it}
  }.sortedWith(compareByDescending<Pair<Entry,Double>>{it.second}.thenBy{it.first.id}).toMutableList()
  val out=mutableListOf<String>();var last=""
  while(sorted.isNotEmpty()&&out.size<limit){
   check(!Thread.currentThread().isInterrupted){"Cancelled"}
   val best=sorted.first().second
   val i=if(last.isBlank())0 else sorted.indexOfFirst{it.second>=best-.055&&it.first.artist.isNotBlank()&&!it.first.artist.trim().equals(last,true)}.takeIf{it>=0}?:0
   val item=sorted.removeAt(i).first;out.add(item.id);last=item.artist.trim()
  }
  return out
 }

 /** Controlled vocabulary, not an LLM. Unknown descriptions are never silently mapped. */
 fun describe(raw:String):Profile? {
  if(raw.length>160)return null
  val tokens=Regex("[\\p{L}]+").findAll(raw.lowercase(java.util.Locale.ROOT).replace('ё','е')).map{it.value}.toList()
  if(tokens.any{it in setOf("не","без","кроме","not","without","no")})return null
  fun has(vararg stems:String)=tokens.any{t->stems.any{t.startsWith(it)}}
  val choices=listOf(
   has("груст","печаль","меланхол","sad") to 0,
   has("спокой","расслаб","тих","calm","relax") to 1,
   has("энерг","быстр","бодр","energy","fast") to 2,
   has("трениров","спорт","gym","workout") to 3,
   has("темн","мрач","dark") to 4,
   has("сосредоточ","фокус","учеб","focus") to 5,
   has("весел","радост","светл","happy") to 6,
   has("атмосфер","dream","ambient") to 7
  ).filter{it.first}.map{profiles[it.second]}
  if(choices.size>1)return null
  val bass=has("бас","bass")
  if(choices.isEmpty()&&!bass)return null
  val p=choices.firstOrNull()?:profiles[2].copy(title="Выраженный бас",detail="Акустический профиль с усиленным низом",energy=.55,activity=.5)
  return if(bass)p.copy(low=.85)else p
 }
 /** Build a finite playlist from intermediate acoustic targets, skipping empty stages. */
 fun journey(entries:List<Entry>,from:Profile,to:Profile,limit:Int=30):List<String>{
  require(limit in 1..100)
  val pool=entries.filter{it.id.isNotBlank()}.distinctBy{it.id}.toMutableList()
  val out=mutableListOf<String>()
  var lastArtist=""
  fun lerp(a:Double,b:Double,t:Double)=a+(b-a)*t
  val count=minOf(limit,pool.size)
  for(i in 0 until count){
   check(!Thread.currentThread().isInterrupted){"Cancelled"}
   val t=if(count==1)0.5 else i.toDouble()/(count-1)
   val v=when{
    t==0.0->from.valence
    t==1.0->to.valence
    from.valence!=null&&to.valence!=null->lerp(from.valence,to.valence,t)
    else->null
   }
   val p=Profile("","",lerp(from.energy,to.energy,t),lerp(from.activity,to.activity,t),lerp(from.brightness,to.brightness,t),lerp(from.low,to.low,t),v,lerp(from.dynamics,to.dynamics,t))
   var best:Entry?=null;var bestScore=-1.0
   var other:Entry?=null;var otherScore=-1.0
   for(e in pool){
    val value=score(e.features,p)?:continue
    if(value>bestScore||(value==bestScore&&e.id<(best?.id?:""))){best=e;bestScore=value}
    if(e.artist.isNotBlank()&&!e.artist.trim().equals(lastArtist,true)&&(value>otherScore||(value==otherScore&&e.id<(other?.id?:"")))){other=e;otherScore=value}
   }
   val pick=(if(otherScore>=bestScore-.035)other else best)?:best?:continue
   out.add(pick.id);lastArtist=pick.artist.trim();pool.remove(pick)
  }
  return out
 }
}
