#!/usr/bin/env python3
"""業務イベントごとの短い操作動画（EV01〜EV09）と、要確認の挙動の再現動画（I01・I10・I11・I13）。
video.py と同じく CDP の Page.startScreencast のフレームを 10fps に並べ直して ffmpeg で mp4 にする。
動画の中で受注を登録し夜間バッチ（pipeline.py）を流すので、最後に登録した受注と得意先の値を元に戻し、
バッチをもう一度流して t_seikyu を元の状態にする。出力: evidence/video/、evidence/batch/run_clips/"""
import os, glob, base64, time, subprocess, threading, html, sys, json, re
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); EVD = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(EVD, '../../..'))
sys.path.insert(0, HERE)
import rlib
OUT = os.path.join(EVD, 'video'); os.makedirs(OUT, exist_ok=True)
RUN = os.path.join(EVD, 'batch', 'run_clips')
B = 'http://localhost:8080/usagi/'
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-1248/chrome-linux*/chrome'))[0]
COMPOSE = ['docker', 'compose', '-f', os.path.join(REPO, 'web/docker-compose.yml')]


def sql(q):
    return subprocess.run(COMPOSE + ['exec', '-T', 'db', 'psql', '-U', 'usagi', '-d', 'usagi', '-Atc', q],
                          capture_output=True, text=True, check=True).stdout.strip()


frames = []; lock = threading.Lock(); made = {}; T0 = [0.0]
CAPCSS = ('position:fixed;left:0;right:0;bottom:0;z-index:99;background:rgba(20,40,70,.92);color:#fff;'
          'font:bold 15px sans-serif;padding:7px 12px')


def page_html(title, body):
    return (f'<html><body style="font-family:sans-serif;padding:12px 16px 60px;font-size:12px"><h2>{title}</h2>{body}'
            f'</body></html>')


def table(rows, keys=None, hl=None):
    keys = keys or list(rows[0].keys())
    tr = lambda r: '<tr' + (' style="background:#ffe08a"' if hl and hl(r) else '') + '>' + ''.join(
        f'<td>{html.escape(str(r[k]))}</td>' for k in keys) + '</tr>'
    return ('<table border="1" cellpadding="4" style="border-collapse:collapse;font-size:11px"><tr>' +
            ''.join(f'<th style="background:#dde">{k}</th>' for k in keys) + '</tr>' + ''.join(tr(r) for r in rows) + '</table>')


def pre(s, size=11):
    return f'<pre style="font-size:{size}px;background:#111;color:#0f0;padding:12px;white-space:pre-wrap">{html.escape(s)}</pre>'


