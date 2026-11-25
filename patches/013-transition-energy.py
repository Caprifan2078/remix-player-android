#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/TransitionMix.kt"
s=p.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
replace('    fun render(first:', '''    private data class Stats(val correlation:Double,val peakA:Double,val peakB:Double)
    /** Analyze only the overlap, with constant memory. Negative correlation is not boosted. */
    private fun analyze(first:File,second:File,skip:Long,frames:Long):Stats {
        var aa=0.0;var bb=0.0;var ab=0.0;var peakA=0.0;var peakB=0.0
        first.inputStream().buffered(65536).use{x->second.inputStream().buffered(65536).use{y->
            var left=skip*4
            while(left>0){val n=x.skip(left);if(n<=0)throw EOFException();left-=n}
            repeatFrames(frames){i->
                if(i%8192==0L)check(!Thread.currentThread().isInterrupted){"Отменено"}
                repeat(2){val a=StemCore.readShort(x)/32768.0;val b=StemCore.readShort(y)/32768.0;aa+=a*a;bb+=b*b;ab+=a*b;peakA=max(peakA,abs(a));peakB=max(peakB,abs(b))}
            }
        }}
        val rho=if(aa>0&&bb>0)(ab/sqrt(aa*bb)).coerceIn(0.0,1.0)else 0.0
        return Stats(rho,peakA,peakB)
    }
    private fun normalizer(a:Double,b:Double,s:Stats):Double {
        val power=sqrt(a*a+b*b+2*s.correlation*a*b)
        val peak=(a*s.peakA+b*s.peakB)/(32767.0/32768)
        return maxOf(1.0,power,peak)
    }
    fun render(first:''')
replace('try{first.inputStream()', 'try{val stats=analyze(first,second,a-overlap,overlap);first.inputStream()')
replace('val norm=max(1.0,gainA+gainB);','val norm=if(i==0L||i==overlap-1)1.0 else normalizer(gainA,gainB,stats);')
p.write_text(s)
