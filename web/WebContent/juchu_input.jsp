<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<html>
<head><title>受注入力</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>受注入力</h2>
<% if (request.getAttribute("msg") != null) { %><p class="msg"><%= request.getAttribute("msg") %></p><% } %>
<html:form action="/juchuConfirm" method="post">
<table>
<tr><td>受注日</td><td><html:text property="juchuYmd" size="10" maxlength="8"/>（YYYYMMDD）</td></tr>
<tr><td>得意先コード</td><td><html:text property="tkCd" size="8" maxlength="6"/></td></tr>
<tr><td>商品</td><td><html:select property="shCd">
<%
List list = (List) request.getAttribute("shohinList");
for (int i = 0; list != null && i < list.size(); i++) {
    Map m = (Map) list.get(i);
%>
<html:option value="<%= (String) m.get(\"shCd\") %>"><%= m.get("shCd") %> <%= m.get("shNm") %>（<%= m.get("tanka") %>円）</html:option>
<% } %>
</html:select></td></tr>
<tr><td>数量</td><td><html:text property="suryo" size="6" maxlength="5"/></td></tr>
<tr><td>受注区分</td><td><html:select property="juchuKbn">
<html:option value="1">1:通常</html:option>
<html:option value="2">2:返品</html:option>
<html:option value="3">3:無償サンプル</html:option>
</html:select></td></tr>
<tr><td>備考</td><td><html:text property="biko" size="40" maxlength="30"/></td></tr>
</table>
<html:submit value="確認"/>
</html:form>
</div>
</body>
</html>
