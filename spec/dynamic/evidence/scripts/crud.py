#!/usr/bin/env python3
"""CRUD 図を実行で確かめる。
・画面／Java: PostgreSQL の log_statement=all のログを、操作ごとの目印 SQL で区切って集計する
・COBOL: pipeline.py を STRACE_DIR 付きで動かし、DD ファイルの open モードを集計する
出力: evidence/crud/crud_actual.json, *.sql.txt, *.strace"""
import os, re, json, subprocess, time, requests
from rules_web import psql, sess, B, WEB, EVD, J, java, dexec  # noqa
OUT = J(EVD, 'crud'); os.makedirs(OUT, exist_ok=True)
TAB = ['m_user', 'm_tokui', 'm_shohin', 't_juchu', 't_seikyu']


def mark(n):
    psql(f"SELECT 'CRUDMARK:{n}'")


def ops(sql):
    res = {}
    for st in sql:
        u = st.strip().upper()
        for t in TAB:
            if not re.search(r'\b' + t.upper() + r'\b', u):
                continue
            c = 'R' if u.startswith('SELECT') else 'C' if u.startswith('INSERT') else 'U' if u.startswith('UPDATE') else 'D' if u.startswith('DELETE') else ''
            if u.startswith('SELECT') and ' FROM ' + t.upper() not in u and 'JOIN ' + t.upper() not in u and ', ' + t.upper() not in u:
                continue
            res[t] = ''.join(sorted(set(res.get(t, '') + c), key='CRUD'.index))
    return res


since = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(time.time() - 2))
psql("DELETE FROM m_tokui WHERE tk_cd='Z00009'")
psql("INSERT INTO m_tokui VALUES ('Z00009','CRUD検証','','','','','99','1','1','31',0,'S999','0','20241201','20241201')")
s = requests.Session()
mark('LoginAction'); s.post(B + 'login.do', data={'userId': 'user01', 'password': 'usagi01'})
mark('TokuiSearchAction'); s.get(B + 'tokuiSearch.do', params={'tkCd': '1', 'tkNm': '', 'search': '1'})
mark('TokuiEditAction'); s.get(B + 'tokuiEdit.do', params={'tkCd': 'Z00009'}); s.get(B + 'tokuiEdit.do', params={'tkCd': 'Z00009', 'mode': 'update', 'tkNm': 'CRUD検証2', 'tel': '', 'simeKbn': '99', 'hasuKbn': '1', 'gendo': '0', 'tanto': 'S999'})
mark('JuchuInputAction'); s.get(B + 'juchuInput.do')
mark('JuchuConfirmAction'); r = s.post(B + 'juchuConfirm.do', data={'juchuYmd': '20241201', 'tkCd': 'Z00009', 'shCd': '200001', 'suryo': '1', 'juchuKbn': '1', 'biko': ''})
from rules_web import hidden
mark('JuchuRegistAction'); r = s.post(B + 'juchuRegist.do', data=hidden(r))
mark('JuchuInquiryAction'); s.get(B + 'juchuInquiry.do', params={'tkCd': 'Z00009', 'search': '1'})
mark('SeikyuInquiryAction'); s.get(B + 'seikyuInquiry.do', params={'tkCd': '100001', 'search': '1'})
mark('PIPELINE')
sd = J(OUT, 'strace'); os.makedirs(sd, exist_ok=True)
subprocess.run(['python3', J(EVD, 'scripts', 'pipeline.py'), J(EVD, 'batch', 'run_crud')], env=dict(os.environ, STRACE_DIR=sd), capture_output=True)
mark('END')
psql("DELETE FROM t_juchu WHERE tk_cd='Z00009'; DELETE FROM m_tokui WHERE tk_cd='Z00009'")
log = subprocess.run(['docker', 'compose', 'logs', '--no-color', '--since', since, 'db'], cwd=WEB, capture_output=True, text=True).stdout
# 複数行 SQL を連結
stm, cur = [], None
for line in log.splitlines():
    line = re.sub(r'^\S+\s+\|\s?', '', line)
    m = re.search(r'LOG:\s+(?:execute [^:]*|statement): (.*)', line)
    if m:
        cur = [m.group(1)]; stm.append(cur)
    elif cur is not None and not re.search(r'\b(LOG|DETAIL|ERROR|STATEMENT):', line):
        cur.append(line)
    else:
        cur = None
stm = [' '.join(x) for x in stm]
act, cur, groups = None, None, {}
for st in stm:
    m = re.search(r"CRUDMARK:(\w+)", st)
    if m:
        cur = m.group(1); groups.setdefault(cur, []); continue
    if cur and cur != 'END' and not st.upper().startswith(('SET ', 'BEGIN', 'COMMIT', 'SHOW', 'ROLLBACK')):
        groups[cur].append(st)
# パイプライン中の Java を分ける（JuchuExtract の後に SeikyuImport が来る。SeikyuImport は t_seikyu の DELETE から始まる）
pl = groups.pop('PIPELINE', [])
i = next((k for k, st in enumerate(pl) if st.upper().startswith('DELETE FROM T_SEIKYU')), len(pl))
groups['JuchuExtract'], groups['SeikyuImport'] = pl[:i], pl[i:]
res = {}
for k, v in groups.items():
    open(J(OUT, k + '.sql.txt'), 'w').write('\n'.join(v) + '\n')
    res[k] = ops(v)
# COBOL: strace
for f in sorted(os.listdir(sd)):
    pgm = f.split('.')[0]; r = {}
    for line in open(J(sd, f)):
        m = re.search(r'openat\([^,]+, "([^"]+)", ([A-Z_|]+)', line)
        if not m or '/run_crud/' not in m.group(1):
            continue
        name = os.path.basename(m.group(1)).replace('USAGI.PROD.', '').replace('.tmp', '')
        fl = m.group(2)
        c = 'R' if 'O_RDONLY' in fl else 'C' if 'O_CREAT' in fl or 'O_TRUNC' in fl else 'U'
        r[name] = ''.join(sorted(set(r.get(name, '') + c), key='CRUD'.index))
    res[pgm] = r
json.dump(res, open(J(OUT, 'crud_actual.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, v)
