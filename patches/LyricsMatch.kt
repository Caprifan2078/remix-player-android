package app.remix.player

import java.util.Locale

/** Normalize common filename artifacts without guessing that a remix is an original. */
internal object LyricsMatch {
    data class Query(val title:String,val artist:String)
    private fun clean(s:String)=s.trim()
        .replace(Regex("(?i)\\.(mp3|flac|wav|m4a|ogg|opus)$"),"")
        .replace(Regex("(?i)[\\[(]?(?:www[._])?[a-z0-9_-]+\\.(?:com|ru|net|org)[\\])]?")," ")
        .replace(Regex("(?i)[\\[(]?www_[a-z0-9_-]+_(?:ru|com|net)[\\])]?")," ")
        .replace('_',' ').replace(Regex("\\s+")," ").trim(' ','-','_')
    fun query(title:String,artist:String):Query{
        var t=clean(title)
        var a=clean(artist).takeUnless{it.lowercase(Locale.ROOT) in setOf("неизвестный исполнитель","unknown artist","unknown","<unknown>","неизвестно")} .orEmpty()
        if(a.isBlank()){
            val parts=t.split(Regex("\\s+[-–—]\\s+"),limit=2)
            if(parts.size==2&&parts.all{it.isNotBlank()}){a=parts[0];t=parts[1]}
        }
        return Query(t,a)
    }
    fun key(s:String)=clean(s).lowercase(Locale.ROOT).replace('ё','е').replace(Regex("[^\\p{L}\\p{N}]+")," ").trim()
    data class Candidate(val title:String,val artist:String,val seconds:Long,val synced:Boolean)
    fun choose(q:Query,seconds:Long?,rows:List<Candidate>):Int?{
        val title=key(q.title);val artist=key(q.artist)
        if(title.isBlank())return null
        val found=rows.indices.filter{i->val r=rows[i];r.synced&&key(r.title)==title&&(artist.isBlank()||key(r.artist)==artist)&&(seconds==null||seconds<=0||kotlin.math.abs(r.seconds-seconds)<=3)}
        if(found.isEmpty())return null
        if(artist.isBlank()&&(seconds==null||seconds<=0||found.map{key(rows[it].artist)}.distinct().size!=1))return null
        if(seconds==null||seconds<=0)return found.singleOrNull()
        val ranked=found.sortedBy{kotlin.math.abs(rows[it].seconds-seconds)}
        return if(ranked.size>1&&kotlin.math.abs(rows[ranked[0]].seconds-seconds)==kotlin.math.abs(rows[ranked[1]].seconds-seconds))null else ranked.first()
    }
}
