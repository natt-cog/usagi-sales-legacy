-- 販売管理システム
CREATE TABLE m_user (
    user_id     VARCHAR(10) PRIMARY KEY,
    password    VARCHAR(20) NOT NULL,
    user_nm     VARCHAR(40),
    kengen      CHAR(1),
    upd_ymd     CHAR(8)
);
CREATE TABLE m_tokui (
    tk_cd       CHAR(6) PRIMARY KEY,
    tk_nm       VARCHAR(60) NOT NULL,
    tk_kana     VARCHAR(60),
    yubin       CHAR(8),
    adr         VARCHAR(100),
    tel         VARCHAR(15),
    sime_kbn    CHAR(2),
    hasu_kbn    CHAR(1),
    kaisyu_m    CHAR(1),
    kaisyu_d    CHAR(2),
    gendo       NUMERIC(11),
    a4          CHAR(4),
    del_flg     CHAR(1) DEFAULT '0',
    ins_ymd     CHAR(8),
    upd_ymd     CHAR(8)
);
CREATE TABLE m_shohin (
    sh_cd       CHAR(6) PRIMARY KEY,
    sh_nm       VARCHAR(60) NOT NULL,
    bunrui      CHAR(2),
    zei_kbn     CHAR(1),
    tanka       NUMERIC(9),
    tani        VARCHAR(6),
    zaiko       NUMERIC(7),
    upd_ymd     CHAR(8)
);
CREATE TABLE t_juchu (
    juchu_no    CHAR(8) PRIMARY KEY,
    juchu_ymd   CHAR(8) NOT NULL,
    tk_cd       CHAR(6) NOT NULL,
    sh_cd       CHAR(6) NOT NULL,
    suryo       NUMERIC(7),
    tanka       NUMERIC(9),
    juchu_kbn   CHAR(1),
    uriage_kin  NUMERIC(11),
    nebiki_ritu NUMERIC(3,1),
    biko        VARCHAR(60),
    flg1        CHAR(1) DEFAULT '0',
    wk_x1       CHAR(1),
    ins_ymd     CHAR(8),
    ins_user    VARCHAR(10)
);
CREATE INDEX t_juchu_ix1 ON t_juchu (tk_cd, juchu_ymd);
CREATE TABLE t_seikyu (
    seikyu_no   CHAR(12) PRIMARY KEY,
    tk_cd       CHAR(6) NOT NULL,
    seikyu_ym   CHAR(6),
    from_ymd    CHAR(8),
    to_ymd      CHAR(8),
    kensu       NUMERIC(5),
    uriage_kin  NUMERIC(11),
    zei_kin     NUMERIC(11),
    seikyu_kin  NUMERIC(11),
    nyukin_kin  NUMERIC(11),
    kesi_kbn    CHAR(1),
    zei10_taisyo NUMERIC(11),
    zei10_kin   NUMERIC(11),
    zei8k_taisyo NUMERIC(11),
    zei8k_kin   NUMERIC(11),
    zeisonota_taisyo NUMERIC(11),
    zeisonota_kin NUMERIC(11),
    torikomi_ymd CHAR(8)
);
