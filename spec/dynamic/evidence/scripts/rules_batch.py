#!/usr/bin/env python3
"""COBOL バッチの業務ルールを境界値の入力で実行して確かめる。
結果: evidence/rules/batch_results.json、各ケースの入力・出力: evidence/rules/<ケースID>/"""
import os, re
from rlib import *

J = os.path.join


def run_t(pgm, cid, lines):
    d = case_dir(cid)
    inp = ''.join(l + '\n' for l in lines)
    open(J(d, 'input.txt'), 'w').write(inp)
    rc, out = cob(pgm, {}, inp)
    open(J(d, 'output.txt'), 'w').write(out + f'\nRC={rc}\n')
    res = {}
    for l in out.splitlines():
        k, v = l.split(' => ')
        res[k.strip()] = dict(re.findall(r'(\w+)=\s*(-?\d+)', v))
    return d, res


def usb100(d, tks, shs, jus):
    jus = sorted(jus, key=lambda r: (r[16:22], r[8:16], r[0:8]))
    write_ls(J(d, 'TOKUI'), tks); write_ls(J(d, 'SHOHIN'), shs); write_ls(J(d, 'JUCHSRT'), jus)
    rc, out = cob('USB100', {k: J(d, k) for k in ('JUCHSRT', 'TOKUI', 'SHOHIN', 'URIAGE')})
    open(J(d, 'USB100.log'), 'w').write(out + f'\nRC={rc}\n')
    return read_uriage(J(d, 'URIAGE')), out


def dump(d, name, rows):
    open(J(d, name), 'w').write('\n'.join(str(r) for r in rows) + '\n')


def sk_line(tk, ym, frm, to, seikyu, nyukin=0, uriage=None, zei=None, z10t=0, z10=0, z8t=0, z8=0, sot=0, so=0, kensu=1):
    s12 = lambda v: ('-' if v < 0 else '+') + str(abs(v)).zfill(11)
    uriage = seikyu if uriage is None else uriage
    zei = 0 if zei is None else zei
    l = (ym + tk + tk + ym + frm + to + str(kensu).zfill(5) + s12(uriage) + s12(zei) + s12(seikyu) + s12(nyukin) + '0'
         + s12(z10t) + s12(z10) + s12(z8t) + s12(z8) + s12(sot) + s12(so) + '    ')
    assert len(l) == 170, len(l)
    return l.encode()


# ---------------- USB110 消費税計算 ----------------
P = 'USB110'
L = lambda d, k, ke, h: f'{d} {"-" if k < 0 else "+"}{str(abs(k)).zfill(11)} {ke} {h}'
cases = {
    'a': L('20191001', 1000, '1', '1'), 'b': L('20190930', 1000, '1', '1'),
    'c': L('20191001', 1000, '0', '1'), 'd': L('20190930', 1000, '0', '1'),
    'e': L('20140401', 1000, '0', '1'), 'f': L('20140331', 1000, '0', '1'),
    'g': L('19970331', 1000, '0', '1'), 'h': L('19890401', 1000, '0', '1'),
    'i': L('20241201', 105, '0', '2'), 'j': L('20241201', 104, '0', '2'),
    'k': L('20241201', 101, '0', '3'), 'l': L('20241201', 100, '0', '3'), 'm': L('20241201', -101, '0', '3'),
    'n': L('20241201', 109, '0', '1'), 'o': L('20241201', 109, '0', ' '), 'p': L('20241201', 109, '0', '9'),
    'q': L('20241201', -109, '0', '1'), 'r': L('20241201', -105, '0', '2'),
}
d, R = run_t('T110', 'USB110', list(cases.values()))
g = lambda k: R[cases[k][:25].strip()] if cases[k][:25].strip() in R else R[cases[k][:25]]
def G(k):
    for kk, v in R.items():
        if kk.strip() == cases[k].strip():
            return v
F = lambda k: f"{cases[k]} → 税率{G(k)['RITU']} 区分{G(k)['KBN']} 税額{G(k)['ZEI']}"
rec(487, P, 'USB110-1', '売上日 20191001／20190930、金額1000、軽減区分1、端数1', '20191001 は 8%・税区分2。20190930 は軽減対象外（8%標準）',
    F('a') + ' ／ ' + F('b'), G('a')['RITU'] == '08' and G('a')['KBN'] == '2' and G('b')['KBN'] != '2', d)
rec(488, P, 'USB110-2', '売上日 20191001／20190930、軽減区分0', '20191001 は 10%、20190930 は 8%', F('c') + ' ／ ' + F('d'),
    G('c')['RITU'] == '10' and G('d')['RITU'] == '08', d)
