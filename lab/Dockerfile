FROM debian:bookworm-slim

LABEL version="2.670" \
      webmin.version="2.670" \
      webmin.commit="3a2b2b8671c0669c129f5275b3dd1853106ae02b"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C \
    WEBMIN_CONFIG=/etc/webmin \
    WEBMIN_VAR=/var/webmin \
    PERLLIB=/usr/share/webmin \
    LIBROOT=/usr/share/webmin

RUN apt-get update \
    && echo "postfix postfix/main_mailer_type select Local only" | debconf-set-selections \
    && echo "postfix postfix/mailname string lab.local" | debconf-set-selections \
    && apt-get install -y --no-install-recommends \
        adduser \
        ca-certificates \
        hostname \
        libio-pty-perl \
        libnet-ssleay-perl \
        openssl \
        perl \
        postfix \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/perl /usr/local/bin/perl \
    && postconf -e inet_protocols=ipv4 \
    && postconf -e inet_interfaces=loopback-only

COPY webmin-src.tar /tmp/webmin-src.tar

RUN mkdir -p /usr/share/webmin \
    && tar -xf /tmp/webmin-src.tar -C /usr/share/webmin \
    && rm -f /tmp/webmin-src.tar \
    && test -s /usr/share/webmin/version \
    && grep -qx "2.670" /usr/share/webmin/version \
    && chmod +x /usr/share/webmin/setup.sh /usr/share/webmin/miniserv.pl \
    && cd /usr/share/webmin \
    && config_dir=/etc/webmin \
       var_dir=/var/webmin \
       perl=/usr/bin/perl \
       autoos=3 \
       port=10000 \
       login=root \
       password=labroot \
       ssl=0 \
       atboot=0 \
       nostart=1 \
       noportcheck=1 \
       noperlpath=1 \
       nochown=1 \
       nouninstall=1 \
       nopostinstall=1 \
       ./setup.sh /usr/share/webmin \
    && test "$(cat /etc/webmin/version)" = "2.670" \
    && grep -q "^ssl=0" /etc/webmin/miniserv.conf \
    && sed -i \
        -e "s/^ssl_enforce=.*/ssl_enforce=0/" \
        -e "s/^ipv6=.*/ipv6=0/" \
        -e "s/^syslog=.*/syslog=0/" \
        /etc/webmin/miniserv.conf \
    && grep -q "^no_testing_cookie=" /etc/webmin/miniserv.conf \
        || echo "no_testing_cookie=1" >> /etc/webmin/miniserv.conf \
    && grep -q "^preroot=" /etc/webmin/miniserv.conf \
        && sed -i "s/^preroot=.*/preroot=gray-theme/" /etc/webmin/miniserv.conf \
        || echo "preroot=gray-theme" >> /etc/webmin/miniserv.conf \
    && grep -q "^theme=" /etc/webmin/config \
        && sed -i "s/^theme=.*/theme=gray-theme/" /etc/webmin/config \
        || echo "theme=gray-theme" >> /etc/webmin/config

EXPOSE 10000
CMD ["/usr/bin/perl", "/usr/share/webmin/miniserv.pl", "--nofork", "/etc/webmin/miniserv.conf"]
