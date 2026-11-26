package app.remix.player
fun main(){
    fun old(primary:Long,preview:Long,elapsed:Long)=kotlin.math.abs(primary-preview)<=250||elapsed>=1000
    check(old(300,2200,1000))
    check(HandoffGuard.decide(300,2200,1000,true,false)==HandoffGuard.Action.RESYNC)
    check(HandoffGuard.decide(300,2200,1000,true,true)==HandoffGuard.Action.WAIT)
    check(HandoffGuard.decide(300,2200,1800,true,true)==HandoffGuard.Action.CUT_FORWARD)
    check(HandoffGuard.decide(2200,300,1800,true,true)==HandoffGuard.Action.CUT)
    val rng=kotlin.random.Random(42)
    repeat(50000){
        val p=rng.nextLong(0,900001);val v=rng.nextLong(0,900001);val t=rng.nextLong(0,2501);val ready=rng.nextBoolean();val used=rng.nextBoolean()
        val a=HandoffGuard.decide(p,v,t,ready,used)
        when(a){
            HandoffGuard.Action.BLEND->check(ready&&kotlin.math.abs(p-v)<=150&&t<1800)
            HandoffGuard.Action.RESYNC->check(ready&&!used&&v-p>150&&t in 350..1799)
            HandoffGuard.Action.CUT_FORWARD->check(v-p>150&&t>=1800)
            HandoffGuard.Action.CUT->check(t>=1800&&v-p<=150)
            HandoffGuard.Action.WAIT->check(t<1800)
        }
    }
    println("PASS: reproduced old unaligned blend; 50000 handoff cases, no backward corrective seek")
}
