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
  return if(phrases?.complete==true)Result(phrases.lrc,false) else null
 }
}
