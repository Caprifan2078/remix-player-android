package app.remix.player
import kotlin.math.roundToLong
object LyricClock {
 data class Anchor(val lyricMs:Long,val audioMs:Long)
 data class Mapping(val factor:Double,val offset:Double){
  fun at(ms:Long)=(ms*factor+offset).roundToLong().coerceIn(0L,Lrc.MAX_MS)
 }
 fun mapping(first:Anchor,second:Anchor?=null):Mapping{
  require(first.lyricMs in 0..Lrc.MAX_MS&&first.audioMs in 0..Lrc.MAX_MS)
  if(second==null)return Mapping(1.0,(first.audioMs-first.lyricMs).toDouble())
  require(second.lyricMs in 0..Lrc.MAX_MS&&second.audioMs in 0..Lrc.MAX_MS)
  val span=second.lyricMs-first.lyricMs;require(span>=15000&&second.audioMs>first.audioMs){"Выберите вторую строку хотя бы через 15 секунд"}
  val factor=(second.audioMs-first.audioMs).toDouble()/span
  require(factor in .5..2.0){"Слишком большое расхождение: проверьте выбранные строки"}
  return Mapping(factor,first.audioMs-first.lyricMs*factor)
 }
 fun correct(raw:String,m:Mapping):String{
  require(Lrc.parse(raw).isNotEmpty());require(m.factor.isFinite()&&m.factor in .5..2.0&&m.offset.isFinite())
  val offset=Lrc.offset(raw)
  val tag=Regex("(\\[|<)(\\d{1,3}):(\\d{2})(?:[.:](\\d{1,3}))?(]|>)")
  val result=tag.replace(Regex("\\[offset:[+-]?\\d+]",RegexOption.IGNORE_CASE).replace(raw,"")){x->
   val g=x.groupValues
   if(g[3].toInt()>=60||(g[1]=="["&&g[5]!="]")||(g[1]=="<"&&g[5]!=">"))x.value
   else{val ms=Lrc.timestamp(g[2].toLong()*60000+g[3].toLong()*1000+g[4].padEnd(3,'0').toLong(),offset);g[1]+SubtitleCore.stamp(m.at(ms))+g[5]}
  }.trimStart('\n','\r')
  require(result.length<=LyricDocument.MAX_CHARS);return result
 }
}
