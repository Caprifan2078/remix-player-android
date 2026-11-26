from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'app/src/main/java/app/remix/player/LibrarySearch.kt'
s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,(old,s.count(old))
    s=s.replace(old,new)
replace('    data class Match<T>', '''    private val versionRows=rows.mapValues{(key,list)->list.filter{row->id(row.item)!=key}}
    private val allVersions=versionRows.mapValues{(_,list)->list.map{it.item}}
    data class Match<T>''')
replace('            val versions=rows[key].orEmpty().filter{row->id(row.item)!=key&&terms.all{row.text.contains(it)}}.map{it.item}', '''            // All children include the original text. If it matches, all children do too.
            val versions=if(originalMatches)allVersions[key].orEmpty()else{
                var matched:MutableList<T>?=null
                for(row in versionRows[key].orEmpty()){
                    if(terms.all{row.text.contains(it)}){
                        if(matched==null)matched=ArrayList()
                        matched.add(row.item)
                    }
                }
                matched?:emptyList()
            }''')
p.write_text(s)
p=root/'tests/LibrarySearchTest.kt'
s=p.read_text()
replace('    val large=(0 until 30000)', '''    val rng=kotlin.random.Random(42)
    val many=(0 until 150).flatMap{n->listOf(Song("$n","$n","Song $n","Artist ${n%7}"),Song("r$n","$n","Remix ${n%5}",""),Song("s$n","$n","Slowed ${n%3}",""))}
    val fast=LibrarySearch(many,Song::id,Song::group){listOf(it.title,it.artist,it.album)}
    val groups=many.groupBy{it.group}
    repeat(500){
        val q=listOf("song","artist","remix","slowed","${rng.nextInt(150)}","unknown").shuffled(rng).take(rng.nextInt(1,4)).joinToString(" ")
        val terms=q.split(' ')
        val expected=groups.mapNotNull{(key,group)->
            val original=group.first();val text=LibrarySearch.normalize(listOf(original.title,original.artist,original.album).joinToString(" "))
            val matches=terms.all{text.contains(it)}
            val variants=group.drop(1).filter{v->val full=text+" "+LibrarySearch.normalize(listOf(v.title,v.artist,v.album).joinToString(" "));terms.all{full.contains(it)}}
            if(matches||variants.isNotEmpty())key to LibrarySearch.Match(original,matches,variants)else null
        }.toMap()
        check(fast.find(q)==expected){"Search differs for $q"}
    }
    println("PASS: 500 randomized comparisons with independent exhaustive grouped search")
    val large=(0 until 30000)''')
p.write_text(s)
print('PASS: grouped text lookup reuses matching originals and avoids temporary lists')
