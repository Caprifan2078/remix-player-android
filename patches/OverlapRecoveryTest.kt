package app.remix.player
import kotlin.math.abs
fun main(){
 val r=OverlapRecovery();check(r.fraction(0)==1f);var cases=0
 for(t in 0L..100000L step 100){r.reset();r.stall();check(r.fraction(t)==0f);check(abs(r.fraction(t+60)-.5f)<1e-6);check(r.fraction(t+120)==1f);check(r.fraction(t+1000)==1f);cases++}
 r.stall();check(r.fraction(100)==0f);check(r.fraction(130)==.25f);r.stall();check(r.fraction(150)==0f);check(r.fraction(270)==1f)
 r.stall();r.reset();check(r.fraction(0)==1f)
 r.stall();var previous=-1f;for(t in 0L..120L){val f=r.fraction(t);check(f>=previous);val out=1f+(0.35f-1f)*f;val incoming=.65f*f;check(out in .349999f..1f&&incoming in 0f.. .65f);previous=f}
 println("PASS: $cases clock origins, repeated stalls, monotonic recovery and reset")
}
