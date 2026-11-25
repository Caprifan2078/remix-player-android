package app.remix.player
import java.io.File
import kotlin.io.path.createTempDirectory
fun main(){
 val root=createTempDirectory("stem-finite").toFile()
 try{
  for((index,bad) in listOf(Float.NaN,Float.POSITIVE_INFINITY,Float.NEGATIVE_INFINITY,33f).withIndex()){
   val dir=File(root,"case-$index"); val c=StemCheckpoint.open(dir,"qa",12,4,8,2)
   c.commit{.1f};check(c.next==1);val snapshot=File(dir,"state.bin").readBytes();val previous=(0..3).map{File(dir,"$it.pcm").readBytes()}
   val result=runCatching{c.commit{if(it==7*8+1)bad else .2f}}
   check(result.isFailure){"Invalid model output was committed: $bad"}
   check(c.next==1&&File(dir,"state.bin").readBytes().contentEquals(snapshot))
   for(i in 0..3)check(File(dir,"$i.pcm").readBytes().contentEquals(previous[i]))
   val reopened=StemCheckpoint.open(dir,"qa",12,4,8,2);check(reopened.next==1);reopened.commit{.2f};check(reopened.committedFrames==12L)
  }
  val d=File(root,"tail");val c=StemCheckpoint.open(d,"qa",12,4,8,2)
  check(runCatching{c.commit{if(it==7*8+7)Float.NaN else .1f}}.isFailure)
  check(c.next==0&&!File(d,"state.bin").exists()&&d.listFiles().orEmpty().isEmpty())
  println("PASS: NaN, positive/negative infinity, extreme output and overlap tail rejected before disk mutation; valid resume preserved")
 }finally{root.deleteRecursively()}
}
