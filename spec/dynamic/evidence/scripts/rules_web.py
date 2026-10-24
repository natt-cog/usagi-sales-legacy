#!/usr/bin/env python3
"""Web 画面（Struts）と Java バッチ（JuchuExtract／SeikyuImport）の業務ルールを実行して確かめる。
前提: web/ で docker compose up 済み、DB は初期データ＋夜間バッチ1回実行済み（t_seikyu 取込済み）。
一時データ（Z0000x）は最後に消す。Java バッチは複製 DB usagi_t で動かす。"""
import os, re, subprocess, datetime, json
import requests
from bs4 import BeautifulSoup
from rlib import *

B = 'http://localhost:8080/usagi/'
WEB = os.path.join(REPO, 'web')
CP = '/usr/local/tomcat/webapps/usagi/WEB-INF/classes:/usr/local/tomcat/webapps/usagi/WEB-INF/lib/*'
TODAY = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y%m%d')  # コンテナは TZ=Asia/Tokyo
J = os.path.join


def psql(sql, db='usagi'):
    r = subprocess.run(['docker', 'compose', 'exec', '-T', 'db', 'psql', '-U', 'usagi', '-d', db, '-At', '-F', '|', '-c', sql],
                       cwd=WEB, capture_output=True, text=True)
    return r.stdout.strip()


def dexec(*cmd, inp=None):
    r = subprocess.run(['docker', 'compose', 'exec', '-T', 'web', *cmd], cwd=WEB, capture_output=True, input=inp)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')


def java(cls, *args, db='usagi_t'):
    return dexec('java', f'-Dusagi.db.url=jdbc:postgresql://db:5432/{db}', '-cp', CP, cls, *args)


def sess(u='user01', p='usagi01'):
    s = requests.Session()
    s.post(B + 'login.do', data={'userId': u, 'password': p})
    return s


def txt(r):
    return re.sub(r'\s+', ' ', BeautifulSoup(r.text, 'html.parser').get_text(' ')).strip()


def msg(r):
    m = BeautifulSoup(r.text, 'html.parser').select_one('p.msg')
    return m.get_text().strip() if m else ''


def hidden(r):
    return {i.get('name'): i.get('value') for i in BeautifulSoup(r.text, 'html.parser').select('input[type=hidden]')}


def rows(r):
    t = BeautifulSoup(r.text, 'html.parser').select('table')
    return [[td.get_text().strip() for td in tr.select('td')] for tr in (t[-1].select('tr') if t else []) if tr.select('td')]


LOG = []


def keep(cid, r_or_s, extra=''):
    d = J(RULES, cid)
    os.makedirs(d, exist_ok=True)
    if hasattr(r_or_s, 'text'):
        body = f'{r_or_s.request.method} {r_or_s.request.url}\n'
        if r_or_s.request.body:
            b = r_or_s.request.body
            body += 'BODY: ' + requests.utils.unquote(b if isinstance(b, str) else b.decode()) + '\n'
        body += f'HTTP {r_or_s.status_code}\n画面テキスト: {txt(r_or_s)[:1500]}\n'
    else:
        body = str(r_or_s)
    with open(J(d, 'http.txt'), 'a') as f:
        f.write(body + (extra and extra + '\n') + '-' * 60 + '\n')
    return d


