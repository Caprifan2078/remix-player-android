package app.remix.player
import kotlin.math.*
fun main(){
    val names=listOf("Hardstyle","Rawstyle","Hardcore","Drift Phonk","Brazilian Phonk","Memphis Phonk","House Phonk","Montagem","Krushfunk","Automotivo")
    var frames=0L
    for(rate in listOf(8000,22050,44100,48000,96000)){
        fun rms(a:DoubleArray,start:Double,end:Double):Double{val from=(rate*start).toInt();val to=(rate*end).toInt();return sqrt((from until to).sumOf{a[it]*a[it]}/(to-from))}
        for(name in names){val a=GenreKick.voice(name,rate,50.0);check(a.size==ceil(.36*rate).toInt());check(a[0]==0.0&&abs(a.last())<.002);check(a.all{it.isFinite()&&abs(it)<=.60});check(rms(a,.01,.07)>.05);check(a.contentEquals(GenreKick.voice(name,rate,50.0)));frames+=a.size}
        val hard=GenreKick.voice("Hardstyle",rate,50.0);val phonk=GenreKick.voice("Drift Phonk",rate,50.0);val raw=GenreKick.voice("Rawstyle",rate,50.0)
        check(rms(hard,.18,.28)>rms(phonk,.18,.28)*1.2);check(!hard.contentEquals(raw));check(!hard.contentEquals(phonk))
        println("$rate Hz: Hardstyle tail RMS=${rms(hard,.18,.28)}, Phonk=${rms(phonk,.18,.28)}")
    }
    check(!GenreKick.supported("House"));check(runCatching{GenreKick.voice("Hardstyle",44100,Double.NaN)}.isFailure)
    println("PASS: 50 voice/rate combinations; $frames samples")
}