rec(489, P, 'USB110-3', '売上日 20140401／20140331', '20140401 は 8%、20140331 は 5%', F('e') + ' ／ ' + F('f'),
    G('e')['RITU'] == '08' and G('f')['RITU'] == '05', d)
rec(490, P, 'USB110-4', '売上日 20140331／19890401', 'どちらも 5%', F('f') + ' ／ ' + F('h'), G('f')['RITU'] == '05' and G('h')['RITU'] == '05', d)
rec(491, P, 'USB110-5', '売上日 19970331（実際の税率3%の期間）', '3% にならず 5%（ZEI-03-RTN に到達しない）', F('g'), G('g')['RITU'] == '05', d)
rec(492, P, 'USB110-6', '端数区分2、金額105／104（10%）', '10.5→11、10.4→10（四捨五入）', F('i') + ' ／ ' + F('j') + ' ／ ' + F('r'),
    G('i')['ZEI'] == '11' and G('j')['ZEI'] == '10', d)
rec(493, P, 'USB110-7', '端数区分3、金額101／100／−101（10%）', '10.1→11、10.0→10（小数がなければ加算しない）',
    F('k') + ' ／ ' + F('l') + ' ／ ' + F('m'), G('k')['ZEI'] == '11' and G('l')['ZEI'] == '10', d,
    note=f"マイナス金額の切上げは {G('m')['ZEI']}")
rec(494, P, 'USB110-8', '端数区分1／空白／9、金額109（10%）', 'いずれも 10.9→10（切捨て）', F('n') + ' ／ ' + F('o') + ' ／ ' + F('p') + ' ／ ' + F('q'),
    G('n')['ZEI'] == G('o')['ZEI'] == G('p')['ZEI'] == '10', d)

# ---------------- USB210 締日算出 ----------------
P = 'USB210'
C = ['99 202400', '99 202413', '99 202401', '00 202401', '29 202401', '98 202401', '01 202401', '28 202401',
     '99 202304', '99 202302', '99 202402', '15 202401', '20 202403', '28 202402', '27 202402', '28 202302',
     '28 210002', '28 200002', '28 202403', '28 202303', '01 202403']
d, R = run_t('T210', 'USB210', C)
S = lambda k: f"{k} → {R[k]['FROM']}〜{R[k]['TO']} RC={R[k]['RC']}"
SS = lambda *ks: ' ／ '.join(S(k) for k in ks)
rec(561, P, 'USB210-1', '締日99、年月 202400／202413／202401', '月0・13 は RC=9、202401 は RC=0', SS('99 202400', '99 202413', '99 202401'),
    R['99 202400']['RC'] == '09' and R['99 202413']['RC'] == '09' and R['99 202401']['RC'] == '00', d)
rec(562, P, 'USB210-2', '締日 00／29／98／01／28（202401）', '00・29・98 は RC=9、01・28 は RC=0', SS('00 202401', '29 202401', '98 202401', '01 202401', '28 202401'),
    [R[k]['RC'] for k in ('00 202401', '29 202401', '98 202401', '01 202401', '28 202401')] == ['09', '09', '09', '00', '00'], d)
rec(563, P, 'USB210-3', '締日99、202401／202304／202302', '当月1日〜末日（31/30/28）', SS('99 202401', '99 202304', '99 202302'),
    (R['99 202401']['FROM'], R['99 202401']['TO'], R['99 202304']['TO'], R['99 202302']['TO']) == ('20240101', '20240131', '20230430', '20230228'), d)
rec(564, P, 'USB210-4', '締日99、202402（うるう年）', '20240201〜20240228（2/29 は期間外）', S('99 202402'),
    R['99 202402']['TO'] == '20240228', d)
rec(565, P, 'USB210-5', '締日15（202401）、締日20（202403）、締日01（202403）', '20231216〜20240115、20240221〜20240320、20240202〜20240301', SS('15 202401', '20 202403', '01 202403'),
    (R['15 202401']['FROM'], R['15 202401']['TO'], R['20 202403']['FROM'], R['20 202403']['TO'], R['01 202403']['FROM']) == ('20231216', '20240115', '20240221', '20240320', '20240202'), d)
rec(566, P, 'USB210-6', '締日28／27（202402）、締日28（202302）', '28 は 20240229 まで、27 は 20240227 のまま、平年 202302 は 20230228',
    SS('28 202402', '27 202402', '28 202302'), (R['28 202402']['TO'], R['27 202402']['TO'], R['28 202302']['TO']) == ('20240229', '20240227', '20230228'), d,
    note=f"翌月の開始日: {S('28 202403')} ／ {S('28 202303')}（平年に 0229 という存在しない日付を作る）")
rec(567, P, 'USB210-7', '締日28、210002／200002', '年÷4 の余り0 でうるう年扱い（2100 年も 29 日）', SS('28 210002', '28 200002'),
    R['28 210002']['TO'] == '21000229' and R['28 200002']['TO'] == '20000229', d)

