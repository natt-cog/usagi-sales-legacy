<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*,jp.co.usagi.sales.common.DBUtil" %>
<%!
    String fmt(Object o) {
        if (o == null) return "";
        return String.format("%,d", Long.parseLong((String) o));
    }
    String ymd(Object o) {
        String s = (String) o;
        return s.substring(0, 4) + "/" + s.substring(4, 6) + "/" + s.substring(6);
    }
%>
<html>
<head><title>請求照会</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>請求照会</h2>
<% if (request.getAttribute("msg") != null) { %><p class="msg"><%= request.getAttribute("msg") %></p><% } %>
<form action="seikyuInquiry.do" method="get">
請求番号 <input type="text" name="no" size="14" value="<%= DBUtil.nvl(request.getParameter("no")) %>">
得意先コード <input type="text" name="tkCd" size="8" value="<%= DBUtil.nvl(request.getParameter("tkCd")) %>">
請求年月 <input type="text" name="fromYm" size="8" value="<%= DBUtil.nvl(request.getParameter("fromYm")) %>">
～ <input type="text" name="toYm" size="8" value="<%= DBUtil.nvl(request.getParameter("toYm")) %>">（YYYYMM）
<input type="submit" name="search" value="検索">
</form>
<%
List list = (List) request.getAttribute("list");
if (list != null) {
%>
<p><%= list.size() %> 件　未入金合計 <%= fmt(request.getAttribute("total")) %> 円</p>
<table class="list">
<tr><th>請求番号</th><th>請求年月</th><th>請求期間</th><th>件数</th><th>売上金額</th><th>消費税</th><th>（内 10%）</th><th>（内 軽減8%）</th><th>（内 旧税率）</th><th>請求金額</th><th>入金額</th><th>消込</th></tr>
<%
    for (int i = 0; i < list.size(); i++) {
        Map m = (Map) list.get(i);
        String kesi = (String) m.get("kesi");
%>
<tr><td><%= m.get("no") %></td><td><%= m.get("ym") %></td><td><%= ymd(m.get("fromYmd")) %>～<%= ymd(m.get("toYmd")) %></td>
<td class="num"><%= m.get("kensu") %></td><td class="num"><%= fmt(m.get("uriage")) %></td><td class="num"><%= fmt(m.get("zei")) %></td>
<td class="num"><%= fmt(m.get("zei10")) %></td><td class="num"><%= fmt(m.get("zei8k")) %></td><td class="num"><%= fmt(m.get("zeiSonota")) %></td>
<td class="num"><%= fmt(m.get("kin")) %></td><td class="num"><%= fmt(m.get("nyukin")) %></td>
<td><%= "2".equals(kesi) ? "済" : ("1".equals(kesi) ? "一部" : "未") %></td></tr>
<% } %>
</table>
<% } %>
</div>
</body>
</html>
