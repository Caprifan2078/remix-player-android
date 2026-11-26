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
    @Test fun karaokeActualWordSpansSeekAndFollowToggle(){
        fixture { p->
            click("Текст")
            main{p.pause();p.seekTo(2500)}
            fun highlighted(word:String):Boolean=texts().any{v->
                val s=v.text as? Spanned?:return@any false
                if(!s.toString().startsWith("Первое второе третье")||s.getSpans(0,s.length,UnderlineSpan::class.java).isNotEmpty())return@any false
                val spans=s.getSpans(0,s.length,MainActivity.LyricInk::class.java)
                if(spans.size!=1)return@any false
                val ink=spans.single();val paint=android.text.TextPaint();ink.updateDrawState(paint)
                s.subSequence(s.getSpanStart(ink),s.getSpanEnd(ink)).toString().trim()==word&&paint.color==android.graphics.Color.WHITE
            }
            await("Expected actual second-word color and no underline"){highlighted("второе")}
            capture("karaoke-word")
            click("Автопрокрутка: вкл.")
            await("Follow off not reflected"){button("Автопрокрутка: выкл.")!=null}
            main{p.seekTo(1000)}
            await("Backward seek left stale active word"){highlighted("Первое")}
            click("Музыка");click("Текст")
            await("Follow preference lost after leaving lyrics"){button("Автопрокрутка: выкл.")!=null}
            click("Автопрокрутка: выкл.")
            await("Follow on not restored"){button("Автопрокрутка: вкл.")!=null}
            main{
                val scroll=views(activity()!!.window.decorView).first{it.tag=="karaoke-scroll"}
                val now=SystemClock.uptimeMillis()
                fun send(action:Int,x:Float,y:Float,time:Long){
                    val e=android.view.MotionEvent.obtain(now,time,action,x,y,0)
                    try{scroll.dispatchTouchEvent(e)}finally{e.recycle()}
                }
                send(android.view.MotionEvent.ACTION_DOWN,20f,140f,now)
                send(android.view.MotionEvent.ACTION_MOVE,20f,40f,now+80)
                send(android.view.MotionEvent.ACTION_CANCEL,20f,40f,now+100)
            }
            await("Manual swipe must pause follow"){button("Автопрокрутка: выкл.")!=null}
            click("Автопрокрутка: выкл.")
            await("Resume follow after manual scroll"){button("Автопрокрутка: вкл.")!=null}
            capture("karaoke-seek")
        }
    }
    @Test fun premiumLibraryAndPlayerVisualAcceptance(){
        fixture { p->
            click("Музыка")
            await("Fixture song not visible in library"){texts().any{it.isShown&&it.text.toString()=="QA UI synthetic"}}
            await("Compact mini player entry missing"){texts().any{it.isShown&&it.contentDescription=="Открыть экран воспроизведения"}}
            main{assertNull("Transport should not crowd library",button("⇄"));assertNull(button("Настройки"));assertNotNull(button("Ещё"))}
            capture("premium-library")
            main{val open=texts().first{it.isShown&&it.contentDescription=="Открыть экран воспроизведения"};assertTrue(open.performClick())}
            await("Full player not visible"){button("Ремикс")!=null&&button("⇄")!=null}
            main{
                assertNull("Bottom nav should not duplicate player actions",button("Музыка"))
                assertTrue(views(activity()!!.window.decorView).any{it.isShown&&it.contentDescription=="Обложка композиции"})
                assertTrue(texts().any{it.isShown&&it.text.toString()=="QA UI synthetic"})
            }
            await("Real waveform never appeared",25000){views(activity()!!.window.decorView).any{it is WaveSeekBar&&it.isShown&&it.tag=="waveform-ready"}}
            main{
                val a=activity()!!
                val bounds=android.graphics.Rect()
                a.window.decorView.getWindowVisibleDisplayFrame(bounds)
                if(a.resources.configuration.screenHeightDp>=650){
                    val actions=listOf("Ремикс","Текст","Очередь")
                    actions.forEach{name->
                        val v=button(name)?:error("Missing primary player action: "+name)
                        val r=android.graphics.Rect()
                        assertTrue("Primary action below fold: "+name,v.getGlobalVisibleRect(r)&&r.height()>=v.height*.9&&bounds.contains(r.centerX(),r.centerY()))
                    }
                }
            }
            capture("premium-player")
            click("Ремикс")
            SystemClock.sleep(400)
            val root=inst.uiAutomation.rootInActiveWindow
            assertTrue("Grouped effect chooser not visible",root?.findAccessibilityNodeInfosByText("Эффекты")?.isNotEmpty()==true)
            capture("premium-effect-menu")
            shell("input keyevent 4")
        }
    }

    @Test fun proModeDefaultsOffAndPersistsWithoutRemovingPlayback(){
        val prefs=c.getSharedPreferences("interface_mode",0)
        val existed=prefs.contains("pro");val before=prefs.getBoolean("pro",false)
        check(prefs.edit().remove("pro").commit())
        try{fixture{p->
            click("Студия")
            fun visible(title:String)=texts().any{it.isShown&&it.text.toString()==title}
            await("Core studio not shown"){visible("Remix Studio")}
            main{assertFalse(visible("Инструментал"));assertFalse(visible("Сведение"));assertNull(button("Пакет эффектов…"))}
            fun settings(){
                click("Ещё")
                val deadline=SystemClock.elapsedRealtime()+5000
                var selected=false
                while(SystemClock.elapsedRealtime()<deadline&&!selected){
                    val nodes=inst.uiAutomation.rootInActiveWindow?.findAccessibilityNodeInfosByText("Настройки").orEmpty()
                    val node=nodes.firstOrNull{it.text?.toString()=="Настройки"}
                    var target=node
                    while(target!=null&&!target.isClickable)target=target.parent
                    selected=target?.performAction(android.view.accessibility.AccessibilityNodeInfo.ACTION_CLICK)==true
                    if(!selected)SystemClock.sleep(100)
                }
                assertTrue("Settings menu action missing",selected)
            }
            settings();click("PRO-инструменты: выкл.")
            await("PRO toggle not persisted"){prefs.getBoolean("pro",false)&&button("PRO-инструменты: вкл.")!=null}
            click("Студия")
            await("Expert tools unavailable after enabling"){visible("Инструментал")&&visible("Сведение")}
            settings();click("PRO-инструменты: вкл.")
            await("PRO toggle not disabled"){!prefs.getBoolean("pro",true)&&button("PRO-инструменты: выкл.")!=null}
            click("Студия")
            main{assertFalse(visible("Инструментал"));assertFalse(visible("Сведение"));assertNotNull(p.currentMediaItem)}
            capture("simple-studio")
        }}finally{prefs.edit().apply{if(existed)putBoolean("pro",before)else remove("pro")}.commit()}
    }

}