# ---------------- USB100 売上計上 ----------------
P = 'USB100'
d = case_dir('USB100')
tks = [tokui('T00001'), tokui('T00002', del_='1')]
shs = [shohin('S00001', '0', 100), shohin('S00002', '1', 100)]
jus = [juchu(1, '20241201', 'T00001', 'S00001', 10, 100, '1'), juchu(2, '20241202', 'T00001', 'S00001', 10, 100, '2'),
       juchu(3, '20241203', 'T00001', 'S00001', 10, 100, '3'), juchu(4, '20241204', 'T00001', 'S00001', 10, 100, '1', kin=999),
       juchu(5, '20241205', 'T00001', 'S00002', 10, 100, '1'), juchu(6, '20241206', 'T00001', 'S99999', 10, 100, '1'),
       juchu(7, '20241207', 'T00002', 'S00001', 10, 100, '1'), juchu(8, '20241208', 'T99999', 'S00001', 10, 100, '1'),
       juchu(9, '20190930', 'T00001', 'S00002', 10, 100, '1')]
U, out = usb100(d, tks, shs, jus)
dump(d, 'URIAGE.decoded.txt', U)
u = {int(r['juno']): r for r in U}
fu = lambda i: f"受注{i}: 数量{u[i]['suryo']} 金額{u[i]['kin']} 税区分'{u[i]['zeikbn']}' 税率{u[i]['ritu']} 税額{u[i]['zei']}" if i in u else f'受注{i}: 出力なし'
rec(468, P, 'USB100-1', '受注2: 区分2 数量10 単価100', '数量 −10', fu(2), u[2]['suryo'] == -10, d)
rec(469, P, 'USB100-2', '受注1: 区分1 数量10／受注3: 区分3 数量10', '数量 10 のまま', fu(1) + ' ／ ' + fu(3), u[1]['suryo'] == 10 and u[3]['suryo'] == 10, d)
rec(470, P, 'USB100-3', '受注4: 数量10 単価100、受注ファイルの金額 JU-KIN=999', '売上金額 1000（JU-KIN を使わない）', fu(4), u[4]['kin'] == 1000, d)
rec(471, P, 'USB100-4', '受注3: 区分3（無償サンプル）数量10 単価100 JU-KIN=0', '売上金額 1000（Web の 0 円ではなく有償で計上）', fu(3), u[3]['kin'] == 1000, d)
rec(472, P, 'USB100-5', '受注5: 20241205 軽減商品／受注9: 20190930 軽減商品', '売上日で税率が変わる（8%軽減・区分2／8%標準）', fu(5) + ' ／ ' + fu(9),
    u[5]['ritu'] == '08' and u[5]['zeikbn'] == '2' and u[9]['zeikbn'] == '1', d)
rec(473, P, 'USB100-6', '受注6: 商品 S99999（商品ファイルにない）', '軽減区分空白→10%', fu(6), u[6]['ritu'] == '10', d)
rec(474, P, 'USB100-7', '受注8: 得意先 T99999（得意先ファイルにない）', '売上を出さず NOTK=1', fu(8) + ' ／ ' + out, 8 not in u and 'NOTK=0000001' in out, d)
rec(475, P, 'USB100-8', '受注7: 得意先 T00002（取引停止 TK-DEL=1）', '売上計上する', fu(7), 7 in u, d)

# ---------------- USB200 月次請求締め ----------------
P = 'USB200'
d = case_dir('USB200-A')
tks = [tokui('A00001', '99'), tokui('A00002', '20'), tokui('A00003', '00'), tokui('A00004', '99'), tokui('A00005', '28')]
shs = [shohin('S00001', '0', 100), shohin('S00003', '0', 105)]
jd = [('A00001', '20231231'), ('A00001', '20240131'), ('A00001', '20240201'), ('A00001', '20240228'), ('A00001', '20240229'),
      ('A00001', '20240301'), ('A00001', '20240415'), ('A00002', '20240120'), ('A00002', '20240121'), ('A00002', '20240320'),
      ('A00002', '20240321'), ('A00003', '20240115'), ('A00005', '20240229')]
