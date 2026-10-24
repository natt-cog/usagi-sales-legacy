//USJ010   JOB (USG,0100),'URIAGE KEIJO',CLASS=A,MSGCLASS=X,
//             MSGLEVEL=(1,1),NOTIFY=&SYSUID
//*********************************************************************
//*  販売管理システム  夜間バッチ
//*  ジョブ名  : USJ010  受注受信・売上計上
//*  先行      : Ｗｅｂ 受注抽出（JuchuExtract）
//*  後続      : USJ020
//*********************************************************************
//*  1995.03  新規  山田
//*  2005.10  受注データをＷｅｂサーバから受信  高橋
//*********************************************************************
//STEP005  EXEC PGM=FTP,PARM='websv01 (EXIT'
//OUTPUT   DD SYSOUT=*
//INPUT    DD *
usagibat ********
binary
get /work/TOKUI.DAT  'USAGI.PROD.TOKUI'  (replace
get /work/SHOHIN.DAT 'USAGI.PROD.SHOHIN' (replace
get /work/JUCHU.DAT  'USAGI.PROD.JUCHU'  (replace
quit
/*
//STEP010  EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=USAGI.PROD.JUCHU,DISP=SHR
//SORTOUT  DD DSN=&&JUCHSRT,DISP=(NEW,PASS),UNIT=SYSDA,
//            SPACE=(CYL,(1,1),RLSE),
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=0)
//SYSIN    DD *
  SORT FIELDS=(17,6,CH,A,9,8,CH,A,1,8,CH,A)
/*
//STEP020  EXEC PGM=USB100
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//JUCHSRT  DD DSN=&&JUCHSRT,DISP=(OLD,DELETE)
//TOKUI    DD DSN=USAGI.PROD.TOKUI,DISP=SHR
//SHOHIN   DD DSN=USAGI.PROD.SHOHIN,DISP=SHR
//URIAGE   DD DSN=USAGI.PROD.URIAGE,DISP=OLD
//SYSOUT   DD SYSOUT=*
//
