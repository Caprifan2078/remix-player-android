package app.remix.player

import kotlin.math.*

/** Conservative bass pitch-class estimate from Basic Pitch note probabilities.
 * A dominant detected pitch is not a musical key or a complete melody transcription. */
object BasicPitchHint {
    const val SAMPLES=43844
    const val FRAMES=172
    const val NOTES=88
    const val RATE=22050
    const val SHA="2c3c1d144bfa61ad236e92e169c13535c880469a12a047d4e73451f2c059a0ec"
    const val BYTES=230444
    fun window(notes:FloatArray):Int?{
        require(notes.size==FRAMES*NOTES&&notes.all{it.isFinite()&&it in 0f..1f})
        val scores=DoubleArray(12);var frames=0
        for(t in 15 until FRAMES-15){
            var best=-1;var top=0f;var second=0f
            for(n in 0..38){
                val p=notes[t*NOTES+n]
                if(p>top){second=top;top=p;best=n}else if(p>second)second=p
            }
            if(best>=0&&top>=.55f&&top-second>=.12f){scores[(best+21)%12]+=top;frames++}
        }
        if(frames<12)return null
        val sorted=scores.indices.sortedByDescending{scores[it]};val total=scores.sum()
        val a=scores[sorted[0]]/total;val b=scores[sorted[1]]/total
        return sorted[0].takeIf{a>=.55&&a-b>=.15}
    }
    fun consensus(windows:List<Int?>):Int?{
        require(windows.size in 1..3&&windows.all{it==null||it in 0..11})
        return windows.filterNotNull().groupingBy{it}.eachCount().entries.singleOrNull{it.value>=2}?.key
    }
    fun frequencyNear(pitchClass:Int,base:Double):Double?{
        require(pitchClass in 0..11)
        if(!base.isFinite()||base !in 40.0..75.0)return null
        return (21..60).filter{it%12==pitchClass}.map{440.0*2.0.pow((it-69)/12.0)}
            .filter{it in 40.0..75.0&&abs(ln(it/base))<=ln(1.26)}
            .minByOrNull{abs(ln(it/base))}
    }
}
