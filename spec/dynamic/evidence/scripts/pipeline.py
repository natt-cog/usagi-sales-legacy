#!/usr/bin/env python3
"""夜間バッチ（USJ010〜USJ040）を JCL どおりの順序で GnuCOBOL 上で実行する。

JCL の各ステップの置き換え:
  FTP get/put        → docker compose exec でコンテナの /work と読み書き
  SORT FIELDS=(...)  → Python でバイト位置のキーで安定ソート（CH,A＝バイト順）
  EXEC PGM=USBxxx    → cobc でコンパイルした実行形式。DD は環境変数 DD_<DD名>
  SYSIN DD *         → 標準入力
使い方: pipeline.py <出力ディレクトリ> [USJ020の SYSIN] [USJ040の SYSIN]
"""
import os, subprocess, sys, shutil, json, time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
BIN = os.environ.get('USAGI_BIN', os.path.expanduser('~/work/bin'))
WEB = os.path.join(REPO, 'web')
CP = '/usr/local/tomcat/webapps/usagi/WEB-INF/classes:/usr/local/tomcat/webapps/usagi/WEB-INF/lib/*'


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)


def container_java(cls, *args):
    return sh(['docker', 'compose', 'exec', '-T', 'web', 'java', '-cp', CP, cls, *args], cwd=WEB)


def container_get(path, dest):
    r = subprocess.run(['docker', 'compose', 'exec', '-T', 'web', 'cat', path], cwd=WEB, capture_output=True)
    open(dest, 'wb').write(r.stdout)
    return r.returncode


def container_put(src, path):
    r = subprocess.run(['docker', 'compose', 'exec', '-T', 'web', 'sh', '-c', f'cat > {path}'], cwd=WEB,
                       input=open(src, 'rb').read(), capture_output=True)
    return r.returncode


def sort_file(src, dst, keys):
    """keys: [(start(1起点), len)] すべて CH,A"""
    recs = [l for l in open(src, 'rb').read().split(b'\n') if l]
    recs.sort(key=lambda r: tuple(r[s - 1:s - 1 + n] for s, n in keys))
    open(dst, 'wb').write(b''.join(r + b'\n' for r in recs))
    return len(recs)


