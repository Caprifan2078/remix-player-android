package app.remix.player
import java.io.File
fun main(){
    val invalid=listOf(Float.NaN,Float.POSITIVE_INFINITY,Float.NEGATIVE_INFINITY)
    for(rate in listOf(8000,44100,48000,96000,192000)){
        val d=GenreDynamics(rate);val k=KickSpace(rate);val low=SourceLowEnd(rate)
        for(x in invalid){
            d.frame(x,.2f);check(d.left==0f&&d.right.isFinite()&&d.right>0f)
            d.frame(.2f,x);check(d.right==0f&&d.left.isFinite()&&d.left>0f)
            check(k.sample(x,1f).isFinite());check(k.sample(1f,x).isFinite())
            low.frame(x,.2f,x);check(low.left.isFinite()&&low.right.isFinite())
            low.frame(.2f,x,.4f);check(low.left.isFinite()&&low.right.isFinite())
        }
        repeat(1000){d.frame(.2f,-.2f);check(d.left.isFinite()&&d.right.isFinite());check(k.sample(1f,.7f) in 0f..1f);low.frame(.2f,-.2f,.5f);check(low.left.isFinite()&&low.right.isFinite())}
        low.frame(Float.MAX_VALUE,-Float.MAX_VALUE,.3f);check(low.left.isFinite()&&low.right.isFinite())
        d.frame(Float.MAX_VALUE,-Float.MAX_VALUE);check(d.left in -1f..1f&&d.right in -1f..1f)
    }
    val dir=kotlin.io.path.createTempDirectory("pulse-export").toFile()
    try {
        val out=File(dir,"mix.wav");out.writeText("old")
        check(runCatching{SafeTransitionOutput.write(out){it.writeText("partial");error("failure")}}.isFailure)
        check(out.readText()=="old"&&dir.list()!!.size==1)
        check(runCatching{SafeTransitionOutput.write(out){0L}}.isFailure);check(out.readText()=="old")
        try{check(runCatching{SafeTransitionOutput.write(out){it.writeText("partial");Thread.currentThread().interrupt();1L}}.isFailure)}finally{Thread.interrupted()}
        check(out.readText()=="old"&&dir.list()!!.size==1)
        check(SafeTransitionOutput.write(out){it.writeText("new");7L}==7L);check(out.readText()=="new")
        val fresh=File(dir,"fresh.wav");check(runCatching{SafeTransitionOutput.write(fresh){it.writeText("partial");error("failure")}}.isFailure);check(!fresh.exists())
        check(dir.list()!!.size==1)
    }finally{dir.deleteRecursively()}
    val stall=OverlapStall();var cases=0
    for(start in 0L..100000L step 100){stall.reset();check(!stall.expired(start));check(!stall.expired(start+1199));check(stall.expired(start+1200));cases++}
    println("PASS: DSP recovery at 5 sample rates, 5000 recovery frames, transactional export, $cases stall clock origins")
}
