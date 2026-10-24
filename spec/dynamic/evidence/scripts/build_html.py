#!/usr/bin/env python3
"""spec/dynamic/index.html（動的仕様書）を作る。build_xlsx.py の後に実行する。
01 プログラム仕様書は Excel の各行（判定付き）から、それ以外は spec/md/*.md を描画して表の行・箇条書きごとに判定を付ける。"""
import os, re, json, html, glob
import markdown
from bs4 import BeautifulSoup
from verdicts import *
HERE = os.path.dirname(os.path.abspath(__file__)); DYN = os.path.abspath(os.path.join(HERE, '..', '..')); SPEC = os.path.dirname(DYN)
J = os.path.join; esc = html.escape
V = json.load(open(J(DYN, 'evidence', 'verdicts.json')))
rules = sorted([x for f in ('batch_results.json', 'web_results.json') for x in json.load(open(J(DYN, 'evidence', 'rules', f)))], key=lambda x: x['row'])
CLS = {EXEC: 'ex', SRC: 'src', EST: 'est', NOT: 'nv'}
mdcnt = {}


def badge(v, why='', ev=''):
    s = f'<span class="b {CLS[v]}">{v}</span>'
    if why: s += f' <span class="why">{esc(why)}</span>'
    if ev: s += f' <a class="ev" href="{esc(ev)}" target="_blank">エビデンス</a>'
    return s


def shots(names):
    return '<div class="shots">' + ''.join(f'<figure><a href="evidence/screens/{n}" target="_blank"><img loading="lazy" src="evidence/screens/{n}"></a><figcaption>{n}</figcaption></figure>' for n in names) + '</div>'


def video():
    return f'<figure class="vid"><video controls preload="metadata" src="{VIDEO}"></video><figcaption>操作動画：受注入力→確認→登録→受注照会→夜間バッチ（JCL 相当を実行）→請求照会（<a href="{VIDEO}">mp4</a>、ジョブログ <a href="evidence/batch/run_e2e.log">run_e2e.log</a>）</figcaption></figure>'


def judge_md(text, ctx):
    m = re.match(r'\s*(Q\d\d|D\d\d|U\d\d|M\d\d)\b', text)
    if m:
        k = m.group(1)
        if k in V['questions']: x = V['questions'][k]; return x['verdict'], x['why'], x['ev']
        if k in V['diff']: x = V['diff'][k]; return x['verdict'], x['why'], x['ev']
        if k in U: return U[k][0], '', U[k][1]
        if k in M: return M[k]
    m = re.match(r'\s*(P\d\d)\b', text)
    if m and m.group(1) in V['program_list']:
        x = V['program_list'][m.group(1)]; return x['verdict'], x['why'], x['ev']
    m = re.match(r'\s*(EV\d\d)\b', text)
    if m:
        return EXEC, '業務イベントを実行（画面操作・夜間バッチ）', EV_LOGS.get(m.group(1), VIDEO)
    for key, v, why, ev in MD_RULES:
        if key in text:
            if v == EXEC and '推定' in text and key not in ('締日エラー',):
                return EST, 'この記述の推定部分は実行で確かめられない（関連する動作は実行で確認）', ev
            return v, why, ev
    if '推定' in text: return EST, '静的版の推定のまま', ''
    return SRC, '', ''


MDFIX = {'F90': '締日エラーの得意先', 'F91': 'Q03', 'F92': 'M01 NYKREC.cpy 復元案', 'F93': 'M07 ジョブ順序', 'F94': 'U01'}


