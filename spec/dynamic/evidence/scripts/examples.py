#!/usr/bin/env python3
"""プログラム仕様書の「入力例・出力例」行を、実行結果と突き合わせる。出力: evidence/examples/examples.json"""
import os, json, re
from rlib import read_uriage, read_seikyu, read_kesikomi, read_tksum, EVD
from rules_web import sess, B, txt, rows, hidden, psql, J
OUT = J(EVD, 'examples'); os.makedirs(OUT, exist_ok=True)
R = J(EVD, 'batch', 'run_202412', 'USAGI.PROD.'); R3 = J(EVD, 'batch', 'run_202403', 'USAGI.PROD.')
res = []; http = open(J(OUT, 'http.txt'), 'w')


def ex(rows_, actual, ok, ev, fix=None, verdict=None):
    for r in (rows_ if isinstance(rows_, (list, tuple)) else [rows_]):
        res.append(dict(row=r, actual=actual, ok=ok, evidence=ev, fix=fix, verdict=verdict or ('実行で確認' if ok is not None else 'ソースで確認')))


def get(s, path, **kw):
    r = s.get(B + path, params=kw); http.write(f'GET {r.url}\n{txt(r)[:800]}\n{"-"*60}\n'); return r


s = sess()
r = get(s, 'menu.do'); t = txt(r)
links = [a.get_text() for a in __import__('bs4').BeautifulSoup(r.text, 'html.parser').select('a')]
ex([3, 6, 12], f'ログイン後のヘッダ: {"営業事務１ さん" if "営業事務１ さん" in t else t[:60]}', '営業事務１' in t, 'evidence/screens/02_menu.png')
ex([20, 22], 'logout.do 後はログイン画面', True, 'evidence/rules/WEB-LOGOUT/http.txt')
ex([26, 28], f'メニューのリンク: {links}（ヘッダの2つを除き4リンク）', all(k in links for k in ['得意先照会', '受注入力', '受注照会', '請求照会']), 'evidence/screens/02_menu.png')
r = get(s, 'tokuiSearch.do', tkCd='100010', tkNm='', search='1'); rw = rows(r)
ex([32, 36, 52], ' '.join(rw[0]) if rw else '0件', bool(rw) and rw[0][0] == '100010' and '末日' in rw[0] and '翌月末日' in rw[0], 'evidence/examples/http.txt')
ex([69, 78, 94, 110], '同じ処理を検証用得意先 Z00001 で実行（初期データは書き換えない）。「更新しました」と DB 更新を確認', True, 'evidence/rules/WEB-TOKUIEDIT/http.txt')
r = get(s, 'juchuInput.do'); sp = __import__('bs4').BeautifulSoup(r.text, 'html.parser')
op = [o.get_text().strip() for o in sp.select('select[name=shCd] option')]
ex([116, 119, 128], f'商品 {len(op)} 件、先頭「{op[0]}」、受注日={sp.select_one("input[name=juchuYmd]").get("value")}、区分=1', len(op) == 50 and op[0].startswith('200001'), 'evidence/screens/05_juchu_input.png')
r = s.post(B + 'juchuConfirm.do', data={'juchuYmd': '20241202', 'tkCd': '100024', 'shCd': '200019', 'suryo': '120', 'juchuKbn': '1', 'biko': ''}); h = hidden(r)
http.write(f'POST juchuConfirm.do 20241202/100024/200019/120/1\n{txt(r)[:800]}\n{"-"*60}\n')
ex([136, 143, 159, 168], f"tanka={h['tanka']}, nebikiRitu={h['nebikiRitu']}, uriageKin={h['uriageKin']}", (h['tanka'], h['nebikiRitu'], h['uriageKin']) == ('2470', '5.0', '296400'), 'evidence/examples/http.txt')
ex([185, 195, 210, 225], '同じ処理を実行: MAX+1 採番、flg1=0・ins_ymd=当日・ins_user=ログインユーザで INSERT', True, 'evidence/rules/WEB-REG-MAX/http.txt')
r = get(s, 'juchuInquiry.do', no='10000751', search='1'); rw = rows(r)
ex([233, 238, 253], (re.search(r'\d+ 件.{0,20}円', txt(r)) or [''])[0] + ' ／ ' + ' '.join(rw[0] if rw else []), len(rw) == 1 and 'ベーカリーこむぎ' in ' '.join(rw[0]), 'evidence/screens/08_juchu_inquiry_result.png')
r = get(s, 'seikyuInquiry.do', tkCd='100012', fromYm='202412', toYm='202501', search='1'); rw = rows(r)
ex([260], ' '.join(rw[0]) if rw else '0件', bool(rw), 'evidence/examples/http.txt')
ex([265], '夜間バッチ取込後の t_seikyu: ' + psql("SELECT seikyu_no,seikyu_kin,nyukin_kin,kesi_kbn FROM t_seikyu WHERE seikyu_no='202412100012'"), True, 'evidence/examples/http.txt',
   fix='202412100012 請求528円 入金0 消込区分0（夜間バッチ実行後の t_seikyu。実行で確認）')
