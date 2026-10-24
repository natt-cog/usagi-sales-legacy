<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*,java.sql.*,jp.co.usagi.sales.common.DBUtil" %>
<html>
<head><title>受注照会</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>受注照会</h2>
<% if (request.getAttribute("msg") != null) { %><p class="msg"><%= request.getAttribute("msg") %></p><% } %>
<form action="juchuInquiry.do" method="get">
受注番号 <input type="text" name="no" size="10" value="<%= DBUtil.nvl(request.getParameter("no")) %>">
得意先コード <input type="text" name="tkCd" size="8" value="<%= DBUtil.nvl(request.getParameter("tkCd")) %>">
受注日 <input type="text" name="fromYmd" size="10" value="<%= DBUtil.nvl(request.getParameter("fromYmd")) %>">
～ <input type="text" name="toYmd" size="10" value="<%= DBUtil.nvl(request.getParameter("toYmd")) %>">
<input type="submit" name="search" value="検索">
</form>
<%
List list = (List) request.getAttribute("list");
if (list != null) {
    Connection con = DBUtil.getConnection();
    PreparedStatement ps1 = con.prepareStatement("SELECT tk_nm FROM m_tokui WHERE tk_cd = ?");
    PreparedStatement ps2 = con.prepareStatement("SELECT sh_nm FROM m_shohin WHERE sh_cd = ?");
%>
<p><%= list.size() %> 件　合計金額 <%= String.format("%,d", Long.parseLong((String) request.getAttribute("total"))) %> 円</p>
<table class="list">
<tr><th>受注番号</th><th>受注日</th><th>得意先</th><th>商品</th><th>数量</th><th>単価</th><th>区分</th><th>金額</th><th>備考</th></tr>
<%
    for (int i = 0; i < list.size(); i++) {
        Map m = (Map) list.get(i);
        ps1.setString(1, (String) m.get("tkCd"));
        ResultSet r1 = ps1.executeQuery();
        String tkNm = r1.next() ? r1.getString(1) : "";
        r1.close();
        ps2.setString(1, (String) m.get("shCd"));
        ResultSet r2 = ps2.executeQuery();
        String shNm = r2.next() ? r2.getString(1) : "";
        r2.close();
        String kbn = (String) m.get("kbn");
        String ymd = (String) m.get("ymd");
%>
<tr><td><%= m.get("no") %></td><td><%= ymd.substring(0, 4) + "/" + ymd.substring(4, 6) + "/" + ymd.substring(6) %></td>
<td><%= m.get("tkCd") %> <%= tkNm %></td><td><%= m.get("shCd") %> <%= shNm %></td>
<td class="num"><%= m.get("suryo") %></td><td class="num"><%= String.format("%,d", Long.parseLong((String) m.get("tanka"))) %></td>
<td><%= "2".equals(kbn) ? "返品" : ("3".equals(kbn) ? "無償" : "通常") %></td>
<td class="num"><%= String.format("%,d", Long.parseLong((String) m.get("kin"))) %></td><td><%= m.get("biko") %></td></tr>
<%
    }
    ps1.close();
    ps2.close();
    con.close();
%>
</table>
<% } %>
</div>
</body>
</html>
