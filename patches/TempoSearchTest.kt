package app.remix.player
fun main(){
    val b=TempoSearch.Kind.BPM;val r=TempoSearch.Kind.RATIO
    check(TempoSearch.parse("120–140 BPM",b)==TempoSearch.Range(b,120.0,140.0))
    check(TempoSearch.parse("1,25×",r)!!.contains(1.25));check(TempoSearch.parse("x0.8-1.0",r)!!.contains(.9))
    for(s in listOf("NaN","Infinity","140-120","-1","0","300-301","1-2-3","garbage"))check(TempoSearch.parse(s,b)==null)
    check(TempoSearch.measured(120.0,.29)==null);check(TempoSearch.measured(120.0,.3)==120.0);check(TempoSearch.measured(Double.NaN,.8)==null)
    val rows=listOf(TempoSearch.Entry("a",130.0,1.25),TempoSearch.Entry("b",null,.8),TempoSearch.Entry("c",132.0,null),TempoSearch.Entry("d",100.0,1.0))
    check(TempoSearch.find(rows,TempoSearch.parse("130",b)!!).map{it.id}==listOf("a","c"));check(TempoSearch.find(rows,TempoSearch.parse("0.8",r)!!).single().id=="b")
    val random=kotlin.random.Random(42)
    repeat(10000){val n=random.nextInt(30,301).toDouble();val range=TempoSearch.parse(n.toString(),b)!!;check(range.contains(n));check(!range.contains(null));check(!range.contains(Double.NaN));check(range.low>=30&&range.high<=300)}
    val large=List(60000){TempoSearch.Entry(it.toString(),(it%270+30).toDouble(),null)};val range=TempoSearch.parse("120-140",b)!!
    val t=System.nanoTime();val found=TempoSearch.find(large,range);val ms=(System.nanoTime()-t)/1e6;check(found.size==large.count{range.contains(it.bpm)})
    println("PASS: 10000 ranges, BPM/ratio distinction, unknown and invalid values, 60000 entries in $ms ms")
}
