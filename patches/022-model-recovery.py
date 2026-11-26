#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def replace(name,a,b):
 p=src/name;s=p.read_text();assert s.count(a)==1,(name,a[:100],s.count(a));p.write_text(s.replace(a,b))
# Use publisher-pinned FP32 AST rather than the INT8 ConvInteger graph that fails on Android CPU.
replace("ModelCatalog.kt",'Entry("ast-gtzan-int8","AST · 10 музыкальных жанров"','Entry("ast-gtzan-fp32","AST · 10 музыкальных жанров"')
replace("ModelCatalog.kt","/onnx/model_int8.onnx","/onnx/model.onnx")
replace("ModelCatalog.kt",',90,"BSD-3-Clause (метаданные издателя)","f7322d9c9a0d40e01bb4fc2feb303864bbfb93b0264e654e2a37f413b86a31bf"',',345,"BSD-3-Clause (метаданные издателя)","71bbd4bd350fdee6c6940778a5a9c85471628cec91a505bad1d4f5cd6b3fb673"')
replace("CatalogDownload.kt","val max=if(entry.kind==ModelCatalog.Kind.SEPARATOR)600L*1024*1024 else 128L*1024*1024","val max=when(entry.kind){ModelCatalog.Kind.SEPARATOR->600L*1024*1024;ModelCatalog.Kind.GENRE->400L*1024*1024;ModelCatalog.Kind.SPEECH->128L*1024*1024}")
# Real Android logcat showed the app killed under severe memory pressure on both Demucs variants.
# A conservative free-memory preflight is a safety guard, not a proven peak usage bound.
p=src/'StemEngine.kt';s=p.read_text()
assert s.count('session(tmp){')==3
s=s.replace('session(tmp){','session(context,tmp){')
assert s.count('session(model(context)){')==1
s=s.replace('session(model(context)){','session(context,model(context)){')
assert s.count('session(modelFile){')==1
s=s.replace('session(modelFile){','session(context,modelFile){')
old='private fun <T> session(file:File, block:(OrtSession)->T):T {'
assert s.count(old)==1
s=s.replace(old,'''private fun checkModelMemory(context:Context,bytes:Long){
        val am=context.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        val info=android.app.ActivityManager.MemoryInfo();am.getMemoryInfo(info)
        require(ModelMemoryBudget.canStart(bytes,info.availMem,info.lowMemory)){"Недостаточно доступной ОЗУ для запуска модели. Освободите память и повторите попытку."}
    }
    private fun <T> session(context:Context,file:File, block:(OrtSession)->T):T {''')
