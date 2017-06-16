#!/usr/bin/env python
#coding:utf-8
import re
import os
import time
import subprocess

def Dumpfile():
    #Dump rrd to xml
    rrd_file = os.popen('ls *.rrd')
    rrd_list = rrd_file.readlines()
    for rrd_f in rrd_list:
        rrd_name = rrd_f.split('.')[0]
        rrd_f = rrd_f.split()[0]
        rrd2xml = "rrdtool dump " + rrd_f + " " + rrd_name + ".xml"
        subprocess.call(rrd2xml, shell=True, stdout=open('/dev/null','w'))
        tmp_file = "cat " + rrd_name + ".xml" + "|egrep -v 'NaN</v><v>NaN' >> " + rrd_name + ".tmp"
        subprocess.call(tmp_file, shell=True, stdout=open('/dev/null','w'))

def some_time(rrd_tmp, sys_time):
    stime_cmd = "tail -50 " + rrd_tmp.strip() + "|egrep -o '(" + sys_time + ".*)CST'|tail -5"
    stime = os.popen(stime_cmd)
    stime_list = stime.readlines()    
    return stime_list

def get_record(rrd_tmp,record_time):
    avg_info_cmd = "cat " +  rrd_tmp.strip() + " |grep " + "'" + record_time.strip() + "'" + "|tail -3|head -1"
    avg_info = os.popen(avg_info_cmd)
    avg_info_content = avg_info.read()
    time_tmp1 = re.findall(r'>([1-9].\d{10}e-01)<', avg_info_content)
    time_tmp2 = re.findall(r'>([1-9].\d{10}e-02)<', avg_info_content)
    time_tmp3 = re.findall(r'>([1-9].\d{10}e-03)<', avg_info_content)
    if len(time_tmp1) > 1:
        time_num = time_tmp1
        multiple = 100
        avg_num = first_avg(rrd_tmp,time_num,multiple)
        return avg_num
    elif len(time_tmp2) > 1:  
        time_num = time_tmp2
        multiple = 10  
        avg_num = first_avg(rrd_tmp,time_num,multiple)
        return avg_num
    elif len(time_tmp3) > 1:
        time_num = time_tmp3
        multiple = 1
        avg_num = first_avg(rrd_tmp,time_num,multiple)
        return avg_num
    else:
        return 1

def first_avg(rrd_tmp,time_num,multiple): 
    time_list = []
    for i in time_num:
        i = float(i[:5])
        time_list.append(i)
    total_num = reduce(lambda x,y: x + y, time_list)
    avg_num = float('%.5f' %(total_num / len(time_list)*multiple))
    return avg_num

def second_avg(rrd_tmp, time_list, filename):
    total_num = reduce(lambda x,y: x + y, time_list)
    
    avg_num = float('%.1f' % (total_num / len(time_list)))
    rrd_name = rrd_tmp.split('.')[0]
    record_info = rrd_name + "        " + str(avg_num)
    with open(filename, 'ab') as f:
        f.write(record_info + "ms" + '\n')

def main():
    Dumpfile()
    sys_time = time.strftime("%Y-%m")
    sys_time2 = time.strftime("%F")
    filename = 'record_' + sys_time2
    with open(filename, 'wb') as f:
        f.write("dest(目的地)    delay(延迟)" + '\n')
    rrd_tmp_all = os.popen('ls *.tmp')
    rrd_list = rrd_tmp_all.readlines()
    for rrd_tmp in rrd_list:
        avg_list = []
        try:
            time_list = some_time(rrd_tmp, sys_time)    
            for record_time in time_list:
                avg_time = get_record(rrd_tmp,record_time)
                if avg_time != 1:
                    avg_list.append(avg_time)
                else:
                   print "Scripts can't handle this kind of network latency ,filename %s " %(rrd_tmp.split('.')[0] + ".rrd" )
                   break
            second_avg(rrd_tmp, avg_list, filename)
        except Exception,err:
            print err

    os.system('rm -f *tmp *xml') 

if __name__ == '__main__':
    res1 = subprocess.call('ls *.rrd', shell=True, stdout=open('/dev/null','w'))
    res2 = subprocess.call('ls /var/lib/smokeping/rrd/Ping/*.rrd', shell=True, stdout=open('/dev/null','w'))
    if res1 == 0:
        main()
    elif res2 == 0:
        os.system('\cp /var/lib/smokeping/rrd/Ping/*.rrd . ')
        main()
    else:
        print "copy this file to rrd  directory"

