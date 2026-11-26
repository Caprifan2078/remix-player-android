package app.remix.player
fun main(){
 val p=AutoTranslationPolicy
 val text="These are some fictional lines for the language confidence tests."
 val supported=setOf("en","ru","es")
 val en=AutoTranslationPolicy.Guess("en",.95f)
 val ru=AutoTranslationPolicy.Guess("ru",.90f)
 check(p.language(text,listOf(en),supported)=="en")
 check(p.language(text,listOf(ru),supported)=="ru")
 check(p.language(text,listOf(en,ru),supported)==null)
 check(p.language(text,listOf(en.copy(confidence=.79f)),supported)==null)
 check(p.language("hello",listOf(en),supported)==null)
 check(p.language(text,listOf(en.copy(language="und")),supported)==null)
 check(p.language(text,listOf(en.copy(language="de")),supported)==null)
 check(p.language(text,listOf(en.copy(confidence=Float.NaN)),supported)==null)
 check(p.valid(listOf("a","","b"),listOf("а","","б")))
 check(!p.valid(listOf("a","b"),listOf("а")))
 check(!p.valid(listOf("a"),listOf("")))
 check(!p.valid(listOf(""),listOf("а")))
 check(p.key("u","a")!=p.key("u","b"))
 check(p.pending(true,"lyrics",false,false))
 check(!p.pending(true,"lyrics",true,false))
 check(!p.pending(true,"lyrics",false,true))
 check(!p.pending(false,"lyrics",false,false))
 println("PASS: 17 automatic language and translation policy checks")
}