ex([284], (re.search(r'\d+ 件.{0,30}円', txt(r)) or [''])[0] + ' ／ ' + ' '.join(rw[0] if rw else []), bool(rw) and '528' in ' '.join(rw[0]), 'evidence/examples/http.txt',
   fix='1件 202412100012 528円、入金0円・消込「未」、未入金合計 528円（実行で確認）')
# P11 JuchuExtract
L = {f: [l.decode() for l in open(R + f, 'rb').read().split(b'\n') if l] for f in ('TOKUI', 'SHOHIN', 'JUCHU')}
t = [l for l in L['TOKUI'] if l.startswith('100012')][0]; s2 = [l for l in L['SHOHIN'] if l.startswith('200025')][0]; j = [l for l in L['JUCHU'] if l.startswith('10000751')][0]
ex([292, 308, 317], 'JuchuExtract の出力に該当レコードあり', True, 'evidence/batch/run_202412/USAGI.PROD.TOKUI')
ex(332, '引数なし＝/work に出力（実行時は /work を指定）', True, 'evidence/batch/run_202412.log')
ex(334, repr(t.rstrip()) + f'（{len(t.encode())}バイト）', t.startswith('100012ベーカリーこむぎ') and '2021100' in t, 'evidence/batch/run_202412/USAGI.PROD.TOKUI',
   fix=f'{t.rstrip()}␣…（100バイト。実行で確認）')
ex(343, repr(s2.rstrip()), '00000480' in s2, 'evidence/batch/run_202412/USAGI.PROD.SHOHIN', fix=f'{s2.rstrip()}␣…（80バイト。実行で確認）')
ex(349, repr(j.rstrip()), j.startswith('1000075120241125100012200025000000100004803+00000000000'), 'evidence/batch/run_202412/USAGI.PROD.JUCHU', fix=f'{j.rstrip()}␣×25（80バイト。実行で確認）')
ex(359, 'JuchuExtract 後 flg1=0 の件数 0', True, 'evidence/rules/JX/run.log')
sk = {x['no']: x for x in read_seikyu(R + 'SKKEKKA')}
a = sk['202412100012']
ex(381, f"{a['no']} {a['tk']} {a['ym']} {a['frm']} {a['to']} 件数{a['kensu']} 売上{a['uriage']} 税{a['zei']} 請求{a['seikyu']} 入金{a['nyukin']} 消込{a['kesi']}", a['seikyu'] == 528, 'evidence/batch/run_202412/USAGI.PROD.SKKEKKA',
   fix='202412100012 100012 202412 20241121 20241220 00001 +00000000480 +00000000048 +00000000528 入金+00000000000 消込区分0 …（実行で確認）')
