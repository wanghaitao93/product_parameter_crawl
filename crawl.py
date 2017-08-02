#This Python file uses the following encoding: utf-8
#!/bin/env python
import time
import sys
import json
import os
import subprocess
import ConfigParser

reload(sys)
sys.setdefaultencoding('utf-8')

name = sys.argv[1]
cnt_process = 20 
cnt  = 1
os.system('rm -rf %s_output && mkdir %s_output' % (name, name))
os.system('rm fw*')

def read_config_file():
    """
    read config file trans dict
    """
    config_dict = {}
    
    cf= ConfigParser.ConfigParser()
    cf.read('ucp_jd_info.conf')
    secs = cf.sections()
    
    for sec in secs:
        print 'sec %s start ------------------' % sec
        
        opts = cf.options(sec)
        opt_dict = {}
        
        for opt in opts:
            opt_dict[opt] = cf.get(sec, opt).strip()
            print '%s = %s' % (opt, cf.get(sec, opt).strip())
            
        config_dict[sec] = opt_dict
    
    print 'end.................'
    return config_dict
            
    
def calculate_num(part_cnt, machine_num, machine_id, index, cnt_process = 20):
    """
    base on total part cnt、machine_num、machine_id、index、cnt_process,
    judge process start num and end num
    """

    cnt_every_machine = part_cnt / machine_num
    
    start_num = (machine_id - 1) * cnt_every_machine 
    end_num = machine_id * cnt_every_machine 
    
    if (machine_id == machine_num):
        end_num = part_cnt

    print 'start_num', start_num
    print 'end_num', end_num
   
    cnt_every_process = (end_num - start_num) / cnt_process 

    start = start_num + cnt_every_process * (index - 1) + 1
    end = start_num + cnt_every_process * index
    
    if (index ==cnt_process ):
        end = end_num
        
    return start, end

if __name__ == "__main__":

    config_dict = read_config_file()

    for index in xrange(1, cnt_process + 1):

        print 'index', index

        for name, k_dict in config_dict.items():
            table_name = k_dict['table_name']
            view_id = k_dict['view_id']
            part_cnt = int(k_dict['part_cnt'])
            field = k_dict['field']
            machine_num = int(k_dict['machine_num'])
            machine_id = int(k_dict['machine_id'])
            cnt_process = int(k_dict['cnt_process'])
        
        start, end = calculate_num(part_cnt, machine_num, machine_id, index, cnt_process)
        
        script = 'python request.py %s %d %s %s %d %d > %s_output/%s_%d 2>%s_output/%s_error_%d' % (name, index, view_id, field, start, end, name, name, index, name, name, index) 
        print script

        cnt += 1
        p2 = subprocess.Popen(script, shell=True,  stdout=subprocess.PIPE)
        time.sleep(2)
