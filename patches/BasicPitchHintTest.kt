package app.remix.player
import kotlin.math.*
fun main(){
 val n=BasicPitchHint.NOTES;val frames=BasicPitchHint.FRAMES
 fun output(block:(Int,Int)->Float)=FloatArray(n*frames){block(it/n,it%n+21)}
 val a=output{_,note->if(note==33).9f else .01f}
 check(BasicPitchHint.window(a)==9)
 check(BasicPitchHint.window(output{_,note->if(note==45).9f else .01f})==9)
 check(BasicPitchHint.window(output{_,note->if(note==33||note==36).9f else .01f})==null)
 check(BasicPitchHint.window(output{t,note->if(note==if(t%2==0)33 else 36).9f else .01f})==null)
 check(BasicPitchHint.window(output{_,note->if(note==72).9f else .01f})==null)
 check(BasicPitchHint.window(output{_,_->0f})==null)
 check(BasicPitchHint.consensus(listOf(9,null,9))==9)
 check(BasicPitchHint.consensus(listOf(9,0,4))==null)
 check(BasicPitchHint.consensus(listOf(9))==null)
 check(abs(BasicPitchHint.frequencyNear(9,49.0)!!-55)<1e-6)
 check(BasicPitchHint.frequencyNear(3,49.0)==null)
 check(BasicPitchHint.frequencyNear(9,Double.NaN)==null)
 val original=HardKick.curve("Hardstyle",44100)!!
 check(!original.contentEquals(HardKick.curve("Hardstyle",44100,55.0)))
 check(original.contentEquals(HardKick.curve("Hardstyle",44100,1000.0)))
 println("PASS: 14 neural note hint and bounded tuning checks")
}
