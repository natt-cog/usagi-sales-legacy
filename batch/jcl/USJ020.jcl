//USJ020   JOB (USG,0100),'SEIKYU SIME',CLASS=A,MSGCLASS=X,
//             MSGLEVEL=(1,1),NOTIFY=&SYSUID
//*********************************************************************
//*  販売管理システム  夜間バッチ
//*  ジョブ名  : USJ020  請求締め
//*  先行      : USJ010
//*  後続      : USJ030
//*********************************************************************
//*  1996.01  新規  山田
//*  1996.09  USB210（締日算出）を LOADLIB に追加  山田
//*********************************************************************
//STEP010  EXEC PGM=USB200
//STEPLIB  DD DSN=USAGI.PROD.LOADLIB,DISP=SHR
//TOKUI    DD DSN=USAGI.PROD.TOKUI,DISP=SHR
//URIAGE   DD DSN=USAGI.PROD.URIAGE,DISP=SHR
//SEIKYU   DD DSN=USAGI.PROD.SEIKYU,DISP=OLD
//SYSOUT   DD SYSOUT=*
//*        業務日付（YYYYMMDD）＋締め開始年月（YYYYMM）
//SYSIN    DD *
20241231201401
/*
//
