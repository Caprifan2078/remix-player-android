package app.remix.player
import kotlin.math.*
fun main(){
 fun measure(f:Double,p:Float):Pair<Double,Double>{val o=StereoOrbit(48000);val x=FloatArray(2);var a=0.0;var b=0.0;repeat(48000){i->x[0]=(.2*sin(2*PI*f*i/48000)).toFloat();x[1]=x[0];o.apply(x,p);check(x.all{it.isFinite()&&abs(it)<1});if(i>=2400){a+=x[0]*x[0];b+=x[1]*x[1]}};return sqrt(a/45600) to sqrt(b/45600)}
 val high=measure(4000.0,.95f);val mirror=measure(4000.0,-.95f);val bass=measure(50.0,.95f)
 check(high.second/high.first>3);check(mirror.first/mirror.second>3);check(abs(high.first-mirror.second)<1e-6);check(abs(bass.first-bass.second)<.04)
 val orbit=StereoOrbit(48000);val x=floatArrayOf(.3f,-.3f);orbit.apply(x,0f);check(x[0]>.1f&&x[1]<-.1f)
 repeat(100){orbit.apply(x,.8f)};orbit.reset();x.fill(0f);orbit.apply(x,1f);check(x.all{it==0f});x[0]=Float.NaN;x[1]=Float.POSITIVE_INFINITY;orbit.apply(x,Float.NaN);check(x.all{it==0f});println("PASS: seven spatial audio checks; high-frequency channel ratio=${high.second/high.first}; bass difference=${abs(bass.first-bass.second)}")
}
