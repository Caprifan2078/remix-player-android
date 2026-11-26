package app.remix.player
fun main(){
    fun s(b:Double,p:Double?,h:Double?,c:Double?)=RadioSimilarity.score(b,.7,p,.6,h,.5,c)
    check(s(.2,.7,.6,.5)<s(.2,.1,.05,1.9))
    check(s(.2,.7,.6,.5)<s(.2,null,null,null))
    check(s(.1,.7,.6,.5)<s(.5,.7,.6,.5))
    check(s(.2,null,null,null)==s(.2,Double.NaN,Double.POSITIVE_INFINITY,-1.0))
    val r=kotlin.random.Random(42)
    repeat(10000){val b=r.nextDouble();val a=List(3){r.nextDouble()};val z=List(3){r.nextDouble()};val x=RadioSimilarity.score(b,a[0],z[0],a[1],z[1],a[2],z[2]);val y=RadioSimilarity.score(b,z[0],a[0],z[1],a[1],z[2],a[2]);check(x in 0.0..1.0&&x==y)}
    val seed=SmartMix.Entry("seed",120.0,"C major",.2,.7,.6,.5)
    val near=seed.copy(id="near")
    val far=seed.copy(id="far",pulse=.1,brightness=.05,contrast=1.9)
    check(SmartMix.arrange(listOf(seed,far,near),"seed",true).map{it.id}==listOf("seed","near","far"))
    println("PASS: 10000 symmetric bounded radio scores, acoustic ranking and missing features")
}
