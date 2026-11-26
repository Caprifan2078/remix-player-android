package app.remix.player
fun main(){
 check(TransportPolicy.target("back10",3000,120000,true)==0L)
 check(TransportPolicy.target("forward10",118000,120000,true)==120000L)
 check(TransportPolicy.target("middle",0,180000,true)==90000L)
 check(TransportPolicy.target("middle",0,-1,true)==null)
 check(TransportPolicy.target("middle",0,1000,false)==null)
 check(TransportPolicy.target("unknown",0,1000,true)==null)
 check(TransportPolicy.speeds.values.toList()==listOf(.8f,1f,1.25f,1.5f))
 val rng=kotlin.random.Random(42)
 repeat(10000){val d=rng.nextLong(1,Long.MAX_VALUE);val p=rng.nextLong(0,d);for(c in listOf("back10","forward10","quarter","middle","threequarters")){val v=TransportPolicy.target(c,p,d,true)!!;check(v in 0..d);if(c=="back10")check(v<=p);if(c=="forward10")check(v>=p)}}
 println("PASS: 50000 randomized seek targets, invalid duration and speed presets")
}
