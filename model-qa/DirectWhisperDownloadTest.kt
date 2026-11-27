package app.remix.player
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.core.content.FileProvider
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File
@RunWith(AndroidJUnit4::class)
class DirectWhisperDownloadTest {
    @Test fun downloadActivateAndTranscribeOnDevice(){benchmark("tiny")}
    @Test fun quantizedBaseSpeech(){benchmark("base-q5_1")}
    @Test fun turboSpeech(){benchmark("large-v3-turbo-q5_0")}
    private fun tokens(s:String)=Regex("[a-z]+").findAll(s.lowercase(java.util.Locale.ROOT)).map{it.value}.toList()
    private fun edits(expected:List<String>,actual:List<String>):Int{
        var prior=IntArray(actual.size+1){it}
        for(i in expected.indices){
            val next=IntArray(actual.size+1);next[0]=i+1
            for(j in actual.indices)next[j+1]=minOf(prior[j+1]+1,next[j]+1,prior[j]+if(expected[i]==actual[j])0 else 1)
            prior=next
        }
        return prior.last()
    }
    private fun benchmark(id:String){
        val c=InstrumentationRegistry.getInstrumentation().targetContext
        val file=File(c.filesDir,"mixes/qa-whisper.wav")
        val spec=WhisperModelSpec.models.single{it.id==id}
        val model=WhisperLocal.model(c)
        val report=File(c.filesDir,"qa-whisper-$id.json")
        report.delete()
        assertFalse("Fixture must not contain predownloaded weights",model.exists())
        try{
            val progress=mutableListOf<Int>()
            val downloadStart=android.os.SystemClock.elapsedRealtime()
            val installed=WhisperLocal.download(c,spec){p->progress.add(p);if(p%10==0)println("Direct download: $p%")}
            val downloadMs=android.os.SystemClock.elapsedRealtime()-downloadStart
            assertEquals(id,installed);assertEquals(spec,WhisperLocal.installed(c))
            assertEquals(spec.size,model.length());assertTrue(VerifiedDownload.matches(model,spec.sha))
            assertTrue(progress.isNotEmpty()&&progress.last()==100&&progress.zipWithNext().all{it.first<=it.second})
            val uri=FileProvider.getUriForFile(c,"app.remix.player.files",file)
            val am=c.getSystemService(android.content.Context.ACTIVITY_SERVICE) as android.app.ActivityManager
            var peakPssKiB=0L
            var minAvailableRam=Long.MAX_VALUE
            var pssSamples=0
            fun sampleMemory(){
                val info=android.app.ActivityManager.MemoryInfo()
                am.getMemoryInfo(info)
                minAvailableRam=minOf(minAvailableRam,info.availMem)
                peakPssKiB=maxOf(peakPssKiB,android.os.Debug.getPss())
                pssSamples++
            }
            sampleMemory()
            val stop=java.util.concurrent.CountDownLatch(1)
            val samplingError=java.util.concurrent.atomic.AtomicReference<Throwable?>()
            val sampler=Thread({
                try{
                    while(!stop.await(500,java.util.concurrent.TimeUnit.MILLISECONDS))sampleMemory()
                }catch(e:Throwable){samplingError.set(e)}
            },"qa-whisper-memory")
            sampler.start()
            val start=android.os.SystemClock.elapsedRealtime()
            var inferenceMs=0L
            val text=try{
                WhisperLocal.transcribe(c,uri,null,"en"){println(it)}
            }finally{
                inferenceMs=android.os.SystemClock.elapsedRealtime()-start
                stop.countDown();sampler.join()
            }
            samplingError.get()?.let{throw AssertionError("Memory sampling failed",it)}
            sampleMemory()
            assertTrue("Missing sampled process PSS",peakPssKiB>0&&pssSamples>=2)
            val parsed=Lrc.parse(text)
            assertTrue(parsed.isNotEmpty())
            assertTrue(parsed.all{it.ms>=0&&it.ms<20000}&&parsed.zipWithNext().all{(a,b)->a.ms<=b.ms})
            val expected=tokens("The music is playing. Listen to the song today. This is a test.")
            val actual=tokens(parsed.joinToString(" "){WordLyrics.parse(it).text})
            val errors=edits(expected,actual)
            val memory=android.app.ActivityManager.MemoryInfo()
            (c.getSystemService(android.content.Context.ACTIVITY_SERVICE) as android.app.ActivityManager).getMemoryInfo(memory)
            println("BENCHMARK Whisper $id modelBytes=${spec.size} downloadMs=$downloadMs inferenceMs=$inferenceMs words=${expected.size} edits=$errors WER=${errors.toDouble()/expected.size} availableRamAfter=${memory.availMem}")
            println("BENCHMARK transcript $id: "+actual.joinToString(" "))
            assertTrue("Recognized speech must contain fixture vocabulary",text.lowercase().contains("music")||text.lowercase().contains("song"))
            val result=org.json.JSONObject().put("id",id).put("modelBytes",spec.size).put("downloadMs",downloadMs).put("inferenceMs",inferenceMs).put("words",expected.size).put("edits",errors).put("wer",errors.toDouble()/expected.size).put("availableRamAfter",memory.availMem).put("transcript",actual.joinToString(" ")).put("peakPssKiB",peakPssKiB).put("pssSamples",pssSamples).put("minAvailableRam",minAvailableRam)
            report.writeText(result.toString())
            println("PASS: Android downloaded publisher weights over HTTPS, verified SHA, activated native model, recognized fixture speech")
        }finally{model.delete()}
    }
}
