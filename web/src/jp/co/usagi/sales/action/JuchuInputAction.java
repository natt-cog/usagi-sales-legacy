package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;
import jp.co.usagi.sales.form.JuchuForm;

public class JuchuInputAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        JuchuForm f = (JuchuForm) form;
        if (f.getJuchuYmd() == null || f.getJuchuYmd().length() == 0) {
            f.setJuchuYmd(new SimpleDateFormat("yyyyMMdd").format(new Date()));
        }
        if (f.getJuchuKbn() == null) {
            f.setJuchuKbn("1");
        }
        ArrayList list = new ArrayList();
        Connection con = null;
        Statement st = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            st = con.createStatement();
            rs = st.executeQuery("SELECT sh_cd, sh_nm, tanka FROM m_shohin ORDER BY sh_cd");
            while (rs.next()) {
                HashMap m = new HashMap();
                m.put("shCd", rs.getString(1));
                m.put("shNm", rs.getString(2));
                m.put("tanka", rs.getString(3));
                list.add(m);
            }
        } finally {
            DBUtil.close(con, st, rs);
        }
        request.setAttribute("shohinList", list);
        return mapping.findForward("success");
    }
}
