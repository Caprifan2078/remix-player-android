from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,old,new):
    p=src/name;s=p.read_text()
    assert s.count(old)==1,(name,old)
    p.write_text(s.replace(old,new))
replace('GenreDynamics.kt','val peak=max(abs(l),abs(r))','val cleanL=l.takeIf{it.isFinite()}?:0f;val cleanR=r.takeIf{it.isFinite()}?:0f\n        val peak=max(abs(cleanL),abs(cleanR))')
replace('GenreDynamics.kt','left=(l*gain).coerceIn(-1f,1f);right=(r*gain).coerceIn(-1f,1f)','left=(cleanL*gain).coerceIn(-1f,1f);right=(cleanR*gain).coerceIn(-1f,1f)')
replace('GenreDynamics.kt','(kickEnvelope*drumLevel).coerceIn(0f,1f)','((kickEnvelope.takeIf{it.isFinite()}?:0f).coerceIn(0f,1f)*(drumLevel.takeIf{it.isFinite()}?:0f).coerceIn(0f,1f))')
replace('GenreDynamics.kt','l1+=a*(l-l1);l2+=a*(l1-l2);r1+=a*(r-r1);r2+=a*(r1-r2)','val cleanL=(l.takeIf{it.isFinite()}?:0f).coerceIn(-32f,32f);val cleanR=(r.takeIf{it.isFinite()}?:0f).coerceIn(-32f,32f)\n        l1+=a*(cleanL-l1);l2+=a*(l1-l2);r1+=a*(cleanR-r1);r2+=a*(r1-r2)')
replace('GenreDynamics.kt','val amount=1f-kickGain.coerceIn(0f,1f)','val amount=1f-(kickGain.takeIf{it.isFinite()}?:1f).coerceIn(0f,1f)')
replace('GenreDynamics.kt','left=l-amount*l2;right=r-amount*r2','left=cleanL-amount*l2;right=cleanR-amount*r2')
(src/'SafeTransitionOutput.kt').write_text('''package app.remix.player
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption
internal object SafeTransitionOutput {
    fun write(out:File, render:(File)->Long):Long {
        check(!Thread.currentThread().isInterrupted){"Отменено"}
        val target=out.absoluteFile
        val temp=File.createTempFile(".transition-", ".part", target.parentFile)
        try {
            val result=render(temp)
            check(!Thread.currentThread().isInterrupted){"Отменено"}
            check(temp.length()>0){"Пустой результат"}
            Files.move(temp.toPath(),target.toPath(),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING)
            return result
        } finally { temp.delete() }
    }
}
''')
replace('TransitionMix.kt','try{val stats=analyze(first,second,a-overlap,overlap);','val written=SafeTransitionOutput.write(out){temp->val stats=analyze(first,second,a-overlap,overlap);')
replace('TransitionMix.kt','out.outputStream().buffered(65536)','temp.outputStream().buffered(65536)')
replace('TransitionMix.kt','}}};check(count==length);progress(100);return length}catch(e:Throwable){out.delete();throw e}','}}};check(count==length);length};progress(100);return written')
print('PASS: finite genre signal and transactional offline transition export overlay')
