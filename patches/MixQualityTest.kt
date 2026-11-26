package app.remix.player
import kotlin.random.Random
fun main(){
 val rng=Random(127); var improved=0; var before=0.0; var after=0.0
 fun cost(x:List<SmartMix.Entry>)=x.zipWithNext().sumOf{(a,b)->SmartMix.distance(a,b)}
 fun greedy(rows:List<SmartMix.Entry>):List<SmartMix.Entry>{val r=rows.drop(1).toMutableList();val out=mutableListOf(rows.first());while(r.isNotEmpty()){val i=r.indices.minByOrNull{SmartMix.distance(out.last(),r[it])}!!;out.add(r.removeAt(i))};return out}
 repeat(1000){val rows=List(20){i->SmartMix.Entry("$i",50+rng.nextDouble()*170,listOf("C major","A minor","D major","F♯ minor",null)[rng.nextInt(5)],.01+rng.nextDouble()*.5)};val old=greedy(rows);val new=SmartMix.arrange(rows,"0",false);val a=cost(old);val b=cost(new);check(new.first()==rows.first()&&new.toSet()==rows.toSet());check(b<=a+1e-8);if(b<a-1e-8)improved++;before+=a;after+=b}
 check(improved>0){"No improvement over greedy"}
 println("PASS: 1000 lists; improved=$improved; cost before=$before after=$after; reduction=${(before-after)/before*100}%")
}
