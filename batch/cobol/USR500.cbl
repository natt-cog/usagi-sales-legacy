      *****************************************************************
      *  システム名  : 販売管理システム
      *  プログラムID: USR500
      *  プログラム名: 請求書発行
      *  作成日      : 1996.02.05
      *  作成者      : 山田
      *-----------------------------------------------------------------
      *  変更履歴
      *  1996.02 新規     山田
      *  2019.08 改修     佐藤  区分記載請求書対応
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.    USR500.
       AUTHOR.        YAMADA.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SKFL    ASSIGN TO SKKEKKA
                          ORGANIZATION IS LINE SEQUENTIAL.
           SELECT URFL    ASSIGN TO URIAGE
                          ORGANIZATION IS SEQUENTIAL.
           SELECT TKFL    ASSIGN TO TOKUI
                          ORGANIZATION IS LINE SEQUENTIAL.
           SELECT PRTFL   ASSIGN TO SEIKYUSH
                          ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  SKFL.
           COPY SEIKREC.
       FD  URFL.
           COPY URIREC.
       FD  TKFL.
           COPY TOKUREC.
       FD  PRTFL.
       01  PRT-REC                 PIC X(132).
       WORKING-STORAGE SECTION.
       01  W-YM                    PIC 9(06).
       01  W-SKEY                  PIC X(06).
       01  W-UKEY                  PIC X(06).
       01  W-TKEY                  PIC X(06).
       01  W-MAISU                 PIC 9(05)  VALUE ZERO.
       01  W-SEN                   PIC X(90)  VALUE ALL '-'.
       01  L1.
           03  FILLER              PIC X(30)  VALUE SPACE.
           03  FILLER              PIC X(15)  VALUE '請　求　書'.
       01  L2.
           03  FILLER              PIC X(15)  VALUE '  請求番号 '.
           03  L2-NO               PIC X(12).
           03  FILLER              PIC X(15)  VALUE '   得意先 '.
           03  L2-TK               PIC X(06).
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  L2-NM               PIC X(40).
       01  L3.
           03  FILLER              PIC X(16)  VALUE '  請求期間 '.
           03  L3-FROM             PIC 9999/99/99.
           03  FILLER              PIC X(05)  VALUE ' ～ '.
           03  L3-TO               PIC 9999/99/99.
       01  L4.
           03  FILLER              PIC X(20)
               VALUE '  ご請求金額 '.
           03  L4-KIN              PIC ---,---,---,--9.
           03  FILLER              PIC X(10)  VALUE ' 円'.
       01  L5.
           03  FILLER              PIC X(31)
               VALUE '  売上日      受注番号  '.
           03  FILLER              PIC X(30)
               VALUE '商品      数量      単価'.
           03  FILLER              PIC X(30)
               VALUE '        金額  税率'.
       01  M1.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-DATE             PIC 9999/99/99.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-JUNO             PIC 9(08).
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-SH               PIC X(06).
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-SURYO            PIC ---,--9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-TANKA            PIC Z,ZZZ,ZZ9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-KIN              PIC ---,---,--9.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  M1-RITU             PIC Z9.
           03  FILLER              PIC X(01)  VALUE '%'.
           03  M1-KOME             PIC X(03).
       01  F1.
           03  FILLER              PIC X(02)  VALUE SPACE.
           03  F1-NM               PIC X(24).
           03  F1-TAISYO           PIC ---,---,---,--9.
           03  FILLER              PIC X(13)  VALUE '  消費税'.
           03  F1-ZEI              PIC ---,---,--9.
       01  F2.
           03  FILLER              PIC X(26)
               VALUE '  合計（税抜）'.
           03  F2-KIN              PIC ---,---,---,--9.
           03  FILLER              PIC X(13)  VALUE '  消費税'.
           03  F2-ZEI              PIC ---,---,--9.
       PROCEDURE DIVISION.
       A000.
           ACCEPT W-YM FROM SYSIN.
           OPEN INPUT SKFL URFL TKFL OUTPUT PRTFL.
           PERFORM R100 THRU R100-EXIT.
           PERFORM R200 THRU R200-EXIT.
           PERFORM R300 THRU R300-EXIT.
       A100.
           IF W-SKEY = HIGH-VALUE
              GO TO A900.
           IF SK-YM NOT = W-YM
              PERFORM R100 THRU R100-EXIT
              GO TO A100.
       A110.
           IF W-TKEY < W-SKEY
              PERFORM R300 THRU R300-EXIT
              GO TO A110.
           WRITE PRT-REC FROM L1 AFTER ADVANCING PAGE.
           MOVE SK-NO TO L2-NO.
           MOVE SK-TK-CD TO L2-TK.
           MOVE SPACE TO L2-NM.
           IF W-TKEY = W-SKEY
              MOVE TK-NM TO L2-NM.
           WRITE PRT-REC FROM L2 AFTER ADVANCING 2.
           MOVE SK-FROM TO L3-FROM.
           MOVE SK-TO   TO L3-TO.
           WRITE PRT-REC FROM L3 AFTER ADVANCING 1.
           MOVE SK-SEIKYU TO L4-KIN.
           WRITE PRT-REC FROM L4 AFTER ADVANCING 2.
           WRITE PRT-REC FROM W-SEN AFTER ADVANCING 2.
           WRITE PRT-REC FROM L5 AFTER ADVANCING 1.
           WRITE PRT-REC FROM W-SEN AFTER ADVANCING 1.
       A200.
           IF W-UKEY < W-SKEY
              PERFORM R200 THRU R200-EXIT
              GO TO A200.
           IF W-UKEY = W-SKEY AND UR-DATE < SK-FROM
              PERFORM R200 THRU R200-EXIT
              GO TO A200.
       A210.
           IF W-UKEY NOT = W-SKEY OR UR-DATE > SK-TO
              GO TO A300.
           MOVE UR-DATE     TO M1-DATE.
           MOVE UR-JU-NO    TO M1-JUNO.
           MOVE UR-SH-CD    TO M1-SH.
           MOVE UR-SURYO    TO M1-SURYO.
           MOVE UR-TANKA    TO M1-TANKA.
           MOVE URIAGE-KIN  TO M1-KIN.
           MOVE UR-ZEI-RITU TO M1-RITU.
           MOVE SPACE       TO M1-KOME.
      * 2019.08 改修 佐藤
           IF ZEI-KBN = '2'
              MOVE '※' TO M1-KOME.
           WRITE PRT-REC FROM M1 AFTER ADVANCING 1.
           PERFORM R200 THRU R200-EXIT.
           GO TO A210.
       A300.
           WRITE PRT-REC FROM W-SEN AFTER ADVANCING 1.
           IF SK-Z10-TAISYO NOT = ZERO
              MOVE '10%対象' TO F1-NM
              MOVE SK-Z10-TAISYO TO F1-TAISYO
              MOVE SK-Z10 TO F1-ZEI
              WRITE PRT-REC FROM F1 AFTER ADVANCING 1.
           IF SK-Z8K-TAISYO NOT = ZERO
              MOVE '8%対象（軽減）※' TO F1-NM
              MOVE SK-Z8K-TAISYO TO F1-TAISYO
              MOVE SK-Z8K TO F1-ZEI
              WRITE PRT-REC FROM F1 AFTER ADVANCING 1.
           IF SK-SONOTA-TAISYO NOT = ZERO
              MOVE '旧税率対象' TO F1-NM
              MOVE SK-SONOTA-TAISYO TO F1-TAISYO
              MOVE SK-SONOTA TO F1-ZEI
              WRITE PRT-REC FROM F1 AFTER ADVANCING 1.
           MOVE SK-URIAGE TO F2-KIN.
           MOVE SK-ZEI    TO F2-ZEI.
           WRITE PRT-REC FROM F2 AFTER ADVANCING 2.
           ADD 1 TO W-MAISU.
           PERFORM R100 THRU R100-EXIT.
           GO TO A100.
       A900.
           CLOSE SKFL URFL TKFL PRTFL.
           DISPLAY 'USR500 YM=' W-YM ' MAISU=' W-MAISU.
           STOP RUN.
       R100.
           READ SKFL AT END MOVE HIGH-VALUE TO W-SKEY
                            GO TO R100-EXIT.
           MOVE SK-TK-CD TO W-SKEY.
       R100-EXIT.
           EXIT.
       R200.
           READ URFL AT END MOVE HIGH-VALUE TO W-UKEY
                            GO TO R200-EXIT.
           MOVE UR-TK-CD TO W-UKEY.
       R200-EXIT.
           EXIT.
       R300.
           READ TKFL AT END MOVE HIGH-VALUE TO W-TKEY
                            GO TO R300-EXIT.
           MOVE TK-CD TO W-TKEY.
       R300-EXIT.
           EXIT.
