package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;
import jp.co.usagi.sales.form.LoginForm;

public class LoginAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        LoginForm f = (LoginForm) form;
        if (f.getUserId() == null) {
            return mapping.findForward("input");
        }
        Connection con = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            ps = con.prepareStatement("SELECT user_nm, kengen FROM m_user WHERE user_id = ? AND password = ?");
            ps.setString(1, f.getUserId());
            ps.setString(2, f.getPassword());
            rs = ps.executeQuery();
            if (!rs.next()) {
                request.setAttribute("msg", "ユーザIDまたはパスワードが違います");
                return mapping.findForward("input");
            }
            HttpSession session = request.getSession(true);
            session.setAttribute("LOGIN_USER", f.getUserId());
            session.setAttribute("LOGIN_NAME", rs.getString(1));
            session.setAttribute("KENGEN", rs.getString(2));
        } finally {
            DBUtil.close(con, ps, rs);
        }
        return mapping.findForward("success");
    }
}
