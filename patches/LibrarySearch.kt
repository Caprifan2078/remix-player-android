package app.remix.player
import java.text.Normalizer
import java.util.Locale
/** Search all metadata, keeping version terms in one recording plus its original. */
class LibrarySearch<T>(items:List<T>, private val id:(T)->String, group:(T)->String, fields:(T)->List<String>){
    private data class Row<T>(val item:T,val text:String,val folded:String=LyricsMatch.searchKey(text))
    private val roots=items.filter{ id(it)==group(it) }.associateBy(id)
    private val rootText=roots.mapValues{(_,item)->normalize(fields(item).joinToString(" "))}
    private val rootFold=rootText.mapValues{(_,text)->LyricsMatch.searchKey(text)}
    private val rows=items.filter{group(it) in roots}.groupBy(group).mapValues{(key,versions)->versions.map{Row(it, if(id(it)==key)rootText.getValue(key)else rootText.getValue(key)+" "+normalize(fields(it).joinToString(" ")))}}
    private val versionRows=rows.mapValues{(key,list)->list.filter{row->id(row.item)!=key}}
    private val allVersions=versionRows.mapValues{(_,list)->list.map{it.item}}
    data class Match<T>(val original:T,val originalMatches:Boolean,val versions:List<T>)
    private var previousTerms:List<String>?=null
    private var previousResult:Map<String,Match<T>> = emptyMap()
    @Synchronized fun find(query:String):Map<String,Match<T>>{
        val direct=findTerms(terms(query))
        if(direct.isNotEmpty())return direct
        for(alternative in LyricsMatch.layoutVariants(query)){
            val next=terms(alternative);if(next.isEmpty()||next==terms(query))continue
            val result=findTerms(next);if(result.isNotEmpty())return result
        }
        return direct
    }
    private fun terms(query:String)=normalize(query).split(' ').filter{it.isNotEmpty()}.distinct()
    private fun findTerms(terms:List<String>):Map<String,Match<T>>{
        val old=previousTerms
        if(old==terms)return previousResult
        if(terms.isEmpty()){
            previousTerms=terms;previousResult=roots.mapValues{(_,root)->Match(root,true,emptyList())};return previousResult
        }
        val folded=terms.map(LyricsMatch::searchKey)
        fun matches(text:String,canonical:String)=terms.indices.all{i->text.contains(terms[i])||(folded[i].isNotBlank()&&canonical.contains(folded[i]))}
        val keys=if(old!=null&&old.isNotEmpty()&&old.all{prior->terms.any{it.contains(prior)&&LyricsMatch.searchKey(it).contains(LyricsMatch.searchKey(prior))}})previousResult.keys else roots.keys
        val out=linkedMapOf<String,Match<T>>()
        for(key in keys){
            val root=roots.getValue(key)
            val originalMatches=matches(rootText.getValue(key),rootFold.getValue(key))
            val versions=if(originalMatches)allVersions[key].orEmpty()else{
                var matched:MutableList<T>?=null
                for(row in versionRows[key].orEmpty()){
                    if(matches(row.text,row.folded)){if(matched==null)matched=ArrayList();matched.add(row.item)}
                }
                matched?:emptyList()
            }
            if(originalMatches||versions.isNotEmpty())out[key]=Match(root,originalMatches,versions)
        }
        previousTerms=terms;previousResult=out;return out
    }
    companion object{
        private val marks=Regex("\\p{M}+")
        private val separators=Regex("[^\\p{L}\\p{N}]+")
        fun normalize(s:String):String=Normalizer.normalize(s.lowercase(Locale.ROOT),Normalizer.Form.NFKD).replace(marks,"").replace(separators," ").trim()
    }
}
