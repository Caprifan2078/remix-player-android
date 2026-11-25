package app.remix.player
import kotlin.math.*
fun main(){
 val names=listOf("House","Hardstyle","Drift Phonk","Brazilian Funk","UK Garage","Synthwave","Amapiano","Dubstep")
 val colors=mutableListOf<Pair<Double,Double>>()
 for(name in names){
   val lead=LeadSynth(listOf(Harmony.Chord(0.0,0,false,.9)),120.0,0.0,GenreEngine.styles.first{it.name==name}.copy(drive=.2f))
   val signal=DoubleArray(4410){lead.sample(it.toLong(),1f).toDouble()}
   fun magnitude(h:Int):Double{var r=0.0;var im=0.0;for(i in 1103 until 4410){val x=signal[i]*(.5-.5*cos(2*PI*(i-1103)/3306));val a=2*PI*(440*2.0.pow((60-69)/12.0))*h*i/44100;r+=x*cos(a);im+=x*sin(a)};return hypot(r,im)}
   val f=magnitude(1);check(f>.01);val ratios=magnitude(2)/f to magnitude(3)/f;colors.add(ratios);println("$name: H2/H1=${"%.3f".format(java.util.Locale.US,ratios.first)}, H3/H1=${"%.3f".format(java.util.Locale.US,ratios.second)}")
 }
 val unique=colors.map{(a,b)->(a*20).roundToInt() to (b*20).roundToInt()}.distinct().size
 println("MEASURE $unique/8 distinct spectral signatures (ratio bins 0.05)");check(unique==8)
}