def render_md(path, docid):
    src = open(path).read()
    src = re.sub(r'\A# .*\n', '', src)
    h = markdown.markdown(src, extensions=['tables', 'fenced_code'])
    sp = BeautifulSoup(h, 'html.parser')
    for code in sp.select('pre > code.language-mermaid'):
        pre = code.parent; pre['class'] = 'mermaid'; pre.string = code.get_text()
    cur = ''
    for el in sp.find_all(['h2', 'h3', 'table', 'li', 'pre']):
        if el.name == 'h2':
            cur = el.get_text(); el['id'] = docid + '-' + re.sub(r'\W+', '', cur.split()[0]) if cur.split() else ''
            m = re.match(r'(EV\d\d)', cur)
            if docid == 'd03' and m:
                add = ''
                if m.group(1) in EV_SCREENS: add += shots(EV_SCREENS[m.group(1)])
                if m.group(1) in ('EV03', 'EV05', 'EV06', 'EV07', 'EV08', 'EV09'): add += video() if m.group(1) in ('EV03', 'EV08') else f'<p>夜間バッチの実行ログ：<a href="{EV_LOGS[m.group(1)]}">{EV_LOGS[m.group(1)]}</a>（操作動画の後半でも実行）</p>'
                el.insert_after(BeautifulSoup(add, 'html.parser'))
            continue
        if el.name == 'pre':
            if 'mermaid' in (el.get('class') or []):
                m = re.match(r'(P\d\d|EV\d\d)', cur)
                if m and m.group(1).startswith('P'): v, why, ev = EXEC, '処理の流れを境界値試験で通した（分岐は業務ルール検証結果を参照）', PEV.get(m.group(1), '')
                elif m: v, why, ev = EXEC, '業務イベントを実行し、SQL ログ・ジョブログで呼出し順を確認', EV_LOGS.get(m.group(1), VIDEO)
                else: v, why, ev = judge_md(cur, docid)
                mdcnt[v] = mdcnt.get(v, 0) + 1
                el.insert_after(BeautifulSoup(f'<p class="vline">図の判定: {badge(v, why, ev)}</p>', 'html.parser'))
            continue
        if el.name == 'table':
            th = sp.new_tag('th'); th.string = '判定'
            if el.thead: el.thead.tr.append(th)
            for tr in el.select('tbody tr'):
                v, why, ev = judge_md(tr.get_text(' '), docid)
                mdcnt[v] = mdcnt.get(v, 0) + 1
                td = sp.new_tag('td'); td['class'] = 'vcell'; td.append(BeautifulSoup(badge(v, why, ev), 'html.parser')); tr.append(td)
            continue
        if el.name == 'li' and not el.find('li'):
            v, why, ev = judge_md(el.get_text(' '), docid)
            mdcnt[v] = mdcnt.get(v, 0) + 1
            el.append(BeautifulSoup(' ' + badge(v, why, ev), 'html.parser'))
    for f in V['fixes']:
        if f['id'] in MDFIX and f['doc'].startswith(docid[1:3]):
            for el in sp.find_all(['tr', 'li', 'h2']):
                if MDFIX[f['id']] in el.get_text():
                    box = f'<div class="fix"><b>修正 {f["id"]}（{f["kind"]}）</b> 修正前：{esc(f["before"])}<br>修正後：{esc(f["after"])} <a href="{f["evidence"]}">エビデンス</a></div>'
                    (el.find_parent('table') or el).insert_after(BeautifulSoup(box, 'html.parser')); break
    return str(sp)


def program_spec():
    out = ['<p>Excel 版（<a href="設計書.xlsx">設計書.xlsx</a>）と同じ行に判定を付けた。黄色は動的版で直した記述。</p>']
    by = {}
    for r, x in V['program_spec'].items(): by.setdefault(x['pid'], []).append((int(r), x))
    for pid in sorted(by):
        rows_ = sorted(by[pid]); x0 = rows_[0][1]
        pl = V['program_list'][pid]
        out.append(f'<h3 id="d01-{pid}">{pid} {esc(x0["name"])}（{esc(x0["prog"])}）</h3><p>{badge(pl["verdict"], pl["why"], pl["ev"])}</p>')
        if pid in SCREENS: out.append('<p><b>画面のスクリーンショット</b></p>' + shots(SCREENS[pid]))
        for kubun in ('概要', '業務ルール', '入力レコード', '出力レコード', '入力例', '出力例'):
            rr = [(r, x) for r, x in rows_ if x['kubun'] == kubun]
            if not rr: continue
            out.append(f'<details {"open" if kubun in ("概要", "業務ルール") else ""}><summary>{kubun}（{len(rr)}行）</summary><table><tr><th>行</th><th>対象／ルール</th><th>項目／条件</th><th>内容／結果</th><th>根拠（静的）</th><th>判定</th><th>判定の根拠</th></tr>')
            for r, x in rr:
                fixed = any(f'Excel {r}行' in f['where'] for f in V['fixes'])
                out.append(f'<tr{" class=fixed" if fixed else ""}><td>{r}</td><td>{esc(x["target"])}</td><td>{esc(x["item"])}</td><td>{esc(x["body"] or "").replace(chr(10), "<br>")}</td><td>{esc(x["src"] or "")}</td>'
                           f'<td>{badge(x["verdict"])}</td><td>{esc(x["why"])}{" <a class=ev target=_blank href=" + chr(34) + esc(x["ev"]) + chr(34) + ">エビデンス</a>" if x["ev"] else ""}</td></tr>')
            out.append('</table></details>')
    return '\n'.join(out)


