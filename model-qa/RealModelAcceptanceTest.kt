package app.remix.player

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.core.content.FileProvider
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File
import kotlin.math.*

/** Real publisher weights, real Android engines; generated fixtures are not a music quality benchmark. */
@RunWith(AndroidJUnit4::class)
class RealModelAcceptanceTest {
    private val c=InstrumentationRegistry.getInstrumentation().targetContext
    private fun uri(file:File)=FileProvider.getUriForFile(c,"app.remix.player.files",file)
    private fun music(raw:File,wav:File,frames:Int){
        raw.outputStream().buffered(65536).use{out->
            repeat(frames){i->
                val t=i/44100.0
                val beat=t%.5
                val bass=.13*sin(2*PI*110*t)
                val drums=.16*exp(-beat*28)*sin(2*PI*(65*beat+35*beat*beat))
                val harmony=.07*(sin(2*PI*261.63*t)+sin(2*PI*329.63*t)+sin(2*PI*392*t))
                val lead=.08*sin(2*PI*440*t+.4*sin(2*PI*5*t))
                StemCore.writeShort(out,StemCore.pcm((bass+drums+harmony+lead).toFloat()))
                StemCore.writeShort(out,StemCore.pcm((bass+drums+harmony-lead).toFloat()))
            }
        }
        wav.outputStream().buffered(65536).use{out->StemCore.header(out,frames.toLong());raw.inputStream().use{it.copyTo(out)}}
    }
    private fun separator(id:String,expected:Int){
        val entry=ModelCatalog.entries.single{it.id==id}
        val folder=File(c.filesDir,"mixes").apply{mkdirs()}
        val raw=File(folder,"qa-model-$expected.pcm");val wav=File(folder,"qa-model-$expected.wav")
        var bundle:StemEngine.Bundle?=null
        var rendered:File?=null
        val model=StemEngine.model(c)
        try{
            music(raw,wav,44100*8)
            StemEngine.installCatalog(c,entry){if(it%10==0)println("MODEL download $id $it")}
            assertTrue(VerifiedDownload.matches(model,entry.sha256!!))
            val diag=StemEngine.diagnose(c)
            assertEquals(expected,diag.count)
            assertTrue("Non-silent finite inference",diag.metrics.rms.isFinite()&&diag.metrics.rms>1e-7)
            assertTrue(diag.metrics.reconstructionRms.isFinite())
            println("MODEL $id diagnostic: $diag")
            val result=StemEngine.separateDecoded(c,uri(wav),raw){println("MODEL $id $it")}
            bundle=result
            assertEquals(expected,result.count);assertEquals(44100L*8,result.frames)
            val hashes=mutableSetOf<String>()
            var audible=0
            for(i in 0 until expected){
                val f=File(result.dir,"$i.pcm")
                assertEquals(result.frames*4,f.length())
                hashes.add(StemCheckpoint.hash(f))
                f.inputStream().buffered().use{input->
                    var power=0.0
                    repeat((result.frames*2).toInt()){val x=StemCore.readShort(input)/32768.0;power+=x*x}
                    val rms=sqrt(power/(result.frames*2));println("MODEL $id stem $i RMS=$rms")
                    if(rms>1e-5)audible++
                }
            }
            assertTrue("Identical or silent model output",hashes.size>=2&&audible>=2)
            assertTrue(StemEngine.matchesSource(result,raw))
            rendered=StemEngine.render(c,result,FloatArray(expected){1f})
            val mixed=rendered!!
            assertEquals(44+result.frames*4,mixed.length())
            val decoded=File(folder,"qa-decode-$expected.pcm")
            try{assertEquals(result.frames,StemEngine.decode(c,uri(mixed),decoded))}finally{decoded.delete()}
            println("PASS REAL MODEL $id: pinned weights, Android ONNX inference, $expected distinct cached stems, mix export and Android decode")
        }finally{
            rendered?.delete();bundle?.dir?.deleteRecursively();StemEngine.discardPending(c,uri(wav));raw.delete();wav.delete();model.delete()
        }
    }
    @Test fun actualFourStemDemucs(){separator("htdemucs-fp16",4)}
    @Test fun actualSixStemDemucs(){separator("htdemucs-6s-fp16",6)}
    @Test fun actualAstClassifier(){
        val folder=File(c.filesDir,"mixes").apply{mkdirs()}
        val raw=File(folder,"qa-ast.pcm");val wav=File(folder,"qa-ast.wav")
        try{
            music(raw,wav,44100*6)
            val entry=ModelCatalog.entries.single{it.id=="ast-gtzan-fp32"}
            AstGenreModel.installCatalog(c,entry){if(it%10==0)println("MODEL AST download $it")}
            assertTrue(VerifiedDownload.matches(AstGenreModel.model(c),entry.sha256!!))
            val scores=AstGenreModel.classify(c,uri(wav)){println("MODEL AST $it")}
            assertEquals(10,scores.scores.size)
            assertEquals(AstGenreCore.labels.toSet(),scores.scores.map{it.label}.toSet())
            assertTrue(scores.scores.all{it.probability.isFinite()&&it.probability in 0.0..1.0})
            assertEquals(1.0,scores.scores.sumOf{it.probability},1e-6)
            assertTrue(scores.scores.zipWithNext().all{(a,b)->a.probability>=b.probability})
            println("PASS REAL MODEL AST: pinned weights, actual audio features and finite normalized classifier scores; no genre accuracy assertion")
        }finally{raw.delete();wav.delete();AstGenreModel.model(c).delete()}
    }
    @Test fun actualWhisperTinySpeech(){
        val folder=File(c.filesDir,"mixes")
        val source=File(folder,"qa-whisper.wav")
        val weights=File(folder,"qa-whisper-tiny.bin")
        try{
            assertTrue(source.isFile&&weights.isFile)
            assertEquals("tiny",WhisperLocal.install(c,uri(weights)))
            val lrc=WhisperLocal.transcribe(c,uri(source),null,"en"){println("MODEL Whisper $it")}
            val parsed=Lrc.parse(lrc)
            assertTrue("No timestamped text",parsed.isNotEmpty())
            val text=parsed.joinToString(" "){WordLyrics.parse(it).text}.lowercase(java.util.Locale.ROOT)
            val recognized=Regex("[a-z]+").findAll(text).map{it.value}.toSet()
            val hits=setOf("music","playing","listen","song","today","test").intersect(recognized)
            println("MODEL Whisper transcript (synthetic speech): $lrc ; expected word hits=$hits")
            assertTrue("Too few expected words: $hits",hits.size>=3)
            assertTrue(parsed.all{it.ms>=0&&it.ms<20000})
            assertTrue(parsed.zipWithNext().all{(a,b)->a.ms<=b.ms})
            println("PASS REAL MODEL Whisper tiny: native model load, speech inference and timestamped LRC; not a singing accuracy benchmark")
        }finally{WhisperLocal.model(c).delete()}
    }
}
