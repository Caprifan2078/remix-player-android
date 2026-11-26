from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'app/src/main/java/app/remix/player/LibrarySearch.kt'
s=p.read_text()
old="""        val terms=normalize(query).split(' ').filter{it.isNotEmpty()}.distinct()
        val old=previousTerms"""
new="""        val direct=findTerms(terms(query))
        if(direct.isNotEmpty())return direct
        val corrected=alternateLayout(query)?:return direct
        val alternative=terms(corrected)
        return if(alternative.isEmpty()||alternative==terms(query))direct else findTerms(alternative)
    }
    private fun terms(query:String)=normalize(query).split(' ').filter{it.isNotEmpty()}.distinct()
    private fun findTerms(terms:List<String>):Map<String,Match<T>>{
        val old=previousTerms"""
assert s.count(old)==1
s=s.replace(old,new)
old='        private val marks='
new='''        private const val latin="`qwertyuiop[]asdfghjkl;'zxcvbnm,."
        private const val cyrillic="ёйцукенгшщзхъфывапролджэячсмитьбю"
        private fun alternateLayout(query:String):String?{
            val lower=query.lowercase(Locale.ROOT)
            val letters=lower.filter{it.isLetter()}
            if(letters.length<3)return null
            val from=when{letters.all{it in latin}->latin;letters.all{it in cyrillic}->cyrillic;else->return null}
            val to=if(from==latin)cyrillic else latin
            return lower.map{ch->val i=from.indexOf(ch);if(i<0)ch else to[i]}.joinToString("")
        }
        private val marks='''
assert s.count(old)==1
p.write_text(s.replace(old,new))
p=root/'tests/run-core.sh'
s=p.read_text()
old='StructureCore,TransitionMix,MixerCore'
assert s.count(old)==1
p.write_text(s.replace(old,'StructureCore,TransitionMix,SafeTransitionOutput,MixerCore'))
print('PASS: search layout fallback and core compile dependency')
