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

public class TokuiSearchAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        String tkCd = DBUtil.nvl(request.getParameter("tkCd"));
        String tkNm = DBUtil.nvl(request.getParameter("tkNm"));
        if (request.getParameter("search") == null) {
            return mapping.findForward("success");
        }
        String sql = "SELECT tk_cd, tk_nm, tel, sime_kbn, hasu_kbn, kaisyu_m, kaisyu_d, gendo, a4, del_flg"
                + " FROM m_tokui WHERE 1 = 1";
        if (tkCd.length() > 0) {
            sql += " AND tk_cd LIKE '" + tkCd + "%'";
        }
        if (tkNm.length() > 0) {
            sql += " AND (tk_nm LIKE '%" + tkNm + "%' OR tk_kana LIKE '%" + tkNm + "%')";
        }
        sql += " ORDER BY tk_cd";
        ArrayList list = new ArrayList();
        Connection con = null;
        Statement st = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            st = con.createStatement();
            rs = st.executeQuery(sql);
            while (rs.next()) {
                HashMap m = new HashMap();
                m.put("tkCd", rs.getString("tk_cd"));
                m.put("tkNm", rs.getString("tk_nm"));
                m.put("tel", rs.getString("tel"));
                String sime = rs.getString("sime_kbn");
                if ("99".equals(sime)) {
                    m.put("sime", "末日");
                } else {
                    m.put("sime", Integer.parseInt(sime) + "日");
                }
                String hasu = rs.getString("hasu_kbn");
                if ("1".equals(hasu)) {
                    m.put("hasu", "切捨て");
                } else if ("2".equals(hasu)) {
                    m.put("hasu", "四捨五入");
                } else if ("3".equals(hasu)) {
                    m.put("hasu", "切上げ");
                } else {
                    m.put("hasu", hasu);
                }
                String km = rs.getString("kaisyu_m");
                String kd = rs.getString("kaisyu_d");
                String kaisyu = "1".equals(km) ? "翌月" : ("2".equals(km) ? "翌々月" : "当月");
                kaisyu += "31".equals(kd) ? "末日" : Integer.parseInt(kd) + "日";
                m.put("kaisyu", kaisyu);
                m.put("gendo", rs.getString("gendo"));
                m.put("tanto", rs.getString("a4"));
                m.put("del", "1".equals(rs.getString("del_flg")) ? "取引停止" : "");
                list.add(m);
            }
        } finally {
            DBUtil.close(con, st, rs);
        }
        request.setAttribute("list", list);
        return mapping.findForward("success");
    }
}
