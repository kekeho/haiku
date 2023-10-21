FROM caddy:2-alpine

RUN mkdir /conf
COPY ./Caddyfile /conf

CMD ["caddy", "run", "--config", "/conf/Caddyfile", "--adapter", "caddyfile"]
