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
    private val ru="абвгдежзийклмнопрстуфхцчшщъыьэюя"
    private val latin=listOf("a","b","v","g","d","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","kh","ts","ch","sh","shch","","y","","e","yu","ya")
    private fun roman(s:String)=buildString{for(c in key(s)){val i=ru.indexOf(c);append(if(i<0)c.toString() else latin[i])}}
    private fun cyrillic(s:String):String{
        val text=key(s);if(text.any{it in ru})return text
        val pairs=latin.zip(ru.toList()).filter{it.first.isNotEmpty()}.distinctBy{it.first}.sortedByDescending{it.first.length}
        return buildString{var i=0;while(i<text.length){val pair=pairs.firstOrNull{text.startsWith(it.first,i)};if(pair==null){append(text[i]);i++}else{append(pair.second);i+=pair.first.length}}}
    }
    /** Loose key for discovery only, never sufficient to attach timed lyrics. */
    fun searchKey(s:String)=roman(s).replace("shch","sch").replace("kh","h").replace("ia","ya").replace("iu","yu").replace("yo","e").replace("iy","i").replace("ii","i").replace("y","i")
    fun layoutVariants(s:String):List<String>{
        val en="`qwertyuiop[]asdfghjkl;'zxcvbnm,.";val cy="ёйцукенгшщзхъфывапролджэячсмитьбю"
        fun flip(word:String):String{
            val w=word.lowercase(Locale.ROOT);val letters=w.filter{it.isLetter()}
            if(letters.length<2)return word
            val from=when{letters.all{it in en}->en;letters.all{it in cy}->cy;else->return word};val to=if(from==en)cy else en
            return w.map{c->val i=from.indexOf(c);if(i<0)c else to[i]}.joinToString("")
        }
        val words=s.trim().split(Regex("\\s+"));val changed=words.map(::flip)
        return (listOf(changed.joinToString(" "))+words.indices.take(8).map{i->words.mapIndexed{j,w->if(i==j)changed[j]else w}.joinToString(" ")}).filter{it!=s}.distinct()
    }
    private fun artistKey(s:String):String{
        val k=key(s)
        return if(k.replace(" ","") in setOf("tatu","тату"))"tatu" else k
    }
    private fun cross(a:String,b:String)=a.isNotBlank()&&b.isNotBlank()&&((a.any{it in ru}&&b.none{it in ru})||(b.any{it in ru}&&a.none{it in ru}))&&roman(a)==roman(b)
    fun variants(q:Query):List<Query>{
        val alias=if(artistKey(q.artist)=="tatu")if(key(q.artist).any{it in ru})"t.A.T.u." else "Тату" else q.artist
        fun other(s:String)=if(key(s).any{it in ru})roman(s) else cyrillic(s)
        val alternate=Query(other(q.title),if(alias!=q.artist)alias else other(q.artist))
        return listOf(q,Query(q.title,if(alias!=q.artist)alias else other(q.artist)),Query(alternate.title,q.artist),alternate).filter{it.title.isNotBlank()}.distinctBy{key(it.title) to key(it.artist)}.take(4)
    }
    data class Candidate(val title:String,val artist:String,val seconds:Long,val synced:Boolean)
    fun choose(q:Query,seconds:Long?,rows:List<Candidate>):Int?{
        val title=key(q.title);val artist=artistKey(q.artist);val timed=seconds!=null&&seconds>0
        if(title.isBlank())return null
        val found=rows.indices.filter{i->
            val r=rows[i];val rt=key(r.title);val ra=artistKey(r.artist)
            val titleOk=rt==title||(timed&&artist.isNotBlank()&&cross(title,rt))
            val artistOk=artist.isBlank()||artist==ra||(timed&&cross(artist,ra))
            r.synced&&titleOk&&artistOk&&(!timed||kotlin.math.abs(r.seconds-seconds!!)<=3)
        }
        if(found.isEmpty())return null
        if(artist.isBlank()&&(!timed||found.map{artistKey(rows[it].artist)}.distinct().size!=1))return null
        if(!timed)return found.singleOrNull()
        val ranked=found.sortedBy{kotlin.math.abs(rows[it].seconds-seconds!!)}
        return if(ranked.size>1&&kotlin.math.abs(rows[ranked[0]].seconds-seconds!!)==kotlin.math.abs(rows[ranked[1]].seconds-seconds!!))null else ranked.first()
    }
}