docs = [(os.path.basename(p)[:2], os.path.basename(p)[3:-3], p) for p in sorted(glob.glob(J(SPEC, 'md', '*.md')))]
body = []; toc = []
for no, title, p in docs:
    did = 'd' + no
    toc.append(f'<li><a href="#{did}">{no} {esc(title)}</a></li>')
    if no == '01':
        content = program_spec()
    else:
        content = render_md(p, did)
        if no == '03': content = video() + content
        if no == '06':
            content += '<h3>実測した CRUD（SQL ログ・strace）</h3><table><tr><th>プログラム</th><th>判定</th><th>実測</th></tr>' + ''.join(
                f'<tr><td>{esc(k)}</td><td>{badge(x["verdict"])}</td><td>{esc(x["why"])} <a class=ev href="{x["ev"]}">エビデンス</a></td></tr>' for k, x in V['crud'].items()) + '</table>'
    body.append(f'<section id="{did}"><h2>{no} {esc(title)}</h2><p class="static">静的版：<a href="../md/{os.path.basename(p)}">spec/md/{os.path.basename(p)}</a></p>{content}</section>')
# 集計（Excel の行＋Markdown のみの記述）
cnt = dict(V['count'])
for k, v in mdcnt.items(): cnt[k] = cnt.get(k, 0) + v
tot = sum(cnt.values())
fx = V['fixes']; nk = lambda k: sum(f['kind'] == k for f in fx)
summary = f'''<section id="summary"><h2>結果の要約</h2>
<table class="sum"><tr><th>判定</th><th>件数</th><th>割合</th><th>内訳（Excel 行／Markdown の記述）</th></tr>''' + ''.join(
    f'<tr><td>{badge(k)}</td><td>{cnt.get(k, 0)}</td><td>{cnt.get(k, 0) / tot:.1%}</td><td>{V["count"].get(k, 0)}／{mdcnt.get(k, 0)}</td></tr>' for k in (EXEC, SRC, EST, NOT)) + f'''
<tr><th>合計</th><th>{tot}</th><th>100%</th><th>{sum(V["count"].values())}／{sum(mdcnt.values())}</th></tr></table>
<ul><li>静的仕様書の誤り：<b>{nk("誤り")}件</b>、不正確な記述：<b>{nk("不正確")}件</b>（いずれも修正）。推定・値不明を実行結果で確定：{nk("推定→確定")}件。<a href="#fixes">修正箇所一覧</a>は計 {len(fx)} 件</li>
<li>業務ルール {len(set(x["row"] for x in rules))} 行すべてに境界値の入力を作って実行（{len(rules)} ケース）：設計書どおり {sum(x["result"] == "一致" for x in rules)} ケース（<a href="#rules">業務ルール検証結果</a>）</li>
<li><a href="#issues">要確認の挙動</a>：{len(V["issues"])} 件</li></ul>
<h3>実行した方法</h3><ul>
<li>画面：<code>web/docker-compose.yml</code> で Tomcat 8.5＋PostgreSQL 9.6 を起動（http://localhost:8080/usagi/）。全画面のスクリーンショット：<a href="#d01">01 プログラム仕様書</a>の各画面の項</li>
<li>COBOL：GnuCOBOL 3.1.2 で <code>cobc -fassign-clause=ibm</code>。USB300 は NYKREC.cpy が欠けておりコンパイル不可 → 復元案を補ってコンパイル・実行（<a href="evidence/logs/compile.log">compile.log</a>、<a href="evidence/restore/NYKREC.cpy">NYKREC.cpy</a>）</li>
<li>JCL：USJ010〜USJ040 を読み <a href="evidence/scripts/pipeline.py">pipeline.py</a> で組み立て（FTP→docker compose exec、SORT→Python、DD→環境変数 DD_xxx、SYSIN→標準入力）。実データ（受注757・入金650）で完走：<a href="evidence/batch/run_202412.log">run_202412.log</a></li>
<li>帳票：請求書 202412／202402、月次売上表 202403 を既存サンプルと比較し一致（<a href="evidence/batch/compare_samples.txt">compare_samples.txt</a>）</li>
<li>起動・コンパイルできなかったもの：USB300（NYKREC.cpy 欠落、復元で解消）のみ。z/OS 固有の動作（JCL の COND、FTP の文字コード変換）は確かめられないため「未検証」</li>
<li>試験スクリプト：<a href="evidence/scripts/">evidence/scripts/</a>（rules_batch.py・rules_web.py・examples.py・crud.py・capture.py・video.py・build_*.py）</li></ul>
<p>判定の付け方：実行で確認＝実行結果（ログ・画面・出力ファイル）で記述どおりと確かめた／ソースで確認＝実行では観測できずソースで確かめた／推定＝静的版の推定のまま／未検証＝確かめられなかった（理由を記載）。</p></section>'''
rules_html = '<section id="rules"><h2>業務ルール検証結果（入力→期待結果→実際の結果）</h2><table><tr><th>行</th><th>プログラム</th><th>ケース</th><th>入力</th><th>期待結果（設計書から）</th><th>実際の結果</th><th>結果</th><th>エビデンス</th></tr>' + ''.join(
    f'<tr><td>{x["row"]}</td><td>{esc(x["prog"])}</td><td>{esc(x["id"])}</td><td>{esc(x["input"])}</td><td>{esc(x["expected"])}</td><td>{esc(x["actual"])}{"<br><i>" + esc(x["note"]) + "</i>" if x["note"] else ""}</td><td>{x["result"]}</td><td><a href="{esc(x["evidence"])}">開く</a></td></tr>' for x in rules) + '</table></section>'
