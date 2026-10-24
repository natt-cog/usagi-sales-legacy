      *****************************************************************
      *  システム名  : 販売管理システム
      *  プログラムID: USB400
      *  プログラム名: 月次売上集計（得意先別）
      *  作成日      : 2012.06.18
      *  作成者      : 伊藤
      *-----------------------------------------------------------------
      *  変更履歴
      *  2012.06 新規     伊藤
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.    USB400.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT URI-FILE   ASSIGN TO URIAGE
                             ORGANIZATION IS SEQUENTIAL
                             FILE STATUS IS WS-URI-ST.
           SELECT SUM-FILE   ASSIGN TO TKSUM
                             ORGANIZATION IS LINE SEQUENTIAL
                             FILE STATUS IS WS-SUM-ST.
       DATA DIVISION.
       FILE SECTION.
       FD  URI-FILE.
           COPY URIREC.
       FD  SUM-FILE.
       01  TS-REC.
           03  TS-TK-CD            PIC X(06).
           03  TS-YM               PIC 9(06).
           03  TS-KENSU            PIC 9(05).
           03  TS-KIN              PIC S9(11) SIGN LEADING SEPARATE.
           03  TS-ZEI              PIC S9(09) SIGN LEADING SEPARATE.
           03  TS-GOKEI            PIC S9(11) SIGN LEADING SEPARATE.
           03  FILLER              PIC X(09).
       WORKING-STORAGE SECTION.
       01  WS-STATUS.
           03  WS-URI-ST           PIC X(02).
           03  WS-SUM-ST           PIC X(02).
       01  WS-FLAGS.
           03  WS-EOF              PIC X(01)  VALUE 'N'.
               88  WS-EOF-YES                 VALUE 'Y'.
       01  WS-BREAK.
           03  WS-CUR-KEY.
               05  WS-CUR-CD       PIC X(06).
               05  WS-CUR-YM       PIC 9(06).
           03  WS-NEW-KEY.
               05  WS-NEW-CD       PIC X(06).
               05  WS-NEW-YM       PIC 9(06).
       01  WS-ACCUM.
           03  WS-KENSU            PIC 9(05)  VALUE ZERO.
           03  WS-KIN              PIC S9(11) COMP-3 VALUE ZERO.
           03  WS-ZEI              PIC S9(09) COMP-3 VALUE ZERO.
       01  WS-COUNTERS.
           03  WS-IN-CNT           PIC 9(07)  VALUE ZERO.
           03  WS-OUT-CNT          PIC 9(07)  VALUE ZERO.
       PROCEDURE DIVISION.
       0000-MAIN.
           PERFORM 1000-INIT.
           PERFORM 2000-PROCESS UNTIL WS-EOF-YES.
           PERFORM 3000-WRITE-SUM.
           PERFORM 9000-TERM.
           STOP RUN.
      *
       1000-INIT.
           OPEN INPUT  URI-FILE
                OUTPUT SUM-FILE.
           PERFORM 8000-READ-URI.
           MOVE WS-NEW-KEY TO WS-CUR-KEY.
      *
       2000-PROCESS.
           IF WS-NEW-KEY NOT = WS-CUR-KEY
               PERFORM 3000-WRITE-SUM
               MOVE WS-NEW-KEY TO WS-CUR-KEY
           END-IF.
      *    得意先別に件数・金額・税額を集計する
           ADD 1          TO WS-KENSU.
           ADD URIAGE-KIN TO WS-KIN.
           ADD UR-ZEI-KIN TO WS-ZEI.
           PERFORM 8000-READ-URI.
      *
       3000-WRITE-SUM.
           IF WS-KENSU > ZERO
               INITIALIZE TS-REC
               MOVE WS-CUR-CD  TO TS-TK-CD
               MOVE WS-CUR-YM  TO TS-YM
               MOVE WS-KENSU   TO TS-KENSU
               MOVE WS-KIN     TO TS-KIN
               MOVE WS-ZEI     TO TS-ZEI
               COMPUTE TS-GOKEI = WS-KIN + WS-ZEI
               WRITE TS-REC
               ADD 1 TO WS-OUT-CNT
           END-IF.
           INITIALIZE WS-ACCUM.
      *
       8000-READ-URI.
           READ URI-FILE
               AT END
                   SET WS-EOF-YES TO TRUE
                   MOVE HIGH-VALUE TO WS-NEW-KEY
               NOT AT END
                   ADD 1 TO WS-IN-CNT
                   MOVE UR-TK-CD        TO WS-NEW-CD
                   MOVE UR-DATE (1:6)   TO WS-NEW-YM
           END-READ.
      *
       9000-TERM.
           CLOSE URI-FILE SUM-FILE.
           DISPLAY 'USB400 IN=' WS-IN-CNT ' OUT=' WS-OUT-CNT.
