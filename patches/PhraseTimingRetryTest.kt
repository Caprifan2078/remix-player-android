package app.remix.player
fun main(){
 val p=PhraseTimingRetry
 val a=PhraseTimingRetry.Span(1000,3500,"Hello bright world",emptyList())
 val b=a.copy(start=1100,end=3400,words=listOf(1200,1800,2500))
 check(p.eligible(a))
 check(p.select(a,listOf(b))==b.words)
 check(p.select(a,listOf(b.copy(text="Hello bright words")))==null)
 check(p.select(a,listOf(b,b))==null)
 check(p.select(a,listOf(b.copy(words=listOf(1200,1200,2500))))==null)
 check(p.select(a,listOf(b.copy(words=listOf(999,1800,2500))))==null)
 check(p.select(a,listOf(b.copy(words=listOf(1200,1800,3500))))==null)
 check(p.select(a,listOf(b.copy(start=1600)))==null)
 check(!p.eligible(a.copy(end=13001)))
 check(!p.eligible(a.copy(words=b.words)))
 check(p.select(a,listOf(b.copy(text="HELLO  bright world")))==b.words)
 println("PASS: 11 phrase timing retry cases")
}
