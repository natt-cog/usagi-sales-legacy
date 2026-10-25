"""動的仕様書の判定データ（修正箇所・要確認の挙動・プログラム別エビデンス・確認事項／差分の判定）。build_*.py から使う。"""
E = 'evidence/'
EXEC, SRC, EST, NOT = '実行で確認', 'ソースで確認', '推定', '未検証'

# プログラム → 主なエビデンス（業務ルール検証のケースディレクトリ）
PEV = {'P01': E + 'rules/WEB-LOGIN/http.txt', 'P02': E + 'rules/WEB-LOGOUT/http.txt', 'P03': E + 'rules/WEB-MENU/http.txt',
       'P04': E + 'rules/WEB-TOKUI/http.txt', 'P05': E + 'rules/WEB-TOKUIEDIT/http.txt', 'P06': E + 'rules/WEB-JUCHUIN/http.txt',
       'P07': E + 'rules/WEB-CONF-NEBIKI/http.txt', 'P08': E + 'rules/WEB-REG-MAX/http.txt', 'P09': E + 'rules/WEB-JINQ/http.txt',
       'P10': E + 'rules/WEB-SINQ/http.txt', 'P11': E + 'rules/JX/run.log', 'P12': E + 'rules/SI/run.log',
       'P13': E + 'rules/USB100', 'P14': E + 'rules/USB110', 'P15': E + 'rules/USB200-A', 'P16': E + 'rules/USB210',
       'P17': E + 'rules/USB300', 'P18': E + 'rules/USB400', 'P19': E + 'rules/USR500', 'P20': E + 'rules/USR510', 'P21': E + 'rules/USB900'}
# 実データでの夜間バッチ実行（ファイル定義の確認に使う）
BATCH_FILE_EV = {'P13': 'USAGI.PROD.URIAGE', 'P14': 'USAGI.PROD.URIAGE', 'P15': 'USAGI.PROD.SEIKYU', 'P16': 'USAGI.PROD.SEIKYU',
                 'P17': 'USAGI.PROD.KESIKOMI', 'P18': 'USAGI.PROD.TKSUM', 'P19': 'SEIKYUSH.txt', 'P20': 'URIGETU.txt', 'P21': None}
SCREENS = {'P01': ['01_login.png', '01_login_error.png'], 'P03': ['02_menu.png'], 'P04': ['03_tokui_search.png', '03_tokui_search_result.png'],
           'P05': ['04_tokui_edit.png'], 'P06': ['05_juchu_input.png', '05_juchu_input_error.png'], 'P07': ['06_juchu_confirm.png'],
           'P08': ['07_juchu_complete.png'], 'P09': ['08_juchu_inquiry.png', '08_juchu_inquiry_result.png', '08_juchu_inquiry_registered.png'],
           'P10': ['09_seikyu_inquiry.png', '09_seikyu_inquiry_result.png', '09_seikyu_inquiry_error.png', '09_seikyu_inquiry_after_batch.png']}
EV_SCREENS = {'EV01': ['01_login.png', '02_menu.png'], 'EV02': ['03_tokui_search_result.png', '04_tokui_edit.png'],
              'EV03': ['05_juchu_input.png', '06_juchu_confirm.png', '07_juchu_complete.png'], 'EV04': ['08_juchu_inquiry_registered.png'],
              'EV08': ['09_seikyu_inquiry_after_batch.png']}
EV_LOGS = {'EV05': E + 'batch/run_202412.log', 'EV06': E + 'batch/run_202412.log', 'EV07': E + 'batch/run_202412.log', 'EV09': E + 'batch/compare_samples.txt'}
VIDEO = E + 'video/EV03-EV08_受注入力から請求照会.mp4'

