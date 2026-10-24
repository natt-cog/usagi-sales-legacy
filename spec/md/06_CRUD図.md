# 06 CRUD図（プログラム／画面 × テーブル・ファイル）

> 凡例：根拠は「ファイル名:行番号」。パスは省略形（例 USB100.cbl＝batch/cobol/USB100.cbl、JuchuRegistAction.java＝web/src/jp/co/usagi/sales/action/JuchuRegistAction.java、02_data.sql＝web/sql/02_data.sql、旧仕様書.xlsx＝docs/旧仕様書.xlsx）。「推定」と書いたものはコードから確定できない記述で、理由を併記する。

C=作成（INSERT・OPEN OUTPUT・FTP 受信）、R=参照、U=更新、D=削除（DELETE・DISP=DELETE の一時ファイル）。USB110/USB210 はファイルを持たない（パラメタのみ）。

## テーブル・ファイル一覧

| 名前 | 種別 | 内容 | 根拠 |
|---|---|---|---|
| m_user | テーブル | 利用者 | 01_ddl.sql:2-8 |
| m_tokui | テーブル | 得意先 | 01_ddl.sql:9-25 |
| m_shohin | テーブル | 商品 | 01_ddl.sql:26-35 |
| t_juchu | テーブル | 受注 | 01_ddl.sql:36-52 |
| t_seikyu | テーブル | 請求（取込） | 01_ddl.sql:53-72 |
| TOKUI | 固定長100 | /work/TOKUI.DAT ⇔ USAGI.PROD.TOKUI | JuchuExtract.java:19, USJ010.jcl:17 |
| SHOHIN | 固定長80 | /work/SHOHIN.DAT ⇔ USAGI.PROD.SHOHIN | USJ010.jcl:18 |
| JUCHU | 固定長80 | /work/JUCHU.DAT ⇔ USAGI.PROD.JUCHU | USJ010.jcl:19 |
| JUCHSRT | 一時80 | &&JUCHSRT | USJ010.jcl:25 |
| URIAGE | 固定長64 | USAGI.PROD.URIAGE | USJ010.jcl:36 |
| SEIKYU | 固定長170 | USAGI.PROD.SEIKYU | USJ020.jcl:16 |
| NYUKIN | 固定長60 | USAGI.PROD.NYUKIN（batch/data/NYUKIN.DAT） | USJ030.jcl:14 |
| NYUKSRT | 一時60 | &&NYUKSRT | USJ030.jcl:15 |
| SKKEKKA | 固定長170 | USAGI.PROD.SKKEKKA ⇔ /work/SKKEKKA.DAT | USJ030.jcl:25,33 |
| KESIKOMI | 固定長80 | USAGI.PROD.KESIKOMI | USJ030.jcl:26 |
| TKSUM | 固定長60 | USAGI.PROD.TKSUM | USJ040.jcl:15 |
| URINEW | 固定長64 | DD 定義なし | USB900.cbl:23 |
| SEIKYUSH | 帳票 | 請求書 SYSOUT=(B,,SK01) | USJ040.jcl:22 |
| URIGETU | 帳票 | 月次売上表 SYSOUT=(A,,STD) | USJ040.jcl:31 |

## CRUD マトリクス

| プログラム／画面 | 種別 | m_user | m_tokui | m_shohin | t_juchu | t_seikyu | TOKUI | SHOHIN | JUCHU | JUCHSRT | URIAGE | SEIKYU | NYUKIN | NYUKSRT | SKKEKKA | KESIKOMI | TKSUM | URINEW | SEIKYUSH | URIGETU | 根拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| login.jsp / LoginAction | 画面 | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | LoginAction.java:29 |
| tokui_search.jsp / TokuiSearchAction | 画面 |  | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | TokuiSearchAction.java:28-44 |
| tokui_edit.jsp / TokuiEditAction | 画面 |  | RU |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | TokuiEditAction.java:31-47 |
| juchu_input.jsp / JuchuInputAction | 画面 |  |  | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | JuchuInputAction.java:40 |
| juchu_confirm.jsp / JuchuConfirmAction | 画面 |  | R | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | JuchuConfirmAction.java:45,59 |
| juchu_complete.jsp / JuchuRegistAction | 画面 |  |  |  | CR |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | JuchuRegistAction.java:36,42-57 |
| juchu_inquiry.jsp / JuchuInquiryAction | 画面 |  | R | R | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | JuchuInquiryAction.java:34-56, juchu_inquiry.jsp:21-22 |
| seikyu_inquiry.jsp / SeikyuInquiryAction | 画面 |  |  |  |  | R |  |  |  |  |  |  |  |  |  |  |  |  |  |  | SeikyuInquiryAction.java:34-56 |
| JuchuExtract | Java |  | R | R | RU |  | C | C | C |  |  |  |  |  |  |  |  |  |  |  | JuchuExtract.java:19-71 |
| USJ010 STEP005 FTP | JCL |  |  |  |  |  | C | C | C |  |  |  |  |  |  |  |  |  |  |  | USJ010.jcl:12-20 |
| USJ010 STEP010 SORT | JCL |  |  |  |  |  |  |  | R | C |  |  |  |  |  |  |  |  |  |  | USJ010.jcl:22-30 |
| USB100 | COBOL |  |  |  |  |  | R | R |  | RD | C |  |  |  |  |  |  |  |  |  | USB100.cbl:64-74, USJ010.jcl:33 |
| USB200 | COBOL |  |  |  |  |  | R |  |  |  | R | C |  |  |  |  |  |  |  |  | USB200.cbl:70-71 |
| USJ030 STEP010 SORT | JCL |  |  |  |  |  |  |  |  |  |  |  | R | C |  |  |  |  |  |  | USJ030.jcl:12-20 |
| USB300 | COBOL |  |  |  |  |  |  |  |  |  |  | R |  | RD | C | C |  |  |  |  | USB300.cbl:67-68, USJ030.jcl:23 |
| USJ030 STEP030 FTP | JCL |  |  |  |  |  |  |  |  |  |  |  |  |  | R |  |  |  |  |  | USJ030.jcl:28-34 |
| SeikyuImport | Java |  |  |  |  | CD |  |  |  |  |  |  |  |  | R |  |  |  |  |  | SeikyuImport.java:19-45 |
| USB400 | COBOL |  |  |  |  |  |  |  |  |  | R |  |  |  |  |  | C |  |  |  | USB400.cbl:65-66 |
| USR500 | COBOL |  |  |  |  |  | R |  |  |  | R |  |  |  | R |  |  |  | C |  | USR500.cbl:102 |
| USR510 | COBOL |  |  |  |  |  | R |  |  |  |  |  |  |  |  |  | R |  |  | C | USR510.cbl:72 |
| USB900（未使用） | COBOL |  |  |  |  |  |  |  |  |  | R |  |  |  |  |  |  | C |  |  | USB900.cbl:37 |
