from pathlib import Path
import sys
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player'
def replace(p,old,new):
    s=p.read_text();assert s.count(old)==1,(p.name,old,s.count(old));p.write_text(s.replace(old,new))
replace(src/'GenreEngine.kt','Style("Synthwave",100,intArrayOf(0,4,8,10,12),intArrayOf(4,12),intArrayOf(0,2,4,6,8,10,12,14),.12f,.12f,1.05f))','''Style("Synthwave",100,intArrayOf(0,4,8,10,12),intArrayOf(4,12),intArrayOf(0,2,4,6,8,10,12,14),.12f,.12f,1.05f),
        Style("Liquid DnB",174,intArrayOf(0,6,10),intArrayOf(4,12),intArrayOf(0,2,3,6,8,11,14,15),.13f,.08f,1.12f),
        Style("Melodic Techno",126,intArrayOf(0,4,8,12),intArrayOf(4,12),intArrayOf(2,6,7,10,14),.24f,.06f,1.08f))''')
replace(src/'AdaptiveGroove.kt','        "Drum & Bass","Breakcore"->Voice','''        "Liquid DnB"->Voice(55.0,88.0,.085,195.0,7400.0,true,.04)
        "Melodic Techno"->Voice(48.0,92.0,.125,180.0,6900.0,false,.018)
        "Drum & Bass","Breakcore"->Voice''')
replace(src/'LeadSynth.kt','else->intArrayOf(0,4,7,10,14)}','"Liquid DnB"->intArrayOf(0,3,6,10,14);"Melodic Techno"->intArrayOf(0,2,4,6,8,10,12,14);else->intArrayOf(0,4,7,10,14)}')
replace(src/'LeadSynth.kt','        "Synthwave","Hypertechno","Hyperflip"->doubleArrayOf','''        "Liquid DnB"->doubleArrayOf(1.0,.08,.09,.025,.0)
        "Melodic Techno"->doubleArrayOf(1.0,.40,.24,.12,.07)
        "Synthwave","Hypertechno","Hyperflip"->doubleArrayOf''')
replace(src/'GenrePhrase.kt','require(genre in 0..29&&slot in 0..15&&previous in 0..8&&temperature in .3..2.0)','''require(genre in GenreEngine.styles.indices&&slot in 0..15&&previous in 0..8&&temperature in .3..2.0)
        if(genre>=30)return ExtendedPhrase.adapt(genre,slot,probabilities(ExtendedPhrase.parent(genre),minor,slot,previous,temperature))''')
p=src/'GenrePhrase.kt';p.write_text(p.read_text()+'\n'+'''/** Rule-based adaptation of existing trained note probabilities, not newly trained weights. */
internal object ExtendedPhrase {
    fun parent(genre:Int)=when(genre){30->8;31->0;else->error("Unknown extended genre")}
    fun adapt(genre:Int,slot:Int,base:DoubleArray):DoubleArray {
        require(genre in 30..31&&slot in 0..15&&base.size==9&&base.all{it.isFinite()&&it>0})
        val accents=if(genre==30) slot in listOf(0,3,6,10,14) else slot%2==0
        val result=DoubleArray(9){k->val w=when{
            k==0->if(accents).65 else if(genre==30)1.65 else 1.20
            genre==30&&k in listOf(1,3,5)->1.30
            genre==31&&k in listOf(1,3,5,8)->if(accents)1.50 else 1.10
            else->.90
        };base[k]*w}
        val total=result.sum();return DoubleArray(9){result[it]/total}
    }
}
''')
replace(src/'GenrePhrase.kt','30 profile-conditioned symbolic melody model. Trained on generated patterns.','30 trained synthetic-pattern profiles plus two rule-adapted profiles.')
replace(src/'GenreCheckpoint.kt','styles.size in 1..30','styles.size in 1..GenreEngine.styles.size')
replace(src/'GenreCheckpoint.kt','genre-render-v8','genre-render-v9')
replace(src/'MainActivity.kt','a.length() in 1..30','a.length() in 1..GenreEngine.styles.size')
replace(src/'MainActivity.kt','30 шаблонов · умное сведение баса и разные тембры','32 шаблона · умное сведение баса и разные тембры')
replace(src/'RemixAdvisor.kt','"Hypertechno"->"hard"','"Hypertechno"->"hard"') if False else None
replace(src/'RemixAdvisor.kt','"Hyperflip","Breakcore","Drum & Bass"->"breaks"','"Hyperflip","Breakcore","Drum & Bass","Liquid DnB"->"breaks"')
replace(root/'tests/GenreTest.kt','check(GenreEngine.styles.size==30)','check(GenreEngine.styles.size==32)')
replace(root/'tests/GenreTest.kt','fingerprints.distinct().size==30','fingerprints.distinct().size==GenreEngine.styles.size')
replace(root/'tests/GenreTest.kt','30 distinct procedural beats','32 distinct procedural beats')
replace(root/'tests/GenrePhraseTest.kt','sequences.distinct().size==30','sequences.distinct().size==GenreEngine.styles.size')
replace(root/'tests/GenrePhraseTest.kt','distributions.distinct().size==30','distributions.distinct().size==GenreEngine.styles.size')
replace(root/'tests/GenrePhraseTest.kt','30 genre-conditioned symbolic distributions, 30 distinct deterministic sequences','32 genre-conditioned distributions (30 trained, 2 adapted), 32 distinct deterministic sequences')
replace(root/'tests/Release09Test.kt','model-free rendering all 30 genres','model-free rendering all 32 genres')
print('PASS: Liquid DnB and Melodic Techno, compatible trained-profile adaptation, expanded checkpoint bounds')