# 修正箇所一覧。kind: 誤り／不正確／推定→確定。where は Excel 行（プログラム仕様書）または md の位置
FIXES = [
    dict(id='F01', kind='誤り', doc='01 プログラム仕様書', where='P17 入金消込（USB300）入力例「請求ファイル SEIKYU」（Excel 577行）', row=577, evidence=E + 'batch/run_202412/USAGI.PROD.KESIKOMI',
         reason='入力例の入金000001（20140930）に対応する請求を 201409100001 と推定していたが、実行すると 201408100001（2014/08分 3,628円）に充当された'),
    dict(id='F02', kind='不正確', doc='01 プログラム仕様書', where='P10 請求照会 処理概要・出力（未入金合計）', match=('P10', '合計'), evidence=E + 'rules/WEB-SINQ/http.txt',
         before='未入金額（請求−入金）の合計を出す', after='表示した最大100件分の未入金額（請求−入金）の合計を出す（101件目以降は合計に含まれない）',
         reason='請求105件の得意先で、合計は表示した100件分だけだった'),
    dict(id='F03', kind='不正確', doc='01 プログラム仕様書', where='P09 受注照会 処理概要・出力（合計金額）', match=('P09', '合計'), evidence=E + 'rules/WEB-JINQ/http.txt',
         before='売上金額の合計を出す', after='表示した最大100件分の売上金額の合計を出す（101件目以降は合計に含まれない）',
         reason='受注105件の得意先で「100 件 合計金額 33,300 円」（333円×100件）だった'),
    dict(id='F04', kind='不正確', doc='01 プログラム仕様書', where='P11 受注抽出 得意先名（TK-NM）', match=('P11', '得意先名'), evidence=E + 'rules/JX/TOKUI.DAT',
         before='m_tokui.tk_nm を UTF-8 で40バイトに切詰め', after='m_tokui.tk_nm を UTF-8 で40バイト以内に切詰め（文字の途中では切らず、余りは空白。例：14文字42バイト→13文字39バイト＋空白1）',
         reason='マルチバイト文字の途中では切らないため、40バイトちょうどにならない場合がある'),
]
# 推定→確定（入力例・出力例）は examples.json の fix 列から自動で追加する。以下は md／その他の推定→確定
FIXES_MD = [
    dict(id='F90', kind='推定→確定', doc='03 アプリケーション詳細設計書', where='EV06 注意点「締日エラーの得意先は請求なしで処理続行・RC は0のまま（推定）」',
         before='（推定：RETURN-CODE を設定していない）', after='（実行で確認：締日区分00の得意先で SIME ERROR を表示し、RC=0 で終了）', evidence=E + 'rules/USB200-A/USB200.log'),
    dict(id='F91', kind='推定→確定', doc='10 確認事項一覧', where='Q03 締日28のうるう年',
         before='2/29の売上が2回集計される計算です（推定：コードからの導出…）', after='2/29の売上が2回集計される（実行で確認：締日28 の 202402 は 20240129〜20240229、202403 は 20240229〜20240328）', evidence=E + 'rules/USB210'),
    dict(id='F92', kind='推定→確定', doc='07 欠けた資産と復元案', where='M01 NYKREC.cpy 復元案',
         before='推定の定義（リポジトリには追加していない）', after='復元案を evidence/restore/NYKREC.cpy に補い、USB300 のコンパイル・実行に成功（入金650件 消込946件 過入金0 不明1。請求書サンプル3本と一致）', evidence=E + 'logs/compile.log'),
    dict(id='F93', kind='推定→確定', doc='07 欠けた資産と復元案', where='M03／M07／M08 起動定義・ジョブ順序・SYSIN',
         before='起動する資産がない（推定で順序を記載）', after='推定どおりの順序（JuchuExtract→USJ010→USJ020→USJ030→SeikyuImport→USJ040）を pipeline.py で組み立てて完走。SYSIN は引数で渡した', evidence=E + 'scripts/pipeline.py'),
    dict(id='F94', kind='推定→確定', doc='09 未使用・類似資産', where='U01／M06 USB900',
         before='1997年の税率改定時に一度だけ実行した臨時ジョブと推定', after='DD URINEW を補って実データ757件で実行：UPD=0、出力は入力とバイト一致（2014年以降のデータは対象外）。境界値 19970401 で 3%→5% 再計算を確認', evidence=E + 'rules/USB900'),
]

