package app.remix.player
fun main(){
 val sparse=ProducerAdaptation.factors(.04,listOf(.02,.1,.2),.3,true)
 val dense=ProducerAdaptation.factors(.30,listOf(.2,.2,.21),.01,false)
 check(sparse.drums>dense.drums&&sparse.bass>dense.bass&&sparse.lead>dense.lead)
 val muted=ProducerAdaptation.adapt(GenreMix(0f,0f,0f,1f,0f,0f),dense)
 check(muted.drums==0f&&muted.bass==0f&&muted.lead==0f&&muted.vocals==0f)
 check(ProducerAdaptation.adapt(GenreMix(),ProducerAdaptation.factors(Double.NaN,listOf(Double.NaN),Double.NaN,false)).values().all{it.isFinite()&&it in 0f..2f})
 println("PASS: source-dependent levels, user mute preservation and finite fallback")
}
