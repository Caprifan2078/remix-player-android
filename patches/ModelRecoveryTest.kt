package app.remix.player
import java.net.URI
fun main(){
 val mb=1024L*1024
 val min=ModelMemoryBudget.MIN_FREE
 val cases=listOf(
  Triple(1L,0L,false) to false,
  Triple(1L,-1L,false) to false,
  Triple(mb,min,true) to false,
  Triple(mb,64*mb-1,false) to false,
  Triple(mb,64*mb,false) to true,
  Triple(32*mb,128*mb-1,false) to false,
  Triple(32*mb,128*mb,false) to true,
  Triple(32*mb+1,min-1,false) to false,
  Triple(32*mb+1,min,false) to true,
  Triple(166*mb,min,true) to false,
  Triple(0L,min,false) to false,
  Triple(-1L,min,false) to false,
  Triple(Long.MAX_VALUE,min,false) to false
 )
 cases.forEachIndexed{i,(c,want)->check(ModelMemoryBudget.canStart(c.first,c.second,c.third)==want){"Memory case ${i+1}"}}
 for(spec in WhisperModelSpec.models){
  val src=WhisperDownload.source(spec);check(WhisperDownload.allowed(src));check(src.path.contains("/resolve/"));check(spec.sha.matches(Regex("[a-f0-9]{64}")))
  for(host in listOf("us.aws.cdn.hf.co","cas-bridge.xethub.hf.co","cdn-lfs.hf.co"))check(WhisperDownload.redirect(src,"https://$host/model?token=abc").host==host)
  for(url in listOf("http://huggingface.co/file","https://huggingface.co.evil.example/file","https://evil.example/file","https://user@huggingface.co/file","https://huggingface.co:444/file","https://huggingface.co/file#fragment","https://127.0.0.1/file"))check(runCatching{WhisperDownload.redirect(src,url)}.isFailure)
 }
 val specs=WhisperModelSpec.models
 val base=WhisperModelSpec.bySize(59707625L)
 val small=WhisperModelSpec.bySize(190085487L)
 val q5Checks=listOf(
  base?.id=="base-q5_1",small?.id=="small-q5_1",
  WhisperModelSpec.matches(59707625L,"422f1ae452ade6f30a004d7e5c6a43195e4433bc370bf23fac9cc591f01a8898"),
  WhisperModelSpec.matches(190085487L,"ae85e4a935d7a567bd102fe55afc16bb595bdb618e11b2fc7591bc08120411bb"),
  base?.source?.endsWith("/ggml-base-q5_1.bin")==true,
  small?.source?.endsWith("/ggml-small-q5_1.bin")==true,
  (base?.minFreeRam?:0)>=768L*1024*1024,
  (small?.minFreeRam?:0)>=1536L*1024*1024,
  specs.map{it.id}.toSet().containsAll(listOf("tiny","base","small")),
  specs.map{it.size}.distinct().size==specs.size,
  !WhisperModelSpec.matches(59707625L,"0".repeat(64)),
  !WhisperModelSpec.matches(190085488L,"ae85e4a935d7a567bd102fe55afc16bb595bdb618e11b2fc7591bc08120411bb"),
  WhisperModelSpec.maxBytes==487601967L)
 q5Checks.forEachIndexed{i,pass->check(pass){"Q5 catalogue case ${i+1}"}}
 println("PASS: 13 compact multilingual Whisper catalogue checks")
 val ast=ModelCatalog.entries.single{it.kind==ModelCatalog.Kind.GENRE}
 check(ast.id=="ast-gtzan-fp32"&&ast.sizeMb==345&&ast.sha256=="71bbd4bd350fdee6c6940778a5a9c85471628cec91a505bad1d4f5cd6b3fb673")
 println("PASS: memory threshold boundaries, pinned full precision AST metadata, official Whisper redirect and unsafe host rejection")
}
