//USJ040   JOB (USG,0100),'GETUJI CHOHYO',CLASS=A,MSGCLASS=X,
//             MSGLEVEL=(1,1),NOTIFY=&SYSUID
//*********************************************************************
//*  販売管理システム  夜間バッチ
//*  ジョブ名  : USJ040  月次集計・帳票出力
//*  先行      : USJ030
//*  後続      : なし
//*********************************************************************
//*  1996.02  新規（請求書）  山田
//*  2012.06  月次売上集計・月次売上表を追加  伊藤
//*********************************************************************
//STEP010  EXEC PGM=USB400
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//URIAGE   DD DSN=USAGI.PROD.URIAGE,DISP=SHR
//TKSUM    DD DSN=USAGI.PROD.TKSUM,DISP=OLD
//SYSOUT   DD SYSOUT=*
//STEP020  EXEC PGM=USR500
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//SKKEKKA  DD DSN=USAGI.PROD.SKKEKKA,DISP=SHR
//URIAGE   DD DSN=USAGI.PROD.URIAGE,DISP=SHR
//TOKUI    DD DSN=USAGI.PROD.TOKUI,DISP=SHR
//SEIKYUSH DD SYSOUT=(B,,SK01)
//SYSOUT   DD SYSOUT=*
//SYSIN    DD *
202412
/*
//STEP030  EXEC PGM=USR510
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//TKSUM    DD DSN=USAGI.PROD.TKSUM,DISP=SHR
//TOKUI    DD DSN=USAGI.PROD.TOKUI,DISP=SHR
//URIGETU  DD SYSOUT=(A,,STD)
//SYSOUT   DD SYSOUT=*
//SYSIN    DD *
202412
/*
//
