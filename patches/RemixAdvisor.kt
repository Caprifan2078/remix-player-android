package app.remix.player
import kotlin.math.*

/** Transparent acoustic heuristics, not a trained genre classifier or taste prediction. */
object RemixAdvisor {
    data class Repetition(val first:Double,val second:Double,val duration:Double,val similarity:Double)
    enum class Goal { ORIGINAL, ENERGETIC, SOFT }
    data class Suggestion(val style:GenreEngine.Style,val score:Double,val speed:Double=1.0,val effectiveBpm:Double=style.target.toDouble(),val reasons:List<String> = emptyList())
    private fun family(style:GenreEngine.Style):String=when(ProducerStyles.family(style)){
        "Hardstyle","Rawstyle","Jumpstyle","Hardcore","Frenchcore","Hardtekk","Hard Techno","Hypertechno"->"hard"
        "Drift Phonk","Brazilian Phonk","House Phonk","Memphis Phonk","Montagem","Krushfunk","Automotivo","Brazilian Funk"->"phonk-funk"
        "House","Slap House","Afro House","Amapiano"->"house"
        "UK Garage","Speed Garage","Jersey Club","Hyperflip","Breakcore","Drum & Bass"->"breaks"
        "Trap","Dubstep"->"bass"
        else->style.name
    }
    fun recommend(report:MusicAnalysis.Report,manualBpm:Double?=null,goal:Goal=Goal.ORIGINAL,neuralArousal:Double?=null):List<Suggestion>{
        if(!report.duration.isFinite()||report.duration<=0||!report.rms.isFinite()||report.rms<.001)return emptyList()
        val bpm=(manualBpm?:report.tempo?.takeIf{it.confidence.isFinite()&&it.confidence>=.30}?.bpm)?.takeIf{it.isFinite()&&it in 50.0..220.0}?:return emptyList()
        val profile=MusicalIntelligence.profile(report)
        val bass=report.spectrum?.takeIf{it.frames>=4&&it.low.isFinite()&&it.low in 0.0..1.0}?.low
        val dynamic=profile.contrast?.takeIf{it.isFinite()}
        val unstable=RhythmMap.unstable(report.tempoWindows.filter{it.bpm.isFinite()&&it.bpm in 50.0..220.0},bpm)
        val measuredDrive=when(goal){Goal.ENERGETIC->.85;Goal.SOFT->.08;Goal.ORIGINAL->profile.pulse?.let{(.10+.85*it).coerceIn(.1,.8)}?:.35}
        val neural=neuralArousal?.takeIf{it.isFinite()&&it in 0.0..1.0&&goal==Goal.ORIGINAL}
        val targetDrive=neural?.let{measuredDrive*.65+(.10+.75*it)*.35}?:measuredDrive
        val speedWeight=(if(goal==Goal.ORIGINAL)1.5 else .7)+(if(unstable).7 else 0.0)
        val remaining=ProducerStyles.all.map{style->val plan=TimeStretch.plan(bpm,style.target)
            val stretch=abs(ln(plan.speed));val miss=abs(ln(plan.effectiveBpm/style.target));val drive=abs(style.drive-targetDrive)
            // In bass-heavy source mixes favor less low-end reinforcement. On dynamic originals avoid excessive drive.
            val bassPenalty=(bass?.let{max(0.0,(it-.40)/.60)}?:0.0)*max(0.0,(style.bass-1.0).toDouble())*(if(goal==Goal.ENERGETIC).45 else 1.1)
            val contrastPenalty=if(goal==Goal.ORIGINAL) (dynamic?.coerceIn(0.0,1.0)?:0.0)*style.drive*.20 else 0.0
            val score=-speedWeight*stretch-2.5*miss-(if(goal==Goal.ORIGINAL).35 else 1.0)*drive-bassPenalty-contrastPenalty
            val reasons=buildList{
                if(manualBpm!=null)add("Ручной BPM")
                if(neural!=null)add("Учтена нейросетевая оценка энергии")
                if(abs(plan.speed-1)<.015)add("Почти без изменения темпа") else add("Изменение скорости ${"%.2f".format(java.util.Locale.ROOT,plan.speed)}×")
                if(miss>.015)add("Достижимый темп отличается от цели")
                add(when{style.drive>=.65->"Жёсткий тембр";style.drive<=.2->"Мягкий тембр";else->"Умеренный тембр"})
                if(bass!=null&&bass>.60&&style.bass<=1.1f)add("Меньше усиления баса при насыщенных низких частотах")
                if(unstable)add("Темп меняется внутри песни")
            }
            Suggestion(style,score,plan.speed,plan.effectiveBpm,reasons)
        }.sortedByDescending{it.score}.toMutableList()
        // Retain the highest-scoring choice and diversify the rest without repeating one family five times.
        val chosen=mutableListOf<Suggestion>();val counts=mutableMapOf<String,Int>()
        while(chosen.size<5&&remaining.isNotEmpty()){
            val eligible=remaining.filter{(counts[family(it.style)]?:0)<2}.ifEmpty{remaining}
            val next=eligible.maxByOrNull{it.score-.18*(counts[family(it.style)]?:0)}!!
            chosen.add(next);remaining.remove(next);val f=family(next.style);counts[f]=(counts[f]?:0)+1
        }
        return chosen
    }
    fun repetitions(report:MusicAnalysis.Report):List<Repetition> = StructureCore.repetitions(report)
    fun energyLabel(report:MusicAnalysis.Report):String {val e=report.energy.filter{it.isFinite()&&it>=0};if(e.isEmpty())return "Недостаточно данных";val avg=e.average();return when{avg<.015->"Тихий сигнал";e.maxOrNull()!!>avg*1.6->"Контрастная динамика";else->"Ровная динамика"}}
}
