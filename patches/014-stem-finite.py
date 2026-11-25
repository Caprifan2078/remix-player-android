from pathlib import Path
import sys
src=Path(sys.argv[1])/"app/src/main/java/app/remix/player"
def replace(name,a,b):
    p=src/name;s=p.read_text();assert s.count(a)==1,(name,a);p.write_text(s.replace(a,b))
replace("StemCheckpoint.kt","tail=FloatArray(tail.size){r.readFloat()};require(r.read()==-1)","tail=FloatArray(tail.size){r.readFloat()};require(tail.all{validSample(it)});require(r.read()==-1)")
replace("StemCheckpoint.kt","    fun commit(values:(Int)->Float){","    private fun validSample(v:Float)=v.isFinite()&&kotlin.math.abs(v)<=32f\n    fun commit(values:(Int)->Float){")
replace("StemCheckpoint.kt","        val index=next;val size=writeSize(index);val digests=LongArray(count);val newTail=FloatArray(tail.size)",'''        val index=next;val size=writeSize(index);val digests=LongArray(count);val newTail=FloatArray(tail.size)
        // Reject malformed output before touching any committed PCM file.
        val used=if(index<starts.lastIndex)block else size
        for(channel in 0 until count*2)for(i in 0 until used){
            if(i%8192==0)check(!Thread.currentThread().isInterrupted)
            require(validSample(values(channel*block+i))){"Модель вернула нечисловой или экстремальный сигнал"}
        }''')
replace("StemEngine.kt",'signature="stem-v1:"','signature="stem-v2:"')
print("PASS: finite stem block validation before commit")
