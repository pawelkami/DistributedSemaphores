FROM openjdk:alpine

EXPOSE 8080

RUN mkdir /client
COPY target/*.jar /client/

ENTRYPOINT sleep 100000000

#CMD ["java", "-jar", "/client/semclient-1.0-SNAPSHOT.jar"]