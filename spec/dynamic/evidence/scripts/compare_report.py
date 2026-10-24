#!/usr/bin/env python3
"""帳票の比較。改ページ（\\f）の位置の差は無視し、空行と行末の空白を除いた行の並びで比べる。
サンプルの txt は改ページ位置で前ページ最終行と次ページ先頭行が連結されているため、
連続する2個以上の空白で始まる見出し「請　求　書」等の手前でも分割する。"""
import sys, re, difflib
def norm(path):
    t = open(path, encoding='utf-8').read().replace('\f', '\n')
    t = re.sub(r'(\S) {20,}(請　求　書|  月次売上表)', r'\1\n                              \2', t)
    return [l.rstrip() for l in t.split('\n') if l.strip()]
a, b = norm(sys.argv[1]), norm(sys.argv[2])
d = list(difflib.unified_diff(b, a, 'サンプル:' + sys.argv[2], '実行結果:' + sys.argv[1], lineterm=''))
print('\n'.join(d) if d else f'一致（{len(a)} 行）')
sys.exit(1 if d else 0)
