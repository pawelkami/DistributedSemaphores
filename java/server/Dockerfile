FROM openjdk:alpine

EXPOSE 8080

RUN mkdir /server
COPY target/*.jar /server/

CMD ["java", "-jar", "/server/semserver-1.0-SNAPSHOT-jar-with-dependencies.jar"]