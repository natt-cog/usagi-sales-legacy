package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.util.Date;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;
import jp.co.usagi.sales.form.JuchuForm;

public class JuchuRegistAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        String user = (String) request.getSession().getAttribute("LOGIN_USER");
        if (user == null) {
            return mapping.findForward("login");
        }
        JuchuForm f = (JuchuForm) form;
        Connection con = null;
        Statement st = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        String no = null;
        try {
            con = DBUtil.getConnection();
            con.setAutoCommit(false);
            st = con.createStatement();
            rs = st.executeQuery("SELECT MAX(juchu_no) FROM t_juchu");
            long n = 10000000;
            if (rs.next() && rs.getString(1) != null) {
                n = Long.parseLong(rs.getString(1));
            }
            no = String.valueOf(n + 1);
            ps = con.prepareStatement("INSERT INTO t_juchu (juchu_no, juchu_ymd, tk_cd, sh_cd, suryo, tanka,"
                    + " juchu_kbn, uriage_kin, nebiki_ritu, biko, flg1, wk_x1, ins_ymd, ins_user)"
                    + " VALUES (?,?,?,?,?,?,?,?,?,?,'0',' ',?,?)");
            ps.setString(1, no);
            ps.setString(2, f.getJuchuYmd());
            ps.setString(3, f.getTkCd());
            ps.setString(4, f.getShCd());
            ps.setInt(5, Integer.parseInt(f.getSuryo()));
            ps.setInt(6, Integer.parseInt(f.getTanka()));
            ps.setString(7, f.getJuchuKbn());
            ps.setLong(8, Long.parseLong(f.getUriageKin()));
            ps.setDouble(9, Double.parseDouble(f.getNebikiRitu()));
            ps.setString(10, DBUtil.nvl(f.getBiko()));
            ps.setString(11, new SimpleDateFormat("yyyyMMdd").format(new Date()));
            ps.setString(12, user);
            ps.executeUpdate();
            con.commit();
        } catch (Exception e) {
            if (con != null) con.rollback();
            throw e;
        } finally {
            if (ps != null) ps.close();
            DBUtil.close(con, st, rs);
        }
        request.setAttribute("juchuNo", no);
        return mapping.findForward("success");
    }
}
