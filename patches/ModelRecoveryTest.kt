package app.remix.player
import java.net.URI
fun main(){
 val min=ModelMemoryBudget.MIN_FREE;val large=166L*1024*1024
 check(!ModelMemoryBudget.canStart(large,min-1,false));check(ModelMemoryBudget.canStart(large,min,false))
 check(!ModelMemoryBudget.canStart(large,min,true));check(ModelMemoryBudget.canStart(1024,0,false));check(!ModelMemoryBudget.canStart(0,min,false))
 for(spec in WhisperModelSpec.models){
  val src=WhisperDownload.source(spec);check(WhisperDownload.allowed(src));check(src.path.contains("/resolve/"));check(spec.sha.matches(Regex("[a-f0-9]{64}")))
  for(host in listOf("us.aws.cdn.hf.co","cas-bridge.xethub.hf.co","cdn-lfs.hf.co"))check(WhisperDownload.redirect(src,"https://$host/model?token=abc").host==host)
  for(url in listOf("http://huggingface.co/file","https://huggingface.co.evil.example/file","https://evil.example/file","https://user@huggingface.co/file","https://huggingface.co:444/file","https://huggingface.co/file#fragment","https://127.0.0.1/file"))check(runCatching{WhisperDownload.redirect(src,url)}.isFailure)
 }
 val ast=ModelCatalog.entries.single{it.kind==ModelCatalog.Kind.GENRE}
 check(ast.id=="ast-gtzan-fp32"&&ast.sizeMb==345&&ast.sha256=="71bbd4bd350fdee6c6940778a5a9c85471628cec91a505bad1d4f5cd6b3fb673")
 println("PASS: memory threshold boundaries, pinned full precision AST metadata, official Whisper redirect and unsafe host rejection")
}
