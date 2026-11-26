package app.remix.player
/** Preserve reference text. Never publish a partial, ambiguous or fabricated mapping. */
object KnownLyricAlignment {
 data class Result(val lrc:String,val wordLevel:Boolean)
 fun align(heard:String,reference:String):Result? {
  if(heard.isBlank()||reference.isBlank())return null
  val words=try{LyricAlign.align(heard,reference)}catch(e:IllegalArgumentException){null}
  if(words?.complete==true)return Result(words.lrc,true)
  check(!Thread.currentThread().isInterrupted)
  val phrases=try{PhraseAlign.align(heard,reference,false)}catch(e:IllegalArgumentException){null}
  return if(phrases?.complete==true)Result(phrases.lrc,false) else alignNoisyPhrases(heard,reference)
 }
 /** Conservative line-level recovery when ASR mishears individual words.
  * Preserve the exact reference and use only observed phrase onsets. Reject ambiguous paths. */
 fun alignNoisyPhrases(heard:String,reference:String):Result?{
  if(heard.length>LyricDocument.MAX_CHARS||reference.length>LyricDocument.MAX_CHARS)return null
  check(!Thread.currentThread().isInterrupted){"Cancelled"}
  val tokenPattern=Regex("[\\p{L}\\p{N}]+")
  fun tokens(s:String)=tokenPattern.findAll(java.text.Normalizer.normalize(s,java.text.Normalizer.Form.NFKC).lowercase(java.util.Locale.ROOT).replace('ё','е')).map{it.value}.take(65).toList()
  val lines=LyricDocument.plain(reference).lineSequence().map{it.trim()}.filter{it.isNotEmpty()}.take(301).toList()
  val source=Lrc.parse(heard).take(501).map{it.ms to tokens(WordLyrics.parse(it).text)}
  if(lines.isEmpty()||lines.size>300||source.size>500||source.size<lines.size)return null
  val targets=lines.map(::tokens)
  if(targets.any{it.isEmpty()||it.size>64})return null
  fun matches(a:List<String>,b:List<String>):Boolean{
   if(b.isEmpty()||b.size>64||a.first()!=b.first())return false
   if(a.size<4||b.size<4)return a==b
   val span=maxOf(a.size,b.size)
   val need=maxOf(3,(span*72+99)/100)
   if(minOf(a.size,b.size)<need)return false
   val d=IntArray(b.size+1)
   for(x in a){
    var diagonal=0
    for(j in b.indices){val before=d[j+1];d[j+1]=if(x==b[j])diagonal+1 else maxOf(d[j],d[j+1]);diagonal=before}
   }
   return d.last()>=need
  }
  val m=source.size
  var prior=IntArray(m)
  val parents=Array(lines.size){IntArray(m){-1}}
  for(i in lines.indices){
   check(!Thread.currentThread().isInterrupted){"Cancelled"}
   val next=IntArray(m);var count=0;var unique=-1
   for(j in 0 until m){
    if(i>0&&j>0&&prior[j-1]>0){
     unique=if(count==0&&prior[j-1]==1)j-1 else -1
     count=minOf(2,count+prior[j-1])
    }
    if((i==0||count>0)&&matches(targets[i],source[j].second)){
     next[j]=if(i==0)1 else count
     parents[i][j]=unique
    }
   }
   prior=next
   if(prior.none{it>0})return null
  }
  if(prior.sum()!=1)return null
  val selected=IntArray(lines.size)
  var j=prior.indexOfFirst{it==1}
  for(i in lines.indices.reversed()){selected[i]=j;j=parents[i][j]}
  val times=selected.map{source[it].first}
  if(times.zipWithNext().any{(a,b)->b<=a})return null
  val lrc=lines.indices.joinToString("\n"){i->"["+SubtitleCore.stamp(times[i])+"]"+lines[i]}
  return Result(lrc,false)
 }
}
