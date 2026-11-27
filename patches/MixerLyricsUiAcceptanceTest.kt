package app.remix.player

import android.content.ComponentName
import android.content.Intent
import android.os.SystemClock
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Button
import android.text.Spanned
import android.text.style.UnderlineSpan
import androidx.core.content.FileProvider
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.session.MediaController
import androidx.media3.session.SessionToken
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.runner.lifecycle.ActivityLifecycleMonitorRegistry
import androidx.test.runner.lifecycle.Stage
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File
import java.io.FileInputStream
import java.util.concurrent.TimeUnit
import kotlin.math.sin

/** Tests actual Android view state on the main looper, not stale uiautomator XML.
 * Synthetic audio only; CI runs on a disposable emulator. */
@RunWith(AndroidJUnit4::class)
@UnstableApi
class MixerLyricsUiAcceptanceTest {
    private val inst=InstrumentationRegistry.getInstrumentation()
    private val c=inst.targetContext
    private fun main(block:()->Unit)=inst.runOnMainSync{block()}
    private fun await(message:String,timeout:Long=15000,condition:()->Boolean){
        val end=SystemClock.elapsedRealtime()+timeout
        while(SystemClock.elapsedRealtime()<end){var ok=false;main{ok=condition()};if(ok)return;SystemClock.sleep(80)}
        fail(message)
    }
    private fun shell(command:String):String=inst.uiAutomation.executeShellCommand(command).use{fd->
        FileInputStream(fd.fileDescriptor).bufferedReader().use{it.readText()}
    }
    private fun activity():MainActivity?=ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(Stage.RESUMED).filterIsInstance<MainActivity>().lastOrNull()
    private fun views(v:View):Sequence<View> = sequence {
        yield(v);if(v is ViewGroup)for(i in 0 until v.childCount)yieldAll(views(v.getChildAt(i)))
    }
    private fun texts():List<TextView> = activity()?.window?.decorView?.let{views(it).filterIsInstance<TextView>().toList()}.orEmpty()
    private fun button(text:String):Button?=texts().filterIsInstance<Button>().firstOrNull{it.text.toString()==text&&it.isShown&&it.isEnabled}
    private fun click(text:String){await("Missing enabled UI button: "+text){button(text)!=null};main{assertTrue(button(text)!!.performClick())}}
    private fun capture(name:String){val bitmap=inst.uiAutomation.takeScreenshot()?:error("Screenshot unavailable");try{File(c.filesDir,"qa-"+name+".png").outputStream().use{assertTrue(bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it))}}finally{bitmap.recycle()}}
    private fun fixture(block:(MediaController)->Unit){
        val uid=java.util.UUID.randomUUID().toString()
        val dir=File(File(c.filesDir,"stems").apply{mkdirs()},uid).apply{check(mkdirs())}
        val wav=File(File(c.filesDir,"mixes").apply{mkdirs()},"qa-ui-"+uid+".wav")
        val frames=44100L*30
        val uri=FileProvider.getUriForFile(c,"app.remix.player.files",wav)
        val lib=c.getSharedPreferences("library",0);val old=lib.getString("tracks",null)
        val cache=c.getSharedPreferences("stem_cache",0)
        val mixer=c.getSharedPreferences("mixer",0);val asked=mixer.contains("asked_notifications");val oldAsked=mixer.getBoolean("asked_notifications",false)
        val lyricsUi=c.getSharedPreferences("lyrics_ui",0);val follow=lyricsUi.contains("follow");val oldFollow=lyricsUi.getBoolean("follow",true)
        var future:com.google.common.util.concurrent.ListenableFuture<MediaController>?=null
        var controller:MediaController?=null
        try {
            val data=java.nio.ByteBuffer.allocate(44100*4).order(java.nio.ByteOrder.LITTLE_ENDIAN)
            repeat(44100){i->val v=(sin(2*Math.PI*i*220/44100)*900).toInt().toShort();data.putShort(v);data.putShort(v)}
            repeat(4){i->File(dir,"$i.pcm").outputStream().buffered().use{w->repeat(30){w.write(data.array())}}}
            File(dir,"meta").writeText("$frames\n4\n")
            wav.outputStream().buffered().use{w->StemCore.header(w,frames);repeat(30){w.write(data.array())}}
            val song=org.json.JSONObject().put("uri",uri.toString()).put("group",uri.toString()).put("title","QA UI synthetic").put("artist","QA")
                .put("lyrics","[00:01.000]<00:01.000>Первое <00:02.000>второе <00:03.000>третье\n[00:08.000]Следующая строка")
            val arr=org.json.JSONArray(old?:"[]").put(song)
            check(lib.edit().putString("tracks",arr.toString()).commit())
            check(cache.edit().putString(uri.toString(),uid).commit())
            check(mixer.edit().putBoolean("asked_notifications",true).commit())
            check(lyricsUi.edit().putBoolean("follow",true).commit())
            main{future=MediaController.Builder(c,SessionToken(c,ComponentName(c,PlaybackService::class.java))).buildAsync()}
            val p=future!!.get(15,TimeUnit.SECONDS);controller=p
            val item=MediaItem.Builder().setMediaId(uri.toString()).setUri(uri).setRequestMetadata(MediaItem.RequestMetadata.Builder().setMediaUri(uri).build()).build()
            main{MixerSession.stop(c);p.pause();p.setMediaItems(listOf(item));p.prepare()}
            await("Fixture queue not loaded"){p.currentMediaItem?.mediaId==uri.toString()&&p.duration in 29900L..30100L}
            inst.startActivitySync(Intent(c,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK).putExtra("open_mixer",true))
            await("Mixer screen not ready"){button("▶ Слушать микс")!=null}
            block(p)
        } finally {
            main{MixerSession.stop(c);controller?.let{it.pause();it.clearMediaItems()};future?.let{MediaController.releaseFuture(it)}
                ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(Stage.RESUMED).filterIsInstance<MainActivity>().forEach{it.finish()}
            }
            lib.edit().apply{if(old==null)remove("tracks")else putString("tracks",old)}.commit()
            cache.edit().remove(uri.toString()).commit()
            mixer.edit().apply{if(asked)putBoolean("asked_notifications",oldAsked)else remove("asked_notifications")}.commit()
            lyricsUi.edit().apply{if(follow)putBoolean("follow",oldFollow)else remove("follow")}.commit()
            wav.delete();dir.deleteRecursively()
        }
    }
    @Test fun mixerActualButtonsBackgroundResumeAndPause(){
        fixture {
            click("▶ Слушать микс")
            await("Click did not start the actual audio track"){MixerSession.active&&MixerSession.position()>44100&&button("Ⅱ Пауза микса")!=null}
            main{val solo=texts().filterIsInstance<Button>().firstOrNull{it.contentDescription=="Только Ударные"}?:error("Solo control not found");assertTrue(solo.performClick())}
            await("Solo did not change live gains"){MixerSession.request?.gains?.contentEquals(floatArrayOf(1f,0f,0f,0f))==true}
            var before=0L;main{before=MixerSession.position()}
            shell("input keyevent 3")
            await("Activity did not leave foreground"){activity()==null}
            await("Mixer not progressing in background"){MixerSession.active&&MixerSession.position()>before+44100*3}
            assertTrue("Foreground mixer service missing",shell("dumpsys activity services app.remix.player/.MixerService").contains("isForeground=true"))
            shell("am start -W --activity-single-top -n app.remix.player/.MainActivity --ez open_mixer true")
            await("Mixer UI did not reflect running session"){MixerSession.active&&button("Ⅱ Пауза микса")!=null&&texts().any{Regex("Микшер · 0:(0[5-9]|[1-2][0-9])").matches(it.text.toString())}}
            capture("mixer-resumed")
            click("Ⅱ Пауза микса")
            await("Pause did not stop mixer"){!MixerSession.active&&button("▶ Слушать микс")!=null}
            val deadline=SystemClock.elapsedRealtime()+5000
            while(SystemClock.elapsedRealtime()<deadline&&shell("dumpsys activity services app.remix.player/.MixerService").contains("isForeground=true"))SystemClock.sleep(100)
            assertFalse("Service still foreground after pause",shell("dumpsys activity services app.remix.player/.MixerService").contains("isForeground=true"))
            main{assertTrue((MixerSession.bookmark?.frame?:0)>44100*3)}
            capture("mixer-paused")
        }
    }
    @Test fun compactLibraryAndExpandedPlayerHaveOneTitleAndVisibleSeek(){
        fixture { p->
            click("Музыка")
            fun shown()=activity()?.window?.decorView?.let{views(it).filter{v->v.isShown}.toList()}.orEmpty()
            fun control(desc:String)=shown().firstOrNull{it.contentDescription==desc&&it.isClickable}
            await("Library mini-player missing"){control("Открыть экран воспроизведения")!=null}
            main{
                assertNull("Full transport must not be visible on library",shown().filterIsInstance<WaveSeekBar>().firstOrNull())
                assertTrue("Library action wall is still visible",texts().none{it.isShown&&it.text.toString() in listOf("Инструменты библиотеки…","Темп / скорость…","Добавить найденные песни в очередь…")})
                assertNotNull(control("Фильтры и инструменты"))
            }
            capture("compact-library")
            main{assertTrue(control("Открыть экран воспроизведения")!!.performClick())}
            await("Expanded player missing visible timeline"){
                val wave=shown().filterIsInstance<WaveSeekBar>().singleOrNull()
                val rect=android.graphics.Rect()
                wave!=null&&wave.getGlobalVisibleRect(rect)&&rect.height()>=((48*c.resources.displayMetrics.density).toInt()-1)&&rect.width()>100
            }
            main{
                assertEquals("Expanded track title repeated",1,texts().count{it.isShown&&it.text.toString()=="QA UI synthetic"})
                assertNull("Mini-player remains visible in full player",control("Открыть экран воспроизведения"))
                for(desc in listOf("В избранное","Версии композиции","Ещё","Очередь","Текст песни","Случайный порядок воспроизведения","Предыдущая композиция","Следующая композиция","Режим повтора")){
                    val v=control(desc)?:error("Missing action: "+desc)
                    val min=(48*c.resources.displayMetrics.density).toInt()-1
                    assertTrue("Touch target too small: "+desc,v.width>=min&&v.height>=min)
                }
                val wave=shown().filterIsInstance<WaveSeekBar>().single()
                val bmp=android.graphics.Bitmap.createBitmap(wave.width,wave.height,android.graphics.Bitmap.Config.ARGB_8888)
                try{
                    wave.draw(android.graphics.Canvas(bmp))
                    val y=(wave.paddingTop+wave.height-wave.paddingBottom)/2
                    assertTrue("No visible timeline pixels",(wave.paddingLeft until wave.width-wave.paddingRight).any{x->bmp.getPixel(x,y)==0xff70677e.toInt()||bmp.getPixel(x,y)==0xffc0b0ff.toInt()||bmp.getPixel(x,y)==0xffe8dfff.toInt()})
                }finally{bmp.recycle()}
            }
            capture("expanded-player")
            main{assertTrue(control("Текст песни")!!.performClick())}
            await("Lyrics screen lacks synchronized content"){texts().any{it.isShown&&it.text.toString().startsWith("Первое второе третье")}}
            capture("lyrics-clean")
        }
    }
    @Test fun karaokeActualWordSpansSeekAndFollowToggle(){
        fixture { p->
            click("Текст")
            main{p.pause();p.seekTo(2500)}
            fun underline(word:String):Boolean=texts().any{v->val s=v.text as? Spanned?:return@any false
                s.toString().startsWith("Первое второе третье")&&s.getSpans(0,s.length,UnderlineSpan::class.java).any{span->s.subSequence(s.getSpanStart(span),s.getSpanEnd(span)).toString().trim()==word}}
            await("Expected actual second-word underline"){underline("второе")}
            capture("karaoke-word")
            click("Автопрокрутка: вкл.")
            await("Follow off not reflected"){button("Автопрокрутка: выкл.")!=null}
            main{p.seekTo(1000)}
            await("Backward seek left stale active word"){underline("Первое")}
            click("Музыка");click("Текст")
            await("Follow preference lost after leaving lyrics"){button("Автопрокрутка: выкл.")!=null}
            click("Автопрокрутка: выкл.")
            await("Follow on not restored"){button("Автопрокрутка: вкл.")!=null}
            capture("karaoke-seek")
        }
    }
}
