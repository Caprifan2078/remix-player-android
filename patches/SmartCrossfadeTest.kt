package app.remix.player
fun main(){
    check(SmartCrossfade.DEFAULT_MS==5000L)
    check(SmartCrossfade.enabled(null,false))
    check(!SmartCrossfade.enabled(null,true))
    check(!SmartCrossfade.enabled(false,false))
    check(SmartCrossfade.enabled(true,true))
    check(SmartCrossfade.duration(180000,240000,5000)==5000L)
    check(SmartCrossfade.duration(30000,180000,5000)==3000L)
    check(SmartCrossfade.duration(180000,15000,5000)==1500L)
    check(SmartCrossfade.duration(5000,5000,5000)==1000L)
    check(SmartCrossfade.duration(1000,5000,5000)==0L)
    check(SmartCrossfade.duration(20000,20000,0)==0L)
    check(SmartCrossfade.duration(20000,20000,9000)==0L)
    repeat(10000){i->
        val a=2000L+i*137L;val b=2000L+i*71L
        val limit=1000L+(i%8)*1000L
        val v=SmartCrossfade.duration(a,b,limit)
        check(v in 1000L..limit)
        check(v==SmartCrossfade.duration(b,a,limit))
    }
    println("PASS: adaptive duration, default preferences, explicit override and 10000 symmetric bounds")
}
