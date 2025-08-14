##1 which base image to use
FROM openjdk:11-jre-slim

## set the working directory
WORKDIR /app

## copy project files
COPY . .

# RUN THE BINARY
CMD ["java", "-cp", "JavaApp.jar", "JavaApp"]