def main():
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=EXE)
        pg = br.new_page(viewport={'width': 800, 'height': 450}, device_scale_factor=1.6, locale='ja-JP')
        cdp = pg.context.new_cdp_session(pg)

        def on_frame(e):
            with lock: frames.append((time.time(), base64.b64decode(e['data'])))
            cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})
        cdp.on('Page.screencastFrame', on_frame)
        w = lambda s=1.2: pg.wait_for_timeout(int(s * 1000))

        def cap(t):
            pg.evaluate('([t,c])=>{let d=document.getElementById("cap");if(!d){d=document.createElement("div");d.id="cap";'
                        'd.style.cssText=c;document.body.appendChild(d)}d.textContent=t}', [t, CAPCSS])

        def go(url, t=None):
            pg.goto(B + url); t and cap(t); w(.8)

        def click(sel, t=None, s=1.2):
            pg.click(sel); t and cap(t); w(s)

        def typ(sel, v):
            pg.click(sel); pg.fill(sel, ''); pg.type(sel, v, delay=50)

        def show(title, body, t, s=4.0):
            pg.set_content(page_html(title, body)); cap(t); w(s)

        def scroll(n=3, s=1.5):
            for _ in range(n):
                pg.mouse.wheel(0, 400); w(s)

        def start():
            with lock: frames.clear()
            T0[0] = time.time()
            cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 80, 'maxWidth': 1280, 'maxHeight': 720})
            w(.3)

        def stop(name, title):
            w(1.5)
            with lock: fr = [f for f in frames if f[0] >= T0[0] + .25] or list(frames)  # 直前の動画の最後の画面を除く
            cdp.send('Page.stopScreencast'); w(.3)
            t0, t1 = fr[0][0], time.time(); seq = []; j = 0
            for k in range(int((t1 - t0) * 10) + 1):
                t = t0 + k / 10
                while j + 1 < len(fr) and fr[j + 1][0] <= t: j += 1
                seq.append(fr[j][1])
            mp4 = os.path.join(OUT, name + '.mp4')
            ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '10', '-i', '-',
                                   '-vf', 'scale=1280:-2', '-pix_fmt', 'yuv420p', '-crf', '28', mp4], stdin=subprocess.PIPE)
            for f in seq: ff.stdin.write(f)
            ff.stdin.close(); ff.wait()
            made[name] = {'file': 'evidence/video/' + name + '.mp4', 'title': title, 'sec': round(len(seq) / 10, 1)}
            print(name, made[name]['sec'], 's')

        def login():
            go('login.jsp'); typ('input[name=userId]', 'user01'); typ('input[name=password]', 'usagi01')
            click('input[type=submit]')

        def juchu(ymd, tk, sh, suryo, kbn='1', t=None):
            go('menu.do'); click('text=受注入力', t)
            typ('input[name=juchuYmd]', ymd); typ('input[name=tkCd]', tk)
            pg.select_option('select[name=shCd]', value=sh); typ('input[name=suryo]', suryo)
            pg.select_option('select[name=juchuKbn]', value=kbn); w(.6)
            click('input[type=submit][value=確認]', t, 2)

        def regist(t=None):
            click('input[type=submit][value=登録]', t, 1.5)
            return pg.inner_text('b').strip()

        def inquiry(no, t):
            go('menu.do'); click('text=受注照会', t)
            typ('input[name=no]', no); click('input[type=submit]', t, 3)

        def seikyu(tk, f, to, t, s=3):
            go('menu.do'); click('text=請求照会', t)
            typ('input[name=tkCd]', tk); typ('input[name=fromYm]', f); typ('input[name=toYm]', to)
            click('input[type=submit]', t, s)

        created = []
        orig_tokui = sql("select sime_kbn||'|'||hasu_kbn from m_tokui where tk_cd='100002'")

        # EV01
        start()
        go('login.jsp', 'EV01 ログイン：誤ったパスワードではエラーになる')
        typ('input[name=userId]', 'user01'); typ('input[name=password]', 'xxxx'); click('input[type=submit]', 'EV01 ログイン：誤ったパスワードではエラーになる', 2)
        typ('input[name=userId]', 'user01'); typ('input[name=password]', 'usagi01'); click('input[type=submit]', 'EV01 正しいパスワードでメニューへ', 2.5)
        stop('EV01_ログイン', 'ログイン失敗→ログイン成功→メニュー')

        # EV02
        start()
        go('menu.do', 'EV02 得意先照会'); click('text=得意先照会', 'EV02 得意先照会')
        typ('input[name=tkCd]', '100001'); click('input[name=search]', 'EV02 得意先コードで検索', 2.5)
        go('tokuiEdit.do', 'EV02 得意先メンテナンス（メニューにリンクがないため URL を直接指定）')
        typ('input[name=tkCd]', '100002'); click('input[type=submit][value=表示]', 'EV02 得意先メンテナンス：締日・端数・与信限度額を表示', 3)
        stop('EV02_得意先照会・メンテナンス', '得意先照会→得意先メンテナンス（直接 URL）')

        # EV03
        start()
        go('menu.do', 'EV03 受注入力'); click('text=受注入力', 'EV03 受注入力：日付の形式が違うとエラー')
        typ('input[name=juchuYmd]', '2024/12/18'); click('input[type=submit][value=確認]', 'EV03 受注入力：日付の形式が違うとエラー', 2)
        juchu('20241218', '100001', '200001', '20', t='EV03 受注入力→確認（単価・値引・金額を計算して表示）')
        no = regist('EV03 登録：受注番号を採番'); created.append(no)
        stop('EV03_受注入力', '受注入力（エラー→確認→登録）')

        # EV04
        start()
        inquiry(no, f'EV04 受注照会：EV03 で登録した受注 {no} を検索')
        go('menu.do'); click('text=受注照会', 'EV04 受注照会：得意先と受注日の範囲で検索')
        typ('input[name=tkCd]', '100001'); typ('input[name=fromYmd]', '20241201'); typ('input[name=toYmd]', '20241231')
        click('input[type=submit]', 'EV04 受注照会：得意先と受注日の範囲で検索（合計は表示行分）', 3); scroll(2, 1)
        stop('EV04_受注照会', '受注照会（受注番号・得意先と日付範囲）')

        # I01（夜間バッチを含む。EV05〜EV09 の素材もこの実行から）
        start()
        seikyu('100001', '202412', '202501', 'I01 夜間バッチ前の請求（得意先100001 の 202412）')
        juchu('20241219', '100001', '200001', '10', kbn='3', t='I01 無償サンプル（受注区分3）を入力：確認画面の金額は 0')
        w(1.5); fno = regist('I01 無償サンプルを登録'); created.append(fno)
        inquiry(fno, f'I01 受注照会：受注 {fno} の金額は 0')
        show('夜間バッチ実行中', '<p>JuchuExtract → USJ010（SORT・USB100）→ USJ020（USB200）→ USJ030（SORT・USB300）→ SeikyuImport → USJ040（USB400・USR500・USR510）</p>',
             'I01 夜間バッチ（JCL 相当）を実行', 1)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'pipeline.py'), RUN], capture_output=True, text=True)
        log = r.stdout + r.stderr
        open(RUN + '.log', 'w').write(log)
        ur = rlib.read_uriage(os.path.join(RUN, 'USAGI.PROD.URIAGE'))
        mine = [u for u in ur if u['juno'] in (fno, no)]
        show('売上ファイル USAGI.PROD.URIAGE（USB100 の出力）', pre(log, 10) + '<h3>今回登録した受注の売上レコード</h3>' +
             table(mine, hl=lambda u: u['juno'] == fno), f'I01 USB100 が無償サンプル {fno} を数量×単価で計算し直し、売上金額が付いた', 6)
        seikyu('100001', '202412', '202501', 'I01 夜間バッチ後：無償サンプルの分が請求に加わった', 5)
        stop('I01_無償サンプルが請求される', '無償サンプル（金額0）を登録→夜間バッチ→売上・請求に金額が付く')

        jobs = json.load(open(os.path.join(RUN, 'joblog.json')))
        jl = lambda *ks: '\n'.join(f"{j['job']:7} {j['step']:28} RC={j['rc']}  {j['out']}" for j in jobs if any(k in j['job'] + j['step'] for k in ks))
        jcl = lambda n: open(os.path.join(REPO, 'batch/jcl', n + '.jcl'), encoding='utf-8', errors='replace').read()

        # EV05
        start()
        show('EV05 売上計上：USJ010', '<h3>JCL（batch/jcl/USJ010.jcl）</h3>' + pre(jcl('USJ010'), 9), 'EV05 USJ010 の JCL：FTP 受信→SORT→USB100', 4)
        show('EV05 売上計上：実行結果', pre(jl('JuchuExtract', 'USJ010')) + '<h3>USAGI.PROD.URIAGE（先頭10件を COMP-3 を戻して表示）</h3>' + table(ur[:10]),
             'EV05 JuchuExtract→SORT→USB100 の実行ログと売上ファイル', 6)
        stop('EV05_売上計上', '売上計上（USJ010）の JCL・実行ログ・売上ファイル')

        # EV06
        sk = rlib.read_seikyu(os.path.join(RUN, 'USAGI.PROD.SEIKYU'))
        start()
        show('EV06 月次請求締め：USJ020', '<h3>JCL（batch/jcl/USJ020.jcl）</h3>' + pre(jcl('USJ020'), 9), 'EV06 USJ020 の JCL：USB200（SYSIN で締め日を渡す）', 4)
        show('EV06 月次請求締め：実行結果', pre(jl('USJ020')) + '<h3>USAGI.PROD.SEIKYU（202412 の先頭10件）</h3>' +
             table([s for s in sk if s['ym'] == '202412'][:10], ['no', 'tk', 'ym', 'frm', 'to', 'kensu', 'uriage', 'zei', 'seikyu']),
             'EV06 USB200 の実行ログと請求ファイル（請求期間 FROM〜TO）', 6)
        stop('EV06_月次請求締め', '月次請求締め（USJ020）の JCL・実行ログ・請求ファイル')

        # EV07
        ks = rlib.read_kesikomi(os.path.join(RUN, 'USAGI.PROD.KESIKOMI'))
        start()
        show('EV07 入金消込：USJ030', '<h3>JCL（batch/jcl/USJ030.jcl）</h3>' + pre(jcl('USJ030'), 9), 'EV07 USJ030 の JCL：SORT→USB300→FTP 送信', 4)
        show('EV07 入金消込：実行結果', pre(jl('USJ030', 'SeikyuImport')) + '<h3>USAGI.PROD.KESIKOMI（先頭10件：入金→充当した請求）</h3>' + table(ks[:10]),
             'EV07 USB300 の消込結果と SeikyuImport（請求結果を DB へ）', 6)
        stop('EV07_入金消込・請求結果連携', '入金消込（USJ030）と SeikyuImport の実行ログ・消込ファイル')

        # EV08
        start()
        seikyu('100001', '202410', '202501', 'EV08 請求照会：得意先と請求年月の範囲で検索（夜間バッチの結果）', 4); scroll(2, 1)
        go('seikyuInquiry.do?search=1', 'EV08 請求照会：条件なしで検索するとエラー')
        stop('EV08_請求照会', '請求照会（検索・入力エラー）')

        # EV09
        rep = open(os.path.join(RUN, 'SEIKYUSH.txt'), encoding='utf-8', errors='replace').read().replace('\f', '\n')
        uri = open(os.path.join(RUN, 'URIGETU.txt'), encoding='utf-8', errors='replace').read().replace('\f', '\n')
        start()
        show('EV09 月次集計・帳票：USJ040', pre(jl('USJ040')) + '<h3>JCL（batch/jcl/USJ040.jcl）</h3>' + pre(jcl('USJ040'), 9), 'EV09 USJ040：USB400→USR500（請求書）→USR510（月次売上表）', 4)
        show('EV09 請求書（USR500 の出力）', pre(rep, 11), 'EV09 請求書（202412）', 3); scroll(3, 1.2)
        show('EV09 月次売上表（USR510 の出力）', pre(uri, 11), 'EV09 月次売上表（202412）', 4)
        stop('EV09_月次集計・帳票出力', '月次集計・帳票（USJ040）の実行ログ・請求書・月次売上表')

        # I10
        start()
        juchu('20241399', '100001', '200001', '1', t='I10 受注日 20241399（13月99日）を入力しても確認画面へ進む')
        ino = regist('I10 そのまま登録できる'); created.append(ino)
        inquiry(ino, f'I10 受注照会：受注日 20241399 の受注 {ino} が登録されている')
        stop('I10_存在しない受注日を受け付ける', '受注日 20241399 を入力→登録→受注照会')

        # I13
        start()
        juchu('20241218', '100001', '200001', '10', t='I13 通常の受注を確認画面まで進める')
        old = pg.evaluate("()=>[document.querySelector('input[name=tanka]').value,document.querySelector('input[name=uriageKin]').value]")
        pg.evaluate("()=>{document.querySelector('input[name=tanka]').value='1';document.querySelector('input[name=uriageKin]').value='10'}")
        cap(f'I13 開発者ツールで hidden を書き換え：tanka {old[0]}→1、uriageKin {old[1]}→10'); w(3.5)
        tno = regist('I13 書き換えた値のまま登録'); created.append(tno)
        inquiry(tno, f'I13 受注照会：受注 {tno} は単価1・金額10 で登録された')
        stop('I13_hidden書き換えでその金額で登録', '確認画面の hidden（tanka・uriageKin）を書き換え→登録→受注照会')

        # I11
        start()
        go('tokuiEdit.do', 'I11 得意先メンテナンス'); typ('input[name=tkCd]', '100002'); click('input[type=submit][value=表示]', 'I11 得意先メンテナンス', 1.5)
        typ('input[name=simeKbn]', '31'); typ('input[name=hasuKbn]', '7')
        cap('I11 締日区分 31・端数区分 7（どちらも仕様外）を入力'); w(2)
        click('input[type=submit][value=更新]', 'I11 更新：入力チェックなしで更新される', 2)
        go('tokuiEdit.do'); typ('input[name=tkCd]', '100002'); click('input[type=submit][value=表示]', 'I11 もう一度表示：31・7 が保存されている', 3)
        stop('I11_得意先メンテで範囲外の値を登録できる', '締日31・端数7を入力→更新→再表示')
        br.close()

    # 後片付け：登録した受注を消し、得意先を戻し、バッチを流し直して t_seikyu を元に戻す
    sime, hasu = orig_tokui.split('|')
    sql(f"update m_tokui set sime_kbn='{sime}', hasu_kbn='{hasu}' where tk_cd='100002'")
    sql('delete from t_juchu where juchu_no in (' + ','.join(f"'{c}'" for c in created) + ')')
    subprocess.run([sys.executable, os.path.join(HERE, 'pipeline.py'), '/tmp/run_restore'], check=True, capture_output=True)
    json.dump(made, open(os.path.join(OUT, 'clips.json'), 'w'), ensure_ascii=False, indent=1)
    print('created', created, 'restored tokui 100002', orig_tokui, 'seikyu', sql('select count(*) from t_seikyu'))


if __name__ == '__main__':
    main()
