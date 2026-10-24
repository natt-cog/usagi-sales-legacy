<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*" %>
<html>
<head><title>得意先メンテナンス</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>得意先メンテナンス</h2>
<% if (request.getAttribute("msg") != null) { %><p class="msg"><%= request.getAttribute("msg") %></p><% } %>
<form action="tokuiEdit.do" method="get">
得意先コード <input type="text" name="tkCd" size="8" value="<%= request.getParameter("tkCd") == null ? "" : request.getParameter("tkCd") %>">
<input type="submit" value="表示">
</form>
<%
Map t = (Map) request.getAttribute("tokui");
if (t != null) {
%>
<form action="tokuiEdit.do" method="post">
<input type="hidden" name="mode" value="update">
<input type="hidden" name="tkCd" value="<%= t.get("tkCd") %>">
<table>
<tr><td>得意先名</td><td><input type="text" name="tkNm" size="40" value="<%= t.get("tkNm") %>"></td></tr>
<tr><td>電話番号</td><td><input type="text" name="tel" size="15" value="<%= t.get("tel") %>"></td></tr>
<tr><td>締日区分</td><td><input type="text" name="simeKbn" size="2" value="<%= t.get("simeKbn") %>">（15/20/99）</td></tr>
<tr><td>端数区分</td><td><input type="text" name="hasuKbn" size="1" value="<%= t.get("hasuKbn") %>"></td></tr>
<tr><td>与信限度額</td><td><input type="text" name="gendo" size="11" value="<%= t.get("gendo") %>"></td></tr>
<tr><td>担当</td><td><input type="text" name="tanto" size="4" value="<%= t.get("tanto") %>"></td></tr>
</table>
<input type="submit" value="更新">
</form>
<% } %>
</div>
</body>
</html>
