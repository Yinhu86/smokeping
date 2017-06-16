#!/bin/sh
#selinux
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

#iptables  or   firewalld 
systemctl status firewalld >>/dev/null
if [ $? -eq 0 ]
then
    firewall-cmd --zone=public --add-port=80/tcp --permanent
    firewall-cmd --reload
fi
systemctl status iptables >>/dev/null
if [ $? -eq 0 ]
then
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    service iptables save
fi

#yum repo configurtion
#centos7  base
sed -i 's/mirrorlist=/#mirrorlist=/g;s/#baseurl=/baseurl=/g;s/mirror.centos.org/mirrors.yun-idc.com/g' /etc/yum.repos.d/CentOS-Base.repo

#repo
rpm -ivh epel-release-7-9.noarch.rpm

sed -i 's/mirrorlist=/#mirrorlist=/g;s/#baseurl=/baseurl=/g;s/download.fedoraproject.org\/pub\/epel\/7/mirrors.yun-idc.com\/epel\/7Server/g' /etc/yum.repos.d/epel.repo

#yum install  package
yum clean all
yum install popt popt-devel  rrdtool fping curl dig httpd perl echoping-6.1-0.3.beta.r434svn.el7.centos.x86_64.rpm  smokeping  ntpdate -y

#sync time
rm -f /etc/localtime
ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ping -c 2 202.120.2.101 >>/dev/null
if [ $? -eq 0 ]
then 
    ntpdate 202.120.2.101
fi

#modify configurtion

#httpd

cp -ap /usr/share/smokeping /var/www/html/
chown apache:apache -R /var/www/html/
sed -i '/#ServerName/a\ServerName localhost:80' /etc/httpd/conf/httpd.conf
sed -i 's#local#all granted#g;s#/usr/share#/var/www/html#g' /etc/httpd/conf.d/smokeping.conf
sed -i '/Require all granted/a\  Options FollowSymLinks'   /etc/httpd/conf.d/smokeping.conf
sed -i '/Require all granted/a\  AllowOverride AuthConfig'   /etc/httpd/conf.d/smokeping.conf


#smokeping

cp config /etc/smokeping/
cp htpasswd /etc/httpd/conf/
cp .htaccess /var/www/html/smokeping/


systemctl start smokeping httpd
systemctl enable smokeping httpd



echo "#####################################"
echo "     "
echo -e "\e[1;31m    Login URL:  http://IP/smokeping/sm.cgi  \e[0m"
echo -e "\e[1;31m    Login User: admin/syscloud.cn@ \e[0m"
echo "     "
echo "####################################"
