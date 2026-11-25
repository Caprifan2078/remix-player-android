package app.remix.player
fun main(){
    fun seg(a:Long,b:Long,t:String,vararg starts:Long)=WhisperSegments.Segment(a,b,t,starts.toList())
    fun merge(a:WhisperSegments.Segment,b:WhisperSegments.Segment)=WhisperSegments.merge(listOf(WhisperSegments.Window(0,25000,listOf(a)),WhisperSegments.Window(23000,48000,listOf(b))))
    val a=seg(21800,24700,"Мы снова здесь",21850,23300,23700)
    val b=seg(23200,25800,"снова здесь сегодня",23340,23740,25000)
    val result=merge(a,b)
    check(result.map{it.text}==listOf("Мы снова здесь","сегодня")){"duplicate words across windows: $result"}
    check(result[1].startMs==25000L && result[1].wordStarts==listOf(25000L))
    val other=seg(23200,27000,"снова здесь сегодня",24500,25100,26000)
    check(merge(a,other).map{it.text}==listOf(a.text,other.text)){"distinct repetition lost"}
    val unrelated=seg(23200,25800,"совсем другие слова",23340,23740,25000)
    check(merge(a,unrelated).map{it.text}==listOf(a.text,unrelated.text))
    val noTimes=b.copy(wordStarts=emptyList())
    check(merge(a,noTimes).map{it.text}==listOf(a.text,noTimes.text))
    val onlyOne=seg(23200,25800,"здесь сегодня",23740,25000)
    check(merge(a,onlyOne).map{it.text}==listOf(a.text,onlyOne.text))
    val punctuation=b.copy(text="СНОВА, здесь! сегодня")
    check(merge(a,punctuation).last().text=="сегодня")
    val repeated=seg(24000,26500,"снова здесь снова здесь",24000,24500,25000,26000)
    check(merge(a,repeated).last().text==repeated.text)
    check(WhisperSegments.lrc(result).contains("[00:25.000]<00:25.000>сегодня"))
    val single=WhisperSegments.parse("10\t30\tHello\t15",1000,1000).single()
    check(single.wordStarts==listOf(1150L))
    val random=kotlin.random.Random(42)
    repeat(2000){
        val delta=random.nextLong(-300,501)
        val sample=b.copy(startMs=23000,wordStarts=listOf(23300+delta,23700+delta,25000))
        val out=merge(a,sample)
        check(out.size==2)
        check(out[1].text==if(kotlin.math.abs(delta)<=200)"сегодня" else sample.text){"Wrong trim at $delta"}
        check(out[0]==a&&out[1].endMs==sample.endMs)
        check(out[1].wordStarts.all{it in out[1].startMs until out[1].endMs})
    }
    println("PASS: 9 Whisper window scenarios and 2000 randomized timestamp cases")
}
