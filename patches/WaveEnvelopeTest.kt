package app.remix.player
fun main(){
    val rate=8000;val duration=2400000L
    fun make(silence:Boolean=false,skip:Int=-1):FloatArray?{
        val e=WaveEnvelope(duration,24)
        repeat(19200){i->val b=i/800;if(b!=skip)e.frame(i*1000000L/rate,if(silence)0f else if(b<12)-.25f else 1f)}
        return e.finish(rate)
    }
    val v=make()!!;check(v.size==24);check(v.take(12).all{it==.5f});check(v.drop(12).all{it==1f})
    check(make(true)!!.all{it==0f});check(make(skip=10)==null)
    val e=WaveEnvelope(duration,24);repeat(19200){e.frame(it*1000000L/rate,Float.NaN)};check(e.finish(rate)==null)
    check(runCatching{WaveEnvelope(900000001)}.isFailure);check(runCatching{WaveEnvelope(duration,0)}.isFailure)
    val h=WaveEnvelope(duration,24);repeat(19200){h.frame(it*1000000L/rate,5f)};check(h.finish(rate)!!.all{it==1f})
    val partial=WaveEnvelope(duration,24)
    repeat(1600){partial.frame(it*125L,0.25f)}
    val preview=partial.preview(rate)!!
    check(preview.size==24&&preview.take(2).all{it==1f}&&preview.drop(2).all{it.isNaN()})
    check(partial.finish(rate)==null)
    repeat(17600){partial.frame((it+1600)*125L,1f)}
    val final=partial.finish(rate)!!
    check(final.take(2).all{it==.5f}&&final.drop(2).all{it==1f})
    check(WaveEnvelope(duration,24).preview(rate)==null)
    val silent=WaveEnvelope(duration,24);repeat(800){silent.frame(it*125L,0f)}
    check(silent.preview(rate)!!.let{it[0]==0f&&it[1].isNaN()})
    println("PASS: 14 envelope checks including progressive measured bins and unknown/silent separation")
}