def main():
    for c in os.listdir(RULES):
        if c.startswith('WEB-') or c.startswith('JX-') or c.startswith('SI-'):
            import shutil; shutil.rmtree(J(RULES, c))

    # 一時データ
    psql("DELETE FROM m_tokui WHERE tk_cd LIKE 'Z%'; DELETE FROM m_shohin WHERE sh_cd LIKE 'Z%'")
    psql("INSERT INTO m_tokui VALUES ('Z00001','検証用得意先','ケンショウ','000-0000','','000','05','3','0','05',100,'S999','0','20241201','20241201'),"
         "('Z00002','検証用停止得意先','ケンショウ','000-0000','','000','99','2','2','31',100,'S999','1','20241201','20241201')")
    psql("INSERT INTO m_shohin VALUES ('Z00001','検証用商品333円','99','0',333,'個',0,'20241201')")
    try:
        # ---- LoginAction ----
        P = 'LoginAction'
        s = requests.Session(); r = s.post(B + 'login.do', data={'userId': 'user01', 'password': 'usagi01'}, allow_redirects=False)
        d = keep('WEB-LOGIN', r, 'Location: ' + r.headers.get('Location', ''))
        r2 = requests.post(B + 'login.do', data={'userId': 'user01', 'password': 'usagi01 '}); keep('WEB-LOGIN', r2)
        rec(16, P, 'WEB-LOGIN-1', 'user01／usagi01（正）、user01／"usagi01 "（末尾空白）', '正しい組合せだけ /menu.do へ', f"HTTP {r.status_code} Location={r.headers.get('Location')} ／ 末尾空白: {msg(r2)}",
            r.status_code == 302 and 'menu.do' in r.headers.get('Location', '') and msg(r2) != '', d)
        r = requests.post(B + 'login.do', data={'userId': 'user01', 'password': 'USAGI01'}); keep('WEB-LOGIN', r)
        r3 = requests.post(B + 'login.do', data={'userId': 'user01', 'password': ''}); keep('WEB-LOGIN', r3)
        rec(17, P, 'WEB-LOGIN-2', 'user01／USAGI01（大文字）、user01／空', '「ユーザIDまたはパスワードが違います」を表示してログイン画面', f'{msg(r)} ／ {msg(r3)}',
            msg(r) == 'ユーザIDまたはパスワードが違います' and msg(r3) == msg(r), d)
        r = requests.get(B + 'login.do'); keep('WEB-LOGIN', r)
        rec(18, P, 'WEB-LOGIN-3', 'GET login.do（userId なし）', 'ログイン画面を表示（メッセージなし）', f'HTTP {r.status_code} パスワード欄={"password" in r.text} メッセージ="{msg(r)}"',
            r.status_code == 200 and 'name="password"' in r.text and msg(r) == '', d)
        # ---- LogoutAction / MenuAction ----
        s = sess(); r0 = s.get(B + 'menu.do'); r = s.get(B + 'logout.do'); r2 = s.get(B + 'menu.do')
        d = keep('WEB-LOGOUT', r0); keep('WEB-LOGOUT', r); keep('WEB-LOGOUT', r2)
        rec(24, 'LogoutAction', 'WEB-LOGOUT-1', 'ログイン→logout.do→menu.do', 'セッション破棄。以後 menu.do はログイン画面', f'logout 後 menu.do: {"ログイン画面" if "name=\"password\"" in r2.text else "メニュー"}',
            'name="password"' in r2.text and 'name="password"' not in r0.text, d)
        r = requests.get(B + 'menu.do'); r2 = requests.get(B + 'juchuInquiry.do'); d = keep('WEB-MENU', r); keep('WEB-MENU', r2)
        rec(30, 'MenuAction', 'WEB-MENU-1', '未ログインで menu.do／juchuInquiry.do', 'login.jsp を表示', f'menu.do: {"ログイン画面" if "name=\"password\"" in r.text else "その他"} ／ juchuInquiry.do: {"ログイン画面" if "name=\"password\"" in r2.text else "その他"}',
            'name="password"' in r.text and 'name="password"' in r2.text, d)
        # ---- TokuiSearchAction ----
        P = 'TokuiSearchAction'
        s = sess(); r = s.get(B + 'tokuiSearch.do', params={'tkCd': '', 'tkNm': '', 'search': '1'}); d = keep('WEB-TOKUI', r)
        R = {x[0]: x for x in rows(r)}
        db = {l.split('|')[0]: l.split('|') for l in psql('SELECT tk_cd,sime_kbn,hasu_kbn,kaisyu_m,kaisyu_d,del_flg FROM m_tokui').splitlines()}
        open(J(d, 'db_m_tokui.txt'), 'w').write(json.dumps(db, ensure_ascii=False, indent=0))
        sm = lambda k: '末日' if k == '99' else f'{int(k)}日'
        ok_s = all(R[c][3] == sm(v[1]) for c, v in db.items())
        rec(62, P, 'WEB-TOKUI-1', f'全得意先 {len(db)} 件（sime_kbn=99 を含む）', 'sime_kbn=99 は「末日」', f"100001(99): {R['100001'][3]} ／ 全件照合 {ok_s}", R['100001'][3] == '末日' and ok_s, d)
        rec(63, P, 'WEB-TOKUI-2', 'sime_kbn=15／20／05（Z00001）', '数値＋「日」（05→5日）', f"100002(15): {R['100002'][3]} ／ Z00001(05): {R['Z00001'][3]}", R['Z00001'][3] == '5日' and ok_s, d)
        hm = {'1': '切捨て', '2': '四捨五入', '3': '切上げ'}
        rec(64, P, 'WEB-TOKUI-3', 'hasu_kbn=1／2／3', '切捨て／四捨五入／切上げ', ' ／ '.join(f'{c}({v[2]}): {R[c][4]}' for c, v in list(db.items())[:3]) + f" ／ Z00001(3): {R['Z00001'][4]}",
            all(R[c][4] == hm[v[2]] for c, v in db.items()), d)
        km = lambda m, dd: ('翌月' if m == '1' else '翌々月' if m == '2' else '当月') + ('末日' if dd == '31' else f'{int(dd)}日')
        rec(65, P, 'WEB-TOKUI-4', 'kaisyu_m=1／2／0（Z00001）', '翌月／翌々月／当月', f"Z00001(0,05): {R['Z00001'][5]} ／ Z00002(2,31): {R['Z00002'][5]}", all(R[c][5] == km(v[3], v[4]) for c, v in db.items()), d)
        rec(66, P, 'WEB-TOKUI-5', 'kaisyu_d=31／10／05', '31 は「末日」、他は N日', f"100001(31): {R['100001'][5]} ／ 100002(10): {R['100002'][5]} ／ Z00001(05): {R['Z00001'][5]}", all(R[c][5] == km(v[3], v[4]) for c, v in db.items()), d)
        rec(67, P, 'WEB-TOKUI-6', 'del_flg=1（Z00002 と既存1件）／0', '「取引停止」／空白', f"Z00002: {R['Z00002'][8]} ／ 100001: '{R['100001'][8]}'", all(R[c][8] == ('取引停止' if v[5] == '1' else '') for c, v in db.items()), d)
        # ---- TokuiEditAction ----
        P = 'TokuiEditAction'
        r = s.get(B + 'tokuiEdit.do', params={'tkCd': 'Z00001', 'mode': 'update', 'tkNm': '検証用得意先（更新）', 'tel': '111', 'simeKbn': '31', 'hasuKbn': '7', 'gendo': '200', 'tanto': 'S998'})
        d = keep('WEB-TOKUIEDIT', r)
        dbv = psql("SELECT tk_nm,tel,sime_kbn,hasu_kbn,gendo,a4,upd_ymd FROM m_tokui WHERE tk_cd='Z00001'")
        rec(112, P, 'WEB-TOKUIEDIT-1', 'Z00001 を mode=update（締日31・端数7 を含む）', '「更新しました」→ UPDATE 後の値を再表示', f'{msg(r)} ／ DB: {dbv}',
            msg(r) == '更新しました' and dbv.startswith('検証用得意先（更新）|111|31|7|200|S998|' + TODAY), d, note='締日31・端数7 のような範囲外の値も入力チェックなしで更新される')
        r = s.get(B + 'tokuiEdit.do', params={'tkCd': '999999'}); keep('WEB-TOKUIEDIT', r)
        vals = [i.get('value') for i in BeautifulSoup(r.text, 'html.parser').select('input[type=text]')]
        rec(113, P, 'WEB-TOKUIEDIT-2', 'tkCd=999999（存在しない）', 'tokui 属性なし（空表示）', f'HTTP {r.status_code} 入力欄の値={vals}', r.status_code == 200, d)
        r = s.get(B + 'tokuiEdit.do', params={'tkCd': 'Z00001', 'mode': 'update', 'tkNm': 'x', 'tel': '1', 'simeKbn': '99', 'hasuKbn': '1', 'gendo': 'abc', 'tanto': 'S'}); keep('WEB-TOKUIEDIT', r)
        rec(114, P, 'WEB-TOKUIEDIT-3', 'gendo=abc', 'NumberFormatException（Tomcat の既定エラー画面）', f"HTTP {r.status_code} {'NumberFormatException' if 'NumberFormatException' in r.text else ''}",
            r.status_code == 500 and 'NumberFormatException' in r.text, d)
        # ---- JuchuInputAction ----
        P = 'JuchuInputAction'
        r = s.get(B + 'juchuInput.do'); d = keep('WEB-JUCHUIN', r)
        sp = BeautifulSoup(r.text, 'html.parser')
        ymd = sp.select_one('input[name=juchuYmd]').get('value')
        kbn = sp.select_one('select[name=juchuKbn] option[selected]')
        opts = [o.get_text() for o in sp.select('select[name=juchuKbn] option')]
        rec(132, P, 'WEB-JUCHUIN-1', 'juchuInput.do（受注日なし）', f'受注日の初期値＝当日 {TODAY}', f'受注日={ymd}', ymd == TODAY, d)
        rec(133, P, 'WEB-JUCHUIN-2', '同上（受注区分なし）', '受注区分 1 を選択', f"選択={kbn.get('value') if kbn else None}", kbn is not None and kbn.get('value') == '1', d)
        rec(134, P, 'WEB-JUCHUIN-3', '同上', '1:通常 2:返品 3:無償サンプル', ' / '.join(opts), opts == ['1:通常', '2:返品', '3:無償サンプル'], d)
        # ---- JuchuConfirmAction ----
        P = 'JuchuConfirmAction'
        base = {'juchuYmd': '20241201', 'tkCd': 'Z00001', 'shCd': 'Z00001', 'suryo': '1', 'juchuKbn': '1', 'biko': ''}
        def conf(cid, **kw):
            r = s.post(B + 'juchuConfirm.do', data=dict(base, **kw)); keep(cid, r); return r
        out = {v: msg(conf('WEB-CONF-YMD', juchuYmd=v)) or '確認画面へ' for v in ['2024120', '202412011', '2024/1/1', '20241399', '20241201']}
        rec(172, P, 'WEB-CONF-1', '受注日 2024120／202412011／2024/1/1／20241399／20241201', '8桁数字以外は「受注日はYYYYMMDDで入力してください」', ' ／ '.join(f'{k}: {v}' for k, v in out.items()),
            all(out[k] == '受注日はYYYYMMDDで入力してください' for k in ['2024120', '202412011', '2024/1/1']) and out['20241201'] == '確認画面へ', J(RULES, 'WEB-CONF-YMD'),
            note=f"20241399（存在しない日付）: {out['20241399']}")
        out = {v: msg(conf('WEB-CONF-SURYO', suryo=v)) or '確認画面へ' for v in ['0', '-1', 'abc', '1.5', '', '1']}
        rec(173, P, 'WEB-CONF-2', '数量 0／-1／abc／1.5／空／1', '1 以外は「数量を正しく入力してください」', ' ／ '.join(f'{k or "空"}: {v}' for k, v in out.items()),
            all(out[k] == '数量を正しく入力してください' for k in ['0', '-1', 'abc', '1.5', '']) and out['1'] == '確認画面へ', J(RULES, 'WEB-CONF-SURYO'))
        m1 = msg(conf('WEB-CONF-MST', tkCd='999999')); m2 = msg(conf('WEB-CONF-MST', tkCd='Z00002')); m3 = msg(conf('WEB-CONF-MST', shCd='999999'))
        d = J(RULES, 'WEB-CONF-MST')
        rec(174, P, 'WEB-CONF-3', '得意先 999999', '「得意先コードが登録されていません」', m1, m1 == '得意先コードが登録されていません', d)
        rec(175, P, 'WEB-CONF-4', '得意先 Z00002（del_flg=1）', '「取引停止中の得意先です」', m2, m2 == '取引停止中の得意先です', d)
        rec(176, P, 'WEB-CONF-5', '商品 999999（選択肢にない値を送信）', '「商品コードが登録されていません」', m3, m3 == '商品コードが登録されていません', d)
        H = {q: hidden(conf('WEB-CONF-NEBIKI', suryo=str(q))) for q in [49, 50, 99, 100]}
        fh = lambda q: f"数量{q}: 割引率{H[q].get('nebikiRitu')} 単価{H[q].get('tanka')} 金額{H[q].get('uriageKin')}"
        d = J(RULES, 'WEB-CONF-NEBIKI')
        rec(177, P, 'WEB-CONF-6', '標準単価333、数量 100', '割引率5% → 単価 316（316.35 切捨て）', fh(100), H[100].get('nebikiRitu') in ('5', '5.0') and H[100].get('tanka') == '316', d)
        rec(178, P, 'WEB-CONF-7', '標準単価333、数量 50／99', '割引率3% → 単価 323（323.01 切捨て）', fh(50) + ' ／ ' + fh(99), H[50].get('nebikiRitu') in ('3', '3.0') and H[99].get('nebikiRitu') in ('3', '3.0'), d)
        rec(179, P, 'WEB-CONF-8', '標準単価333、数量 49', '割引率0% → 単価 333', fh(49), H[49].get('nebikiRitu') in ('0', '0.0') and H[49].get('tanka') == '333', d)
        rec(180, P, 'WEB-CONF-9', '標準単価333、数量 50／100', '割引後単価は整数に切捨て（323.01→323、316.35→316）', fh(50) + ' ／ ' + fh(100), H[50].get('tanka') == '323' and H[100].get('tanka') == '316', d)
        h2 = hidden(conf('WEB-CONF-KBN', suryo='10', juchuKbn='2')); h3 = hidden(conf('WEB-CONF-KBN', suryo='10', juchuKbn='3')); d = J(RULES, 'WEB-CONF-KBN')
        rec(181, P, 'WEB-CONF-10', '区分2（返品）数量10 単価333', '金額 −3330', f"金額{h2.get('uriageKin')}", h2.get('uriageKin') == '-3330', d)
        rec(182, P, 'WEB-CONF-11', '区分3（無償サンプル）数量10', '金額 0', f"金額{h3.get('uriageKin')} 単価{h3.get('tanka')}", h3.get('uriageKin') == '0', d)
        r = conf('WEB-CONF-GENDO', suryo='9999999'); h = hidden(r)
        rec(183, P, 'WEB-CONF-12', 'Z00001（与信限度額100）に 数量9999999', 'チェックなしで確認画面へ', f"{msg(r) or '確認画面へ'} 金額{h.get('uriageKin')}", msg(r) == '' and 'uriageKin' in h, J(RULES, 'WEB-CONF-GENDO'))
        # ---- JuchuRegistAction ----
        P = 'JuchuRegistAction'
        def regist(cid, **kw):
            h = hidden(conf(cid, **{k: v for k, v in kw.items() if k in base}))
            h.update({k: v for k, v in kw.items() if k in ('tanka', 'uriageKin', 'nebikiRitu')})
            r = s.post(B + 'juchuRegist.do', data=h); keep(cid, r)
            m = re.search(r'受注番号 (\d+) で登録', txt(r))
            return r, m.group(1) if m else None
        psql("DROP TABLE IF EXISTS t_juchu_bk; CREATE TABLE t_juchu_bk AS SELECT * FROM t_juchu; DELETE FROM t_juchu")
        try:
            r, no = regist('WEB-REG-EMPTY')
            rec(227, P, 'WEB-REG-1', 't_juchu を空にして登録', '受注番号 10000001', f'受注番号 {no}', no == '10000001', J(RULES, 'WEB-REG-EMPTY'))
        finally:
            psql("DELETE FROM t_juchu; INSERT INTO t_juchu SELECT * FROM t_juchu_bk; DROP TABLE t_juchu_bk")
        mx = psql('SELECT MAX(juchu_no) FROM t_juchu')
        r, no = regist('WEB-REG-MAX', biko='検証')
        rec(228, P, 'WEB-REG-2', f'登録前 MAX={mx}', f'MAX+1＝{int(mx) + 1}', f'受注番号 {no}', no == str(int(mx) + 1), J(RULES, 'WEB-REG-MAX'))
        row = psql(f"SELECT flg1, '['||wk_x1||']', ins_ymd, ins_user FROM t_juchu WHERE juchu_no='{no}'")
        keep('WEB-REG-MAX', 'DB: ' + row)
        rec(229, P, 'WEB-REG-3', f'受注 {no} の DB 行', f'flg1=0, wk_x1=空白, ins_ymd={TODAY}, ins_user=user01', row, row.split('|')[0] == '0' and row.split('|')[2:] == [TODAY, 'user01'], J(RULES, 'WEB-REG-MAX'),
            note='wk_x1 は CHAR(1) の空白（psql の連結表示では空）')
        c0 = psql('SELECT count(*) FROM t_juchu')
        h = hidden(conf('WEB-REG-ERR')); h['biko'] = 'あ' * 61
        r = s.post(B + 'juchuRegist.do', data=h); keep('WEB-REG-ERR', r)
        c1 = psql('SELECT count(*) FROM t_juchu')
        rec(230, P, 'WEB-REG-4', '備考 61 文字（VARCHAR(60) 超過）で登録', '例外 → ロールバック（件数が増えない）', f'HTTP {r.status_code} 件数 {c0}→{c1}', r.status_code == 500 and c0 == c1, J(RULES, 'WEB-REG-ERR'))
        r, no = regist('WEB-REG-HIDDEN', suryo='10', uriageKin='1', tanka='1')
        row = psql(f"SELECT suryo,tanka,uriage_kin FROM t_juchu WHERE juchu_no='{no}'"); keep('WEB-REG-HIDDEN', 'DB: ' + row)
        rec(231, P, 'WEB-REG-5', '確認画面の hidden を tanka=1・uriageKin=1 に書き換えて登録（数量10 単価333）', 'サーバ側で再計算せずそのまま登録', f'DB suryo|tanka|uriage_kin = {row}', row == '10|1|1', J(RULES, 'WEB-REG-HIDDEN'))
        # ---- JuchuInquiryAction ----
        P = 'JuchuInquiryAction'
        r = s.get(B + 'juchuInquiry.do', params={'search': '1'}); d = keep('WEB-JINQ', r)
        rec(256, P, 'WEB-JINQ-1', '得意先コード・番号とも空で検索', '「得意先コードか番号を入力してください」', msg(r), msg(r) == '得意先コードか番号を入力してください', d)
        dt = psql("SELECT juchu_ymd FROM t_juchu WHERE tk_cd='100002' ORDER BY juchu_ymd DESC LIMIT 1")
        nd = psql(f"SELECT count(*) FROM t_juchu WHERE tk_cd='100002' AND juchu_ymd='{dt}'")
        r = s.get(B + 'juchuInquiry.do', params={'tkCd': '100002', 'fromYmd': dt, 'toYmd': dt, 'search': '1'}); keep('WEB-JINQ', r)
        rec(257, P, 'WEB-JINQ-2', f'得意先 100002、fromYmd=toYmd={dt}', f'その日の受注 {nd} 件を表示（toYmd を含む）', f'{len(rows(r))} 件', str(len(rows(r))) == nd, d)
        psql("INSERT INTO t_juchu SELECT lpad((90000000+g)::text,8,'0'),'20241201','Z00001','Z00001',1,333,'1',333,0,'LIMIT検証','1',' ','20241201','test' FROM generate_series(1,105) g")
        r = s.get(B + 'juchuInquiry.do', params={'tkCd': 'Z00001', 'search': '1'}); keep('WEB-JINQ', r)
        nos = [x[0] for x in rows(r)]
        rec(258, P, 'WEB-JINQ-3', 'Z00001 の受注 105 件＋α', '受注番号降順で 100 件', f'{len(nos)} 件、先頭 {nos[0]}、末尾 {nos[-1]}', len(nos) == 100 and nos == sorted(nos, reverse=True), d)
        psql("DELETE FROM t_juchu WHERE tk_cd='Z00001'")
        # ---- SeikyuInquiryAction ----
        P = 'SeikyuInquiryAction'
        r = s.get(B + 'seikyuInquiry.do', params={'search': '1'}); d = keep('WEB-SINQ', r)
        rec(287, P, 'WEB-SINQ-1', '得意先コード・番号とも空', '「得意先コードか番号を入力してください」', msg(r), msg(r) == '得意先コードか番号を入力してください', d)
        tk = psql("SELECT tk_cd FROM t_seikyu WHERE seikyu_ym='202412' ORDER BY tk_cd LIMIT 1")
        a = s.get(B + 'seikyuInquiry.do', params={'tkCd': tk, 'fromYm': '202412', 'toYm': '202412', 'search': '1'}); keep('WEB-SINQ', a)
        b = s.get(B + 'seikyuInquiry.do', params={'tkCd': tk, 'fromYm': '202412', 'toYm': '202501', 'search': '1'}); keep('WEB-SINQ', b)
        rec(288, P, 'WEB-SINQ-2', f'得意先 {tk}、202412〜202412／202412〜202501', 'toYm は含まない（0 件／1 件）', f'{len(rows(a))} 件 ／ {len(rows(b))} 件', len(rows(a)) == 0 and len(rows(b)) == 1, d,
            note='画面で「2024/12〜2024/12」と入れると 2024/12 が出ない')
        big = psql("SELECT tk_cd FROM t_seikyu GROUP BY 1 HAVING count(*)>100 LIMIT 1")
        if not big:
            psql("INSERT INTO t_seikyu SELECT lpad(g::text,6,'0')||'Z00001','Z00001',lpad((190000+g)::text,6,'0'),'','',1,100,10,110,50,'1',0,0,0,0,0,0,'20241201' FROM generate_series(1,105) g")
            big = 'Z00001'
        r = s.get(B + 'seikyuInquiry.do', params={'tkCd': big, 'search': '1'}); keep('WEB-SINQ', r)
        n = psql(f"SELECT count(*) FROM t_seikyu WHERE tk_cd='{big}'")
        rec(289, P, 'WEB-SINQ-3', f'得意先 {big}（請求 {n} 件）', '100 件まで', f'{len(rows(r))} 件', len(rows(r)) == 100, d)
        exp = psql(f"SELECT sum(seikyu_kin-nyukin_kin) FROM (SELECT * FROM t_seikyu WHERE tk_cd='{big}' ORDER BY seikyu_ym DESC, seikyu_no LIMIT 100) x")
        tot = re.search(r'未入金合計 ([\d,\-]+) 円', txt(r)).group(1)
        rec(290, P, 'WEB-SINQ-4', f'同上', f'未入金合計＝表示行の (請求−入金) の合計 {int(exp):,}', f'画面: {tot} 円', tot.replace(',', '') == exp, d,
            note='合計は表示した100件分だけ（101件目以降は含まない）')
        psql("DELETE FROM t_seikyu WHERE tk_cd='Z00001'")
    finally:
        psql("DELETE FROM t_juchu WHERE tk_cd LIKE 'Z%'; DELETE FROM m_tokui WHERE tk_cd LIKE 'Z%'; DELETE FROM m_shohin WHERE sh_cd LIKE 'Z%'")

    # ---- JuchuExtract / SeikyuImport（複製 DB usagi_t で実行）----
    psql('DROP DATABASE IF EXISTS usagi_t', 'postgres'); psql('CREATE DATABASE usagi_t', 'postgres')
    subprocess.run('docker compose exec -T db pg_dump -U usagi usagi | docker compose exec -T db psql -q -U usagi -d usagi_t', shell=True, cwd=WEB, capture_output=True)
    dexec('sh', '-c', 'rm -rf /work/t && mkdir -p /work/t')
    P = 'JuchuExtract'
    d = case_dir('JX')
    psql("UPDATE t_juchu SET flg1 = CASE WHEN juchu_no < '10000300' THEN '1' ELSE '0' END", 'usagi_t')
    psql("UPDATE m_tokui SET tk_nm='あいうえおかきくけこさしすせ' WHERE tk_cd='100001'; UPDATE m_tokui SET tk_nm='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnX' WHERE tk_cd='100002'", 'usagi_t')
    psql("INSERT INTO t_juchu VALUES ('99999999','20241201','100001','200025',1,480,'2',-12345,0,'','0',' ','20241201','test')", 'usagi_t')
    before = psql("SELECT count(*), sum((flg1='0')::int) FROM t_juchu", 'usagi_t')
    rc, out = java('jp.co.usagi.batch.JuchuExtract', '/work/t')
    after = psql("SELECT count(*), sum((flg1='0')::int) FROM t_juchu", 'usagi_t')
    for f in ('TOKUI', 'SHOHIN', 'JUCHU'):
        _, c = dexec('sh', '-c', f'cat /work/t/{f}.DAT | base64 -w0')
        import base64; open(J(d, f + '.DAT'), 'wb').write(base64.b64decode(c))
    open(J(d, 'run.log'), 'w').write(f'事前 件数|flg1=0 件数: {before}\nRC={rc}\n{out}\n事後: {after}\n')
    JU = open(J(d, 'JUCHU.DAT'), 'rb').read().split(b'\n'); TK = open(J(d, 'TOKUI.DAT'), 'rb').read().split(b'\n')
    rec(374, P, 'JX-1', f'受注 {before.split("|")[0]} 件（うち flg1=1 を約300件にした）', '全件を JUCHU.DAT に出力', f'{out.strip()} ／ JUCHU.DAT {len([l for l in JU if l])} 行', len([l for l in JU if l]) == int(before.split('|')[0]), d)
    rec(375, P, 'JX-2', f'flg1=0 の受注 {before.split("|")[1]} 件', 'すべて 1 に更新', f'事後の flg1=0 件数: {after.split("|")[1]}', after.split('|')[1] == '0', d)
    t1 = [l for l in TK if l.startswith(b'100001')][0]; t2 = [l for l in TK if l.startswith(b'100002')][0]
    rec(376, P, 'JX-3', '得意先名 14文字の漢字かな（42バイト）／英字41文字', '13文字（39バイト）＋空白1、英字は40文字で切る', f"{t1[6:46].decode()!r} ／ {t2[6:46].decode()!r}",
        t1[6:46] == 'あいうえおかきくけこさしす'.encode() + b' ' and t2[6:46] == b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn', d)
    j9 = [l for l in JU if l.startswith(b'99999999')][0]
    rec(377, P, 'JX-4', '受注 99999999 uriage_kin=−12345', '"-"＋00000012345', j9[43:55].decode(), j9[43:55] == b'-00000012345', d)
    raw = open(J(d, 'TOKUI.DAT'), 'rb').read()
    rec(378, P, 'JX-5', '出力ファイル', '各レコードの後に LF（TOKUI 101・SHOHIN/JUCHU 81 バイト周期）', f"TOKUI {len(raw)} バイト／{raw.count(b'\n')} 行、CR なし={b'\r' not in raw}", len(raw) == 101 * raw.count(b'\n') and b'\r' not in raw, d)
    psql("UPDATE t_juchu SET flg1='0' WHERE juchu_no='99999999'", 'usagi_t')
    rc, out = java('jp.co.usagi.batch.JuchuExtract', '/nonexistent')
    aft = psql("SELECT flg1 FROM t_juchu WHERE juchu_no='99999999'", 'usagi_t')
    open(J(d, 'run_error.log'), 'w').write(f'RC={rc}\n{out}\nflg1(99999999)={aft}\n')
    rec(379, P, 'JX-6', '出力先 /nonexistent', '例外を main から送出（終了コード≠0）', f"RC={rc} {out.strip().splitlines()[0][:120]} ／ flg1 は {aft} のまま", rc != 0 and 'Exception' in out, d)
    P = 'SeikyuImport'
    d = case_dir('SI')
    sk = open(J(EVD, 'batch/run_202412/USAGI.PROD.SKKEKKA'), 'rb').read().split(b'\n')
    sk = [l for l in sk if l]
    def imp(name, lines):
        data = b''.join(l + b'\n' for l in lines)
        open(J(d, name), 'wb').write(data)
        dexec('sh', '-c', f'cat > /work/t/{name}', inp=data)
        return java('jp.co.usagi.batch.SeikyuImport', f'/work/t/{name}', '20241231')
    psql("INSERT INTO t_seikyu (seikyu_no,tk_cd) VALUES ('DUMMY0000001','Z00001')", 'usagi_t')
    lines = sk[:10]
    neg = bytearray(lines[0]); neg[81:93] = b'-00000000500'; lines[0] = bytes(neg)
    lines[1] = lines[1][:166] + 'あ'.encode() + b' '
    rc, out = imp('SK_ok.DAT', [lines[0], b'', b'   ', *lines[1:]])
    res = psql("SELECT count(*), sum((seikyu_no='DUMMY0000001')::int) FROM t_seikyu", 'usagi_t')
    v0 = psql(f"SELECT nyukin_kin FROM t_seikyu WHERE seikyu_no='{lines[0][:12].decode()}'", 'usagi_t')
    v1 = psql(f"SELECT seikyu_no||'|'||zeisonota_kin FROM t_seikyu WHERE seikyu_no='{lines[1][:12].decode()}'", 'usagi_t')
    open(J(d, 'run.log'), 'w').write(f'SK_ok.DAT RC={rc}\n{out}\n件数|DUMMY残={res}\n1行目 nyukin_kin={v0}\n2行目={v1}\n')
    rec(422, P, 'SI-1', '取込前に t_seikyu へダミー1件、10行のファイルを取込', 'ダミーは消え、10件だけになる', f'{out.strip()} ／ 件数|ダミー残 = {res}', res == '10|0', d)
    rec(423, P, 'SI-2', '空行と空白だけの行を2行はさむ', '読み飛ばす', f'{out.strip()}', res.startswith('10|'), d)
    rec(424, P, 'SI-3', '1行目の入金額を "-00000000500"', 'nyukin_kin = −500', f'nyukin_kin={v0}', v0 == '-500', d)
    rec(425, P, 'SI-4', '2行目の末尾 FILLER に UTF-8 の「あ」（3バイト）', '1文字ずつ＝1バイトずつ切り出すので位置がずれない', f'{v1}', rc == 0 and v1.startswith(lines[1][:12].decode()), d)
    bad = bytearray(sk[20]); bad[45:57] = b'+0000000ABCD'
    rc2, out2 = imp('SK_bad.DAT', [*sk[10:20], bytes(bad)])
    res2 = psql("SELECT count(*) FROM t_seikyu", 'usagi_t')
    open(J(d, 'run_error.log'), 'w').write(f'SK_bad.DAT RC={rc2}\n{out2}\n取込後件数={res2}\n')
    rec(426, P, 'SI-5', '11行目の売上金額を "+0000000ABCD"（数値でない）', '例外で終了し、DELETE も含めて取り消される（前回の10件が残る）', f'RC={rc2} {out2.strip().splitlines()[0][:100] if out2.strip() else ""} ／ 取込後件数 {res2}', rc2 != 0 and res2 == '10', d)
    psql('DROP DATABASE IF EXISTS usagi_t', 'postgres')
    save('web_results.json')


if __name__ == '__main__':
    main()
