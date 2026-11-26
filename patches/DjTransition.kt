package app.remix.player
import java.io.*
import kotlin.math.*
/** Optional offline beat and key matching, not live crossfade. */
object DjTransition {
    private const val RATE=44100L
    data class Window(val start:Long,val report:MusicAnalysis.Report)
    data class Result(val frames:Long,val overlap:Long,val notes:List<String>)
    private fun tempo(w:Window?)=w?.report?.tempo?.takeIf{it.bpm.isFinite()&&it.bpm in 65.0..190.0&&it.confidence>=.4&&!RhythmMap.unstable(w.report.tempoWindows,it.bpm)}
    fun plan(a:Window?,b:Window?,key:Boolean):BackingFit.Plan {
        val x=tempo(a);val y=tempo(b);val original=BackingFit.plan(a?.report,b?.report,BackingFit.Options(tempo=x!=null&&y!=null,key=key,phase=false))
        val speed=original.speed.takeIf{it in .92..1.08}?:1.0
        val shift=original.semitones.takeIf{abs(it)<=2}?:0
        return BackingFit.Plan(speed,shift,0,listOf("Скорость второй песни: ${"%.3f".format(java.util.Locale.ROOT,speed)}×","Тональность: $shift полутонов", "При слабом анализе или большом различии параметры сохраняются"))
    }
    fun analyze(raw:File,tail:Boolean):Window {
        require(raw.isFile&&raw.length()>0&&raw.length()%4==0L)
        val frames=raw.length()/4;val count=minOf(frames,32*RATE);val start=if(tail)frames-count else 0L
        val analyzer=MusicAnalysis.Analyzer(RATE.toInt());val mono=AnalysisMono{analyzer.sample(it)}
        raw.inputStream().buffered(65536).use{r->var remaining=start*4;while(remaining>0){val n=r.skip(remaining);if(n<=0)throw EOFException();remaining-=n}
            for(i in 0 until count){if(i%8192==0L)check(!Thread.currentThread().isInterrupted){"Отменено"};mono.frame(StemCore.readShort(r)/32768.0,StemCore.readShort(r)/32768.0)}
        };mono.finish();return Window(start,analyzer.finish())
    }
    /** Move the overlap by at most half a beat, never trim the incoming intro. */
    fun overlapFrames(first:Long,second:Long,seconds:Int,a:Window?,b:Window?):Long {
        require(first>0&&second>0&&seconds in 1..10)
        val cap=minOf(10*RATE,first/2,second/2);val desired=minOf(seconds*RATE,cap);require(desired>=2)
        val x=tempo(a)?:return desired;val y=tempo(b)?:return desired
        if(abs(x.bpm/y.bpm-1)>.005)return desired
        val ap=a!!.report.phaseSeconds?.takeIf{it.isFinite()&&it>=0&&it<60/x.bpm}?:return desired
        val bp=b!!.report.phaseSeconds?.takeIf{it.isFinite()&&it>=0&&it<60/y.bpm}?:return desired
        val period=60*RATE/x.bpm;val reference=first-a.start-ap*RATE+b.start+bp*RATE
        val candidate=(reference-round((reference-desired)/period)*period).roundToLong()
        return if(candidate in RATE..cap&&abs(candidate-desired)<=period/2+1)candidate else desired
    }
    fun render(first:File,second:File,out:File,seconds:Int,key:Boolean,progress:(String)->Unit={}):Result {
        require(first.isFile&&second.isFile&&first.length()%4==0L&&second.length()%4==0L&&out.canonicalFile!=first.canonicalFile&&out.canonicalFile!=second.canonicalFile)
        var fitted:File?=null
        try {
            progress("Анализ конца первой песни…");val a=analyze(first,true)
            progress("Анализ начала второй песни…");val b=analyze(second,false)
            val plan=plan(a,b,key);val notes=plan.notes.toMutableList()
            val prepared=if(plan.changed){val tmp=File.createTempFile("dj-fit-",".pcm",out.absoluteFile.parentFile);fitted=tmp;BackingFit.prepare(second,tmp,plan){progress("Подгонка второй песни: $it%")}}else second
            val measured=if(plan.changed){progress("Проверка долей после подгонки…");analyze(prepared,false)}else b
            val n=overlapFrames(first.length()/4,prepared.length()/4,seconds,a,measured)
            val default=minOf(seconds*RATE,first.length()/8,prepared.length()/8)
            notes.add(if(n!=default)"Доли: длина наложения скорректирована на ${((n-default)*1000.0/RATE).roundToLong()} мс" else "Доли: исходная длина наложения сохранена")
            notes.add("Уровень: плавная коррекция разницы RMS до 6 дБ при достаточном сигнале")
            return Result(TransitionMix.renderFrames(first,prepared,out,n,levelMatch=true){progress("Сведение: $it%")},n,notes)
        }finally{fitted?.delete()}
    }
}
