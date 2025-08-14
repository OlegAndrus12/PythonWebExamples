FROM node:24.0-slim

WORKDIR /app

COPY package-lock.json package.json /app/
RUN npm install

COPY . .
EXPOSE 3000

CMD [ "node", "app.js" ]