FROM node:alpine as build-stage

ARG backend_url
ENV VITE_BACKEND_URL $backend_url

WORKDIR /usr/src/app

COPY ./ ./

RUN npm install
RUN npm run build

FROM nginx 
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /usr/src/app/dist /usr/share/nginx/html

EXPOSE 80