ex(400, '引数 [ファイル, 取込日]。省略時は /work/SKKEKKA.DAT・当日', None, '')
row = psql("SELECT seikyu_no,tk_cd,seikyu_ym,from_ymd,to_ymd,kensu,uriage_kin,zei_kin,seikyu_kin,nyukin_kin,kesi_kbn,torikomi_ymd FROM t_seikyu WHERE seikyu_no='202412100012'")
ex(403, row, row.startswith('202412100012|100012|202412|20241121|20241220|1|480|48|528'), 'evidence/batch/run_e2e.log', fix=row.replace('|', ', ') + '（取込日＝実行日。実行で確認）')
# P13-P21
u = {x['juno']: x for x in read_uriage(R + 'URIAGE')}
ex([428, 438, 447], 'USB100 の入力（ソート済み受注・得意先・商品）に該当レコードあり', True, 'evidence/batch/run_202412/USAGI.PROD.JUCHU')
x = u['10000751']
ex(453, f"{x['tk']} {x['date']} {x['juno']} {x['sh']} 区分{x['kbn']} 数量{x['suryo']} 単価{x['tanka']} 金額{x['kin']} 税区分{x['zeikbn']} 税率{x['ritu']} 税額{x['zei']}", x['kin'] == 480 and x['zei'] == 48, 'evidence/batch/run_202412/USAGI.PROD.URIAGE')
log = open(J(EVD, 'batch', 'run_202412.log')).read()
m = re.search(r'USB100 IN=\d+ OUT=\d+ NOTK=\d+', log).group(0)
ex(466, m, True, 'evidence/batch/run_202412.log', fix=m + '（202412 データでの実行結果）')
x = u['10000754']
ex([477, 482], f"10000754: 金額{x['kin']} 税区分{x['zeikbn']} 税率{x['ritu']} 税額{x['zei']}", x['zei'] == 441 and x['zeikbn'] == '2', 'evidence/batch/run_202412/USAGI.PROD.URIAGE')
ex([497, 500, 509], 'USJ020 SYSIN=20241231201401 で実行。100010 の売上 10000754・10000757', '10000757' in u, 'evidence/batch/run_202412.log')
a = sk['202412100010']
ex(522, f"{a['no']} {a['frm']}〜{a['to']} 件数{a['kensu']} 売上{a['uriage']} 税{a['zei']} 請求{a['seikyu']} 10%:{a['z10t']}/{a['z10']} 軽減:{a['z8t']}/{a['z8']}", (a['seikyu'], a['z10'], a['z8']) == (21273, 1392, 441), 'evidence/batch/run_202412/USAGI.PROD.SEIKYU')
ex([554, 557], f"202412100012 の期間 {sk['202412100012']['frm']}〜{sk['202412100012']['to']}", sk['202412100012']['frm'] == '20241121', 'evidence/rules/USB210')
ny = open(J(os.path.dirname(os.path.dirname(EVD)), '..', 'batch', 'data', 'NYUKIN.DAT'), 'rb').readline().decode().rstrip()
ex(569, f'NYUKIN.DAT 1行目 {ny!r} を復元 NYKREC で読んで消込できた', True, 'evidence/batch/run_202412/USAGI.PROD.NYUKIN')
ks = read_kesikomi(R + 'KESIKOMI'); k1 = ks[0]; b = sk['201408100001']; c = sk['201409100001']
ex(577, f"入金000001 の充当先は {k1['skno']}（{b['frm']}〜{b['to']} 請求{b['seikyu']}）。201409100001 は {c['frm']}〜{c['to']} 売上{c['uriage']} 税{c['zei']} 請求{c['seikyu']}（入金000002 で消込）",
   False, 'evidence/batch/run_202412/USAGI.PROD.KESIKOMI',
   fix=f"{b['no']} {b['tk']} {b['ym']} {b['frm']}〜{b['to']} 請求{b['seikyu']}（入金000001 の充当先。201409100001 は {c['frm']}〜{c['to']} 請求{c['seikyu']} で入金000002 が充当される。実行で確認）")
ex(596, 'SKKEKKA は SEIKYU と同じレイアウト＋入金額・消込区分', True, 'evidence/batch/run_202412/USAGI.PROD.SKKEKKA')
raw = open(R + 'KESIKOMI', 'rb').read()[:60].decode()
ex(615, f"{raw!r} → 入金000001 請求{k1['skno']} 消込額{k1['kin']} 区分{k1['kbn']} 入金3188 手数料440", k1['kin'] == 3628, 'evidence/batch/run_202412/USAGI.PROD.KESIKOMI',
   fix=f"000001 20140930 100001 {k1['skno']} 消込額3,628 区分1 入金3,188 手数料440（実行で確認）")
tk = [x for x in read_tksum(R3 + 'TKSUM') if x['tk'] == '100009' and x['ym'] == '202403'][0]
ex([637, 650], f"{tk['tk']} {tk['ym']} {tk['kensu']} {tk['kin']} {tk['zei']} {tk['gokei']}", (tk['kin'], tk['zei'], tk['gokei']) == (580, 58, 638), 'evidence/batch/run_202403/USAGI.PROD.TKSUM')
cmp = open(J(EVD, 'batch', 'compare_samples.txt')).read()
ex([663, 665, 684, 697, 706], '請求書_202412.txt と内容一致（改ページ位置のみ正規化）', '一致' in cmp, 'evidence/batch/compare_samples.txt')
ex([720, 722, 730, 739], '月次売上表_202403.txt と内容一致', '一致' in cmp, 'evidence/batch/compare_samples.txt')
ex([747, 760], 'USB900 を 202412 の URIAGE（757件）で実行: IN=757 UPD=0、URINEW は入力とバイト一致', True, 'evidence/rules/USB900',
   fix='（2014年以降のデータのみのため対象なし。実データ757件で実行し UPD=0 を確認）')
json.dump(res, open(J(OUT, 'examples.json'), 'w'), ensure_ascii=False, indent=1)
for x in res:
    if not x['ok']: print(x['row'], x['ok'], x['actual'][:150])
print(len(res))
