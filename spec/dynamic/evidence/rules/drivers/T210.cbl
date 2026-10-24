       IDENTIFICATION DIVISION.
       PROGRAM-ID. T210.
      * USB210 テストドライバ: 標準入力 1 行 = 締日区分(2) 年月(6)  例 "99 202402"
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  IN-LINE                 PIC X(40).
       01  EOF-FLG                 PIC X VALUE 'N'.
       01  SP-AREA.
           03  SP-SIME                 PIC 9(02).
           03  SP-YM                   PIC 9(06).
           03  SP-FROM                 PIC 9(08).
           03  SP-TO                   PIC 9(08).
           03  SP-RC                   PIC 9(02).
       PROCEDURE DIVISION.
           PERFORM UNTIL EOF-FLG = 'Y'
              MOVE SPACE TO IN-LINE
              ACCEPT IN-LINE FROM SYSIN
                    IF IN-LINE = SPACE
                       MOVE 'Y' TO EOF-FLG
                    ELSE
                       INITIALIZE SP-AREA
                       MOVE IN-LINE(1:2) TO SP-SIME
                       MOVE IN-LINE(4:6) TO SP-YM
                       CALL 'USB210' USING SP-AREA
                       DISPLAY IN-LINE(1:9) ' => FROM=' SP-FROM
                               ' TO=' SP-TO ' RC=' SP-RC
                    END-IF
           END-PERFORM
           STOP RUN.
