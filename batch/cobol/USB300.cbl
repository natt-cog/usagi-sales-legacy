      *****************************************************************
      *  システム名  : 販売管理システム
      *  プログラムID: USB300
      *  プログラム名: 入金消込
      *  作成日      : 1996.03.04
      *  作成者      : 山田
      *-----------------------------------------------------------------
      *  変更履歴
      *  1996.03 新規     山田
      *  2005.07 改修     山田  全面書き直し（構造化）
      *  2011.05 改修     高橋  振込手数料の加算
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.    USB300.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT NYFL    ASSIGN TO NYUKSRT
                          ORGANIZATION IS LINE SEQUENTIAL.
           SELECT SKIN    ASSIGN TO SEIKYU
                          ORGANIZATION IS LINE SEQUENTIAL.
           SELECT SKOUT   ASSIGN TO SKKEKKA
                          ORGANIZATION IS LINE SEQUENTIAL.
           SELECT KSFL    ASSIGN TO KESIKOMI
                          ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  NYFL.
           COPY NYKREC.
       FD  SKIN.
       01  SKIN-REC                PIC X(170).
       FD  SKOUT.
       01  SKOUT-REC               PIC X(170).
       FD  KSFL.
       01  KS-REC.
           03  KS-NY-NO            PIC 9(06).
           03  KS-DATE             PIC 9(08).
           03  KS-TK-CD            PIC X(06).
           03  KS-SK-NO            PIC X(12).
           03  KS-KIN              PIC 9(09).
           03  KS-KBN              PIC X(01).
           03  KS-NY-KIN           PIC 9(09).
           03  KS-TESURYO          PIC 9(05).
           03  FILLER              PIC X(24).
       WORKING-STORAGE SECTION.
           COPY SEIKREC.
       01  WK-KEY.
           03  WK-TK-KEY           PIC X(06).
           03  WK-SK-KEY           PIC X(06).
           03  WK-NY-KEY           PIC X(06).
       01  WK-SK-TBL.
           03  WK-SK-CNT           PIC 9(04)  VALUE ZERO.
           03  WK-SK-ENT           OCCURS 400.
               05  WK-SK-DATA      PIC X(170).
       01  WK-WORK.
           03  WK-I                PIC 9(04).
           03  WK-AMT              PIC S9(11) COMP-3.
           03  WK-ZAN              PIC S9(11) COMP-3.
           03  WK-APPLY            PIC S9(11) COMP-3.
       01  WK-CNT.
           03  WK-NY-IN            PIC 9(07)  VALUE ZERO.
           03  WK-KS-OUT           PIC 9(07)  VALUE ZERO.
           03  WK-KAJO             PIC 9(07)  VALUE ZERO.
           03  WK-FUMEI            PIC 9(07)  VALUE ZERO.
       PROCEDURE DIVISION.
       MAIN-RTN.
           OPEN INPUT  NYFL SKIN
                OUTPUT SKOUT KSFL.
           PERFORM READ-SK-RTN.
           PERFORM READ-NY-RTN.
           PERFORM UNTIL WK-SK-KEY = HIGH-VALUE
               PERFORM TOKUI-RTN
           END-PERFORM.
           PERFORM UNTIL WK-NY-KEY = HIGH-VALUE
               PERFORM FUMEI-RTN
           END-PERFORM.
           CLOSE NYFL SKIN SKOUT KSFL.
           DISPLAY 'USB300 NYUKIN=' WK-NY-IN ' KESIKOMI=' WK-KS-OUT
                   ' KAJO=' WK-KAJO ' FUMEI=' WK-FUMEI.
           STOP RUN.
      *
       TOKUI-RTN.
           MOVE WK-SK-KEY TO WK-TK-KEY.
           PERFORM UNTIL WK-NY-KEY NOT < WK-TK-KEY
               PERFORM FUMEI-RTN
           END-PERFORM.
           MOVE ZERO TO WK-SK-CNT.
           PERFORM UNTIL WK-SK-KEY NOT = WK-TK-KEY
               ADD 1 TO WK-SK-CNT
               MOVE SKIN-REC TO WK-SK-DATA (WK-SK-CNT)
               PERFORM READ-SK-RTN
           END-PERFORM.
           PERFORM UNTIL WK-NY-KEY NOT = WK-TK-KEY
               PERFORM KESIKOMI-RTN
               PERFORM READ-NY-RTN
           END-PERFORM.
           PERFORM VARYING WK-I FROM 1 BY 1 UNTIL WK-I > WK-SK-CNT
               MOVE WK-SK-DATA (WK-I) TO SK-REC
               EVALUATE TRUE
                   WHEN SK-NYUKIN = ZERO
                       MOVE '0' TO SK-KESI
                   WHEN SK-NYUKIN < SK-SEIKYU
                       MOVE '1' TO SK-KESI
                   WHEN OTHER
                       MOVE '2' TO SK-KESI
               END-EVALUATE
               WRITE SKOUT-REC FROM SK-REC
           END-PERFORM.
      *
       KESIKOMI-RTN.
           COMPUTE WK-AMT = NY-KIN + NY-TESURYO.
      * 2005.07 改修 山田 消込を新しい請求から順に
           PERFORM VARYING WK-I FROM 1 BY 1
                   UNTIL WK-I > WK-SK-CNT OR WK-AMT = ZERO
               MOVE WK-SK-DATA (WK-I) TO SK-REC
               COMPUTE WK-ZAN = SK-SEIKYU - SK-NYUKIN
               IF SK-TO < NY-DATE AND WK-ZAN > ZERO
                   IF WK-AMT < WK-ZAN
                       MOVE WK-AMT TO WK-APPLY
                   ELSE
                       MOVE WK-ZAN TO WK-APPLY
                   END-IF
                   ADD WK-APPLY      TO SK-NYUKIN
                   SUBTRACT WK-APPLY FROM WK-AMT
                   MOVE SK-REC       TO WK-SK-DATA (WK-I)
                   MOVE SK-NO        TO KS-SK-NO
                   MOVE WK-APPLY     TO KS-KIN
                   MOVE '1'          TO KS-KBN
                   PERFORM KS-OUT-RTN
               END-IF
           END-PERFORM.
           IF WK-AMT > ZERO
               MOVE SPACE  TO KS-SK-NO
               MOVE WK-AMT TO KS-KIN
               MOVE '9'    TO KS-KBN
               ADD 1 TO WK-KAJO
               PERFORM KS-OUT-RTN
           END-IF.
      *
       FUMEI-RTN.
           MOVE SPACE  TO KS-SK-NO.
           COMPUTE KS-KIN = NY-KIN + NY-TESURYO.
           MOVE '8'    TO KS-KBN.
           ADD 1 TO WK-FUMEI.
           PERFORM KS-OUT-RTN.
           PERFORM READ-NY-RTN.
      *
       KS-OUT-RTN.
           MOVE NY-NO      TO KS-NY-NO.
           MOVE NY-DATE    TO KS-DATE.
           MOVE NY-TK-CD   TO KS-TK-CD.
           MOVE NY-KIN     TO KS-NY-KIN.
           MOVE NY-TESURYO TO KS-TESURYO.
           WRITE KS-REC.
           ADD 1 TO WK-KS-OUT.
      *
       READ-SK-RTN.
           READ SKIN
               AT END MOVE HIGH-VALUE TO WK-SK-KEY
               NOT AT END MOVE SKIN-REC (13:6) TO WK-SK-KEY
           END-READ.
      *
       READ-NY-RTN.
           READ NYFL
               AT END MOVE HIGH-VALUE TO WK-NY-KEY
               NOT AT END
                   ADD 1 TO WK-NY-IN
                   MOVE NY-TK-CD TO WK-NY-KEY
           END-READ.
