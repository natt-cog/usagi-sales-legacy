package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashMap;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;

public class JuchuInquiryAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        String tkCd = DBUtil.nvl(request.getParameter("tkCd"));
        String no = DBUtil.nvl(request.getParameter("no"));
        String fromYmd = DBUtil.nvl(request.getParameter("fromYmd"));
        String toYmd = DBUtil.nvl(request.getParameter("toYmd"));
        if (request.getParameter("search") == null) {
            return mapping.findForward("success");
        }
        if (tkCd.length() == 0 && no.length() == 0) {
            request.setAttribute("msg", "得意先コードか番号を入力してください");
            return mapping.findForward("success");
        }
        String sql = "SELECT * FROM t_juchu WHERE 1 = 1";
        if (no.length() > 0) {
            sql += " AND juchu_no = '" + no + "'";
        }
        if (tkCd.length() > 0) {
            sql += " AND tk_cd = '" + tkCd + "'";
        }
        if (fromYmd.length() > 0) {
            sql += " AND juchu_ymd >= '" + fromYmd + "'";
        }
        if (toYmd.length() > 0) {
            sql += " AND juchu_ymd <= '" + toYmd + "'";
        }
        sql += " ORDER BY juchu_no DESC LIMIT 100";
        ArrayList list = new ArrayList();
        long total = 0;
        Connection con = null;
        Statement st = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            st = con.createStatement();
            rs = st.executeQuery(sql);
            while (rs.next()) {
                HashMap m = new HashMap();
                m.put("no", rs.getString("juchu_no"));
                m.put("ymd", rs.getString("juchu_ymd"));
                m.put("tkCd", rs.getString("tk_cd"));
                m.put("shCd", rs.getString("sh_cd"));
                m.put("suryo", rs.getString("suryo"));
                m.put("tanka", rs.getString("tanka"));
                m.put("kbn", rs.getString("juchu_kbn"));
                m.put("kin", rs.getString("uriage_kin"));
                m.put("biko", rs.getString("biko"));
                total += rs.getLong("uriage_kin");
                list.add(m);
            }
        } finally {
            DBUtil.close(con, st, rs);
        }
        request.setAttribute("list", list);
        request.setAttribute("total", String.valueOf(total));
        return mapping.findForward("success");
    }
}
