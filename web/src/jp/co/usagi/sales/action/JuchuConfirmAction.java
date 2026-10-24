package jp.co.usagi.sales.action;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import jp.co.usagi.sales.common.DBUtil;
import jp.co.usagi.sales.form.JuchuForm;

public class JuchuConfirmAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) throws Exception {
        if (request.getSession().getAttribute("LOGIN_USER") == null) {
            return mapping.findForward("login");
        }
        JuchuForm f = (JuchuForm) form;
        String msg = null;
        String ymd = DBUtil.nvl(f.getJuchuYmd());
        if (!ymd.matches("[0-9]{8}")) {
            msg = "受注日はYYYYMMDDで入力してください";
        }
        int suryo = 0;
        if (msg == null) {
            try {
                suryo = Integer.parseInt(DBUtil.nvl(f.getSuryo()));
            } catch (NumberFormatException e) {
                suryo = 0;
            }
            if (suryo <= 0) {
                msg = "数量を正しく入力してください";
            }
        }
        Connection con = null;
        PreparedStatement ps = null;
        ResultSet rs = null;
        try {
            con = DBUtil.getConnection();
            if (msg == null) {
                ps = con.prepareStatement("SELECT tk_nm, del_flg FROM m_tokui WHERE tk_cd = ?");
                ps.setString(1, DBUtil.nvl(f.getTkCd()));
                rs = ps.executeQuery();
                if (!rs.next()) {
                    msg = "得意先コードが登録されていません";
                } else if ("1".equals(rs.getString(2))) {
                    msg = "取引停止中の得意先です";
                } else {
                    request.setAttribute("tkNm", rs.getString(1));
                }
                rs.close();
                ps.close();
            }
            if (msg == null) {
                ps = con.prepareStatement("SELECT sh_nm, tanka, zei_kbn FROM m_shohin WHERE sh_cd = ?");
                ps.setString(1, DBUtil.nvl(f.getShCd()));
                rs = ps.executeQuery();
                if (!rs.next()) {
                    msg = "商品コードが登録されていません";
                } else {
                    request.setAttribute("shNm", rs.getString(1));
                    request.setAttribute("masterTanka", rs.getString(2));
                    request.setAttribute("zeiKbn", rs.getString(3));
                }
            }
        } finally {
            DBUtil.close(con, ps, rs);
        }
        if (msg != null) {
            request.setAttribute("msg", msg);
            return mapping.findForward("input");
        }
        return mapping.findForward("success");
    }
}
