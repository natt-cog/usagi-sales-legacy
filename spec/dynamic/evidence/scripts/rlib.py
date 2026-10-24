"""業務ルール検証の共通部品（固定長ファイルの組立て・COBOL 実行・結果記録）"""
import os, subprocess, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '../../../..'))
EVD = os.path.abspath(os.path.join(HERE, '..'))
RULES = os.path.join(EVD, 'rules')
BIN = os.environ.get('USAGI_BIN', os.path.expanduser('~/work/bin'))
RESULTS = []


def x(s, n):
    b = s.encode('utf-8')[:n]
    while True:
        try:
            b.decode('utf-8'); break
        except UnicodeDecodeError:
            b = b[:-1]
    return b + b' ' * (n - len(b))


def n(v, w):
    return str(v).zfill(w).encode()


def tokui(cd, sime='99', hasu='1', nm='テスト得意先', del_='0'):
    return x(cd, 6) + x(nm, 40) + n(int(sime), 2) + hasu.encode() + b'1' + b'31' + del_.encode() + b' ' * 47


def shohin(cd, zei='0', tanka=100, nm='テスト商品'):
    return x(cd, 6) + x(nm, 40) + zei.encode() + n(tanka, 7) + b' ' * 26


def juchu(no, ymd, tk, sh, suryo, tanka, kbn='1', kin=None):
    kin = suryo * tanka * (-1 if kbn == '2' else 1) * (0 if kbn == '3' else 1) if kin is None else kin
    return (n(no, 8) + ymd.encode() + x(tk, 6) + x(sh, 6) + n(suryo, 7) + n(tanka, 7) + kbn.encode()
            + (b'-' if kin < 0 else b'+') + n(abs(kin), 11) + b' ' * 25)


def nyukin(no, ymd, tk, kin, tesu=0, kbn='1', tekiyo='テスト入金'):
    return n(no, 6) + ymd.encode() + x(tk, 6) + n(kin, 9) + kbn.encode() + n(tesu, 5) + x(tekiyo, 25)


def write_ls(path, recs):
    open(path, 'wb').write(b''.join(r + b'\n' for r in recs))


def comp3(b, scale=0):
    h = b.hex()
    v = int(h[:-1])
    return -v if h[-1] in 'bd' else v


def read_uriage(path):
    d = open(path, 'rb').read()
    out = []
    for i in range(0, len(d), 64):
        r = d[i:i + 64]
        out.append(dict(tk=r[0:6].decode(), date=r[6:14].decode(), juno=r[14:22].decode(), sh=r[22:28].decode(),
                        kbn=r[28:29].decode(), suryo=comp3(r[29:33]), tanka=comp3(r[33:37]), kin=comp3(r[37:43]),
                        zeikbn=r[43:44].decode(), ritu=r[44:46].decode(), zei=comp3(r[46:51])))
    return out


def sls(s):
    return int(s)


def read_seikyu(path):
    out = []
    for l in open(path, 'rb').read().split(b'\n'):
        if not l.strip():
            continue
        s = l.decode('latin-1')
        f = lambda p: int(s[p:p + 12])
        out.append(dict(no=s[0:12], tk=s[12:18], ym=s[18:24], frm=s[24:32], to=s[32:40], kensu=int(s[40:45]),
                        uriage=f(45), zei=f(57), seikyu=f(69), nyukin=f(81), kesi=s[93], z10t=f(94), z10=f(106),
                        z8t=f(118), z8=f(130), sot=f(142), so=f(154)))
    return out


def read_kesikomi(path):
    out = []
    for l in open(path, 'rb').read().split(b'\n'):
        if not l.strip():
            continue
        s = l.decode('utf-8', 'replace')
        out.append(dict(nyno=s[0:6], date=s[6:14], tk=s[14:20], skno=s[20:32], kin=int(s[32:41]), kbn=s[41]))
    return out


def read_tksum(path):
    out = []
    for l in open(path, 'rb').read().split(b'\n'):
        if not l.strip():
            continue
        s = l.decode()
        out.append(dict(tk=s[0:6], ym=s[6:12], kensu=int(s[12:17]), kin=int(s[17:29]), zei=int(s[29:39]), gokei=int(s[39:51])))
    return out


def cob(pgm, dd, sysin=None, cwd=None):
    env = dict(os.environ, COB_LIBRARY_PATH=BIN)
    for k, v in dd.items():
        env['DD_' + k] = v
    r = subprocess.run([os.path.join(BIN, pgm)], env=env, input=sysin, capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr).strip()


def case_dir(cid):
    d = os.path.join(RULES, cid)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    return d


def rec(row, prog, cid, inp, exp, act, ok, evidence, note=''):
    RESULTS.append(dict(row=row, prog=prog, id=cid, input=inp, expected=exp, actual=act,
                        result='一致' if ok else '不一致', evidence=os.path.relpath(evidence, os.path.dirname(EVD)) if evidence else '',
                        note=note))
    print(f"[{'OK' if ok else 'NG'}] {row} {prog} {cid}: {act}")


def save(name):
    p = os.path.join(RULES, name)
    json.dump(RESULTS, open(p, 'w'), ensure_ascii=False, indent=1)
