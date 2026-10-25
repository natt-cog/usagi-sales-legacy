#!/usr/bin/env python3
"""主な業務フローの操作動画: 受注入力→確認→登録→受注照会→夜間バッチ（pipeline.py）→請求照会。
CDP の Page.startScreencast のフレームを 10fps に並べ直して ffmpeg で mp4 にする。出力: evidence/video/"""
import os, glob, base64, time, subprocess, threading, html, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); EVD = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(EVD, 'video'); os.makedirs(OUT, exist_ok=True)
B = 'http://localhost:8080/usagi/'
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-1248/chrome-linux*/chrome'))[0]
frames = []; lock = threading.Lock()
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=EXE)
    pg = br.new_page(viewport={'width': 1280, 'height': 720}, locale='ja-JP')
    cdp = pg.context.new_cdp_session(pg)
    def on_frame(e):
        with lock: frames.append((time.time(), base64.b64decode(e['data'])))
        cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})
    cdp.on('Page.screencastFrame', on_frame)
    cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 80, 'maxWidth': 1280, 'maxHeight': 720})
    w = lambda s=1.2: pg.wait_for_timeout(int(s * 1000))
    def typ(sel, v): pg.click(sel); pg.fill(sel, ''); pg.type(sel, v, delay=60)
    pg.goto(B + 'login.jsp'); w()
    typ('input[name=userId]', 'user01'); typ('input[name=password]', 'usagi01'); w(.5); pg.click('input[type=submit]'); w()
    pg.click('text=受注入力'); w()
    typ('input[name=juchuYmd]', '20241220'); typ('input[name=tkCd]', '100001')
    pg.select_option('select[name=shCd]', value='200001'); typ('input[name=suryo]', '100'); w()
    pg.click('input[type=submit]'); w(2.5)
    pg.click('input[type=submit][value=登録]'); w(1.5)
    pg.screenshot(path=os.path.join(EVD, 'screens', '07_juchu_complete.png'))
    no = pg.inner_text('b'); w(1)
    pg.click('text=受注照会へ'); w(3)
    pg.screenshot(path=os.path.join(EVD, 'screens', '08_juchu_inquiry_registered.png'))
    pg.set_content('<html><body style="font-family:sans-serif;padding:40px"><h2>夜間バッチ実行中</h2><p>JuchuExtract → USJ010（SORT・USB100）→ USJ020（USB200）→ USJ030（SORT・USB300）→ SeikyuImport → USJ040（USB400・USR500・USR510）</p></body></html>')
    w(1)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'pipeline.py'), os.path.join(EVD, 'batch', 'run_e2e')], capture_output=True, text=True)
    open(os.path.join(EVD, 'batch', 'run_e2e.log'), 'w').write(r.stdout + r.stderr)
    pg.set_content('<html><body style="font-family:sans-serif;padding:30px"><h2>夜間バッチ ジョブログ（受注 ' + no + ' を含めて実行）</h2><pre style="font-size:15px;background:#111;color:#0f0;padding:16px">'
                   + html.escape(r.stdout) + '</pre></body></html>')
    w(5)
    pg.goto(B + 'menu.do'); w(.8); pg.click('text=請求照会'); w()
    typ('input[name=tkCd]', '100001'); typ('input[name=fromYm]', '202412'); typ('input[name=toYm]', '202501'); w(.5)
    pg.click('input[type=submit]'); w(4)
    pg.screenshot(path=os.path.join(EVD, 'screens', '09_seikyu_inquiry_after_batch.png'))
    cdp.send('Page.stopScreencast'); br.close()
open(os.path.join(OUT, 'juchu_no.txt'), 'w').write(no + '\n')
# 10fps に並べ直す
t0, t1 = frames[0][0], frames[-1][0]; seq = []; j = 0
for k in range(int((t1 - t0) * 10) + 1):
    t = t0 + k / 10
    while j + 1 < len(frames) and frames[j + 1][0] <= t: j += 1
    seq.append(frames[j][1])
mp4 = os.path.join(OUT, 'EV03-EV08_受注入力から請求照会.mp4')
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '10', '-i', '-', '-vf', 'scale=1280:-2', '-pix_fmt', 'yuv420p', mp4], stdin=subprocess.PIPE)
for f in seq: ff.stdin.write(f)
ff.stdin.close(); ff.wait()
print(no, len(seq) / 10, 's', mp4)
