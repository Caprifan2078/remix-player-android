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
    @Test fun downloadActivateAndTranscribeOnDevice(){
        val c=InstrumentationRegistry.getInstrumentation().targetContext
        val file=File(c.filesDir,"mixes/qa-whisper.wav")
        val spec=WhisperModelSpec.models.first{it.id=="tiny"}
        val model=WhisperLocal.model(c)
        assertFalse("Fixture must not contain predownloaded weights",model.exists())
        try{
            val progress=mutableListOf<Int>()
            val installed=WhisperLocal.download(c,spec){p->progress.add(p);if(p%10==0)println("Direct download: $p%")}
            assertEquals("tiny",installed);assertEquals(spec,WhisperLocal.installed(c))
            assertEquals(spec.size,model.length());assertTrue(VerifiedDownload.matches(model,spec.sha))
            assertTrue(progress.isNotEmpty()&&progress.last()==100&&progress.zipWithNext().all{it.first<=it.second})
            val uri=FileProvider.getUriForFile(c,"app.remix.player.files",file)
            val text=WhisperLocal.transcribe(c,uri,null,"en"){println(it)}
            assertTrue(Lrc.parse(text).isNotEmpty())
            assertTrue("Recognized speech must contain fixture vocabulary",text.lowercase().contains("music")||text.lowercase().contains("song"))
            println("PASS: Android downloaded publisher weights over HTTPS, verified SHA, activated native model, recognized fixture speech")
        }finally{model.delete()}
    }
}
