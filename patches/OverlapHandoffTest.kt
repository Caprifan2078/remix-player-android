package app.remix.player
fun main(){
    val h=OverlapHandoff()
    h.observe(3000,30000,0f);check(h.audibleUntil==0L)
    h.observe(3200,30000,.4f);check(h.audibleUntil==3200L)
    h.observe(0,30000,0f);check(h.target(0,30000)==3200L)
    check(!h.aligned(0,3500,true)){"Repeated intro: primary at zero"}
    check(!h.aligned(1200,3500,true)){"Timeout must not unmute a lagging decoder"}
    check(h.aligned(3420,3500,true))
    check(!h.aligned(3000,3000,false))
    check(h.aligned(3200,0,false))
    check(h.target(3400,30000)==3400L)
    h.observe(3500,30000,.8f);check(h.target(0,30000)==3500L)
    h.observe(8000,6000,1f);check(h.audibleUntil==5999L)
    check(h.recovery(2999,3000,false,0,true)==OverlapHandoff.Recovery.WAIT)
    check(h.recovery(3000,3000,false,0,true)==OverlapHandoff.Recovery.START)
    check(!h.aligned(0,0,false))
    check(h.recovery(3999,999,true,0,true)==OverlapHandoff.Recovery.WAIT)
    check(h.recovery(4000,1000,true,0,true)==OverlapHandoff.Recovery.RETRY)
    check(h.recovery(4000,1000,true,8000,false)==OverlapHandoff.Recovery.RETRY)
    check(h.recovery(4000,1000,true,5999,true)==OverlapHandoff.Recovery.WAIT)
    check(h.recovery(12000,2000,true,0,true)==OverlapHandoff.Recovery.PAUSE)
    check(h.primaryGain(0)==0f&&h.primaryGain(60)==.5f&&h.primaryGain(120)==1f)
    check(h.primaryGain(-1)==0f&&h.primaryGain(300)==1f)
    h.reset();check(h.audibleUntil==0L&&h.target(0,30000)==0L)
    println("PASS: 22 audible position, timeout recovery and linear handoff checks")
}
