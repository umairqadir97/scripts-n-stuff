# Dockerfile for freeipa servers
ARG centos_ver=centos7.6.1810
FROM centos:${centos_ver}
LABEL maintainer="lrountree@plume.com" \
version="1.0" \
purpose="test build freeipa on docker"
RUN while yum check-update; do sleep 1; done && yum update -y
RUN yum install \
ntp \
bind-utils \
nc \
lsof \
net-tools \
expect -y
# wont need if volume bind works: RUN echo "server $(hostname -i | sed 's/.$/1/')" >> /etc/ntp.conf
RUN mkdir /root/ipa && \
touch /root/ipa/admin.pw && \
touch /root/ipa/directorymanager.pw
RUN yum install \
ipa-server \
ipa-server-dns -y
CMD ["/usr/sbin/init"]
