package jp.co.usagi.sales.form;

import org.apache.struts.action.ActionForm;

public class JuchuForm extends ActionForm {
    private String juchuYmd;
    private String tkCd;
    private String shCd;
    private String suryo;
    private String juchuKbn;
    private String biko;
    private String tanka;
    private String nebikiRitu;
    private String uriageKin;

    public String getJuchuYmd() { return juchuYmd; }
    public void setJuchuYmd(String s) { juchuYmd = s; }
    public String getTkCd() { return tkCd; }
    public void setTkCd(String s) { tkCd = s; }
    public String getShCd() { return shCd; }
    public void setShCd(String s) { shCd = s; }
    public String getSuryo() { return suryo; }
    public void setSuryo(String s) { suryo = s; }
    public String getJuchuKbn() { return juchuKbn; }
    public void setJuchuKbn(String s) { juchuKbn = s; }
    public String getBiko() { return biko; }
    public void setBiko(String s) { biko = s; }
    public String getTanka() { return tanka; }
    public void setTanka(String s) { tanka = s; }
    public String getNebikiRitu() { return nebikiRitu; }
    public void setNebikiRitu(String s) { nebikiRitu = s; }
    public String getUriageKin() { return uriageKin; }
    public void setUriageKin(String s) { uriageKin = s; }
}
