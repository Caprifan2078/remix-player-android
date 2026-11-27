package app.remix.player

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.core.content.FileProvider
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File
import java.io.ByteArrayOutputStream
import java.io.ByteArrayInputStream
import java.security.MessageDigest
import java.util.zip.ZipInputStream
import kotlin.math.sin

/** Real Android filesystem, FileProvider and MediaCodec; generated audio only. */
@RunWith(AndroidJUnit4::class)
class StudioAcceptanceTest {
    private val c=InstrumentationRegistry.getInstrumentation().targetContext
    private fun folder()=File(File(c.filesDir,"mixes").apply{mkdirs()},"qa-studio-"+java.util.UUID.randomUUID()).apply{check(mkdirs())}
    private fun raw(f:File,n:Int=44100,freq:Double=440.0){
        f.outputStream().buffered().use{w->repeat(n){i->val v=(sin(2*Math.PI*i*freq/44100)*4000).toInt().toShort();StemCore.writeShort(w,v);StemCore.writeShort(w,(-v).toShort())}}
    }
    private fun wav(raw:File,out:File){
        out.outputStream().buffered().use{w->StemCore.header(w,raw.length()/4);raw.inputStream().use{it.copyTo(w)}}
    }
    private fun decode(f:File,dst:File)=StemEngine.decode(c,FileProvider.getUriForFile(c,"app.remix.player.files",f),dst)
    private fun hash(f:File)=MessageDigest.getInstance("SHA-256").digest(f.readBytes()).joinToString(""){"%02x".format(it)}
    @Test fun waveformFallbackIsVisibleAndTracksPosition(){
        val inst=InstrumentationRegistry.getInstrumentation()
        inst.runOnMainSync{
            val view=WaveSeekBar(c);view.max=1000;view.progress=500
            val density=c.resources.displayMetrics.density
            val width=(300*density).toInt();val height=(48*density).toInt()
            view.measure(android.view.View.MeasureSpec.makeMeasureSpec(width,android.view.View.MeasureSpec.EXACTLY),android.view.View.MeasureSpec.makeMeasureSpec(height,android.view.View.MeasureSpec.EXACTLY))
            view.layout(0,0,width,height)
            val bitmap=android.graphics.Bitmap.createBitmap(width,height,android.graphics.Bitmap.Config.ARGB_8888)
            val canvas=android.graphics.Canvas(bitmap)
            val left=view.paddingLeft;val right=width-view.paddingRight;val middle=(left+right)/2;val y=(view.paddingTop+height-view.paddingBottom)/2
            try{
                canvas.drawColor(0xff101019.toInt());view.draw(canvas)
                assertEquals("Fallback played track",0xffc0b0ff.toInt(),bitmap.getPixel((left+middle)/2,y))
                assertEquals("Fallback remaining track",0xff70677e.toInt(),bitmap.getPixel((middle+right)/2,y))
                assertEquals("Fallback playhead",0xffe8dfff.toInt(),bitmap.getPixel(middle,y))
                view.setWaveform(FloatArray(160){.5f});canvas.drawColor(0xff101019.toInt());view.draw(canvas)
                assertEquals("Waveform playhead",0xffe8dfff.toInt(),bitmap.getPixel(middle,y))
                view.progress=250;canvas.drawColor(0xff101019.toInt());view.draw(canvas)
                assertEquals("Updated playhead",0xffe8dfff.toInt(),bitmap.getPixel(left+(right-left)/4,y))
                view.setWaveform(null);view.progress=750;canvas.drawColor(0xff101019.toInt());view.draw(canvas)
                assertEquals("Fallback after clearing waveform",0xffe8dfff.toInt(),bitmap.getPixel(left+(right-left)*3/4,y))
            }finally{bitmap.recycle()}
        }
    }
    @Test fun allOfflineEffectsAndAndroidDecoder(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,22050);val expected=hash(input)
            val inst=InstrumentationRegistry.getInstrumentation()
            inst.runOnMainSync{
                for((width,height) in listOf(120 to 64,230 to 160,280 to 208)){
                    val view=PulseWidget.testView(c,width,height).apply(c,android.widget.FrameLayout(c))
                    assertEquals("QA Track",view.findViewById<android.widget.TextView>(R.id.widget_title).text.toString())
                    assertEquals(if(width>=230&&height>=160)android.view.View.VISIBLE else android.view.View.GONE,view.findViewById<android.view.View>(R.id.widget_effects).visibility)
                    assertEquals(if(width>=280&&height>=208)android.view.View.VISIBLE else android.view.View.GONE,view.findViewById<android.view.View>(R.id.widget_studio).visibility)
                    val density=c.resources.displayMetrics.density
                    view.measure(android.view.View.MeasureSpec.makeMeasureSpec((width*density).toInt(),android.view.View.MeasureSpec.EXACTLY),android.view.View.MeasureSpec.makeMeasureSpec((height*density).toInt(),android.view.View.MeasureSpec.EXACTLY))
                    view.layout(0,0,view.measuredWidth,view.measuredHeight)
                    assertTrue(view.findViewById<android.view.View>(R.id.widget_play).width>0)
                    assertTrue(view.findViewById<android.view.View>(R.id.widget_art) is android.widget.ImageView)
                    assertEquals(if(width>=230&&height>=160)android.view.View.VISIBLE else android.view.View.GONE,view.findViewById<android.view.View>(R.id.widget_detail).visibility)
                    assertNotNull(view.findViewById<android.view.View>(R.id.widget_speed125));assertNotNull(view.findViewById<android.view.View>(R.id.widget_middle))
                }
            }
            println("PASS Android: three actual RemoteViews layout inflations and size visibility")
            assertEquals(44,Presets.all.size)
            for((i,preset) in Presets.all.withIndex()){
                val out=File(dir,"effect.wav");val pcm=File(dir,"decoded.pcm")
                EffectRender.render(input,out,preset)
                assertEquals(preset.name,EffectRender.outputBytes(input.length()/4,preset),out.length())
                assertEquals(preset.name,(out.length()-44)/4,decode(out,pcm))
                assertArrayEquals(preset.name,out.readBytes().copyOfRange(44,out.length().toInt()),pcm.readBytes())
                if(i==0)assertArrayEquals(input.readBytes(),pcm.readBytes())
                out.delete();pcm.delete()
            }
            assertEquals(expected,hash(input))
            assertTrue(dir.listFiles()!!.none{it.name.startsWith("pitch-")||it.name.startsWith("stretch-")})
            println("PASS Android: 44 effect exports + independent MediaCodec WAV decode")
        }finally{dir.deleteRecursively()}
    }
    @androidx.media3.common.util.UnstableApi
    @Test fun realCrossfadeContinuesIncomingAndCancelsOnSeek(){
        val dir=folder()
        val inst=InstrumentationRegistry.getInstrumentation()
        val pcm=File(dir,"crossfade.pcm")
        val first=File(dir,"a.wav");val second=File(dir,"b.wav")
        var player:androidx.media3.exoplayer.ExoPlayer?=null
        var coordinator:LiveOverlap?=null
        try{
            raw(pcm,44100*14,440.0);wav(pcm,first)
            raw(pcm,44100*14,660.0);wav(pcm,second)
            val uriA=FileProvider.getUriForFile(c,"app.remix.player.files",first)
            val uriB=FileProvider.getUriForFile(c,"app.remix.player.files",second)
            inst.runOnMainSync{
                val p=androidx.media3.exoplayer.ExoPlayer.Builder(c).build();player=p
                p.setAudioAttributes(androidx.media3.common.AudioAttributes.Builder().setUsage(androidx.media3.common.C.USAGE_MEDIA).setContentType(androidx.media3.common.C.AUDIO_CONTENT_TYPE_MUSIC).build(),false)
                p.setMediaItems(listOf(
                    androidx.media3.common.MediaItem.Builder().setUri(uriA).setMediaId("crossfade-a").build(),
                    androidx.media3.common.MediaItem.Builder().setUri(uriB).setMediaId("crossfade-b").build()
                ),0,5500)
                coordinator=LiveOverlap(c,p)
                p.prepare();p.play()
            }
            var firstAudible=-1L;var lastAudible=-1L;var mixed=false;var done=false
            val deadline=android.os.SystemClock.elapsedRealtime()+26000
            while(!done&&android.os.SystemClock.elapsedRealtime()<deadline){
                inst.runOnMainSync{
                    val p=player!!
                    val owned=coordinator!!.tick(3000,true)
                    if(p.currentMediaItemIndex==0&&owned&&p.volume<.9f)mixed=true
                    if(p.currentMediaItemIndex==1&&p.isPlaying&&p.volume>.2f){
                        val position=p.currentPosition
                        if(firstAudible<0)firstAudible=position
                        if(lastAudible>=0)assertTrue("Incoming restarted after audible handoff: $lastAudible -> $position",position+200>=lastAudible)
                        lastAudible=position
                        done=!owned&&p.volume>.98f&&position>firstAudible+350
                    }
                    assertNull(p.playerError)
                }
                android.os.SystemClock.sleep(25)
            }
            assertTrue("No audible overlap before transition",mixed)
            assertTrue("Incoming intro replayed: first audible position $firstAudible",firstAudible>=1000)
            assertTrue("Handoff never completed",done)
            println("PASS Android crossfade: incoming first audible position=$firstAudible ms, no sampled backward restart")
            inst.runOnMainSync{
                val p=player!!;coordinator!!.close()
                p.seekTo(0,8500);coordinator=LiveOverlap(c,p);p.play()
            }
            var cancelled=false
            val cancelDeadline=android.os.SystemClock.elapsedRealtime()+12000
            while(!cancelled&&android.os.SystemClock.elapsedRealtime()<cancelDeadline){
                inst.runOnMainSync{
                    val p=player!!;val owned=coordinator!!.tick(3000,true)
                    if(owned&&p.currentMediaItemIndex==0&&p.volume<.9f){
                        p.seekTo(0,3000)
                        coordinator!!.tick(3000,true)
                        assertTrue("Volume remained attenuated after manual seek",p.volume>.98f)
                        assertEquals(0,p.currentMediaItemIndex)
                        cancelled=true
                    }
                }
                android.os.SystemClock.sleep(25)
            }
            assertTrue("Never entered overlap for manual seek test",cancelled)
        }finally{
            inst.runOnMainSync{coordinator?.close();player?.release()}
            dir.deleteRecursively()
        }
    }
    @Test fun thirtyGenresDistinctDecodableAndNonSilent(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,88200)
            val before=hash(input);val hashes=mutableSetOf<String>()
            assertEquals(32,GenreEngine.styles.size)
            for(style in GenreEngine.styles){
                val out=File(dir,"genre.wav");val pcm=File(dir,"decoded.pcm")
                GenreEngine.renderFromMix(input,out,style,120.0,0.0,emptyList(),listOf(.1))
                assertEquals(style.name,88200L,decode(out,pcm))
                assertTrue(style.name,pcm.readBytes().any{it!=0.toByte()})
                assertTrue("Duplicate output: "+style.name,hashes.add(hash(pcm)))
                out.delete();pcm.delete()
            }
            assertEquals(before,hash(input));assertEquals(32,hashes.size)
            println("PASS Android: 32 distinct procedural genre WAV outputs")
        }finally{dir.deleteRecursively()}
    }
    @Test fun flacRoundTripAndTenBandEqualizer(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,12345)
            val source=File(dir,"source.wav");wav(input,source)
            val flac=File(dir,"output.flac");val pcm=File(dir,"decoded.pcm")
            source.inputStream().buffered().use{r->flac.outputStream().buffered().use{FlacExport.encode(r,it)}}
            assertEquals(12345L,decode(flac,pcm));assertArrayEquals(input.readBytes(),pcm.readBytes())
            val eq=File(dir,"eq.wav");EqRender.render(input,eq,List(10){0f});assertEquals(12345L,decode(eq,pcm))
            assertArrayEquals(input.readBytes(),pcm.readBytes())
            EqRender.render(input,eq,List(10){if(it==4)9f else 0f});assertEquals(12345L,decode(eq,pcm))
            assertFalse(input.readBytes().contentEquals(pcm.readBytes()))
            println("PASS Android: bit-exact FLAC, flat EQ identity, non-flat EQ signal change")
        }finally{dir.deleteRecursively()}
    }
    @Test fun fourAndSixStemCacheMixExportAndInvalidCache(){
        for(count in listOf(4,6)){
            val dir=File(File(c.filesDir,"stems").apply{mkdirs()},java.util.UUID.randomUUID().toString()).apply{check(mkdirs())}
            var mix:File?=null
            try{
                val frames=4410L
                repeat(count){raw(File(dir,"$it.pcm"),frames.toInt(),110.0*(it+1))}
                File(dir,"meta").writeText("$frames\n$count\n")
                val b=StemEngine.load(c,dir.name)?:error("Valid cache rejected")
                assertEquals(count,b.count);assertEquals(frames,b.frames)
                mix=StemEngine.render(c,b,FloatArray(count){if(it==3)1f else 0f})
                assertArrayEquals(File(dir,"3.pcm").readBytes(),mix.readBytes().copyOfRange(44,mix.length().toInt()))
                val bytes=ByteArrayOutputStream()
                StemZip.export(dir,frames,count,bytes)
                val names=listOf("drums","bass","other","vocals","guitar","piano")
                ZipInputStream(ByteArrayInputStream(bytes.toByteArray())).use{z->
                    repeat(count){i->assertEquals(names[i]+".wav",z.nextEntry!!.name);val wav=z.readBytes();assertEquals(44+frames*4,wav.size.toLong());assertArrayEquals(File(dir,"$i.pcm").readBytes(),wav.copyOfRange(44,wav.size));z.closeEntry()}
                    assertNull(z.nextEntry)
                }
                File(dir,"0.pcm").writeBytes(byteArrayOf(1))
                assertNull(StemEngine.load(c,dir.name))
                assertTrue(runCatching{StemZip.export(dir,frames,count,ByteArrayOutputStream())}.isFailure)
                println("PASS Android: $count cached stems, solo vocal mix, ZIP and damaged cache rejection")
            }finally{mix?.delete();dir.deleteRecursively()}
        }
    }
    @Test fun backupRoundTripAndMaliciousArchiveRollback(){
        val dir=folder()
        try{
            val original=File(dir,"input.pcm");raw(original,2205);val source=File(dir,"song.wav");wav(original,source)
            val archive=ByteArrayOutputStream()
            val metadata="""{"tracks":[{"title":"QA synthetic"}]}""".toByteArray()
            BackupCore.write(archive,metadata,listOf(BackupCore.Item("wav"){source.inputStream()}))
            val restored=BackupCore.read(ByteArrayInputStream(archive.toByteArray()),File(dir,"restore"))
            assertArrayEquals(metadata,restored.metadata);assertArrayEquals(source.readBytes(),restored.files.single().readBytes())
            val decoded=File(dir,"restored.pcm");assertEquals(2205L,decode(restored.files.single(),decoded))
            // Android 14+ can reject traversal inside ZipInputStream before application validation.
            // A syntactically safe but invalid ordinal independently exercises our own validator.
            for(entryName in listOf("audio/00.wav","../escape.wav")){
                val malicious=ByteArrayOutputStream()
                java.util.zip.ZipOutputStream(malicious).use{z->
                    for((name,data) in listOf("remix-backup-v1" to "1".toByteArray(),"library.json" to metadata,entryName to source.readBytes())){
                        z.putNextEntry(java.util.zip.ZipEntry(name));z.write(data);z.closeEntry()
                    }
                }
                val bad=File(dir,"bad")
                val rejected=runCatching{BackupCore.read(ByteArrayInputStream(malicious.toByteArray()),bad)}.exceptionOrNull()
                val appRejection=rejected is IllegalArgumentException&&rejected.message=="Недопустимая запись архива"
                val platformRejection=entryName=="../escape.wav"&&android.os.Build.VERSION.SDK_INT>=34&&rejected is java.util.zip.ZipException&&rejected.message.orEmpty().contains(entryName)
                assertTrue("Expected specific path rejection: "+rejected?.javaClass?.simpleName+": "+rejected?.message,appRejection||platformRejection)
                assertFalse(bad.exists());assertFalse(File(dir,"escape.wav").exists())
            }
            println("PASS Android: portable audio backup restore, playable file and traversal rollback")
        }finally{dir.deleteRecursively()}
    }
    @Test fun audioAnalyzerAndInvalidMedia(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,44100*4);val source=File(dir,"source.wav");wav(input,source)
            val report=TrackAnalyzer.report(c,FileProvider.getUriForFile(c,"app.remix.player.files",source))?:error("Analysis rejected valid audio")
            assertEquals(4.0,report.duration,.02);assertTrue(report.rms>.01)
            val waveform=WaveReader.read(c,FileProvider.getUriForFile(c,"app.remix.player.files",source))?:error("Waveform rejected valid WAV")
            assertEquals(160,waveform.size);assertTrue(waveform.all{it.isFinite()&&it in .05f.. .2f})
            println("PASS Android: actual MediaCodec waveform of four-second synthetic WAV")
            val bad=File(dir,"invalid.wav");bad.writeText("not an audio file")
            assertTrue(runCatching{decode(bad,File(dir,"bad.pcm"))}.isFailure)
            println("PASS Android: actual media analysis duration, non-silent signal, invalid audio rejected")
        }finally{dir.deleteRecursively()}
    }
}
