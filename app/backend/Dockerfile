FROM node:alpine

WORKDIR /usr/src/app

COPY ./ ./

RUN npm install
EXPOSE 8000

CMD ["npm", "run", "dev"]