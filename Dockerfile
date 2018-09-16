FROM alpine:latest
  
MAINTAINER Yaniv Rozenboim <yanivr@radware.com>

RUN apk add --no-cache bash python py-pip \ 
    && pip install --upgrade pip \ 
    && pip install exabgp \
    && mkdir -p /etc/exabgp \
    && exabgp --fi > /etc/exabgp/exabgp.env \
    && sed -i 's/bind = .*/bind = 0.0.0.0/' /etc/exabgp/exabgp.env

COPY exabgp.conf http_api.py /etc/exabgp/
COPY entrypoint.sh /bin/

#ENTRYPOINT ["exabgp", "/etc/exabgp/exabgp.conf"]
ENTRYPOINT ["entrypoint.sh"]

EXPOSE 179
EXPOSE 5001
