ARG centos_ver=centos7.6.1810
FROM centos:${centos_ver}
LABEL maintainer="lrountree@plume.com" \
version="2.0" \
purpose="build freeipa on docker"
RUN while yum check-update; do sleep 1; done && yum update -y
RUN yum install \
ntp \
bind-utils \
nc \
lsof \
net-tools \
expect -y
RUN yum install \
ipa-server \
ipa-server-dns \
ipa-server-trust-ad \
patch -y && \
yum clean all
ENTRYPOINT ["/usr/sbin/init"]
