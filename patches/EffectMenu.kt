package app.remix.player

/** UI labels only. Persisted preset IDs and DSP parameters remain unchanged. */
object EffectMenu {
    private val labels=linkedMapOf(
        "Оригинал" to ("Основное" to "Оригинал"),
        "Sped Up" to ("Скорость" to "Ускорение"),
        "Nightcore" to ("Скорость" to "Найткор"),
        "Super Sped Up" to ("Скорость" to "Сильное ускорение"),
        "Slowed" to ("Скорость" to "Замедление"),
        "Daycore" to ("Скорость" to "Дэйкор"),
        "Slowed + Reverb" to ("Скорость" to "Медленно + эхо"),
        "Super Slowed" to ("Скорость" to "Сильное замедление"),
        "Super Slowed + Reverb" to ("Скорость" to "Сильное замедление + эхо"),
        "Ultra Slowed" to ("Скорость" to "Ультрамедленно"),
        "Sped Up + Reverb" to ("Скорость" to "Ускорение + эхо"),
        "Bass Boost" to ("Бас" to "Усиление баса"),
        "Deep Bass" to ("Бас" to "Глубокий бас"),
        "8D Audio" to ("Пространство" to "8D-звук"),
        "Concert Hall" to ("Пространство" to "Концертный зал"),
        "Dreamy" to ("Атмосфера" to "Мечтательный"),
        "Underwater" to ("Атмосфера" to "Под водой"),
        "Vintage" to ("Атмосфера" to "Винтаж"),
        "Distorted" to ("Искажение" to "Искажение"),
        "Dark Edit" to ("Атмосфера" to "Тёмный звук"),
        "Gym Edit" to ("Атмосфера" to "Для тренировки"),
        "Vaporwave effect" to ("Атмосфера" to "Вейпорвейв"),
        "Ultra Sped Up" to ("Скорость" to "Ультраускорение"),
        "Extreme Slowed" to ("Скорость" to "Экстремальное замедление"),
        "Slow Dream" to ("Атмосфера" to "Медленный сон"),
        "Nightcore Reverb" to ("Скорость" to "Найткор + эхо"),
        "Daycore Echo" to ("Скорость" to "Дэйкор + эхо"),
        "Deep Space" to ("Пространство" to "Космос"),
        "Cathedral" to ("Пространство" to "Собор"),
        "Small Room" to ("Пространство" to "Малая комната"),
        "Next Room" to ("Пространство" to "За стеной"),
        "Soft Bass" to ("Бас" to "Мягкий бас"),
        "Bass + Reverb" to ("Бас" to "Бас + эхо"),
        "Sub Bass" to ("Бас" to "Саббас"),
        "Overdrive" to ("Искажение" to "Перегруз"),
        "Extreme Distortion" to ("Искажение" to "Сильное искажение"),
        "Lo-Fi Filter" to ("Атмосфера" to "Лоу-фай"),
        "Cassette Filter" to ("Атмосфера" to "Кассета"),
        "Radio Filter" to ("Атмосфера" to "Радио"),
        "Slow Stereo Orbit" to ("Пространство" to "Медленная орбита"),
        "Fast Stereo Orbit" to ("Пространство" to "Быстрая орбита")
    )
    fun title(name:String)=labels[name]?.second?:name
    fun groups(presets:List<Preset>):Map<String,List<Preset>> = presets.groupBy{labels[it.name]?.first?:"Другие"}
}
