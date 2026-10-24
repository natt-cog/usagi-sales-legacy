package jp.co.usagi.sales.common;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DBUtil {

    private static final String URL = "jdbc:postgresql://db:5432/usagi";
    private static final String USER = "usagi";
    private static final String PASS = "usagi";

    public static Connection getConnection() throws SQLException {
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            throw new SQLException(e.toString());
        }
        String url = System.getProperty("usagi.db.url", URL);
        return DriverManager.getConnection(url, USER, PASS);
    }

    public static void close(Connection con, Statement st, ResultSet rs) {
        try { if (rs != null) rs.close(); } catch (Exception e) { }
        try { if (st != null) st.close(); } catch (Exception e) { }
        try { if (con != null) con.close(); } catch (Exception e) { }
    }

    public static String nvl(String s) {
        return s == null ? "" : s.trim();
    }
}
