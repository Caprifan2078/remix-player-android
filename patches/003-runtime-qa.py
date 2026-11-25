#!/usr/bin/env python3
"""Checked overlay applied after original ZIP integrity check and patches 001/002."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
src="app/src/main/java/app/remix/player/"
test="app/src/androidTest/java/app/remix/player/PlaybackInstrumentedTest.kt"
def replace(path, old, new):
    f=root/path
    s=f.read_text()
    assert s.count(old)==1, f"{path}: expected exactly one occurrence"
    f.write_text(s.replace(old,new))
# Native alignment: upstream fix is present from 1.22.0. APK audit remains mandatory.
replace("app/build.gradle.kts","onnxruntime-android:1.20.0","onnxruntime-android:1.22.0")
# Keep visible navigation labels on one line on 320dp screens.
replace(src+"MainActivity.kt","button.textSize=12f;button.minHeight=dp(48);","button.textSize=12f;button.setSingleLine(true);button.setPadding(dp(2),dp(5),dp(2),dp(5));button.setAutoSizeTextTypeUniformWithConfiguration(9,12,1,android.util.TypedValue.COMPLEX_UNIT_SP);button.minHeight=dp(48);")
# LiveStemPlayer needs the context only to obtain its AudioManager, not as a retained property.
replace(src+"LiveStemPlayer.kt","class LiveStemPlayer(private val context:Context,","class LiveStemPlayer(context:Context,")
# Diagnostics without media titles, URIs or file contents.
replace(src+"PlaybackService.kt","val player=ExoPlayer.Builder(this,renderers).build()","""val player=ExoPlayer.Builder(this,renderers).build()
        player.addListener(object:Player.Listener{
            override fun onPlayerError(error:PlaybackException){android.util.Log.e("RemixPlayback","Player error: "+error.errorCodeName+" cause="+error.cause?.javaClass?.simpleName)}
            override fun onPlaybackStateChanged(playbackState:Int){if(BuildConfig.DEBUG)android.util.Log.d("RemixPlayback","state="+playbackState+" count="+player.mediaItemCount)}
            override fun onPlayWhenReadyChanged(playWhenReady:Boolean,reason:Int){if(BuildConfig.DEBUG)android.util.Log.d("RemixPlayback","ready="+playWhenReady+" reason="+reason)}
            override fun onPlaybackSuppressionReasonChanged(playbackSuppressionReason:Int){if(BuildConfig.DEBUG)android.util.Log.d("RemixPlayback","suppression="+playbackSuppressionReason)}
        })""".replace("if(BuildConfig.DEBUG)","if((applicationInfo.flags and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE)!=0)"))
# Explicitly record controller state on assertion failure, preserving the old assertion.
replace(test,'await("Local WAV not playing"){p.isPlaying&&p.currentPosition>300&&p.duration in 11900L..12100L}',"""try{await("Local WAV not playing"){p.isPlaying&&p.currentPosition>300&&p.duration in 11900L..12100L}}catch(e:AssertionError){
                var detail="";main{detail="state="+p.playbackState+" ready="+p.playWhenReady+" playing="+p.isPlaying+" position="+p.currentPosition+" duration="+p.duration+" count="+p.mediaItemCount+" suppression="+p.playbackSuppressionReason+" error="+p.playerError?.errorCodeName}
                throw AssertionError("Local WAV not playing; "+detail,e)
            }""")
# Actual JNI load + ONNX inference, not merely library presence.
replace(test,"    @Test fun localPlaybackSeekQueueAndPause(){","""    @Test fun onnxRuntimeIdentityInference(){
        val model=android.util.Base64.decode("CAg6QQoQCgF4EgF5IghJZGVudGl0eRILcWFfaWRlbnRpdHlaDwoBeBIKCggIARIECgIIAmIPCgF5EgoKCAgBEgQKAggCQgIQDQ==",android.util.Base64.DEFAULT)
        val env=ai.onnxruntime.OrtEnvironment.getEnvironment()
        ai.onnxruntime.OrtSession.SessionOptions().use{opts->
            env.createSession(model,opts).use{s->
                ai.onnxruntime.OnnxTensor.createTensor(env,java.nio.FloatBuffer.wrap(floatArrayOf(-.25f,.75f)),longArrayOf(2)).use{input->
                    s.run(mapOf("x" to input)).use{result->
                        val output=result.get("y").get() as ai.onnxruntime.OnnxTensor
                        val values=output.floatBuffer
                        assertEquals(2,values.remaining())
                        assertEquals(-.25f,values.get(),0.000001f)
                        assertEquals(.75f,values.get(),0.000001f)
                    }
                }
            }
        }
    }
    @Test fun localPlaybackSeekQueueAndPause(){""")
# Always retain logs from the *actual* failed playback test, not just pre-test startup.
replace("tests/android-playback.sh","mkdir -p smoke-output\n","""mkdir -p smoke-output
trap 'adb logcat -d -t 4000 > smoke-output/playback-logcat.txt || true; adb shell dumpsys media_session > smoke-output/playback-sessions.txt || true; adb exec-out screencap -p > smoke-output/playback-screen.png || true' EXIT
adb logcat -c
""")
# Prevent the first failing scenario from masking separate mixer results.
f=root/"tests/android-all-smoke.sh"
f.write_text("""#!/usr/bin/env bash
set -uo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
status=0
bash "$root/android-smoke.sh" "$1" || status=1
bash "$root/android-playback.sh" "$2" || status=1
adb shell am force-stop app.remix.player || status=1
bash "$root/android-mixer-smoke.sh" || status=1
exit "$status"
""")
print("Applied runtime QA overlay; 6 Android instrumentation tests expected")
