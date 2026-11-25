#!/usr/bin/env python3
"""Obtain a fresh app-owned library hierarchy; never accept a system dialog as the UI."""
import pathlib, re, subprocess, sys, time, xml.etree.ElementTree as ET
PKG='app.remix.player'
ACTIVITY=PKG+'/.MainActivity'
REMOTE='/sdcard/remix-startup.xml'

def classify(raw):
    try: nodes=list(ET.fromstring(raw).iter('node'))
    except ET.ParseError: return 'invalid', None
    # Only recover a known emulator launcher ANR, never an application crash or ANR.
    launcher=any(n.get('package')=='android' and n.get('text')=="Pixel Launcher isn't responding" for n in nodes)
    if launcher:
        close=[n for n in nodes if n.get('package')=='android' and n.get('resource-id')=='android:id/aerr_close' and n.get('clickable')=='true']
        if len(close)==1:
            coords=list(map(int,re.findall(r'-?\d+',close[0].get('bounds',''))))
            if len(coords)==4 and coords[2]>coords[0] and coords[3]>coords[1]:
                return 'launcher-anr',((coords[0]+coords[2])//2,(coords[1]+coords[3])//2)
        return 'blocked',None
    if any(n.get('package')=='android' and n.get('resource-id')=='android:id/alertTitle' for n in nodes): return 'blocked',None
    app=[n for n in nodes if n.get('package')==PKG]
    labels={n.get('text') for n in app}
    if {'Моя музыка','Найти музыку на телефоне'}<=labels:return 'library',None
    return 'other',None

def adb(*args): return subprocess.check_output(['adb',*args],stderr=subprocess.STDOUT,timeout=25)

def capture(destination, attempts=4):
    destination=pathlib.Path(destination);destination.parent.mkdir(parents=True,exist_ok=True);destination.unlink(missing_ok=True)
    for i in range(attempts):
        try:
            adb('shell','am','start','-W','-n',ACTIVITY)
            # A failed dump must never leave an earlier, valid snapshot available for reuse.
            adb('shell','rm','-f',REMOTE)
            reply=adb('shell','uiautomator','dump',REMOTE)
            if b'ERROR' in reply or b'dumped to' not in reply: raise RuntimeError(reply.decode(errors='replace'))
            raw=adb('exec-out','cat',REMOTE)
            state,point=classify(raw)
            destination.with_name(f'{destination.stem}-attempt-{i+1}.xml').write_bytes(raw)
            if state=='library':
                assert adb('shell','pidof',PKG).strip(), 'App process missing'
                destination.write_bytes(raw);print('PASS: fresh app-owned library hierarchy',flush=True);return
            if state=='launcher-anr':
                print('Infrastructure: recovering Pixel Launcher ANR; not counting as app success',flush=True)
                adb('shell','input','tap',*map(str,point))
            elif state=='blocked':raise SystemExit('Unexpected system dialog, refusing to dismiss')
            else:print(f'Attempt {i+1}: {state}',flush=True)
        except (subprocess.SubprocessError,RuntimeError) as exc: print(f'Attempt {i+1}: {exc}',flush=True)
        time.sleep(1)
    raise SystemExit('No fresh app library hierarchy; startup acceptance failed')

if __name__=='__main__': capture(sys.argv[1])
