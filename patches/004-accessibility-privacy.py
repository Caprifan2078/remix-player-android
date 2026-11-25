#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])
def replace(path,old,new):
    f=root/path
    s=f.read_text()
    assert s.count(old)==1, f"{path}: expected exactly one occurrence of {old}"
    f.write_text(s.replace(old,new))
main="app/src/main/java/app/remix/player/MainActivity.kt"
replace(main,"minHeight=dp(44);minimumHeight=dp(44);setPadding","minHeight=dp(48);minimumHeight=dp(48);setPadding")
replace(main,"text=s;isAllCaps=false;textSize=14f;","""text=s;contentDescription=when(s){"⇄"->"Случайный порядок воспроизведения";"|◀"->"Предыдущая композиция";"▶|"->"Следующая композиция";"↻"->"Режим повтора";else->null};isAllCaps=false;textSize=14f;""")
replace(main,'bar.addView(now);now.contentDescription=','bar.addView(now);now.minimumHeight=dp(48);now.contentDescription=')
manifest="app/src/main/AndroidManifest.xml"
replace(manifest,'android:allowBackup="false"','android:allowBackup="false" android:dataExtractionRules="@xml/data_extraction_rules" android:icon="@drawable/ic_remix"')
xml=root/"app/src/main/res/xml/data_extraction_rules.xml"
exclusions="".join(f'<exclude domain="{domain}" path="."/>' for domain in ("root","file","database","sharedpref","external","device_root","device_file","device_database","device_sharedpref"))
xml.write_text(f'<?xml version="1.0" encoding="utf-8"?>\n<data-extraction-rules><cloud-backup>{exclusions}</cloud-backup><device-transfer>{exclusions}</device-transfer></data-extraction-rules>\n')
drawable=root/"app/src/main/res/drawable";drawable.mkdir(exist_ok=True)
(drawable/"ic_remix.xml").write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="48dp" android:height="48dp" android:viewportWidth="48" android:viewportHeight="48">
<path android:fillColor="#0C0E14" android:pathData="M0,0h48v48h-48z"/>
<path android:fillColor="#C0B0FF" android:pathData="M12,11L31,24L12,37Z M33,15h3v18h-3z M39,19h3v10h-3z"/>
</vector>''')
print("Applied checked accessibility/privacy overlay")
