#!/usr/bin/env python3
from pathlib import Path
import sys, xml.etree.ElementTree as ET
root=Path(sys.argv[1]); m=(root/'app/src/main/java/app/remix/player/MainActivity.kt').read_text()
manifest=ET.parse(root/'app/src/main/AndroidManifest.xml').getroot(); a='{http://schemas.android.com/apk/res/android}'; app=manifest.find('application')
checks={
'Android: 48dp default button target': 'minHeight=dp(48);minimumHeight=dp(48);setPadding' in m,
'Android: four transport accessibility names': all(s in m for s in ['Случайный порядок воспроизведения','Предыдущая композиция','Следующая композиция','Режим повтора']),
'Android: playback row target 48dp': 'now.minimumHeight=dp(48)' in m,
'Android: explicit icon': app.get(a+'icon')=='@drawable/ic_remix' and (root/'app/src/main/res/drawable/ic_remix.xml').is_file(),
'MASVS: cleartext disabled':app.get(a+'usesCleartextTraffic')=='false',
'MASVS: cloud backup disabled':app.get(a+'allowBackup')=='false',
'MASVS: services/provider not exported':all(e.get(a+'exported')=='false' for tag in ('service','provider') for e in app.findall(tag)),
'MASVS: file provider restricted to mixes/downloads': {(e.tag,e.get('path')) for e in ET.parse(root/'app/src/main/res/xml/file_paths.xml').getroot()}=={('files-path','mixes/'),('files-path','downloads/')},
'MASVS: explicit device transfer exclusion':app.get(a+'dataExtractionRules')=='@xml/data_extraction_rules',
'MASVS: no broad storage/recording permission':not any(e.get(a+'name','').split('.')[-1] in ('MANAGE_EXTERNAL_STORAGE','RECORD_AUDIO','READ_CONTACTS','ACCESS_FINE_LOCATION') for e in manifest.findall('uses-permission')),
}
if checks['MASVS: explicit device transfer exclusion']:
    rules=ET.parse(root/'app/src/main/res/xml/data_extraction_rules.xml').getroot()
    expected={(d,'.') for d in ('root','file','database','sharedpref','external','device_root','device_file','device_database','device_sharedpref')}
    checks['MASVS: explicit device transfer exclusion']=all({(e.get('domain'),e.get('path')) for e in rules.findall(tag+'/exclude')}==expected for tag in ('cloud-backup','device-transfer'))
for name,ok in checks.items():print(('PASS' if ok else 'FAIL')+': '+name.replace('\u200b',''))
print(f'{sum(checks.values())}/{len(checks)} PASS; static assertions only')
sys.exit(not all(checks.values()))
