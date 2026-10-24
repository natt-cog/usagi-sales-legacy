<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*" %>
<html>
<head><title>得意先照会</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>得意先照会</h2>
<form action="tokuiSearch.do" method="get">
得意先コード <input type="text" name="tkCd" size="8" value="<%= request.getParameter("tkCd") == null ? "" : request.getParameter("tkCd") %>">
得意先名 <input type="text" name="tkNm" size="20" value="<%= request.getParameter("tkNm") == null ? "" : request.getParameter("tkNm") %>">
<input type="submit" name="search" value="検索">
</form>
<%
List list = (List) request.getAttribute("list");
if (list != null) {
%>
<p><%= list.size() %> 件</p>
<table class="list">
<tr><th>コード</th><th>得意先名</th><th>電話番号</th><th>締日</th><th>端数</th><th>回収</th><th>与信限度額</th><th>担当</th><th>状態</th></tr>
<%
    for (int i = 0; i < list.size(); i++) {
        Map m = (Map) list.get(i);
%>
<tr><td><%= m.get("tkCd") %></td><td><%= m.get("tkNm") %></td><td><%= m.get("tel") %></td>
<td><%= m.get("sime") %></td><td><%= m.get("hasu") %></td><td><%= m.get("kaisyu") %></td>
<td class="num"><%= String.format("%,d", Long.parseLong((String) m.get("gendo"))) %></td>
<td><%= m.get("tanto") %></td><td><%= m.get("del") %></td></tr>
<% } %>
</table>
<% } %>
</div>
</body>
</html>
