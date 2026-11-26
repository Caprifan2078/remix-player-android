package app.remix.player
import kotlin.math.*
fun main(){
 val baseline=MusicAnalysis.Report(Tempo.Result(145.0,.8),.1,"C major",.2,.15,32.0,List(8){.15},spectrum=SoundProfile.Features(.8,.15,.05,230.0,64))
 check(RemixAdvisor.recommend(baseline.copy(tempo=Tempo.Result(145.0,.15))).isEmpty()){"Low confidence should not produce recommendations"}
 check(RemixAdvisor.recommend(baseline.copy(rms=0.0)).isEmpty())
 check(RemixAdvisor.recommend(baseline.copy(tempo=null),145.0).size==5)
 check(RemixAdvisor.recommend(baseline,Double.NaN).isEmpty())
 val hard=setOf("Hardstyle","Rawstyle","Jumpstyle","Hardcore","Frenchcore","Hardtekk","Hard Techno","Hypertechno")
 val phonk=setOf("Drift Phonk","Brazilian Phonk","House Phonk","Memphis Phonk","Montagem","Krushfunk","Automotivo","Brazilian Funk")
 var count=0
 for(bpm in 50..220){val report=baseline.copy(tempo=Tempo.Result(bpm.toDouble(),.9));for(goal in RemixAdvisor.Goal.values()){
   val picks=RemixAdvisor.recommend(report,goal=goal)
   check(picks.size==5&&picks.map{it.style.name}.distinct().size==5)
   check(picks.count{it.style.name in hard}<=2&&picks.count{it.style.name in phonk}<=2)
   check(picks.all{it.score.isFinite()&&it.speed in .75..1.33&&it.effectiveBpm.isFinite()&&it.reasons.isNotEmpty()})
   check(picks==RemixAdvisor.recommend(report,goal=goal))
   count++
 }}
 val soft=RemixAdvisor.recommend(baseline,goal=RemixAdvisor.Goal.SOFT);val hardP=RemixAdvisor.recommend(baseline,goal=RemixAdvisor.Goal.ENERGETIC)
 check(soft.map{it.style.drive}.average()<hardP.map{it.style.drive}.average())
 val dry=baseline.copy(spectrum=SoundProfile.Features(.1,.8,.1,1000.0,64));val a=RemixAdvisor.recommend(baseline);val b=RemixAdvisor.recommend(dry)
 println("Bass-heavy: ${a.map{it.style.name}}; less bass: ${b.map{it.style.name}}")
 check(a.map{it.style.name}!=b.map{it.style.name}||a.zip(b).any{(x,y)->x.score!=y.score})
 check(a.any{it.reasons.any{reason->reason.contains("баса")}})
 val moving=baseline.copy(tempoWindows=listOf(RhythmMap.Window(0.0,16.0,120.0,.9),RhythmMap.Window(16.0,32.0,145.0,.9)))
 check(RemixAdvisor.recommend(moving).all{it.reasons.any{reason->reason.contains("меняется")}})
 check(ProducerStyles.all.size==40&&ProducerStyles.all.map{it.name}.distinct().size==40)
 val normal=RemixAdvisor.recommend(baseline)
 check(RemixAdvisor.recommend(baseline,neuralArousal=Double.NaN)==normal)
 check(RemixAdvisor.recommend(baseline,neuralArousal=-.1)==normal)
 check(RemixAdvisor.recommend(baseline,neuralArousal=1.1)==normal)
 val neuralLow=RemixAdvisor.recommend(baseline,neuralArousal=.05)
 val neuralHigh=RemixAdvisor.recommend(baseline,neuralArousal=.95)
 check(neuralLow.all{it.reasons.any{r->r.contains("нейросетевая")}})
 check(neuralHigh.all{it.reasons.any{r->r.contains("нейросетевая")}})
 check(neuralLow!=neuralHigh)
 check(RemixAdvisor.recommend(baseline,goal=RemixAdvisor.Goal.SOFT,neuralArousal=.95)==soft)
 check(RemixAdvisor.recommend(baseline,goal=RemixAdvisor.Goal.ENERGETIC,neuralArousal=.05)==hardP)
 println("PASS: nine optional neural score, style catalogue and explicit goal checks")
 println("PASS: $count BPM/goal combinations; confidence gate, manual override, silence, diversity, acoustic score, explanations and deterministic recommendations")
}
