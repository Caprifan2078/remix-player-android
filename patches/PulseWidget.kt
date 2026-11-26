package app.remix.player
import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.media.MediaMetadataRetriever
import android.os.Handler
import android.os.Looper
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.ArrayBlockingQueue
import android.util.SizeF
import android.view.View
import android.widget.RemoteViews
import androidx.media3.common.Player
import androidx.media3.common.PlaybackParameters

/** No periodic work or service launch. Only UI events and existing playback events. */
class PulseWidget:AppWidgetProvider(){
    override fun onUpdate(context:Context,manager:AppWidgetManager,ids:IntArray){ids.forEach{render(context,manager,it)};requestCover(context)}
    override fun onAppWidgetOptionsChanged(context:Context,manager:AppWidgetManager,id:Int,options:Bundle){render(context,manager,id)}
    override fun onReceive(context:Context,intent:Intent){
        if(intent.action==COMMAND){
            val p=player?:return
            val command=intent.getStringExtra("command")?:return
            if(!WidgetPolicy.allowed(intent.getStringExtra(TRACK),p.currentMediaItem?.mediaId,MixerSession.active)){publish(context);return}
            when(command){
                "prev"->if(p.hasPreviousMediaItem())p.seekToPreviousMediaItem()
                "next"->if(p.hasNextMediaItem())p.seekToNextMediaItem()
                "play"->if(p.mediaItemCount>0){
                    if(p.playWhenReady&&p.playbackState!=Player.STATE_ENDED&&p.playerError==null)p.pause()
                    else{if(p.playbackState==Player.STATE_ENDED)p.seekTo(0);if(p.playbackState==Player.STATE_IDLE)p.prepare();p.play()}
                }
                else->{
                    val name=WidgetPolicy.selection(command,Presets.active.name)?:return
                    val preset=Presets.all.firstOrNull{it.name==name}?:return
                    Presets.active=preset;p.playbackParameters=PlaybackParameters(preset.speed,preset.pitch)
                }
            }
            publish(context);return
        }
        super.onReceive(context,intent)
    }
    companion object{
        private const val COMMAND="app.remix.player.widget.COMMAND"
        const val OPEN="app.remix.player.widget.OPEN"
        const val TRACK="widget_track"
        const val ROUTE="widget_route"
        private data class State(val id:String?,val title:String,val artist:String,val playing:Boolean,val ready:Boolean,val prev:Boolean,val next:Boolean,val preset:String)
        private var player:Player?=null
        private var listener:Player.Listener?=null
        private var last:State?=null
        private var coverId:String?=null
        private var cover:Bitmap?=null
        private var coverGeneration=0L
        private val main=Handler(Looper.getMainLooper())
        private val covers=ThreadPoolExecutor(0,1,15L,TimeUnit.SECONDS,ArrayBlockingQueue<Runnable>(1),ThreadPoolExecutor.DiscardOldestPolicy())
        private fun requestCover(context:Context){
            val manager=AppWidgetManager.getInstance(context)
            if(manager.getAppWidgetIds(ComponentName(context,PulseWidget::class.java)).isEmpty())return
            val s=state();val id=s.id
            if(id==coverId)return
            coverId=id;cover=null;val generation=++coverGeneration
            covers.queue.clear()
            val uri=id?.let{Uri.parse(it)}
            if(id==null||uri?.scheme!="content")return
            val app=context.applicationContext
            covers.execute{
                val bitmap=runCatching{
                    val retriever=MediaMetadataRetriever()
                    try{
                        retriever.setDataSource(app,uri)
                        val bytes=retriever.embeddedPicture?:return@runCatching null
                        if(bytes.size>8*1024*1024)return@runCatching null
                        val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true}
                        BitmapFactory.decodeByteArray(bytes,0,bytes.size,bounds)
                        if(bounds.outWidth !in 1..16384||bounds.outHeight !in 1..16384)return@runCatching null
                        var sample=1
                        while(maxOf(bounds.outWidth,bounds.outHeight)/sample>256)sample*=2
                        BitmapFactory.decodeByteArray(bytes,0,bytes.size,BitmapFactory.Options().apply{inSampleSize=sample})
                    }finally{retriever.release()}
                }.getOrNull()
                main.post{
                    if(generation==coverGeneration&&state().id==id){
                        cover=bitmap
                        manager.getAppWidgetIds(ComponentName(app,PulseWidget::class.java)).forEach{render(app,manager,it)}
                    }
                }
            }
        }
        private fun state():State{
            val p=player
            return if(p==null||p.mediaItemCount==0||MixerSession.active)State(null,"Pulse","Откройте плеер",false,false,false,false,"Оригинал")
            else State(p.currentMediaItem?.mediaId,p.mediaMetadata.title?.toString()?.take(200).orEmpty().ifBlank{"Pulse"},p.mediaMetadata.artist?.toString()?.take(200).orEmpty(),p.playWhenReady&&p.playbackState!=Player.STATE_ENDED,true,p.hasPreviousMediaItem(),p.hasNextMediaItem(),Presets.active.name)
        }
        fun attach(context:Context,p:Player){
            detach(context);player=p
            val app=context.applicationContext
            listener=object:Player.Listener{override fun onEvents(player:Player,events:Player.Events){publish(app)}}
            p.addListener(listener!!);publish(app)
        }
        fun detach(context:Context){listener?.let{player?.removeListener(it)};listener=null;player=null;publish(context)}
        fun refresh(context:Context)=publish(context)
        private fun publish(context:Context){
            val s=state();if(last==s)return;last=s
            requestCover(context)
            val manager=AppWidgetManager.getInstance(context)
            manager.getAppWidgetIds(ComponentName(context,PulseWidget::class.java)).forEach{render(context,manager,it)}
        }
        private fun render(context:Context,manager:AppWidgetManager,id:Int){
            val s=state()
            if(Build.VERSION.SDK_INT>=31){
                manager.updateAppWidget(id,RemoteViews(mapOf(
                    SizeF(120f,64f) to build(context,s,WidgetPolicy.Size.COMPACT),
                    SizeF(230f,116f) to build(context,s,WidgetPolicy.Size.MIX),
                    SizeF(280f,184f) to build(context,s,WidgetPolicy.Size.STUDIO)
                )))
            }else{
                val options=manager.getAppWidgetOptions(id)
                manager.updateAppWidget(id,build(context,s,WidgetPolicy.size(options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,230),options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,116))))
            }
        }
        internal fun testView(context:Context,width:Int,height:Int):RemoteViews=build(context,State("qa-track","QA Track","QA Artist",true,true,true,true,"Nightcore + Bass"),WidgetPolicy.size(width,height))
        private fun build(context:Context,s:State,size:WidgetPolicy.Size):RemoteViews{
            val expanded=size!=WidgetPolicy.Size.COMPACT
            val studio=size==WidgetPolicy.Size.STUDIO
            val v=RemoteViews(context.packageName,R.layout.pulse_widget)
            val flags=PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            fun uri(kind:String,action:String)=Uri.Builder().scheme("pulsewidget").authority(kind).appendPath(action).appendPath(s.id.orEmpty()).build()
            fun open(route:String)=PendingIntent.getActivity(context,90,Intent(context,MainActivity::class.java).setAction(OPEN).setData(uri("open",route)).putExtra(TRACK,s.id).putExtra(ROUTE,route).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP),flags)
            fun command(action:String)=PendingIntent.getBroadcast(context,91,Intent(context,PulseWidget::class.java).setAction(COMMAND).setData(uri("command",action)).putExtra(TRACK,s.id).putExtra("command",action),flags)
            fun visible(id:Int,on:Boolean){v.setViewVisibility(id,if(on)View.VISIBLE else View.GONE)}
            v.setTextViewText(R.id.widget_title,s.title);v.setTextViewText(R.id.widget_artist,s.artist)
            val art=cover.takeIf{s.id!=null&&coverId==s.id}
            if(art!=null)v.setImageViewBitmap(R.id.widget_art,art)else v.setImageViewResource(R.id.widget_art,android.R.drawable.ic_media_play)
            v.setOnClickPendingIntent(R.id.widget_search,open("search"))
            v.setTextViewText(R.id.widget_mode,if(s.preset=="Оригинал")"ORIGINAL" else s.preset)
            v.setImageViewResource(R.id.widget_play,if(s.playing)android.R.drawable.ic_media_pause else android.R.drawable.ic_media_play)
            v.setContentDescription(R.id.widget_play,if(s.playing)"Пауза" else "Воспроизвести")
            visible(R.id.widget_art,expanded);visible(R.id.widget_artist,expanded)
            visible(R.id.widget_prev,expanded&&s.prev);visible(R.id.widget_next,expanded&&s.next)
            visible(R.id.widget_effects,expanded&&s.ready);visible(R.id.widget_studio,studio&&s.ready);visible(R.id.widget_detail,studio)
            v.setOnClickPendingIntent(R.id.widget_title,open("player"));v.setOnClickPendingIntent(R.id.widget_artist,open("player"));v.setOnClickPendingIntent(R.id.widget_art,open("player"))
            v.setOnClickPendingIntent(R.id.widget_play,if(s.ready)command("play")else open("player"))
            v.setOnClickPendingIntent(R.id.widget_prev,command("prev"));v.setOnClickPendingIntent(R.id.widget_next,command("next"))
            for((id,action) in listOf(R.id.widget_fast to "fast",R.id.widget_night to "night",R.id.widget_slow to "slow",R.id.widget_reset to "reset")){
                v.setInt(id,"setBackgroundResource",if(WidgetPolicy.effects[action]==s.preset)R.drawable.pulse_widget_chip_active else R.drawable.pulse_widget_chip)
                v.setTextColor(id,if(WidgetPolicy.effects[action]==s.preset)0xff171126.toInt() else 0xffe9e4ff.toInt())
                v.setOnClickPendingIntent(id,command(action))
            }
            v.setOnClickPendingIntent(R.id.widget_edit,open("edit"));v.setOnClickPendingIntent(R.id.widget_save,open("save"));v.setOnClickPendingIntent(R.id.widget_genres,open("genres"));v.setOnClickPendingIntent(R.id.widget_lyrics,open("lyrics"))
            return v
        }
    }
}
