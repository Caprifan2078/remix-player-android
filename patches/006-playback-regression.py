#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])
src="app/src/main/java/app/remix/player/"
test="app/src/androidTest/java/app/remix/player/PlaybackInstrumentedTest.kt"
def replace(path,old,new):
    f=root/path
    s=f.read_text()
    assert s.count(old)==1,f"{path}: expected one match: {old[:100]}"
    f.write_text(s.replace(old,new))
# QA7: both API29 and API35 failed at RemixProcessor.queueInput; BaseAudioProcessor
# can return its singleton EMPTY_BUFFER for a zero-size request.
replace(src+"PlaybackService.kt","override fun queueInput(inputBuffer: ByteBuffer) {\n","""override fun queueInput(inputBuffer: ByteBuffer) {
        // Media3 drains processors with EMPTY_BUFFER; never copy a buffer into itself.
        if(!inputBuffer.hasRemaining())return
""")
replace(test,"    @Test fun onnxRuntimeIdentityInference(){","""    @Test fun audioProcessorEmptyBufferAndPcmRegression(){
        val p=RemixProcessor()
        val previous=Presets.active;val eq=EqualizerSettings.get()
        try{
            EqualizerSettings.set(List(10){0f})
            for(preset in Presets.all){
                Presets.active=preset
                p.configure(androidx.media3.common.audio.AudioProcessor.AudioFormat(44100,2,androidx.media3.common.C.ENCODING_PCM_16BIT))
                p.flush()
                p.queueInput(androidx.media3.common.audio.AudioProcessor.EMPTY_BUFFER)
                assertFalse("Empty drain produced audio",p.getOutput().hasRemaining())
                repeat(3){
                    val pcm=java.nio.ByteBuffer.allocateDirect(4096).order(java.nio.ByteOrder.nativeOrder())
                    repeat(1024){i->pcm.putShort((i%127*50-3000).toShort());pcm.putShort((3000-i%127*50).toShort())}
                    pcm.flip()
                    val original=ByteArray(pcm.remaining());pcm.duplicate().get(original)
                    p.queueInput(pcm)
                    assertFalse("Input not consumed",pcm.hasRemaining())
                    val output=p.getOutput()
                    assertEquals("Output size for "+preset.name,original.size,output.remaining())
                    val bytes=ByteArray(output.remaining());output.get(bytes)
                    if(preset==Presets.all.first())assertArrayEquals("Original PCM changed",original,bytes)
                    p.queueInput(androidx.media3.common.audio.AudioProcessor.EMPTY_BUFFER)
                    assertFalse(p.getOutput().hasRemaining())
                }
                p.queueEndOfStream()
                assertTrue("Processor failed to drain",p.isEnded())
            }
        }finally{p.reset();Presets.active=previous;EqualizerSettings.set(eq)}
    }
    @Test fun onnxRuntimeIdentityInference(){""")
# Verify live AudioTrack progress separately from UI automation, using synthetic stems.
replace(test,"    @Test fun localPlaybackSeekQueueAndPause(){","""    @Test fun liveMixerAudioTrackAndBackground(){
        val c=inst.targetContext
        val activity=inst.startActivitySync(Intent(c,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        inst.waitForIdleSync()
        val dir=File(File(c.filesDir,"stems"),java.util.UUID.randomUUID().toString()).apply{mkdirs()}
        val frames=44100L*15
        val source="content://app.remix.player.files/mixes/qa-mixer-fixture.wav"
        var future:com.google.common.util.concurrent.ListenableFuture<MediaController>?=null
        try{
            val block=java.nio.ByteBuffer.allocate(44100*4).order(java.nio.ByteOrder.LITTLE_ENDIAN)
            repeat(44100){i->val v=(sin(2*Math.PI*i*220/44100)*600).toInt().toShort();block.putShort(v);block.putShort(v)}
            repeat(4){i->File(dir,"$i.pcm").outputStream().buffered().use{out->repeat(15){out.write(block.array())}}}
            File(dir,"meta").writeText("$frames\\n4\\n")
            main{future=MediaController.Builder(c,SessionToken(c,ComponentName(c,PlaybackService::class.java))).buildAsync()}
            val player=future!!.get(15,TimeUnit.SECONDS)
            main{player.pause();player.clearMediaItems();MixerSession.start(activity,source,"QA synthetic",StemEngine.Bundle(dir,frames,4),FloatArray(4){0.25f},0)}
            await("Mixer AudioTrack did not advance"){MixerSession.active&&MixerSession.position()>22050}
            main{MixerSession.update(floatArrayOf(1f,0f,0f,0f));assertEquals(1f,MixerSession.request!!.gains[0],0f)}
            inst.uiAutomation.executeShellCommand("input keyevent 3").close()
            var pos=0L;main{pos=MixerSession.position()}
            await("Mixer stopped advancing in background"){MixerSession.active&&MixerSession.position()>pos+22050}
            main{MixerSession.stop(c)}
            await("Mixer failed to stop"){!MixerSession.active}
        }finally{main{MixerSession.stop(c);future?.let{MediaController.releaseFuture(it)};activity.finish()};dir.deleteRecursively()}
    }
    @Test fun localPlaybackSeekQueueAndPause(){""")
# Preserve mixer diagnostics even on assertion failure; no permission grant below API 33.
replace("tests/android-mixer-smoke.sh","mkdir -p smoke-output\n","""mkdir -p smoke-output
trap 'adb logcat -d -t 5000 > smoke-output/mixer-logcat.txt || true; adb shell dumpsys media.audio_flinger > smoke-output/mixer-audio.txt || true; adb shell dumpsys activity services "$pkg/.MixerService" > smoke-output/mixer-final-service.txt || true; adb exec-out screencap -p > smoke-output/mixer-final.png || true; rm -rf "$work"' EXIT
adb logcat -c
""")
replace("tests/android-mixer-smoke.sh",'adb shell pm grant "$pkg" android.permission.POST_NOTIFICATIONS || true','if (( $(adb shell getprop ro.build.version.sdk | tr -d "\\r") >= 33 )); then adb shell pm grant "$pkg" android.permission.POST_NOTIFICATIONS; fi')
replace(src+"MixerService.kt","fun stop(context:Context){val token=generation.active?:return;","""fun stop(context:Context){val token=generation.active?:return;if((context.applicationInfo.flags and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE)!=0)android.util.Log.d("RemixMixer","stop via "+Throwable().stackTrace.take(4).joinToString{it.className+"."+it.methodName});""")
replace(src+"MixerService.kt","if(r!=null)bookmark=Bookmark(r.source,frame,r.gains.copyOf())","""android.util.Log.d("RemixMixer","finish token="+token+" frame="+frame+" failure="+(failure!=null))
        if(r!=null)bookmark=Bookmark(r.source,frame,r.gains.copyOf())""")
replace(src+"LiveStemPlayer.kt","setOnAudioFocusChangeListener{if(it!=AudioManager.AUDIOFOCUS_GAIN)close()}","setOnAudioFocusChangeListener{android.util.Log.d(\"RemixMixer\",\"audio focus change=\"+it);if(it!=AudioManager.AUDIOFOCUS_GAIN)close()}")
print("Applied playback self-copy fix and two independent Android regressions")
