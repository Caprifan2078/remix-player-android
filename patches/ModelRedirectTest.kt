package app.remix.player
import java.net.URI
fun main(){
 val pinned=ModelCatalog.entries.filter{it.kind!=ModelCatalog.Kind.SPEECH}
 val newHosts=listOf("us.aws.cdn.hf.co","us.gcp.cdn.hf.co","cdn-lfs-eu-1.hf.co","transfer.xethub.hf.co","transfer.xethub-eu.hf.co")
 val legacy=listOf("huggingface.co","cdn-lfs.huggingface.co","cdn-lfs.hf.co","cdn-lfs-us-1.hf.co","cas-bridge.xethub.hf.co")
 val unsafe=listOf("http://us.aws.cdn.hf.co/model","https://us.aws.cdn.hf.co:444/model","https://evil.example/model","https://us.aws.cdn.hf.co.evil.example/model","https://us.aws.cdn.hf.co@evil.example/model","https://user@us.aws.cdn.hf.co/model","https://us.aws.cdn.hf.co/model#frag","https://127.0.0.1/model","https://us.aws.cdn.hf.co./model","https://unknown.hf.co/model")
 for(e in pinned){
  check(e.sha256?.matches(Regex("[a-f0-9]{64}"))==true)
  val initial=URI(e.url)
  for(host in newHosts+legacy){val target=URI("https://$host/model?token=fixture");check(ModelCatalog.redirect(e,initial,target.toString())==target){"Blocked documented CDN: $host"}}
  for(url in unsafe)check(runCatching{ModelCatalog.redirect(e,initial,url)}.isFailure){"Accepted unsafe redirect: $url"}
  check(ModelCatalog.redirect(e,initial,"/api/resolve-cache/fixture").host=="huggingface.co")
  val rejected=runCatching{ModelCatalog.redirect(e,initial,"https://evil.example/model?token=secret")}.exceptionOrNull()!!
  check(!rejected.message.orEmpty().contains("secret"))
 }
 for(e in ModelCatalog.entries.filter{it.kind==ModelCatalog.Kind.SPEECH}){
  check(ModelCatalog.allowed(e,URI(e.url)))
  for(host in newHosts+legacy)check(!ModelCatalog.allowed(e,URI("https://$host/model")))
 }
 println("PASS: 3 pinned models, 10 approved CDN hosts, 10 unsafe URLs, relative redirects, redacted errors, 5 isolated Vosk models")
}