jus = [juchu(i + 1, dt, tk, 'S00001', 1, 100) for i, (tk, dt) in enumerate(jd)]
jus += [juchu(51, '20240110', 'A00001', 'S00003', 1, 105), juchu(52, '20240111', 'A00001', 'S00003', 1, 105)]
U, _ = usb100(d, tks, shs, jus)
raw = open(J(d, 'URIAGE'), 'rb').read()
open(J(d, 'URIAGE'), 'wb').write(b'A00000' + raw[6:64] + raw)  # 得意先ファイルにない得意先の売上を先頭に1件追加
write_ls(J(d, 'TOKUI'), tks)
rc, out = cob('USB200', {'TOKUI': J(d, 'TOKUI'), 'URIAGE': J(d, 'URIAGE'), 'SEIKYU': J(d, 'SEIKYU')}, '20240331202401\n')
open(J(d, 'USB200.log'), 'w').write('SYSIN=20240331202401\n' + out + f'\nRC={rc}\n')
dump(d, 'URIAGE.decoded.txt', read_uriage(J(d, 'URIAGE')))
SK = read_seikyu(J(d, 'SEIKYU')); dump(d, 'SEIKYU.decoded.txt', SK)
sk = {(r['tk'], r['ym']): r for r in SK}
fs = lambda k: (f"{k[0]} {k[1]}: {sk[k]['frm']}〜{sk[k]['to']} 件数{sk[k]['kensu']} 売上{sk[k]['uriage']} 税{sk[k]['zei']} 請求{sk[k]['seikyu']}" if k in sk else f'{k[0]} {k[1]}: 請求なし')
rec(541, P, 'USB200-1', 'SYSIN 20240331202401、A00001 の売上 20231231〜20240415', '202401〜202403 の3か月分だけ作る（20240415 は対象外）',
    ' ／ '.join(fs(('A00001', y)) for y in ('202401', '202402', '202403', '202404')),
    all(('A00001', y) in sk for y in ('202401', '202402', '202403')) and ('A00001', '202404') not in sk, d)
rec(542, P, 'USB200-2', 'A00002（締日20）202402', '20240121〜20240220（USB210 の結果）', fs(('A00002', '202402')),
    sk.get(('A00002', '202402'), {}).get('frm') == '20240121' and sk[('A00002', '202402')]['to'] == '20240220', d)
rec(543, P, 'USB200-3', 'A00003（締日区分00）', 'エラー表示し請求を作らない', out.replace('\n', ' ／ '),
    'SIME ERROR A00003' in out and not any(k[0] == 'A00003' for k in sk), d)
rec(544, P, 'USB200-4', 'A00001 の 20240131（期間末日）・20240201（期間初日）、A00002 の 20240120', '期間の両端の日を含めて集計する',
    fs(('A00001', '202401')) + ' ／ ' + fs(('A00001', '202402')) + ' ／ ' + fs(('A00002', '202401')),
    sk[('A00001', '202401')]['kensu'] == 3 and sk[('A00002', '202401')]['kensu'] == 1, d)
rec(545, P, 'USB200-5', 'A00001 の 20231231（開始年月 202401 の期間より前）', 'TOBASI に数え、どの請求にも載らない', out.replace('\n', ' ／ '),
    'TOBASI=' in out, d, note='TOBASI には 20231231、A00000、末日締め 20240229 の3件が入る')
rec(546, P, 'USB200-6', '得意先ファイルにない A00000 の売上1件', 'TOBASI に数えて読み捨て', out.replace('\n', ' ／ '),
    not any(k[0] == 'A00000' for k in sk), d)
rec(547, P, 'USB200-7', 'A00004（売上なし）、A00005（202402 のみ売上）', '売上0件の月は請求を出さない',
    ' ／ '.join(fs(k) for k in (('A00004', '202401'), ('A00005', '202401'), ('A00005', '202402'), ('A00005', '202403'))),
    not any(k[0] == 'A00004' for k in sk) and list(k for k in sk if k[0] == 'A00005') == [('A00005', '202402')], d)
rec(548, P, 'USB200-8', '全請求', '請求番号＝年月6桁＋得意先コード6桁', ', '.join(r['no'] for r in SK[:4]) + ' …',
    all(r['no'] == r['ym'] + r['tk'] for r in SK), d)
rec(549, P, 'USB200-9', 'A00001 202401: 100円×1・105円×2（10%・切捨て）', '請求金額＝売上＋税。税は明細ごと（10+10+10=30）', fs(('A00001', '202401')),
    all(r['seikyu'] == r['uriage'] + r['zei'] for r in SK) and sk[('A00001', '202401')]['zei'] == 30, d)
rec(495, 'USB110', 'USB110-9', 'USB200-A の A00001 202401: 105円の明細2件（10%・切捨て）', '明細ごとに 10円ずつ（請求単位なら 31円）', fs(('A00001', '202401')),
    sk[('A00001', '202401')]['zei'] == 30, d)
rec(564, 'USB210', 'USB210-8', 'USB200-A の A00001（末日締め）20240229 の売上', '2/29 の売上はどの請求にも載らない', fs(('A00001', '202402')) + ' ／ ' + fs(('A00001', '202403')),
    sk[('A00001', '202402')]['kensu'] == 2 and sk[('A00001', '202403')]['kensu'] == 1, d,
    note='202402 は 0201・0228 の2件、202403 は 0301 の1件。0229 は TOBASI')
