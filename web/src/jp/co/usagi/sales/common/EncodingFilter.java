package jp.co.usagi.sales.common;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

public class EncodingFilter implements Filter {
    private String encoding = "UTF-8";

    public void init(FilterConfig config) throws ServletException {
        if (config.getInitParameter("encoding") != null) {
            encoding = config.getInitParameter("encoding");
        }
    }

    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        req.setCharacterEncoding(encoding);
        chain.doFilter(req, res);
    }

    public void destroy() {
    }
}
