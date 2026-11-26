package app.remix.player
import kotlin.math.*
/** Bounded 250ms RMS bins, measured from decoded PCM (not metadata or volume slider). */
object AdaptiveOverlap {
    const val BIN_MS=250L
    data class Plan(val duration:Long,val naturalOutro:Boolean,val quietIntro:Boolean)
    fun plan(tail:DoubleArray?,head:DoubleArray?):Plan {
        fun valid(x:DoubleArray?)=x!=null&&x.size>=8&&x.size<=48&&x.all{it.isFinite()&&it in 0.0..1.0}
        if(!valid(tail)||!valid(head))return Plan(4500,false,false)
        val t=tail!!;val h=head!!
        fun ref(x:DoubleArray)=x.sorted()[((x.size-1)*.8).toInt()]
        val tr=ref(t);val hr=ref(h)
        val suffix=if(tr>.005)t.reversed().takeWhile{it<=tr*.70}.size else 0
        val natural=suffix>=6&&t.takeLast(4).average()<tr*.30
        val prefix=if(hr>.005)h.takeWhile{it<=hr*.40}.size else 0
        val quiet=prefix>=4
        val length=maxOf(if(natural)(suffix*BIN_MS+1000).coerceIn(3000,8000) else 4000L,if(quiet)(prefix*BIN_MS+2500).coerceIn(4000,8000) else 0L)
        return Plan(length,natural,quiet)
    }
    fun gains(elapsed:Long,duration:Long,plan:Plan):OverlapCore.Gains {
        require(duration>0)
        val x=(elapsed.toDouble()/duration).coerceIn(0.0,1.0)
        val a=cos(PI/2*(if(plan.naturalOutro)x.pow(1.5) else x))
        val b=sin(PI/2*(if(plan.quietIntro)x.pow(.75) else x))
        val norm=maxOf(1.0,a+b)
        return OverlapCore.Gains((a/norm).toFloat(),(b/norm).toFloat())
    }
}