d = case_dir('USB200-B')
tks = [tokui('A00006', '99')]
shs = [shohin('S00001', '0', 1000), shohin('S00002', '1', 1000)]
jus = [juchu(1, '20190930', 'A00006', 'S00001', 1, 1000), juchu(2, '20191001', 'A00006', 'S00001', 1, 1000),
       juchu(3, '20191002', 'A00006', 'S00002', 1, 1000), juchu(4, '20190915', 'A00006', 'S00002', 1, 1000)]
usb100(d, tks, shs, jus)
rc, out = cob('USB200', {'TOKUI': J(d, 'TOKUI'), 'URIAGE': J(d, 'URIAGE'), 'SEIKYU': J(d, 'SEIKYU')}, '20191031201909\n')
open(J(d, 'USB200.log'), 'w').write('SYSIN=20191031201909\n' + out + f'\nRC={rc}\n')
dump(d, 'URIAGE.decoded.txt', read_uriage(J(d, 'URIAGE')))
SK = read_seikyu(J(d, 'SEIKYU')); dump(d, 'SEIKYU.decoded.txt', SK)
sk = {r['ym']: r for r in SK}
fb = lambda y: f"{y}: 10%対象{sk[y]['z10t']}/税{sk[y]['z10']} 軽減8%対象{sk[y]['z8t']}/税{sk[y]['z8']} 旧税率対象{sk[y]['sot']}/税{sk[y]['so']}"
rec(550, P, 'USB200-10', '201910: 20191002 軽減商品1000円', '軽減8% 欄 1000／80', fb('201910'), sk['201910']['z8t'] == 1000 and sk['201910']['z8'] == 80, d)
rec(551, P, 'USB200-11', '201910: 20191001 標準商品1000円', '10% 欄 1000／100', fb('201910'), sk['201910']['z10t'] == 1000 and sk['201910']['z10'] == 100, d)
rec(552, P, 'USB200-12', '201909: 20190915 軽減商品・20190930 標準商品（8%）', '旧税率欄 2000／160', fb('201909'), sk['201909']['sot'] == 2000 and sk['201909']['so'] == 160, d)

# ---------------- USB300 入金消込 ----------------
P = 'USB300'
d = case_dir('USB300')
sks = [sk_line('B00001', '202401', '20240101', '20240131', 11000), sk_line('B00001', '202402', '20240201', '20240229', 22000),
       sk_line('B00002', '202401', '20240101', '20240131', 11000), sk_line('B00002', '202402', '20240201', '20240229', 11000),
       sk_line('B00003', '202401', '20240101', '20240131', 5000)]
nys = [nyukin(1, '20240205', 'B00001', 10560, 440), nyukin(2, '20240310', 'B00001', 5000), nyukin(3, '20240310', 'B00002', 15000),
       nyukin(4, '20240311', 'B00002', 10000), nyukin(5, '20240131', 'B00003', 5000), nyukin(6, '20240201', 'B00000', 1000, 330),
       nyukin(7, '20240201', 'B00009', 2000, 0)]
nys.sort(key=lambda r: (r[14:20], r[6:14], r[0:6]))
write_ls(J(d, 'SEIKYU'), sks); write_ls(J(d, 'NYUKSRT'), nys)
rc, out = cob('USB300', {k: J(d, k) for k in ('NYUKSRT', 'SEIKYU', 'SKKEKKA', 'KESIKOMI')})
open(J(d, 'USB300.log'), 'w').write(out + f'\nRC={rc}\n')
KS = read_kesikomi(J(d, 'KESIKOMI')); SK = read_seikyu(J(d, 'SKKEKKA'))
dump(d, 'KESIKOMI.decoded.txt', KS); dump(d, 'SKKEKKA.decoded.txt', SK)
ks = {}
for r in KS:
    ks.setdefault(int(r['nyno']), []).append(r)
fk = lambda i: f"入金{i}: " + ', '.join(f"{r['skno'].strip() or '(請求番号なし)'} {r['kin']} 区分{r['kbn']}" for r in ks.get(i, []))
skk = {r['no']: r for r in SK}
fsk = lambda no: f"{no}: 請求{skk[no]['seikyu']} 入金{skk[no]['nyukin']} 消込{skk[no]['kesi']}"
rec(625, P, 'USB300-1', '入金1: 入金額10560＋手数料440（B00001 202401 請求11000）', '11000 を消込', fk(1), ks[1][0]['kin'] == 11000, d)
rec(626, P, 'USB300-2', '入金5: 入金日20240131＝B00003 202401 の締日', '締日＜入金日 でないので充当しない（→過入金）', fk(5),
    ks[5][0]['kbn'] == '9', d)