fix_html = '<section id="fixes"><h2>修正箇所一覧</h2><table><tr><th>No</th><th>種類</th><th>設計書・箇所</th><th>修正前</th><th>修正後</th><th>理由</th><th>エビデンス</th></tr>' + ''.join(
    f'<tr><td>{f["id"]}</td><td>{f["kind"]}</td><td>{esc(f["doc"])}<br>{esc(f["where"])}</td><td>{esc(f["before"])}</td><td>{esc(f["after"])}</td><td>{esc(f["reason"])}</td><td><a href="{esc(f["evidence"])}">開く</a></td></tr>' for f in fx) + '</table></section>'
iss_html = '<section id="issues"><h2>要確認の挙動（実行して見つかったバグ・業務上おかしい動き）</h2><table><tr><th>No</th><th>挙動</th><th>内容（実行結果）</th><th>確認事項</th><th>エビデンス</th></tr>' + ''.join(
    f'<tr><td>{i}</td><td>{esc(t)}</td><td>{esc(d)}</td><td>{q}</td><td><a href="{esc(e)}">開く</a></td></tr>' for i, t, d, q, e in V['issues']) + '</table></section>'
evl = []
for root, ds, fs in os.walk(J(DYN, 'evidence')):
    ds.sort()
    for f in sorted(fs):
        rel = os.path.relpath(J(root, f), DYN); evl.append(f'<li><a href="{esc(rel)}">{esc(rel)}</a></li>')
ev_html = f'<section id="evidence"><h2>エビデンス一覧</h2><details><summary>{len(evl)} ファイル</summary><ul class="evl">{"".join(evl)}</ul></details></section>'
CSS = '''body{margin:0;font-family:"Noto Sans CJK JP","Hiragino Sans",Meiryo,sans-serif;font-size:14px;color:#222}
nav{position:fixed;top:0;left:0;bottom:0;width:250px;overflow:auto;background:#1f3b57;color:#fff;padding:12px;box-sizing:border-box}
nav a{color:#dfe9f3;text-decoration:none}nav ul{padding-left:16px}nav li{margin:4px 0}main{margin-left:250px;padding:16px 28px;max-width:1500px}
h2{border-left:6px solid #1f3b57;padding-left:8px;margin-top:40px}table{border-collapse:collapse;margin:8px 0;width:100%}th,td{border:1px solid #bbb;padding:3px 6px;vertical-align:top}
th{background:#ddebf7}.b{display:inline-block;padding:1px 6px;border-radius:3px;font-size:12px;white-space:nowrap}.ex{background:#c6efce}.src{background:#ddebf7}.est{background:#ffeb9c}.nv{background:#f4cccc}
.why{color:#555;font-size:12px}.ev{font-size:12px}tr.fixed td{background:#fff2cc}.fix{background:#fff2cc;border:1px solid #e0b000;padding:6px;margin:6px 0}
.shots{display:flex;flex-wrap:wrap;gap:10px}.shots img{width:420px;border:1px solid #999}figure{margin:4px}figcaption{font-size:12px;color:#555}
video{width:900px;max-width:100%;border:1px solid #999}.static{font-size:12px;color:#666}details summary{cursor:pointer;font-weight:bold;margin:6px 0}.sum{width:auto}.evl{columns:2;font-size:12px}'''
toc_html = '<nav><b>動的仕様書</b><ul><li><a href="#summary">結果の要約</a></li>' + ''.join(toc) + '<li><a href="#rules">業務ルール検証結果</a></li><li><a href="#fixes">修正箇所一覧</a></li><li><a href="#issues">要確認の挙動</a></li><li><a href="#evidence">エビデンス一覧</a></li></ul><p style="font-size:12px">Excel 版：<a href="設計書.xlsx">設計書.xlsx</a><br>静的版：<a href="../設計書.xlsx">spec/設計書.xlsx</a></p></nav>'
page = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>販売管理システム 動的仕様書</title><style>{CSS}</style>
<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";mermaid.initialize({{startOnLoad:true}});</script></head>
<body>{toc_html}<main><h1>販売管理システム（usagi-sales-legacy）動的仕様書</h1><p>静的仕様書（spec/md・spec/設計書.xlsx）の記述を、システムを実際に動かして確かめた結果。静的版は変更していない。</p>
{summary}{"".join(body)}{rules_html}{fix_html}{iss_html}{ev_html}</main></body></html>'''
open(J(DYN, 'index.html'), 'w').write(page)
print(cnt, tot, {k: f'{v / tot:.1%}' for k, v in cnt.items()}, 'md', mdcnt)
