package jp.co.usagi.batch;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import jp.co.usagi.sales.common.DBUtil;

public class JuchuExtract {

    public static void main(String[] args) throws Exception {
        String dir = args.length > 0 ? args[0] : "/work";
        Connection con = DBUtil.getConnection();
        Statement st = con.createStatement();
        int n1 = 0, n2 = 0, n3 = 0;

        OutputStream out = new BufferedOutputStream(new FileOutputStream(dir + "/TOKUI.DAT"));
        ResultSet rs = st.executeQuery("SELECT tk_cd, tk_nm, sime_kbn, hasu_kbn, kaisyu_m, kaisyu_d, del_flg"
                + " FROM m_tokui ORDER BY tk_cd");
        while (rs.next()) {
            out.write(x(rs.getString(1), 6));
            out.write(x(rs.getString(2), 40));
            out.write(x(rs.getString(3), 2));
            out.write(x(rs.getString(4), 1));
            out.write(x(rs.getString(5), 1));
            out.write(x(rs.getString(6), 2));
            out.write(x(rs.getString(7), 1));
            out.write(x("", 47));
            out.write('\n');
            n1++;
        }
        rs.close();
        out.close();

        out = new BufferedOutputStream(new FileOutputStream(dir + "/SHOHIN.DAT"));
        rs = st.executeQuery("SELECT sh_cd, sh_nm, zei_kbn, tanka FROM m_shohin ORDER BY sh_cd");
        while (rs.next()) {
            out.write(x(rs.getString(1), 6));
            out.write(x(rs.getString(2), 40));
            out.write(x(rs.getString(3), 1));
            out.write(n(rs.getLong(4), 7));
            out.write(x("", 26));
            out.write('\n');
            n2++;
        }
        rs.close();
        out.close();

        out = new BufferedOutputStream(new FileOutputStream(dir + "/JUCHU.DAT"));
        rs = st.executeQuery("SELECT juchu_no, juchu_ymd, tk_cd, sh_cd, suryo, tanka, juchu_kbn, uriage_kin"
                + " FROM t_juchu ORDER BY juchu_no");
        while (rs.next()) {
            out.write(x(rs.getString(1), 8));
            out.write(x(rs.getString(2), 8));
            out.write(x(rs.getString(3), 6));
            out.write(x(rs.getString(4), 6));
            out.write(n(rs.getLong(5), 7));
            out.write(n(rs.getLong(6), 7));
            out.write(x(rs.getString(7), 1));
            long kin = rs.getLong(8);
            out.write((kin < 0 ? "-" : "+").getBytes());
            out.write(n(Math.abs(kin), 11));
            out.write(x("", 25));
            out.write('\n');
            n3++;
        }
        rs.close();
        out.close();
        st.executeUpdate("UPDATE t_juchu SET flg1 = '1' WHERE flg1 = '0'");
        st.close();
        con.close();
        System.out.println("JuchuExtract TOKUI=" + n1 + " SHOHIN=" + n2 + " JUCHU=" + n3);
    }

    static byte[] x(String s, int len) throws Exception {
        byte[] b = new byte[len];
        java.util.Arrays.fill(b, (byte) ' ');
        if (s == null) return b;
        byte[] src = s.getBytes("UTF-8");
        int l = Math.min(src.length, len);
        while (l > 0 && l < src.length && (src[l] & 0xC0) == 0x80) l--;
        System.arraycopy(src, 0, b, 0, l);
        return b;
    }

    static byte[] n(long v, int len) {
        String s = String.valueOf(v);
        while (s.length() < len) s = "0" + s;
        return s.getBytes();
    }
}
