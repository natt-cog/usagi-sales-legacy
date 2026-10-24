#!/usr/bin/env python3
"""全画面のスクリーンショットを撮る（playwright headless）。出力: evidence/screens/*.png"""
import os, glob
from playwright.sync_api import sync_playwright
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'screens')
B = 'http://localhost:8080/usagi/'
EXE = glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-1248/chrome-linux*/chrome'))[0]
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=EXE)
    pg = br.new_page(viewport={'width': 1280, 'height': 800}, locale='ja-JP')
    shot = lambda n: pg.screenshot(path=os.path.join(OUT, n + '.png'), full_page=True)
    pg.goto(B + 'login.jsp'); shot('01_login')
    pg.fill('input[name=userId]', 'user01'); pg.fill('input[name=password]', 'xxxx'); pg.click('input[type=submit]'); shot('01_login_error')
    pg.fill('input[name=userId]', 'user01'); pg.fill('input[name=password]', 'usagi01'); pg.click('input[type=submit]'); shot('02_menu')
    pg.goto(B + 'tokuiSearch.do'); shot('03_tokui_search')
    pg.goto(B + 'tokuiSearch.do?tkCd=1000&tkNm=&search=1'); shot('03_tokui_search_result')
    pg.goto(B + 'tokuiEdit.do?tkCd=100001'); shot('04_tokui_edit')
    pg.goto(B + 'juchuInput.do'); shot('05_juchu_input')
    pg.fill('input[name=juchuYmd]', '2024/12/01'); pg.click('input[type=submit]'); shot('05_juchu_input_error')
    pg.fill('input[name=juchuYmd]', '20241215'); pg.fill('input[name=tkCd]', '100001'); pg.select_option('select[name=shCd]', index=1)
    pg.fill('input[name=suryo]', '50'); pg.click('input[type=submit]'); shot('06_juchu_confirm')
    pg.goto(B + 'juchuInquiry.do'); shot('08_juchu_inquiry')
    pg.goto(B + 'juchuInquiry.do?tkCd=100001&no=&fromYmd=20241101&toYmd=20241231&search=1'); shot('08_juchu_inquiry_result')
    pg.goto(B + 'seikyuInquiry.do'); shot('09_seikyu_inquiry')
    pg.goto(B + 'seikyuInquiry.do?tkCd=100001&no=&fromYm=202401&toYm=202501&search=1'); shot('09_seikyu_inquiry_result')
    pg.goto(B + 'seikyuInquiry.do?search=1'); shot('09_seikyu_inquiry_error')
    br.close()
print(sorted(os.listdir(OUT)))
