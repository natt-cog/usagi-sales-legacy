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

public class SeikyuInquiryAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        String tkCd = DBUtil.nvl(request.getParameter("tkCd"));
        String no = DBUtil.nvl(request.getParameter("no"));
        String fromYm = DBUtil.nvl(request.getParameter("fromYm"));
        String toYm = DBUtil.nvl(request.getParameter("toYm"));
        if (request.getParameter("search") == null) {
            return mapping.findForward("success");
        }
        if (tkCd.length() == 0 && no.length() == 0) {
            request.setAttribute("msg", "得意先コードか番号を入力してください");
            return mapping.findForward("success");
        }
        String sql = "SELECT * FROM t_seikyu WHERE 1 = 1";
        if (no.length() > 0) {
            sql += " AND seikyu_no = '" + no + "'";
        }
        if (tkCd.length() > 0) {
            sql += " AND tk_cd = '" + tkCd + "'";
        }
        if (fromYm.length() > 0) {
            sql += " AND seikyu_ym >= '" + fromYm + "'";
        }
        if (toYm.length() > 0) {
            sql += " AND seikyu_ym < '" + toYm + "'";
        }
        sql += " ORDER BY seikyu_ym DESC, seikyu_no LIMIT 100";
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
                m.put("no", rs.getString("seikyu_no"));
                m.put("ym", rs.getString("seikyu_ym"));
                m.put("tkCd", rs.getString("tk_cd"));
                m.put("fromYmd", rs.getString("from_ymd"));
                m.put("toYmd", rs.getString("to_ymd"));
                m.put("kensu", rs.getString("kensu"));
                m.put("uriage", rs.getString("uriage_kin"));
                m.put("zei", rs.getString("zei_kin"));
                m.put("kin", rs.getString("seikyu_kin"));
                m.put("nyukin", rs.getString("nyukin_kin"));
                m.put("kesi", rs.getString("kesi_kbn"));
                m.put("zei10", rs.getString("zei10_kin"));
                m.put("zei8k", rs.getString("zei8k_kin"));
                m.put("zeiSonota", rs.getString("zeisonota_kin"));
                total += rs.getLong("seikyu_kin") - rs.getLong("nyukin_kin");
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
