      *****************************************************************
      *  システム名  : 販売管理システム
      *  プログラムID: USR510
      *  プログラム名: 月次売上表
      *  作成日      : 2012.06.25
      *  作成者      : 伊藤
      *-----------------------------------------------------------------
      *  変更履歴
      *  2012.06 新規     伊藤
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.    USR510.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT TS-FILE    ASSIGN TO TKSUM
                             ORGANIZATION IS LINE SEQUENTIAL.
           SELECT TK-FILE    ASSIGN TO TOKUI
                             ORGANIZATION IS LINE SEQUENTIAL.
           SELECT PRT-FILE   ASSIGN TO URIGETU
                             ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  TS-FILE.
       01  TS-REC.
           03  TS-TK-CD            PIC X(06).
           03  TS-YM               PIC 9(06).
           03  TS-KENSU            PIC 9(05).
           03  TS-KIN              PIC S9(11) SIGN LEADING SEPARATE.
           03  TS-ZEI              PIC S9(09) SIGN LEADING SEPARATE.
           03  TS-GOKEI            PIC S9(11) SIGN LEADING SEPARATE.
           03  FILLER              PIC X(09).
       FD  TK-FILE.
           COPY TOKUREC.
       FD  PRT-FILE.
       01  PRT-REC                 PIC X(132).
       WORKING-STORAGE SECTION.
       01  WS-YM                   PIC 9(06).
       01  WS-FLAGS.
           03  WS-EOF              PIC X(01)  VALUE 'N'.
               88  WS-EOF-YES                 VALUE 'Y'.
       01  WS-TOTAL.
           03  WS-T-KENSU          PIC 9(07)  VALUE ZERO.
           03  WS-T-KIN            PIC S9(13) COMP-3 VALUE ZERO.
           03  WS-T-ZEI            PIC S9(11) COMP-3 VALUE ZERO.
       01  HD1.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  FILLER              PIC X(36)
               VALUE '月次売上表（得意先別）'.
           03  HD1-YM              PIC 9999/99.
       01  HD2.
           03  FILLER              PIC X(44)
               VALUE '  コード     件数        売上金額'.
           03  FILLER              PIC X(48)
               VALUE '      消費税          合計  得意先名'.
       01  DT1.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-CD              PIC X(06).
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-KENSU           PIC ZZZ,ZZ9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-KIN             PIC ---,---,---,--9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-ZEI             PIC --,---,--9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-GOKEI           PIC ---,---,---,--9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  DT1-NM              PIC X(40).
       PROCEDURE DIVISION.
       0000-MAIN.
           ACCEPT WS-YM FROM SYSIN.
           OPEN INPUT TS-FILE TK-FILE OUTPUT PRT-FILE.
           MOVE WS-YM TO HD1-YM.
           WRITE PRT-REC FROM HD1 AFTER ADVANCING PAGE.
           WRITE PRT-REC FROM HD2 AFTER ADVANCING 2.
           MOVE SPACE TO PRT-REC.
           WRITE PRT-REC AFTER ADVANCING 1.
           PERFORM UNTIL WS-EOF-YES
               READ TS-FILE
                   AT END SET WS-EOF-YES TO TRUE
                   NOT AT END
                       IF TS-YM = WS-YM
                           PERFORM 2000-LINE
                       END-IF
               END-READ
           END-PERFORM.
           MOVE SPACE      TO DT1-CD.
           MOVE '合計'     TO DT1-NM.
           MOVE WS-T-KENSU TO DT1-KENSU.
           MOVE WS-T-KIN   TO DT1-KIN.
           MOVE WS-T-ZEI   TO DT1-ZEI.
           COMPUTE DT1-GOKEI = WS-T-KIN + WS-T-ZEI.
           WRITE PRT-REC FROM DT1 AFTER ADVANCING 2.
           CLOSE TS-FILE TK-FILE PRT-FILE.
           DISPLAY 'USR510 YM=' WS-YM ' KENSU=' WS-T-KENSU.
           STOP RUN.
      *
       2000-LINE.
           PERFORM UNTIL TK-CD NOT < TS-TK-CD OR TK-CD = HIGH-VALUE
               READ TK-FILE
                   AT END MOVE HIGH-VALUE TO TK-CD
               END-READ
           END-PERFORM.
           MOVE TS-TK-CD  TO DT1-CD.
           MOVE TS-KENSU  TO DT1-KENSU.
           MOVE TS-KIN    TO DT1-KIN.
           MOVE TS-ZEI    TO DT1-ZEI.
           MOVE TS-GOKEI  TO DT1-GOKEI.
           MOVE SPACE     TO DT1-NM.
           IF TK-CD = TS-TK-CD
               MOVE TK-NM TO DT1-NM
           END-IF.
           WRITE PRT-REC FROM DT1 AFTER ADVANCING 1.
           ADD TS-KENSU   TO WS-T-KENSU.
           ADD TS-KIN     TO WS-T-KIN.
           ADD TS-ZEI     TO WS-T-ZEI.
