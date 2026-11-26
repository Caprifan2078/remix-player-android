package app.remix.player
fun main(){
 val c=MixFeatureCache<Int>(3,100)
 val rev=c.revision
 check(c.get("a",0)==null)
 check(c.put("a",1,0,rev)&&c.put("b",2,1,rev)&&c.put("c",3,2,rev))
 check(c.get("a",3)==1);check(c.put("d",4,4,rev));check(c.get("b",4)==null&&c.get("a",4)==1)
 check(c.get("a",99)==1&&c.get("a",100)==null)
 check(c.get("d",3)==null)
 c.invalidate();check(c.get("c",5)==null&&!c.put("c",3,5,rev))
 check(c.put("c",3,5,c.revision)&&c.get("c",5)==3)
 val cache=MixFeatureCache<Int>(128,100000)
 repeat(10000){check(cache.put("$it",it,it.toLong(),cache.revision))}
 check(cache.get("9871",10000)==null&&cache.get("9872",10000)==9872)
 println("PASS: bounded LRU, expiry, stale generation, clock reset, 10000 inserts")
}
