package app.remix.player
/** Respect user mix settings: conservative source-aware scaling, never fabricate a reliable tempo. */
object ProducerAdaptation {
 data class Factors(val drums:Float,val bass:Float,val lead:Float,val oldDrums:Float)
 fun factors(rms:Double,energy:List<Double>,harmonyConfidence:Double,isolated:Boolean):Factors{
  val e=energy.filter{it.isFinite()&&it>=0}.sorted()
  val median=e.getOrNull(e.size/2)?:0.0
  val top=e.getOrNull((e.size*.9).toInt().coerceAtMost((e.size-1).coerceAtLeast(0)))?:0.0
  val dense=if(rms.isFinite())((rms-.08)/.18).coerceIn(0.0,1.0) else .5
  val dynamic=if(top>1e-8)(1-median/top).coerceIn(0.0,1.0) else 0.0
  val confidence=if(harmonyConfidence.isFinite())harmonyConfidence.coerceIn(0.0,1.0) else 0.0
  return Factors((1.05-.25*dense+.08*dynamic).toFloat(),(1.02-.30*dense).toFloat(),(if(confidence<.06).5 else .72+.20*dynamic).toFloat(),if(isolated).85f else 1f)
 }
 fun adapt(m:GenreMix,f:Factors)=m.copy(drums=(m.drums*f.drums).coerceIn(0f,2f),bass=(m.bass*f.bass).coerceIn(0f,2f),lead=(m.lead*f.lead).coerceIn(0f,2f),oldDrums=(m.oldDrums*f.oldDrums).coerceIn(0f,2f))
}