# 要確認の挙動
ISSUES = [
    ('I01', '無償サンプルが請求される', '受注区分3（Web で金額0）を USB100 が数量×単価で計算し直し、売上・請求に載る', 'Q01', E + 'rules/USB100'),
    ('I02', '末日締めでうるう年の2/29が請求から漏れる', '締日99 の 202402 は 20240201〜20240228。2/29 の売上はどの請求にも載らない（TOBASI にも数えない）', 'Q02', E + 'rules/USB200-A'),
    ('I03', '締日28でうるう年の2/29を二重に集計', '202402 は 〜20240229、202403 は 20240229〜。2/29 の売上が2回請求される', 'Q03', E + 'rules/USB210'),
    ('I04', '締日28の平年3月に存在しない日付', '28 202303 → 開始日 20230229（存在しない日付）。結果として 2/28 以前と重ならないが日付として不正', '新規', E + 'rules/USB210'),
    ('I05', 'うるう年判定が「年÷4」だけ', '2100年2月（平年）も29日まで扱う（USB210）', '新規', E + 'rules/USB210'),
    ('I06', '消込順とソースコメントが逆', 'コメントは「新しい請求から」だが、実際は古い請求から充当', 'Q07', E + 'rules/USB300'),
    ('I07', '締日当日の入金が充当されない', '入金日20240131＝202401 締日の入金は請求に充当されず過入金（9）', 'Q09', E + 'rules/USB300'),
    ('I08', '1得意先の請求が400件を超えてもエラーにならない', '401件の請求で RC=0、402件を出力（表の上限を超えて書き込み）', '新規', E + 'rules/USB300-400'),
    ('I09', '端数「切上げ」で返品の税額が0側に丸まる', '端数区分3、金額−101 → 税額 −10（−10.1 の絶対値は切り捨て）', '新規', E + 'rules/USB110'),
    ('I10', '存在しない受注日を受け付ける', '受注日 20241399 が確認画面へ進む（8桁数字かだけを見ている）', '新規', E + 'rules/WEB-CONF-YMD/http.txt'),
    ('I11', '得意先メンテで範囲外の値を登録できる', '締日区分31・端数区分7 を「更新しました」で登録', 'Q23', E + 'rules/WEB-TOKUIEDIT/http.txt'),
    ('I12', '与信限度額を超える受注ができる', '限度額100 の得意先に 数量9,999,999（金額3,159,999,684円）で確認画面へ', 'Q15', E + 'rules/WEB-CONF-GENDO/http.txt'),
    ('I13', '確認画面の hidden を書き換えるとその金額で登録', 'tanka=1・uriageKin=1 に書き換えて送ると、数量10 単価1 金額1 で登録', 'Q25', E + 'rules/WEB-REG-HIDDEN/http.txt'),
    ('I14', '請求照会の終了年月が「未満」', '202412〜202412 で 0件、202412〜202501 で 1件', 'Q20', E + 'rules/WEB-SINQ/http.txt'),
    ('I15', '照会画面の合計が表示100件分だけ', '受注照会・請求照会とも、101件目以降は合計に含まれない', '新規', E + 'rules/WEB-JINQ/http.txt'),
    ('I16', '入力エラーがシステムエラー画面になる', '得意先メンテの与信限度額に文字（NumberFormatException）、備考61文字（DB 桁あふれ）で HTTP 500', '新規', E + 'rules/WEB-REG-ERR/http.txt'),
    ('I17', '取引停止の得意先も夜間バッチで売上計上', 'TK-DEL=1 の得意先の受注も売上・請求に載る', 'Q14', E + 'rules/USB100'),
    ('I18', '締日エラーでも RC=0', '締日区分00 の得意先は SIME ERROR を表示するが RC=0 で後続ジョブが動く', '新規', E + 'rules/USB200-A/USB200.log'),
]

