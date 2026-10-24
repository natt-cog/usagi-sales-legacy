//USJ030   JOB (USG,0100),'NYUKIN KESIKOMI',CLASS=A,MSGCLASS=X,
//             MSGLEVEL=(1,1),NOTIFY=&SYSUID
//*********************************************************************
//*  販売管理システム  夜間バッチ
//*  ジョブ名  : USJ030  入金消込・請求結果送信
//*  先行      : USJ020
//*  後続      : USJ040、Ｗｅｂ 請求取込
//*********************************************************************
//*  1996.03  新規  山田
//*  2005.10  請求結果をＷｅｂサーバへ送信  高橋
//*********************************************************************
//STEP010  EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=USAGI.PROD.NYUKIN,DISP=SHR
//SORTOUT  DD DSN=&&NYUKSRT,DISP=(NEW,PASS),UNIT=SYSDA,
//            SPACE=(TRK,(10,5),RLSE),
//            DCB=(RECFM=FB,LRECL=60,BLKSIZE=0)
//SYSIN    DD *
  SORT FIELDS=(15,6,CH,A,7,8,CH,A,1,6,CH,A)
/*
//STEP020  EXEC PGM=USB300
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//NYUKSRT  DD DSN=&&NYUKSRT,DISP=(OLD,DELETE)
//SEIKYU   DD DSN=USAGI.PROD.SEIKYU,DISP=SHR
//SKKEKKA  DD DSN=USAGI.PROD.SKKEKKA,DISP=OLD
//KESIKOMI DD DSN=USAGI.PROD.KESIKOMI,DISP=OLD
//SYSOUT   DD SYSOUT=*
//STEP030  EXEC PGM=FTP,PARM='websv01 (EXIT',COND=(0,NE,STEP020)
//OUTPUT   DD SYSOUT=*
//INPUT    DD *
usagibat ********
binary
put 'USAGI.PROD.SKKEKKA' /work/SKKEKKA.DAT
quit
/*
//
