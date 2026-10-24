package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;

public class TokuiEditAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        String tkCd = DBUtil.nvl(request.getParameter("tkCd"));
        Connection con = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            if ("update".equals(request.getParameter("mode"))) {
                ps = con.prepareStatement("UPDATE m_tokui SET tk_nm = ?, tel = ?, sime_kbn = ?, hasu_kbn = ?,"
                        + " gendo = ?, a4 = ?, upd_ymd = ? WHERE tk_cd = ?");
                ps.setString(1, request.getParameter("tkNm"));
                ps.setString(2, request.getParameter("tel"));
                ps.setString(3, request.getParameter("simeKbn"));
                ps.setString(4, request.getParameter("hasuKbn"));
                ps.setLong(5, Long.parseLong(request.getParameter("gendo")));
                ps.setString(6, request.getParameter("tanto"));
                ps.setString(7, new SimpleDateFormat("yyyyMMdd").format(new Date()));
                ps.setString(8, tkCd);
                ps.executeUpdate();
                ps.close();
                request.setAttribute("msg", "更新しました");
            }
            ps = con.prepareStatement("SELECT * FROM m_tokui WHERE tk_cd = ?");
            ps.setString(1, tkCd);
            rs = ps.executeQuery();
            if (rs.next()) {
                HashMap m = new HashMap();
                m.put("tkCd", rs.getString("tk_cd"));
                m.put("tkNm", rs.getString("tk_nm"));
                m.put("tel", rs.getString("tel"));
                m.put("simeKbn", rs.getString("sime_kbn"));
                m.put("hasuKbn", rs.getString("hasu_kbn"));
                m.put("gendo", rs.getString("gendo"));
                m.put("tanto", rs.getString("a4"));
                request.setAttribute("tokui", m);
            }
        } finally {
            DBUtil.close(con, ps, rs);
        }
        return mapping.findForward("success");
    }
}