s=s.replace('require(file.isFile){"Сначала импортируйте модель ONNX"}','require(file.isFile){"Сначала импортируйте модель ONNX"};checkModelMemory(context,file.length())')
old='opts.setIntraOpNumThreads(2);opts.setInterOpNumThreads(1);env.createSession(file.absolutePath,opts)'
assert s.count(old)==1
s=s.replace(old,'opts.setIntraOpNumThreads(2);opts.setInterOpNumThreads(1);if(file.length()>32L*1024*1024){opts.setCPUArenaAllocator(false);opts.setMemoryPatternOptimization(false)};env.createSession(file.absolutePath,opts)')
old='require(entry.kind==ModelCatalog.Kind.SEPARATOR&&entry.sha256!=null);val tmp='
assert s.count(old)==1
s=s.replace(old,'require(entry.kind==ModelCatalog.Kind.SEPARATOR&&entry.sha256!=null);checkModelMemory(context,entry.sizeMb.toLong()*1024*1024);val tmp=')
p.write_text(s)
# Install the extended multilingual artifact catalogue before compiling either app or host tests.
(src/'WhisperModelSpec.kt').write_bytes((Path(__file__).parent/'WhisperModelSpec.kt').read_bytes())
test=Path(sys.argv[1])/'tests/WhisperModel62Test.kt'
t=test.read_text()
old='check(models.map{it.id}==listOf("tiny","base","small"))'
assert t.count(old)==1
t=t.replace(old,'check(models.map{it.id}==listOf("tiny","base-q5_1","base","small-q5_1","small"))')
old='check(models.zipWithNext().all{(a,b)->a.size<b.size&&a.minFreeRam<b.minFreeRam})'
assert t.count(old)==1
t=t.replace(old,'check(models.map{it.size}.distinct().size==models.size&&models.zipWithNext().all{(a,b)->a.minFreeRam<=b.minFreeRam})')
test.write_text(t)
# Direct Whisper download, sharing the same checked activation as local import.
p=src/'WhisperLocal.kt';s=p.read_text()
a=s.index('            val spec=WhisperModelSpec.bySize(tmp.length())')
b=s.index('    fun transcribe(',a)
s=s[:a]+'''            return activate(c,tmp)
        }finally{tmp.delete()}
    }
    private fun activate(c:Context,tmp:File):String{
        val spec=WhisperModelSpec.bySize(tmp.length())?:error("Неподдерживаемый файл: выберите модель Whisper из каталога")
        require(VerifiedDownload.matches(tmp,spec.sha)){"SHA-256 не совпадает"};checkMemory(c,spec)
        val h=open(tmp.absolutePath);check(h!=0L){"Не удалось загрузить Whisper"};close(h);check(!Thread.currentThread().isInterrupted)
        java.nio.file.Files.move(tmp.toPath(),model(c).toPath(),java.nio.file.StandardCopyOption.ATOMIC_MOVE,java.nio.file.StandardCopyOption.REPLACE_EXISTING)
        return spec.id
    }
    fun download(c:Context,spec:WhisperModelSpec.Model,progress:(Int)->Unit):String{
        require(available){"Whisper не включён в сборку"};require(spec in WhisperModelSpec.models);checkMemory(c,spec)
        require(c.filesDir.usableSpace>spec.size+32L*1024*1024){"Недостаточно места для модели"}
        val tmp=File(c.filesDir,"whisper-download-"+java.util.UUID.randomUUID()+".bin")
        try{WhisperDownload.fetch(spec,tmp,progress);return activate(c,tmp)}finally{tmp.delete()}
    }
'''+s[b:]
p.write_text(s)
# Give larger Whisper models a bounded beam search when there is additional free memory.
replace("WhisperLocal.kt","private external fun recognize(handle:Long,pcm:FloatArray,language:String,threads:Int):ByteArray?","private external fun recognize(handle:Long,pcm:FloatArray,language:String,threads:Int,beam:Int):ByteArray?")
replace("WhisperLocal.kt","handle=open(model(c).absolutePath);check(handle!=0L)","checkMemory(c,spec);val memory=android.app.ActivityManager.MemoryInfo();(c.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager).getMemoryInfo(memory);val beam=spec.beamSize(memory.availMem,memory.lowMemory);status(if(beam>1)\"Whisper · точный поиск\" else \"Whisper · обычный поиск\");handle=open(model(c).absolutePath);check(handle!=0L)")
replace("WhisperLocal.kt","availableProcessors().coerceIn(1,4))?:error","availableProcessors().coerceIn(1,4),beam)?:error")
bridge=Path(sys.argv[1])/'native/whisper/bridge.cpp'
s=bridge.read_text()
def native(a,b):
 global s
 assert s.count(a)==1,("Whisper JNI",a[:80],s.count(a))
 s=s.replace(a,b)
native('starts.size()<2||starts.size()>200','starts.empty()||starts.size()>200')
native('jstring language,jint threads){','jstring language,jint threads,jint beam){')
native('auto p=whisper_full_default_params(WHISPER_SAMPLING_GREEDY);','const bool accurate=beam==3;auto p=whisper_full_default_params(accurate?WHISPER_SAMPLING_BEAM_SEARCH:WHISPER_SAMPLING_GREEDY);if(accurate){p.beam_search.beam_size=3;p.greedy.best_of=3;}')
bridge.write_text(s)
p=src/'MainActivity.kt';s=p.read_text()
a=s.index('    private fun whisperModelDialog(){')
b=s.index('    private fun recognizeWhisper(',a)
s=s[:a]+'''    private fun whisperModelDialog(){
        if(stemBusy)return
        if(!WhisperLocal.available){toast("Whisper не включён в сборку");return}
        val active=WhisperLocal.installed(this)?.title?:"не установлена"
        val models=WhisperModelSpec.models
        android.app.AlertDialog.Builder(this).setTitle("Распознавание вокала · Whisper").setItems(models.map{it.title+when(it.id){"tiny"->" · быстрая";"base-q5_1"->" · компактная, баланс";"base"->" · полная Base";"small-q5_1"->" · рекомендуемая для точности";else->" · полная Small, тяжёлая"}}.toTypedArray()){_,i->
            val spec=models[i]
            android.app.AlertDialog.Builder(this).setTitle(spec.title).setMessage("Текущая модель: $active.\\nЗагрузка из официального источника, проверка размера, SHA-256 и запуска модели. Музыка не отправляется. Точность на пении не гарантирована.").setNegativeButton("Отмена",null).setPositiveButton("Скачать"){_,_->stemWork("Загрузка Whisper…",{WhisperLocal.download(this,spec){updateWork("Whisper: $it%")}}){id->toast("Whisper $id установлен");render()}}.show()
        }.setNeutralButton("Импорт файла"){_,_->whisperPicker.launch(arrayOf("*/*"))}.setNegativeButton("Закрыть",null).show()
    }
'''+s[b:]
p.write_text(s)
print("PASS: direct pinned Whisper download, FP32 AST candidate and Demucs memory preflight")
