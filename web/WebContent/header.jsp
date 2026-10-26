<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<div class="head">株式会社うさぎ商事　販売管理システム　
<% if (session.getAttribute("LOGIN_USER") != null) { %>
　<%= session.getAttribute("LOGIN_NAME") %> さん　<a href="menu.do">メニュー</a>　<a href="logout.do">ログアウト</a>
<% } %>
<a href="#" id="theme-toggle" class="theme-toggle" onclick="return usagiToggleTheme();">ダークモード</a>
</div>
<script type="text/javascript">
function usagiApplyTheme(dark) {
    var b = document.body;
    b.className = (' ' + b.className + ' ').replace(' dark ', ' ').replace(/^\s+|\s+$/g, '');
    if (dark) { b.className = b.className ? b.className + ' dark' : 'dark'; }
    var t = document.getElementById('theme-toggle');
    if (t) { t.innerHTML = dark ? 'ライトモード' : 'ダークモード'; }
}
function usagiToggleTheme() {
    var dark = !/(^|\s)dark(\s|$)/.test(document.body.className);
    try { window.localStorage.setItem('usagi.theme', dark ? 'dark' : 'light'); } catch (e) {}
    usagiApplyTheme(dark);
    return false;
}
(function () {
    var saved = null;
    try { saved = window.localStorage.getItem('usagi.theme'); } catch (e) {}
    var dark = saved ? saved === 'dark'
        : !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
    usagiApplyTheme(dark);
})();
</script>
