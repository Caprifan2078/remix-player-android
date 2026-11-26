package app.remix.player
import android.content.Context
import android.media.MediaMetadataRetriever
import android.net.Uri
object TrackLyricSource {
 data class Info(val title:String,val artist:String,val album:String,val seconds:Long?,val tagTitle:String?=null,val tagArtist:String?=null)
 fun embedded(c:Context,uri:Uri):String?=runCatching{c.contentResolver.openInputStream(uri)?.buffered()?.use{EmbeddedLyrics.read(it)}}.getOrNull()
 fun metadata(c:Context,uri:Uri,title:String,artist:String,seconds:Long?):Info{
  val r=MediaMetadataRetriever()
  try{
   r.setDataSource(c,uri)
   fun tag(key:Int)=r.extractMetadata(key)?.trim()?.takeIf{it.isNotBlank()}?.take(300)
   val actualTitle=tag(MediaMetadataRetriever.METADATA_KEY_TITLE)
   val actualArtist=tag(MediaMetadataRetriever.METADATA_KEY_ARTIST)?:tag(MediaMetadataRetriever.METADATA_KEY_ALBUMARTIST)?:tag(MediaMetadataRetriever.METADATA_KEY_AUTHOR)?:tag(MediaMetadataRetriever.METADATA_KEY_COMPOSER)
   return Info(title.ifBlank{actualTitle.orEmpty()},if(LyricsSearchPlan.artistKnown(artist))artist else actualArtist?:artist,tag(MediaMetadataRetriever.METADATA_KEY_ALBUM).orEmpty(),tag(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull()?.takeIf{it>0}?.let{(it+500)/1000}?:seconds,actualTitle,actualArtist)
  }catch(e:Exception){return Info(title,artist,"",seconds)}finally{runCatching{r.release()}}
 }
 fun search(c:Context,uri:Uri,title:String,artist:String,seconds:Long?):Pair<List<LyricsMatch.Candidate>,Long?>{
  val info=metadata(c,uri,title,artist,seconds)
  val local=embedded(c,uri)
  val stored=local?.let{raw->
   val timed=Lrc.parse(raw).isNotEmpty()
   LyricsMatch.Candidate(-1,info.title+" · из файла",info.artist,info.seconds,raw.takeIf{timed},LyricDocument.plain(raw))
  }
  val results=mutableListOf<LyricsMatch.Candidate>()
  var replied=false
  var failure:Exception?=null
  val titles=LyricsSearchPlan.metadataTitles(info.title,info.tagTitle)
  for((i,queryTitle) in titles.withIndex()){
   if(Thread.currentThread().isInterrupted)throw InterruptedException()
   val queryArtist=if(i>0&&LyricsSearchPlan.artistKnown(info.tagArtist.orEmpty()))info.tagArtist.orEmpty() else info.artist
   try{
    val found=LyricsLookup.search(queryTitle,queryArtist,info.seconds,expanded=i==0)
    replied=true;results.addAll(found)
    if(found.any{LyricsSearchPlan.exact(queryTitle,queryArtist,info.seconds,it)})break
   }catch(e:Exception){
    if(e is InterruptedException||Thread.currentThread().isInterrupted)throw InterruptedException()
    failure=e;break
   }
  }
  if(!replied&&stored==null&&failure!=null)throw failure
  val online=LyricsMatch.rank(results,info.title,info.artist,info.seconds).take(10)
  // Embedded lyrics are a selectable local source, never a reason to suppress internet lookup.
  return (listOfNotNull(stored)+online) to info.seconds
 }
 /** Shared one-track and whole-library automatic search. Keep a valid saved text on network failure. */
 fun automatic(c:Context,uri:Uri,title:String,artist:String,current:String,online:Boolean):String?{
  check(!Thread.currentThread().isInterrupted)
  fun merge(base:String?,next:String?)=BatchLyricPolicy.merge(base,next,{Lrc.parse(it).isNotEmpty()},LyricDocument::plain)
  var known=merge(current,embedded(c,uri))
  if(!online||known?.let{Lrc.parse(it).isNotEmpty()}==true)return known
  val info=metadata(c,uri,title,artist,null)
  val identities=listOf(info.title to info.artist,(info.tagTitle?:info.title) to (info.tagArtist?:info.artist)).distinctBy{LyricsMatch.normalize(it.first) to LyricsMatch.normalize(it.second)}
  for((name,who) in identities){
   if(!LyricsSearchPlan.artistKnown(who)||name.isBlank()||info.seconds==null)continue
   try{
    val matches=LyricsLookup.search(name,who,info.seconds,false)
    val candidate=BatchLyricPolicy.chooseAutomatic(matches,name,who,info.seconds)
    known=merge(known,candidate)
    if(known?.let{Lrc.parse(it).isNotEmpty()}==true)break
   }catch(e:Exception){
    if(e is InterruptedException||Thread.currentThread().isInterrupted)throw InterruptedException()
    if(known==null)throw e
    break
   }
  }
  check(!Thread.currentThread().isInterrupted)
  return known
 }
}
