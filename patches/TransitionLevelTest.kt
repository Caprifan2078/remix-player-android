package app.remix.player
import kotlin.math.*
fun main(){
 val m=TransitionLevel.match(.05,.4)
 check(m.incoming<.6&&m.outgoing==1.0){"Louder incoming source is not attenuated"}
 check(m.incomingAt(1.0)==1.0&&m.outgoingAt(0.0)==1.0)
 check(m.incomingAt(.25)<m.incomingAt(.75))
 val opposite=TransitionLevel.match(.4,.05)
 check(opposite.outgoing==m.incoming&&opposite.incoming==1.0)
 check(opposite.outgoingAt(.25)>opposite.outgoingAt(.75))
 check(TransitionLevel.match(.2,.21)==TransitionLevel.Match())
 for(x in listOf(0.0,.001,Double.NaN,Double.POSITIVE_INFINITY,-.5,1.1))check(TransitionLevel.match(x,.2)==TransitionLevel.Match())
 val r=kotlin.random.Random(42)
 repeat(10000){val a=.01+r.nextDouble()*.99;val b=.01+r.nextDouble()*.99;val t=r.nextDouble();val v=TransitionLevel.match(a,b);val w=TransitionLevel.match(b,a);check(v.outgoingAt(t) in .5..1.0&&v.incomingAt(t) in .5..1.0);check(abs(v.outgoingAt(t)-w.incomingAt(1-t))<1e-12)}
 val before=sin(PI/4)*.4/(cos(PI/4)*.05)
 val after=sin(PI/4)*.4*m.incomingAt(.5)/(cos(PI/4)*.05*m.outgoingAt(.5))
 check(after<before)
 println("PASS: 10000 bounded symmetric level matches, exact endpoints, silence and invalid values; midpoint ratio $before -> $after")
}
