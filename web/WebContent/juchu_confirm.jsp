<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>
<%
    String kbn = request.getParameter("juchuKbn");
    int suryo = Integer.parseInt(request.getParameter("suryo").trim());
    int tanka = Integer.parseInt((String) request.getAttribute("masterTanka"));
    double ritu = 0;
    if (suryo >= 100) {
        ritu = 5;
    } else if (suryo >= 50) {
        ritu = 3;
    }
    int netTanka = (int) (tanka * (100 - ritu) / 100);
    long kin = (long) suryo * netTanka;
    if ("2".equals(kbn)) {
        kin = -kin;
    } else if ("3".equals(kbn)) {
        kin = 0;
    }
    String kbnNm = "2".equals(kbn) ? "返品" : ("3".equals(kbn) ? "無償サンプル" : "通常");
%>
<html>
<head><title>受注入力（確認）</title><link rel="stylesheet" href="common.css"></head>
<body>
<%@ include file="header.jsp" %>
<div class="main">
<h2>受注入力（確認）</h2>
<p>以下の内容で登録します。</p>
<html:form action="/juchuRegist" method="post">
<table class="list">
<tr><th>受注日</th><td><bean:write name="juchuForm" property="juchuYmd"/></td></tr>
<tr><th>得意先</th><td><bean:write name="juchuForm" property="tkCd"/> <%= request.getAttribute("tkNm") %></td></tr>
<tr><th>商品</th><td><bean:write name="juchuForm" property="shCd"/> <%= request.getAttribute("shNm") %><%= "1".equals(request.getAttribute("zeiKbn")) ? "（軽減税率対象）" : "" %></td></tr>
<tr><th>数量</th><td class="num"><%= suryo %></td></tr>
<tr><th>単価</th><td class="num"><%= String.format("%,d", netTanka) %><% if (ritu > 0) { %>（定価 <%= String.format("%,d", tanka) %> から <%= (int) ritu %>% 引き）<% } %></td></tr>
<tr><th>受注区分</th><td><%= kbnNm %></td></tr>
<tr><th>金額（税抜）</th><td class="num"><%= String.format("%,d", kin) %></td></tr>
<tr><th>備考</th><td><bean:write name="juchuForm" property="biko"/></td></tr>
</table>
<html:hidden property="juchuYmd"/>
<html:hidden property="tkCd"/>
<html:hidden property="shCd"/>
<html:hidden property="suryo"/>
<html:hidden property="juchuKbn"/>
<html:hidden property="biko"/>
<input type="hidden" name="tanka" value="<%= netTanka %>">
<input type="hidden" name="nebikiRitu" value="<%= ritu %>">
<input type="hidden" name="uriageKin" value="<%= kin %>">
<html:submit value="登録"/>
<input type="button" value="戻る" onclick="history.back()">
</html:form>
</div>
</body>
</html>