# 確認事項一覧（Q）: (判定, 実行結果, エビデンス)
Q = {'Q01': (EXEC, '受注区分3 数量10 単価100 → 売上1,000円・税100円', E + 'rules/USB100'),
     'Q02': (EXEC, '末日締め 202402 は 0228 まで。2/29 は請求に載らない', E + 'rules/USB200-A'),
     'Q03': (EXEC, '締日28: 202402 は 〜0229、202403 は 0229〜（二重集計）', E + 'rules/USB210'),
     'Q04': (EXEC, '数量49/50/99/100 で 0%/3%/3%/5%', E + 'rules/WEB-CONF-NEBIKI/http.txt'),
     'Q05': (EXEC, '端数区分 1:切捨て 2:四捨五入 3:切上げ（画面表示・税計算とも）', E + 'rules/USB110'),
     'Q06': (EXEC, '明細ごとに税計算（105円×2・100円 → 税10+10+10=30）', E + 'rules/USB200-A'),
     'Q07': (EXEC, '古い請求（202401）から充当', E + 'rules/USB300'),
     'Q08': (EXEC, '入金10,560＋手数料440 で 11,000 を消込', E + 'rules/USB300'),
     'Q09': (EXEC, '締日当日（20240131）の入金も過入金（9）', E + 'rules/USB300'),
     'Q10': (EXEC, 'KESIKOMI はどのジョブも読まない（CRUD 実測でも読み手なし）', E + 'crud/crud_actual.json'),
     'Q11': (NOT, '入金データの作成元はリポジトリになく、実行では確かめられない（NYKREC は復元案で動作）', ''),
     'Q12': (NOT, '起動定義がないため運用は確認できない。推定の順序で完走することは確認', E + 'batch/run_202412.log'),
     'Q13': (EXEC, 'SYSIN 20241231201401 で 201401〜202412 の請求を毎回作り直す（693件）', E + 'batch/run_202412.log'),
     'Q14': (EXEC, '取引停止の得意先は画面で「取引停止中の得意先です」、バッチでは売上計上', E + 'rules/USB100'),
     'Q15': (EXEC, '限度額100 に 3,159,999,684円の受注が通る', E + 'rules/WEB-CONF-GENDO/http.txt'),
     'Q16': (EXEC, 'メニューに得意先メンテのリンクなし（URL 直打ちで開ける）', E + 'screens/02_menu.png'),
     'Q17': (SRC, '権限による画面制御なし（user01 でも全画面を開ける）', E + 'screens/04_tokui_edit.png'),
     'Q18': (EXEC, 'JCL からの呼出しなし。単独実行は可能', E + 'rules/USB900'),
     'Q19': (EXEC, 'flg1=1 の受注も再抽出（全件）', E + 'rules/JX/run.log'),
     'Q20': (EXEC, '終了年月は含まない', E + 'rules/WEB-SINQ/http.txt'),
     'Q21': (EXEC, 'MAX+1 採番（空なら 10000001）。同時登録は試していない', E + 'rules/WEB-REG-MAX/http.txt'),
     'Q22': (EXEC, '月次売上表は暦月（USB400）、請求は締め期間', E + 'rules/USB400'),
     'Q23': (EXEC, '締日31 を登録でき、バッチは 29〜98 を RC=09', E + 'rules/WEB-TOKUIEDIT/http.txt'),
     'Q24': (SRC, '回収月・回収日は照会画面に表示されるだけ', E + 'screens/03_tokui_search_result.png'),
     'Q25': (EXEC, 'hidden 書き換えがそのまま登録される。平文パスワード・SQL 連結はソースで確認', E + 'rules/WEB-REG-HIDDEN/http.txt')}
# 旧仕様書との差分（D）
D = {'D01': (EXEC, E + 'rules/WEB-CONF-NEBIKI/http.txt'), 'D02': (EXEC, E + 'rules/WEB-CONF-KBN/http.txt'), 'D03': (EXEC, E + 'rules/USB110'),
     'D04': (EXEC, E + 'rules/USB200-A'), 'D05': (EXEC, E + 'rules/USB210'), 'D06': (EXEC, E + 'rules/USB300'), 'D07': (EXEC, E + 'rules/USB300'),
     'D08': (EXEC, E + 'rules/USB300'), 'D09': (EXEC, E + 'rules/WEB-TOKUIEDIT/http.txt'), 'D10': (EXEC, E + 'rules/WEB-SINQ/http.txt'),
     'D11': (EXEC, E + 'rules/JX/run.log'), 'D12': (EXEC, E + 'rules/USB110'), 'D13': (EXEC, E + 'rules/SI/run.log'), 'D14': (EXEC, E + 'batch/run_202412.log'),
     'D15': (EXEC, E + 'rules/USB100'), 'D16': (EXEC, E + 'screens/06_juchu_confirm.png')}
U = {'U01': (EXEC, E + 'rules/USB900'), 'U02': (EXEC, E + 'rules/USB110'), 'U03': (SRC, ''), 'U04': (EXEC, E + 'screens/02_menu.png'),
     'U05': (SRC, ''), 'U06': (SRC, ''), 'U07': (EXEC, E + 'crud/crud_actual.json'), 'U08': (EXEC, E + 'screens/01_login.png')}
