       IDENTIFICATION DIVISION.
       PROGRAM-ID. T110.
      * USB110 テストドライバ: 標準入力 1 行 = 売上日(8) 金額(符号+11) 軽減(1) 端数(1)
      * 例 "20190930 +00000000105 1 2"。結果を 1 行で表示する。
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  IN-LINE                 PIC X(40).
       01  W-KIN                   PIC S9(11) SIGN LEADING SEPARATE.
       01  W-ZEI                   PIC -(9)9.
       01  EOF-FLG                 PIC X VALUE 'N'.
       01  ZP-AREA.
           03  ZP-DATE                 PIC 9(08).
           03  ZP-KIN                  PIC S9(11)    COMP-3.
           03  ZP-KEIGEN               PIC X(01).
           03  ZP-HASU                 PIC X(01).
           03  ZP-RITU                 PIC 9(02).
           03  ZP-KBN                  PIC X(01).
           03  ZP-ZEI                  PIC S9(09)    COMP-3.
           03  ZP-RC                   PIC 9(02).
       PROCEDURE DIVISION.
           PERFORM UNTIL EOF-FLG = 'Y'
              MOVE SPACE TO IN-LINE
              ACCEPT IN-LINE FROM SYSIN
                    IF IN-LINE = SPACE
                       MOVE 'Y' TO EOF-FLG
                    ELSE
                       INITIALIZE ZP-AREA
                       MOVE IN-LINE(1:8)  TO ZP-DATE
                       MOVE IN-LINE(10:12) TO W-KIN
                       MOVE W-KIN TO ZP-KIN
                       MOVE IN-LINE(23:1) TO ZP-KEIGEN
                       MOVE IN-LINE(25:1) TO ZP-HASU
                       CALL 'USB110' USING ZP-AREA
                       MOVE ZP-ZEI TO W-ZEI
                       DISPLAY IN-LINE(1:25) ' => RITU=' ZP-RITU
                               ' KBN=' ZP-KBN ' ZEI=' W-ZEI ' RC=' ZP-RC
                    END-IF
           END-PERFORM
           STOP RUN.
