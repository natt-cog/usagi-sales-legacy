package jp.co.usagi.batch;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.text.SimpleDateFormat;
import java.util.Date;
import jp.co.usagi.sales.common.DBUtil;

public class SeikyuImport {

    public static void main(String[] args) throws Exception {
        String file = args.length > 0 ? args[0] : "/work/SKKEKKA.DAT";
        String ymd = args.length > 1 ? args[1] : new SimpleDateFormat("yyyyMMdd").format(new Date());
        Connection con = DBUtil.getConnection();
        con.setAutoCommit(false);
        con.createStatement().executeUpdate("DELETE FROM t_seikyu");
        PreparedStatement ps = con.prepareStatement("INSERT INTO t_seikyu VALUES"
                + " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");
        BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(file), "ISO-8859-1"));
        String line;
        int cnt = 0;
        while ((line = in.readLine()) != null) {
            if (line.trim().length() == 0) continue;
            ps.setString(1, line.substring(0, 12));
            ps.setString(2, line.substring(12, 18));
            ps.setString(3, line.substring(18, 24));
            ps.setString(4, line.substring(24, 32));
            ps.setString(5, line.substring(32, 40));
            ps.setInt(6, Integer.parseInt(line.substring(40, 45)));
            ps.setLong(7, sls(line, 45));
            ps.setLong(8, sls(line, 57));
            ps.setLong(9, sls(line, 69));
            ps.setLong(10, sls(line, 81));
            ps.setString(11, line.substring(93, 94));
            ps.setLong(12, sls(line, 94));
            ps.setLong(13, sls(line, 106));
            ps.setLong(14, sls(line, 118));
            ps.setLong(15, sls(line, 130));
            ps.setLong(16, sls(line, 142));
            ps.setLong(17, sls(line, 154));
            ps.setString(18, ymd);
            ps.executeUpdate();
            cnt++;
        }
        in.close();
        con.commit();
        ps.close();
        con.close();
        System.out.println("SeikyuImport SEIKYU=" + cnt);
    }

    static long sls(String s, int p) {
        long v = Long.parseLong(s.substring(p + 1, p + 12));
        return s.charAt(p) == '-' ? -v : v;
    }
}
