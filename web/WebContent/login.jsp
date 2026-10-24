<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<html>
<head><title>ログイン</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>ログイン</h2>
<% if (request.getAttribute("msg") != null) { %><p class="msg"><%= request.getAttribute("msg") %></p><% } %>
<form action="login.do" method="post">
<table>
<tr><td>ユーザID</td><td><input type="text" name="userId" size="12"></td></tr>
<tr><td>パスワード</td><td><input type="password" name="password" size="12"></td></tr>
</table>
<input type="submit" value="ログイン">
</form>
</div>
</body>
</html>