rec(627, P, 'USB300-3', '入金3: B00002 に 15000（202401・202402 とも残高11000）', '古い請求（202401）から充当: 11000＋4000', fk(3),
    [(r['skno'][:6], r['kin']) for r in ks[3]] == [('202401', 11000), ('202402', 4000)], d,
    note='ソースのコメント「新しい請求から順に」とは逆')
rec(628, P, 'USB300-4', '入金2: B00001 202402（残高22000）に 5000', '5000 を一部消込', fk(2), ks[2][0]['kin'] == 5000 and ks[2][0]['kbn'] == '1', d)
rec(629, P, 'USB300-5', '入金4: B00002 202402（残高7000）に 10000', '7000 を充当', fk(4), ks[4][0]['kin'] == 7000, d)
rec(630, P, 'USB300-6', '入金4 の残り3000', '請求番号空白・区分9で 3000', fk(4), ks[4][-1]['kbn'] == '9' and ks[4][-1]['kin'] == 3000 and not ks[4][-1]['skno'].strip(), d)
rec(631, P, 'USB300-7', '入金6: 請求がない B00000 に 1000＋手数料330／入金7: B00009 に 2000', '区分8で 1330／2000', fk(6) + ' ／ ' + fk(7),
    ks[6][0]['kbn'] == '8' and ks[6][0]['kin'] == 1330 and ks[7][0]['kbn'] == '8', d)
rec(632, P, 'USB300-8', 'B00003 202401（入金なし）', '消込区分0', fsk('202401B00003'), skk['202401B00003']['kesi'] == '0', d)
rec(633, P, 'USB300-9', 'B00001 202402（22000 に 5000）', '消込区分1', fsk('202402B00001'), skk['202402B00001']['kesi'] == '1', d)
rec(634, P, 'USB300-10', 'B00001 202401（11000 に 11000）', '消込区分2', fsk('202401B00001'), skk['202401B00001']['kesi'] == '2', d)
d = case_dir('USB300-400')
sks = []
for i in range(401):
    yy, mm = 1990 + i // 12, i % 12 + 1
    sks.append(sk_line('C00001', f'{yy}{mm:02}', f'{yy}{mm:02}01', f'{yy}{mm:02}28', 100))
sks.append(sk_line('C00002', '202401', '20240101', '20240131', 100))
write_ls(J(d, 'SEIKYU'), sks); write_ls(J(d, 'NYUKSRT'), [nyukin(1, '20240301', 'C00001', 50000), nyukin(2, '20240301', 'C00002', 100)])
rc, out = cob('USB300', {k: J(d, k) for k in ('NYUKSRT', 'SEIKYU', 'SKKEKKA', 'KESIKOMI')})
open(J(d, 'USB300.log'), 'w').write(out + f'\nRC={rc}\n')
n_out = len(read_seikyu(J(d, 'SKKEKKA'))) if os.path.exists(J(d, 'SKKEKKA')) else 0
rec(635, P, 'USB300-11', '得意先 C00001 の請求 401 件（表は 400 件）', '超過チェックなし（推定: 表あふれ）', f'RC={rc} 出力請求 {n_out} 件 / 入力 402 件。{out[:200]}',
    True, d, note='判定はソース記述どおりチェックが無いことの確認。挙動は要確認の挙動に記録')

# ---------------- USB400 月次集計 ----------------
P = 'USB400'
d = case_dir('USB400')
tks = [tokui('D00001'), tokui('D00002')]
shs = [shohin('S00001', '0', 1000)]
jus = [juchu(1, '20240131', 'D00001', 'S00001', 1, 1000), juchu(2, '20240201', 'D00001', 'S00001', 1, 1000),
       juchu(3, '20240215', 'D00001', 'S00001', 2, 1000), juchu(4, '20240201', 'D00002', 'S00001', 1, 1000)]
usb100(d, tks, shs, jus)
rc, out = cob('USB400', {'URIAGE': J(d, 'URIAGE'), 'TKSUM': J(d, 'TKSUM')})
open(J(d, 'USB400.log'), 'w').write(out + f'\nRC={rc}\n')
TS = read_tksum(J(d, 'TKSUM')); dump(d, 'TKSUM.decoded.txt', TS)
ft = ' ／ '.join(f"{r['tk']} {r['ym']} 件数{r['kensu']} 売上{r['kin']} 税{r['zei']} 合計{r['gokei']}" for r in TS)
rec(658, P, 'USB400-1', 'D00001: 20240131・20240201・20240215、D00002: 20240201', 'D00001 202401(1件)・202402(2件)、D00002 202402(1件)', ft,
    [(r['tk'], r['ym'], r['kensu']) for r in TS] == [('D00001', '202401', 1), ('D00001', '202402', 2), ('D00002', '202402', 1)], d)
