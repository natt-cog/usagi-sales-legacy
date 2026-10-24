<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<html>
<head><title>受注入力（完了）</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>受注入力（完了）</h2>
<p>受注番号 <b><%= request.getAttribute("juchuNo") %></b> で登録しました。</p>
<p><a href="juchuInquiry.do?no=<%= request.getAttribute("juchuNo") %>&search=1">受注照会へ</a>　<a href="juchuInput.do">続けて入力</a></p>
</div>
</body>
</html>
