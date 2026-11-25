#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/WhisperSegments.kt"
s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,a[:80]
    s=s.replace(a,b)
replace("words in 2..200","words in 1..200")
replace("count in 2..200","count in 1..200")
replace("    fun merge(windows:List<Window>):List<Segment> {",r'''    /** Adjacent inference windows can repeat only the tail of an utterance.
     * Trim a repeated prefix only when at least two exact normalized words and their
     * measured starts agree. Never use text similarity alone to delete a refrain. */
    private fun trimSharedPrefix(previous:Segment,next:Segment):Segment {
        if(overlap(previous,next)<=0||!validWords(previous)||!validWords(next))return next
        val a=Regex("\\S+").findAll(previous.text).toList()
        val b=Regex("\\S+").findAll(next.text).toList()
        fun normalized(word:String)=tokens.findAll(java.text.Normalizer.normalize(word,java.text.Normalizer.Form.NFKC).lowercase(java.util.Locale.ROOT)).joinToString(" "){it.value}
        val an=a.map{normalized(it.value)};val bn=b.map{normalized(it.value)}
        val shared=(minOf(a.size,b.size-1) downTo 2).firstOrNull{k->
            val offset=a.size-k
            (0 until k).all{i->an[offset+i].isNotEmpty()&&an[offset+i]==bn[i]&&kotlin.math.abs(previous.wordStarts[offset+i]-next.wordStarts[i])<=200}
                &&next.wordStarts[k]>previous.wordStarts.last()
        }?:return next
        return next.copy(startMs=next.wordStarts[shared],text=next.text.substring(b[shared].range.first),wordStarts=next.wordStarts.drop(shared))
    }
    fun merge(windows:List<Window>):List<Segment> {''')
replace("        return chosen.map{it.segment}.sortedBy{it.startMs}",'''        val result=mutableListOf<Candidate>()
        val ordered=chosen.sortedBy{it.segment.startMs}
        for((i,c) in ordered.withIndex()){
            val prior=result.lastOrNull()
            val cleaned=if(prior!=null&&prior.window!=c.window)trimSharedPrefix(prior.segment,c.segment)else c.segment
            val nextStart=ordered.getOrNull(i+1)?.segment?.startMs?:Long.MAX_VALUE
            result.add(if(cleaned.startMs<nextStart)c.copy(segment=cleaned)else c)
        }
        return result.map{it.segment}.sortedBy{it.startMs}''')
p.write_text(s)
print("PASS: conservative Whisper partial boundary duplicate removal")
