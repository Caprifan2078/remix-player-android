package app.remix.player
fun main(){
    fun e(id:String,bpm:Double?,key:String?,rms:Double?=.2)=SmartMix.Entry(id,bpm,key,rms)
    val seed=e("seed",120.0,"C major");val near=e("near",121.0,"G major");val rel=e("relative",120.0,"A minor");val far=e("far",90.0,"F♯ major",.02);val unknown=e("unknown",Double.NaN,"bad",null)
    check(SmartMix.distance(seed,rel)<SmartMix.distance(seed,far));check(SmartMix.distance(seed,near)<SmartMix.distance(seed,far))
    check(SmartMix.distance(seed,e("half",60.0,"C major"))<SmartMix.distance(seed,far))
    check(SmartMix.distance(seed,seed)==0.0)
    val entries=listOf(seed,far,unknown,near,rel)
    val mix=SmartMix.arrange(entries,"seed",false);check(mix.first()==seed&&mix.last()==unknown&&mix.toSet()==entries.toSet())
    val radio=SmartMix.arrange(entries,"seed",true);check(radio.size==4&&radio.first()==seed&&radio.last()==far)
    check(SmartMix.arrange(entries,"unknown",true).isEmpty());check(SmartMix.arrange(entries,"missing",false).isEmpty())
    check(runCatching{SmartMix.arrange(listOf(seed,seed),"seed",false)}.isFailure)
    val random=kotlin.random.Random(42)
    repeat(1000){val rows=List(20){i->e("$i",50+random.nextDouble()*170,listOf("C major","A minor","D major",null)[random.nextInt(4)])};val result=SmartMix.arrange(rows,"0",false);check(result.size==20&&result.first().id=="0"&&result.toSet()==rows.toSet());check(result==SmartMix.arrange(rows,"0",false));check(rows.all{SmartMix.distance(it,rows[0]).isFinite()})}
    println("PASS: 1000 randomized mixes, identity, relative key, half tempo, unknown and deterministic ordering")
}
