package app.remix.player
import java.io.File
import java.security.MessageDigest
fun main(){
 val file=File.createTempFile("qa-model", ".bin")
 try{
  val bytes=ByteArray(1_048_576){(it*31).toByte()};file.writeBytes(bytes)
  val sha=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString(""){"%02x".format(it)}
  check(VerifiedDownload.matches(file,sha));check(!VerifiedDownload.matches(file,"0".repeat(64)))
  Thread.currentThread().interrupt()
  val result=try{runCatching{VerifiedDownload.matches(file,sha)}}finally{Thread.interrupted()}
  check(result.isFailure){"Cancelled checksum returned successfully"}
  check(file.readBytes().contentEquals(bytes));check(VerifiedDownload.matches(file,sha))
  println("PASS: checksum correctness, mismatch, cancellation, unchanged model, retry")
 }finally{file.delete()}
}