def run_pgm(pgm, dd, out, sysin=None):
    env = dict(os.environ, COB_LIBRARY_PATH=BIN)
    for k, v in dd.items():
        env['DD_' + k] = v
    cmd = [os.path.join(BIN, pgm)]
    if os.environ.get('STRACE_DIR'):  # CRUD 確認用: ファイルの open/unlink を記録
        cmd = ['strace', '-f', '-e', 'trace=openat,unlink,rename', '-o', os.path.join(os.environ['STRACE_DIR'], pgm + '.strace')] + cmd
    r = subprocess.run(cmd, env=env, input=sysin, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    out = os.path.abspath(sys.argv[1])
    usj020_sysin = sys.argv[2] if len(sys.argv) > 2 else '20241231201401'
    usj040_sysin = sys.argv[3] if len(sys.argv) > 3 else '202412'
    nyukin = os.environ.get('NYUKIN', os.path.join(REPO, 'batch/data/NYUKIN.DAT'))
    os.makedirs(out, exist_ok=True)
    ds = lambda n: os.path.join(out, n)
    log = []

    def step(job, name, rc, msg):
        log.append({'job': job, 'step': name, 'rc': rc, 'out': msg})
        print(f'{job:7} {name:28} RC={rc}  {msg}')

    r = container_java('jp.co.usagi.batch.JuchuExtract', '/work')
    step('(Web)', 'JuchuExtract /work', r.returncode, (r.stdout + r.stderr).strip())
    # USJ010
    rcs = [container_get('/work/' + f, ds('USAGI.PROD.' + f[:-4])) for f in ('TOKUI.DAT', 'SHOHIN.DAT', 'JUCHU.DAT')]
    step('USJ010', 'STEP005 FTP get', max(rcs), 'TOKUI/SHOHIN/JUCHU を受信')
    n = sort_file(ds('USAGI.PROD.JUCHU'), ds('JUCHSRT.tmp'), [(17, 6), (9, 8), (1, 8)])
    step('USJ010', 'STEP010 SORT', 0, f'{n} 件 FIELDS=(17,6,CH,A,9,8,CH,A,1,8,CH,A)')
    rc, m = run_pgm('USB100', {'JUCHSRT': ds('JUCHSRT.tmp'), 'TOKUI': ds('USAGI.PROD.TOKUI'),
                               'SHOHIN': ds('USAGI.PROD.SHOHIN'), 'URIAGE': ds('USAGI.PROD.URIAGE')}, out)
    step('USJ010', 'STEP020 USB100', rc, m)
    os.remove(ds('JUCHSRT.tmp'))  # DISP=(OLD,DELETE)
    # USJ020
    rc, m = run_pgm('USB200', {'TOKUI': ds('USAGI.PROD.TOKUI'), 'URIAGE': ds('USAGI.PROD.URIAGE'),
                               'SEIKYU': ds('USAGI.PROD.SEIKYU')}, out, usj020_sysin + '\n')
    step('USJ020', 'STEP010 USB200 SYSIN=' + usj020_sysin, rc, m)
    # USJ030
    shutil.copy(nyukin, ds('USAGI.PROD.NYUKIN'))
    n = sort_file(ds('USAGI.PROD.NYUKIN'), ds('NYUKSRT.tmp'), [(15, 6), (7, 8), (1, 6)])
    step('USJ030', 'STEP010 SORT', 0, f'{n} 件 FIELDS=(15,6,CH,A,7,8,CH,A,1,6,CH,A)')
    rc020, m = run_pgm('USB300', {'NYUKSRT': ds('NYUKSRT.tmp'), 'SEIKYU': ds('USAGI.PROD.SEIKYU'),
                                  'SKKEKKA': ds('USAGI.PROD.SKKEKKA'), 'KESIKOMI': ds('USAGI.PROD.KESIKOMI')}, out)
    step('USJ030', 'STEP020 USB300', rc020, m)
    os.remove(ds('NYUKSRT.tmp'))
    if rc020 == 0:  # COND=(0,NE,STEP020)
        step('USJ030', 'STEP030 FTP put', container_put(ds('USAGI.PROD.SKKEKKA'), '/work/SKKEKKA.DAT'), '/work/SKKEKKA.DAT')
        r = container_java('jp.co.usagi.batch.SeikyuImport', '/work/SKKEKKA.DAT')
        step('(Web)', 'SeikyuImport', r.returncode, (r.stdout + r.stderr).strip())
    else:
        step('USJ030', 'STEP030 FTP put', 'SKIP', 'COND=(0,NE,STEP020) で実行しない')
    # USJ040
    rc, m = run_pgm('USB400', {'URIAGE': ds('USAGI.PROD.URIAGE'), 'TKSUM': ds('USAGI.PROD.TKSUM')}, out)
    step('USJ040', 'STEP010 USB400', rc, m)
    rc, m = run_pgm('USR500', {'SKKEKKA': ds('USAGI.PROD.SKKEKKA'), 'URIAGE': ds('USAGI.PROD.URIAGE'),
                               'TOKUI': ds('USAGI.PROD.TOKUI'), 'SEIKYUSH': ds('SEIKYUSH.txt')}, out, usj040_sysin + '\n')
    step('USJ040', 'STEP020 USR500 SYSIN=' + usj040_sysin, rc, m)
    rc, m = run_pgm('USR510', {'TKSUM': ds('USAGI.PROD.TKSUM'), 'TOKUI': ds('USAGI.PROD.TOKUI'),
                               'URIGETU': ds('URIGETU.txt')}, out, usj040_sysin + '\n')
    step('USJ040', 'STEP030 USR510 SYSIN=' + usj040_sysin, rc, m)
    json.dump(log, open(ds('joblog.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
