package app.remix.player
fun main(){
 fun e(id:String,a:String,x:Double,v:Double?=.2)=LocalDiscovery.Entry(id,a,listOf(x,x,x,x,v,x))
 val seed=e("seed","A",.2);val same=e("1","A",.21);val other=e("2","B",.22);val farther=e("3","C",.55);val far=e("4","D",.99)
 val rows=listOf(seed,same,other,farther,far,same)
 check(LocalDiscovery.distance(seed,seed)==0.0)
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR)==listOf("2","1"))
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.VARIED).toSet()==setOf("1","2","3"))
 check(LocalDiscovery.rank(seed,rows.reversed(),LocalDiscovery.Mode.SIMILAR)==listOf("2","1"))
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR,1)==listOf("2"))
 check(LocalDiscovery.rank(seed,emptyList(),LocalDiscovery.Mode.VARIED).isEmpty())
 check(LocalDiscovery.distance(seed,e("x","",.2,null))==0.0)
 check(runCatching{e("x","",Double.NaN)}.isFailure)
 check(LocalDiscovery.append(listOf("1","2"),listOf("2","3","3","4",""))==listOf("3","4"))
 check(LocalDiscovery.append(emptyList(),listOf("1","2"),1)==listOf("1"))
 val many=(0 until 10000).map{e(it.toString(),"Artist "+it%50,.21)}
 check(LocalDiscovery.rank(seed,many,LocalDiscovery.Mode.VARIED).distinct().size==50)
 val full=(1..100).map{it.toString()}
 check(LocalDiscovery.append(emptyList(),full,100)==full)
 check(LocalDiscovery.append(listOf("1","2"),full+"3",100)==full.drop(2))
 check(LocalDiscovery.append(emptyList(),full+full,100).size==100)
 val q=listOf("a","b","c");val s=listOf("a","d","d","e","")
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR,excluded=setOf("1"))==listOf("2"))
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR,excluded=setOf("1","2")).isEmpty())
 check(LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.VARIED,1,setOf("1"))==listOf("2"))
 check(LocalDiscovery.queuePlan(q,1,s,true,false)==LocalDiscovery.QueuePlan(2,listOf("d","e")))
 check(LocalDiscovery.queuePlan(q,2,s,true,false)==LocalDiscovery.QueuePlan(3,listOf("d","e")))
 check(LocalDiscovery.queuePlan(q,0,s,false,true)==LocalDiscovery.QueuePlan(3,listOf("d","e")))
 check(LocalDiscovery.queuePlan(q,1,s,true,true)==null)
 check(LocalDiscovery.queuePlan(q,-1,s,true,false)==null)
 check(LocalDiscovery.queuePlan(emptyList(),0,s,true,false)==null)
 check(LocalDiscovery.queuePlan(q,1,q,true,false)?.ids?.isEmpty()==true)
 check(LocalDiscovery.queuePlan(q,1,(0..200).map{it.toString()},true,false)?.ids?.size==100)
 check(LocalDiscovery.queuePlan(q,1,s,true,false,1)?.ids==listOf("d"))
 val favorites=listOf(e("liked-low","A",.1),e("liked-high","B",.9),e("low","C",.12),e("high","D",.88),e("middle","E",.5),e("low","C",.12),e("","F",.1))
 val liked=setOf("liked-low","liked-high")
 check(LocalDiscovery.favorites(favorites,liked,LocalDiscovery.Mode.SIMILAR).toSet()==setOf("low","high"))
 check(LocalDiscovery.favorites(favorites.reversed(),liked,LocalDiscovery.Mode.SIMILAR)==LocalDiscovery.favorites(favorites,liked,LocalDiscovery.Mode.SIMILAR))
 check(LocalDiscovery.favorites(favorites,emptySet()).isEmpty())
 check(LocalDiscovery.favorites(favorites,setOf("missing")).isEmpty())
 check(LocalDiscovery.favorites(favorites,liked,limit=1).size==1)
 check(LocalDiscovery.favorites(favorites,liked+"low",LocalDiscovery.Mode.SIMILAR)==listOf("high"))
 check(LocalDiscovery.favorites(favorites,liked,LocalDiscovery.Mode.SIMILAR).none{it in liked||it.isBlank()})
 val largeLikes=(0 until 10000).map{e("track-"+it,"Artist "+it%50,(it%100)/100.0)}
 val likeIds=largeLikes.take(200).map{it.id}.toSet()
 val picks=LocalDiscovery.favorites(largeLikes,likeIds,limit=100)
 check(picks.size==100&&picks.distinct().size==100&&picks.none{it in likeIds})
 check(runCatching{LocalDiscovery.favorites(favorites,liked,limit=0)}.isFailure)
 fun cancelled(block:()->Any?):Boolean {
  Thread.currentThread().interrupt()
  return try{runCatching{block()}.isFailure}finally{Thread.interrupted()}
 }
 val cases=listOf(
  cancelled{LocalDiscovery.rank(seed,emptyList(),LocalDiscovery.Mode.SIMILAR)},
  cancelled{LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR,excluded=rows.map{it.id}.toSet())},
  cancelled{LocalDiscovery.favorites(favorites,emptySet())},
  cancelled{LocalDiscovery.favorites(favorites,liked)},
  cancelled{LocalDiscovery.rank(seed,rows,LocalDiscovery.Mode.SIMILAR)}
 )
 println("Cancellation: "+cases.count{it}+"/"+cases.size)
 check(cases.all{it})
 println("PASS: 40 local discovery, favorites, queue and cancellation checks")
}
