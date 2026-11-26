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
    h.reset();check(h.audibleUntil==0L&&h.target(0,30000)==0L)
    println("PASS: 12 audible position and no-replay handoff checks")
}
