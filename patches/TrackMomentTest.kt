package app.remix.player
fun main(){
    check(TrackMoment.position(0,1000)==0L)
    check(TrackMoment.position(999,1000)==999L)
    for(v in listOf(null,-1L,1000L,1001L,Long.MAX_VALUE))check(TrackMoment.position(v,1000)==null)
    check(TrackMoment.position(100,0)==null)
    check(!TrackMoment.canApply("a","b",false,true));check(!TrackMoment.canApply("a","a",true,true));check(!TrackMoment.canApply("a","a",false,false));check(TrackMoment.canApply("a","a",false,true))
    val rng=kotlin.random.Random(42)
    repeat(10000){val d=rng.nextLong(1,Long.MAX_VALUE);val p=rng.nextLong(0,d);check(TrackMoment.position(p,d)==p);check(TrackMoment.position(d,d)==null);check(TrackMoment.position(-p-1,d)==null);val id="id-${rng.nextInt(100)}";check(TrackMoment.canApply(id,id,false,true));check(!TrackMoment.canApply(id,"$id-other",false,true))}
    println("PASS: 10000 randomized bookmark position/identity cases; invalid duration and stale track checks")
}
