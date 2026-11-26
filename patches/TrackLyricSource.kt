package app.remix.player
import android.content.Context
import android.media.MediaMetadataRetriever
import android.net.Uri
object TrackLyricSource {
 data class Info(val title:String,val artist:String,val album:String,val seconds:Long?)
 fun embedded(c:Context,uri:Uri):String?=runCatching{c.contentResolver.openInputStream(uri)?.buffered()?.use{EmbeddedLyrics.read(it)}}.getOrNull()
 fun metadata(c:Context,uri:Uri,title:String,artist:String,seconds:Long?):Info{
  val r=MediaMetadataRetriever()
  try{
   r.setDataSource(c,uri)
   fun tag(key:Int)=r.extractMetadata(key)?.trim()?.takeIf{it.isNotBlank()}?.take(300)
   val actualTitle=tag(MediaMetadataRetriever.METADATA_KEY_TITLE)
   val actualArtist=tag(MediaMetadataRetriever.METADATA_KEY_ARTIST)?:tag(MediaMetadataRetriever.METADATA_KEY_ALBUMARTIST)?:tag(MediaMetadataRetriever.METADATA_KEY_AUTHOR)?:tag(MediaMetadataRetriever.METADATA_KEY_COMPOSER)
   return Info(title.ifBlank{actualTitle.orEmpty()},if(LyricsSearchPlan.artistKnown(artist))artist else actualArtist?:artist,tag(MediaMetadataRetriever.METADATA_KEY_ALBUM).orEmpty(),tag(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull()?.takeIf{it>0}?.let{(it+500)/1000}?:seconds)
  }catch(e:Exception){return Info(title,artist,"",seconds)}finally{runCatching{r.release()}}
 }
 fun search(c:Context,uri:Uri,title:String,artist:String,seconds:Long?):Pair<List<LyricsMatch.Candidate>,Long?>{
  val info=metadata(c,uri,title,artist,seconds)
  val local=embedded(c,uri)
  if(local!=null){val timed=Lrc.parse(local).isNotEmpty();return listOf(LyricsMatch.Candidate(-1,info.title+" · из файла",info.artist,info.seconds,local.takeIf{timed},LyricDocument.plain(local))) to info.seconds}
  return LyricsLookup.search(info.title,info.artist,info.seconds) to info.seconds
 }
}
