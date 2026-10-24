FROM tomcat:8.5-jdk8-temurin
ENV TZ=Asia/Tokyo
RUN rm -rf /usr/local/tomcat/webapps/*
COPY WebContent /usr/local/tomcat/webapps/usagi
COPY src /tmp/src
RUN mkdir -p /usr/local/tomcat/webapps/usagi/WEB-INF/classes \
 && javac -encoding UTF-8 -nowarn -source 1.8 -target 1.8 \
      -cp "/usr/local/tomcat/lib/servlet-api.jar:/usr/local/tomcat/webapps/usagi/WEB-INF/lib/*" \
      -d /usr/local/tomcat/webapps/usagi/WEB-INF/classes $(find /tmp/src -name '*.java') \
 && rm -rf /tmp/src
EXPOSE 8080