rec(659, P, 'USB400-2', '同上', '先頭に空キーのレコードを出さない', f'{len(TS)} レコード。先頭 {TS[0]["tk"]}', TS[0]['tk'].strip() != '', d)
rec(660, P, 'USB400-3', '同上', '合計＝売上＋税', ft, all(r['gokei'] == r['kin'] + r['zei'] for r in TS), d)
raw = open(J(d, 'URIAGE'), 'rb').read()
d2 = case_dir('USB400-unsorted')
open(J(d2, 'URIAGE'), 'wb').write(raw[0:64] + raw[192:256] + raw[64:192])
rc, out = cob('USB400', {'URIAGE': J(d2, 'URIAGE'), 'TKSUM': J(d2, 'TKSUM')})
open(J(d2, 'USB400.log'), 'w').write(out + f'\nRC={rc}\n')
TS = read_tksum(J(d2, 'TKSUM')); dump(d2, 'TKSUM.decoded.txt', TS)
ft = ' ／ '.join(f"{r['tk']} {r['ym']} 件数{r['kensu']}" for r in TS)
rec(661, P, 'USB400-4', '売上の並びを D00001 202401 → D00002 → D00001 202402 に入れ替え', '（前提）並んでいないと同じキーが複数行に分かれる', ft, len(TS) == 3 and TS[1]['tk'] == 'D00002', d2,
    note='JCL どおりの順（USB100 がソート済み受注から作る）なら前提を満たす: evidence/batch/run_202412')

# ---------------- USR500 請求書 ----------------
P = 'USR500'
d = case_dir('USR500')
tks = [tokui('E00001', nm='テスト商事')]
shs = [shohin('S00001', '0', 1000), shohin('S00002', '1', 1000)]
jus = [juchu(1, '20241130', 'E00001', 'S00001', 1, 1000), juchu(2, '20241201', 'E00001', 'S00001', 1, 1000),
       juchu(3, '20241231', 'E00001', 'S00002', 1, 1000), juchu(4, '20241201', 'E00009', 'S00001', 1, 1000)]
usb100(d, tks + [tokui('E00009')], shs, jus)
write_ls(J(d, 'TOKUI'), tks)
skl = [sk_line('E00001', '202411', '20241101', '20241130', 1100, uriage=1000, zei=100, z10t=1000, z10=100),
       sk_line('E00001', '202412', '20241201', '20241231', 2180, uriage=2000, zei=180, z10t=1000, z10=100, z8t=1000, z8=80, kensu=2),
       sk_line('E00009', '202412', '20241201', '20241231', 1100, uriage=1000, zei=100, z10t=1000, z10=100)]
write_ls(J(d, 'SKKEKKA'), skl)
rc, out = cob('USR500', {'SKKEKKA': J(d, 'SKKEKKA'), 'URIAGE': J(d, 'URIAGE'), 'TOKUI': J(d, 'TOKUI'), 'SEIKYUSH': J(d, 'SEIKYUSH.txt')}, '202412\n')
open(J(d, 'USR500.log'), 'w').write('SYSIN=202412\n' + out + f'\nRC={rc}\n')
txt = open(J(d, 'SEIKYUSH.txt'), encoding='utf-8').read()
pages = [p for p in txt.split('\f') if p.strip()]
p1 = pages[0] if pages else ''
rec(713, P, 'USR500-1', 'SKKEKKA に E00001 の 202411・202412、SYSIN=202412', '202412 だけ出力（202411 は読み飛ばし）', f'{len(pages)} 枚: ' + ', '.join(l.strip() for l in txt.splitlines() if '請求番号' in l),
    '202411E00001' not in txt and '202412E00001' in txt, d)
rec(714, P, 'USR500-2', 'E00009（得意先ファイルにない）の 202412 請求', '得意先名を空白で出力', [l.rstrip() for l in txt.splitlines() if 'E00009' in l][0] if 'E00009' in txt else '出力なし',
    'E00009' in txt, d)
det = [l.rstrip() for l in p1.splitlines() if l.strip()[:4].isdigit() or '/' in l[:14]]
rec(715, P, 'USR500-3', 'E00001 の売上 20241130・20241201・20241231（請求期間 20241201〜20241231）', '20241201・20241231 の2行だけ', ' ／ '.join(det),
    '2024/11/30' not in p1 and '2024/12/01' in p1 and '2024/12/31' in p1, d)
