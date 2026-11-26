package app.remix.player
import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.RemoteViews
import androidx.media3.common.Player

/** Event-driven home screen controls; no timer, service startup or network in receiver. */
class PulseWidget:AppWidgetProvider(){
    override fun onUpdate(context:Context,manager:AppWidgetManager,ids:IntArray){ids.forEach{render(context,manager,it)}}
    override fun onAppWidgetOptionsChanged(context:Context,manager:AppWidgetManager,id:Int,options:Bundle){render(context,manager,id)}
    override fun onReceive(context:Context,intent:Intent){
        if(intent.action in listOf(PREV,PLAY,NEXT)){
            val p=player?:return
            when(intent.action){
                PREV->if(p.hasPreviousMediaItem())p.seekToPreviousMediaItem()
                NEXT->if(p.hasNextMediaItem())p.seekToNextMediaItem()
                PLAY->if(p.mediaItemCount>0){if(p.playWhenReady)p.pause()else p.play()}
            }
            publish(context);return
        }
        super.onReceive(context,intent)
    }
    companion object{
        private const val PREV="app.remix.player.widget.PREV"
        private const val PLAY="app.remix.player.widget.PLAY"
        private const val NEXT="app.remix.player.widget.NEXT"
        private data class State(val title:String,val artist:String,val playing:Boolean,val ready:Boolean,val prev:Boolean,val next:Boolean)
        private var player:Player?=null
        private var listener:Player.Listener?=null
        private var last:State?=null
        private fun state():State{
            val p=player
            return if(p==null||p.mediaItemCount==0)State("Pulse","Откройте плеер",false,false,false,false)
            else State(p.mediaMetadata.title?.toString()?.take(200).orEmpty().ifBlank{"Pulse"},p.mediaMetadata.artist?.toString()?.take(200).orEmpty(),p.playWhenReady,true,p.hasPreviousMediaItem(),p.hasNextMediaItem())
        }
        fun attach(context:Context,p:Player){
            detach(context);player=p
            val app=context.applicationContext
            listener=object:Player.Listener{override fun onEvents(player:Player,events:Player.Events){publish(app)}}
            p.addListener(listener!!);publish(app)
        }
        fun detach(context:Context){listener?.let{player?.removeListener(it)};listener=null;player=null;publish(context)}
        private fun publish(context:Context){
            val s=state();if(last==s)return;last=s
            val manager=AppWidgetManager.getInstance(context)
            manager.getAppWidgetIds(ComponentName(context,PulseWidget::class.java)).forEach{render(context,manager,it)}
        }
        private fun render(context:Context,manager:AppWidgetManager,id:Int){
            val s=state();val options=manager.getAppWidgetOptions(id)
            val wide=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,220)>=170
            val tall=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,96)>=85
            val v=RemoteViews(context.packageName,R.layout.pulse_widget)
            val open=PendingIntent.getActivity(context,90,Intent(context,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
            fun command(action:String,n:Int)=PendingIntent.getBroadcast(context,n,Intent(context,PulseWidget::class.java).setAction(action),PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
            v.setTextViewText(R.id.widget_title,s.title);v.setTextViewText(R.id.widget_artist,s.artist)
            v.setTextViewText(R.id.widget_play,if(s.playing)"Ⅱ" else "▶")
            v.setContentDescription(R.id.widget_play,if(s.playing)"Пауза" else "Воспроизвести")
            v.setViewVisibility(R.id.widget_artist,if(tall)View.VISIBLE else View.GONE)
            v.setViewVisibility(R.id.widget_prev,if(wide&&s.prev)View.VISIBLE else View.GONE)
            v.setViewVisibility(R.id.widget_next,if(wide&&s.next)View.VISIBLE else View.GONE)
            v.setOnClickPendingIntent(R.id.widget_title,open);v.setOnClickPendingIntent(R.id.widget_artist,open)
            v.setOnClickPendingIntent(R.id.widget_play,if(s.ready)command(PLAY,91)else open)
            v.setOnClickPendingIntent(R.id.widget_prev,command(PREV,92));v.setOnClickPendingIntent(R.id.widget_next,command(NEXT,93))
            manager.updateAppWidget(id,v)
        }
    }
}
