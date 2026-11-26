package app.remix.player
fun main(){
    check(WidgetPolicy.size(120,64)==WidgetPolicy.Size.COMPACT)
    check(WidgetPolicy.size(230,160)==WidgetPolicy.Size.MIX)
    check(WidgetPolicy.size(280,208)==WidgetPolicy.Size.STUDIO)
    check(WidgetPolicy.size(279,208)==WidgetPolicy.Size.MIX)
    check(WidgetPolicy.size(280,207)==WidgetPolicy.Size.MIX)
    check(WidgetPolicy.size(500,64)==WidgetPolicy.Size.COMPACT)
    check(WidgetPolicy.selection("fast","Оригинал")=="Sped Up + Bass")
    check(WidgetPolicy.selection("fast","Sped Up + Bass")=="Оригинал")
    check(WidgetPolicy.selection("reset","Nightcore")=="Оригинал")
    check(WidgetPolicy.selection("unknown","Оригинал")==null)
    val random=kotlin.random.Random(42)
    repeat(10000){
        val a=random.nextInt(0,800);val b=random.nextInt(0,800)
        val old=WidgetPolicy.size(a,b);val expanded=WidgetPolicy.size(a+random.nextInt(0,200),b+random.nextInt(0,200))
        check(expanded.ordinal>=old.ordinal)
        val id="track-${random.nextInt(100)}";check(WidgetPolicy.allowed(id,id,false));check(!WidgetPolicy.allowed(id,"other-$id",false));check(!WidgetPolicy.allowed(id,id,true));check(!WidgetPolicy.allowed(null,id,false))
    }
    println("PASS: 10000 responsive size and stale track checks; effect toggling and invalid command rejection")
}
