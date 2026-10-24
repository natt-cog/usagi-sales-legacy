      *****************************************************************
      *    受注ファイル（Ｗｅｂ抽出）  レコード長 80
      *****************************************************************
       01  JU-REC.
           03  JU-NO                   PIC 9(08).
           03  JU-DATE                 PIC 9(08).
           03  JU-DATE-R REDEFINES JU-DATE.
               05  JU-YYYY             PIC 9(04).
               05  JU-MM               PIC 9(02).
               05  JU-DD               PIC 9(02).
           03  JU-TK-CD                PIC X(06).
           03  JU-SH-CD                PIC X(06).
           03  JU-SURYO                PIC 9(07).
           03  JU-TANKA                PIC 9(07).
           03  JU-KBN                  PIC X(01).
           03  JU-KIN                  PIC S9(11)
                                       SIGN LEADING SEPARATE.
           03  FILLER                  PIC X(25).
