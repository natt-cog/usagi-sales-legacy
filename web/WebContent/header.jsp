<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<div class="head">株式会社うさぎ商事　販売管理システム　
<% if (session.getAttribute("LOGIN_USER") != null) { %>
　<%= session.getAttribute("LOGIN_NAME") %> さん　<a href="menu.do">メニュー</a>　<a href="logout.do">ログアウト</a>
<% } %>
</div>
