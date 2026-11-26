package app.remix.player
fun main() {
    val stall = OverlapStall()
    val startedAt = 1000L
    val legacyExpired = 5000L-startedAt > 1200L
    check(legacyExpired)
    check(!stall.expired(5000))
    check(!stall.expired(6199))
    check(stall.expired(6200))
    stall.reset()
    check(!stall.expired(9000)); stall.reset()
    check(!stall.expired(11000)); check(!stall.expired(11500)); stall.reset()
    check(!stall.expired(13000)); check(stall.expired(14200))
    stall.reset();check(!stall.expired(0));check(stall.expired(1200))
    var count=0
    for (start in 0L..100000L step 100) {
        stall.reset();check(!stall.expired(start));check(!stall.expired(start+1199));check(stall.expired(start+1200));count++
    }
    println("PASS: late stall, exact timeout, recovery, repeated stalls, zero clock, $count shifted time origins")
}