M = {'M01': (EXEC, '復元案で USB300 のコンパイル・実行に成功', E + 'logs/compile.log'), 'M02': (EXEC, 'なくても画面は起動・動作（null=true）', E + 'screens/01_login.png'),
     'M03': (EXEC, '推定の起動順で pipeline.py を組み立てて完走', E + 'scripts/pipeline.py'), 'M04': (NOT, '作成ジョブはなく NYUKIN.DAT をそのまま使った', E + 'batch/run_202412/USAGI.PROD.NYUKIN'),
     'M05': (EXEC, 'KESIKOMI を出力し、読み手がないことを確認', E + 'batch/run_202412/USAGI.PROD.KESIKOMI'), 'M06': (EXEC, 'DD URINEW を補って USB900 を実行', E + 'rules/USB900'),
     'M07': (EXEC, '出力データセットは毎回新規作成で代替し完走', E + 'batch/run_202412.log'), 'M08': (EXEC, 'SYSIN は引数で渡して実行（202412／202402／202403）', E + 'batch/compare_samples.txt')}
# md の記述（表の行・箇条書き）に付ける判定。部分一致で先に当たったもの。該当なしは「推定」を含めば推定、それ以外はソースで確認
MD_RULES = [
    ('COND がない', NOT, 'z/OS の JCL 実行環境がなく、COND 既定動作は確かめられない', ''),
    ('EBCDIC', NOT, 'ホストへの FTP 転送は再現できない（Linux 上はバイナリのまま処理）', ''),
    ('スケジューラ', NOT, 'スケジューラ定義がなく運用は確かめられない。推定の順序で完走することは確認', E + 'batch/run_202412.log'),
    ('締日エラー', EXEC, '締日区分00 で SIME ERROR、RC=0', E + 'rules/USB200-A/USB200.log'),
    ('2/29', EXEC, '', E + 'rules/USB210'), ('うるう', EXEC, '', E + 'rules/USB210'),
    ('充当', EXEC, '', E + 'rules/USB300'), ('消込', EXEC, '', E + 'rules/USB300'), ('手数料', EXEC, '', E + 'rules/USB300'),
    ('割引', EXEC, '', E + 'rules/WEB-CONF-NEBIKI/http.txt'), ('無償', EXEC, '', E + 'rules/USB100'), ('返品', EXEC, '', E + 'rules/USB100'),
    ('税率', EXEC, '', E + 'rules/USB110'), ('端数', EXEC, '', E + 'rules/USB110'), ('軽減', EXEC, '', E + 'rules/USB110'),
    ('TOBASI', EXEC, '', E + 'rules/USB200-A'), ('請求期間', EXEC, '', E + 'rules/USB200-A'), ('締日', EXEC, '', E + 'rules/USB210'),
    ('MAX', EXEC, '', E + 'rules/WEB-REG-MAX/http.txt'), ('hidden', EXEC, '', E + 'rules/WEB-REG-HIDDEN/http.txt'),
    ('取引停止', EXEC, '', E + 'rules/WEB-CONF-MST/http.txt'), ('与信', EXEC, '', E + 'rules/WEB-CONF-GENDO/http.txt'),
    ('flg1', EXEC, '', E + 'rules/JX/run.log'), ('抽出', EXEC, '', E + 'rules/JX/run.log'), ('洗い替え', EXEC, '', E + 'rules/SI/run.log'),
    ('t_seikyu', EXEC, '', E + 'rules/SI/run.log'), ('SeikyuImport', EXEC, '', E + 'rules/SI/run.log'), ('JuchuExtract', EXEC, '', E + 'rules/JX/run.log'),
    ('USB900', EXEC, '', E + 'rules/USB900'), ('ZEI-03', EXEC, '', E + 'rules/USB110'),
    ('請求書', EXEC, '', E + 'batch/compare_samples.txt'), ('月次売上', EXEC, '', E + 'batch/compare_samples.txt'),
    ('USJ0', EXEC, '', E + 'batch/run_202412.log'), ('SORT', EXEC, '', E + 'batch/run_202412.log'), ('FTP', EXEC, 'FTP は docker compose exec のファイル受け渡しで代替', E + 'scripts/pipeline.py'),
    ('ログイン', EXEC, '', E + 'rules/WEB-LOGIN/http.txt'), ('得意先照会', EXEC, '', E + 'rules/WEB-TOKUI/http.txt'), ('受注照会', EXEC, '', E + 'rules/WEB-JINQ/http.txt'),
    ('請求照会', EXEC, '', E + 'rules/WEB-SINQ/http.txt'), ('受注入力', EXEC, '', E + 'rules/WEB-CONF-YMD/http.txt'), ('得意先メンテ', EXEC, '', E + 'rules/WEB-TOKUIEDIT/http.txt'),
]