rec(716, P, 'USR500-4', '20241231 の軽減商品', '明細の末尾に ※', ' ／ '.join(l for l in p1.splitlines() if '2024/12/31' in l), any('2024/12/31' in l and l.rstrip().endswith('※') for l in p1.splitlines()), d)
rec(717, P, 'USR500-5', 'E00001 202412: 10% 1000、軽減8% 1000、旧税率 0', '10%・軽減8% の行だけ出す', ' ／ '.join(l.strip() for l in p1.splitlines() if '%' in l or '旧税率' in l),
    ('旧税率' not in p1) and ('10%' in p1), d)
rec(718, P, 'USR500-6', '202412 の請求2件', '請求ごとに改ページ（\\f）', f"改ページ {txt.count(chr(12))} 回 / 請求 {len(pages)} 件", txt.count('\f') == 2, d)

# ---------------- USR510 月次売上表 ----------------
P = 'USR510'
d = case_dir('USR510')
tks = [tokui('F00001', nm='テスト一商店'), tokui('F00002', nm='テスト二商店')]
write_ls(J(d, 'TOKUI'), tks)
s = lambda v, w: ('-' if v < 0 else '+') + str(abs(v)).zfill(w)
ts = [f'{tk}{ym}{str(k).zfill(5)}{s(kin, 11)}{s(zei, 9)}{s(kin + zei, 11)}         '.encode()
      for tk, ym, k, kin, zei in [('F00001', '202411', 9, 9000, 900), ('F00001', '202412', 2, 2000, 200), ('F00002', '202412', 1, 1000, 80), ('F00009', '202412', 1, 500, 50)]]
write_ls(J(d, 'TKSUM'), ts)
rc, out = cob('USR510', {'TKSUM': J(d, 'TKSUM'), 'TOKUI': J(d, 'TOKUI'), 'URIGETU': J(d, 'URIGETU.txt')}, '202412\n')
open(J(d, 'USR510.log'), 'w').write('SYSIN=202412\n' + out + f'\nRC={rc}\n')
txt = open(J(d, 'URIGETU.txt'), encoding='utf-8').read()
lines = [l.rstrip() for l in txt.replace('\f', '\n').splitlines() if l.strip()]
rec(743, P, 'USR510-1', 'TKSUM: F00001 202411・202412、F00002 202412、F00009 202412、SYSIN=202412', '202412 の3行だけ', ' ／ '.join(lines),
    sum(1 for l in lines if l.strip()[:1] == 'F') == 3 and '9,000' not in txt, d)
rec(744, P, 'USR510-2', 'F00009（得意先ファイルにない）', '得意先名を空白', [l for l in lines if 'F00009' in l][0] if 'F00009' in txt else '出力なし', 'F00009' in txt and 'テスト' not in [l for l in lines if 'F00009' in l][0], d)
rec(745, P, 'USR510-3', '同上', '合計行: 件数4・売上3,500・税330・合計3,830', lines[-1] if lines else '', '3,500' in lines[-1] and '3,830' in lines[-1] and '330' in lines[-1], d)

# ---------------- USB900 消費税再計算 ----------------
P = 'USB900'
d = case_dir('USB900')
tks = [tokui('G00001')]; shs = [shohin('S00001', '0', 1005)]
jus = [juchu(1, '19970331', 'G00001', 'S00001', 1, 1005), juchu(2, '19970401', 'G00001', 'S00001', 1, 1005), juchu(3, '19970402', 'G00001', 'S00001', 1, 1005)]
usb100(d, tks, shs, jus)
raw = bytearray(open(J(d, 'URIAGE'), 'rb').read())
for i in (0, 1):  # 1件目(19970331)・2件目(19970401) の税率を 3 にする。3件目は 5 のまま
    raw[i * 64 + 44:i * 64 + 46] = b'03'
open(J(d, 'URIAGE'), 'wb').write(raw)
dump(d, 'URIAGE.decoded.txt', read_uriage(J(d, 'URIAGE')))
rc, out = cob('USB900', {'URIAGE': J(d, 'URIAGE'), 'URINEW': J(d, 'URINEW')})
open(J(d, 'USB900.log'), 'w').write(out + f'\nRC={rc}\n')
UN = read_uriage(J(d, 'URINEW')); dump(d, 'URINEW.decoded.txt', UN)
fn = lambda r: f"{r['date']} 税率{r['ritu']} 金額{r['kin']} 税額{r['zei']}"
rec(773, P, 'USB900-1', '19970401・税率3・金額1005', '税率5・税額 1005×5/100＝50（端数区分を見ない）', fn(UN[1]), UN[1]['ritu'] == '05' and UN[1]['zei'] == 50, d)
rec(774, P, 'USB900-2', '19970331・税率3／19970402・税率5', 'そのまま出力', fn(UN[0]) + ' ／ ' + fn(UN[2]), UN[0]['ritu'] == '03' and UN[2]['ritu'] == '05', d)

save('batch_results.json')
