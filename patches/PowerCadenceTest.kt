package app.remix.player
fun main(){
 fun d(p:Long,playing:Boolean=true,fade:Long=0,overlap:Long=0,loop:Boolean=false,sleep:Long?=null)=PlaybackCadence.delay(playing,p,180000,fade,overlap,loop,sleep)
 check(d(90000)==2000L);check(d(90000,overlap=5000)==500L);check(d(169500,overlap=5000)==50L);check(d(100,fade=3000)==50L);check(d(176500,fade=3000)==50L);check(d(90000,loop=true)==50L);check(d(0,false)==2000L);check(d(0,false,sleep=100)==100L);check(d(0,false,sleep=0)==1L)
 val r=kotlin.random.Random(42);repeat(10000){val v=PlaybackCadence.delay(r.nextBoolean(),r.nextLong(0,180001),180000,r.nextLong(0,5001),r.nextLong(0,8001),r.nextBoolean(),r.nextLong(1,100000));check(v in 1..2000)}
 var p=0L;var count=0;while(p<180000){p+=d(p,overlap=5000);count++};check(count<600);println("PASS 10000 cases; 180s track with 5s overlap: old 3600 vs new $count timer callbacks")
}
