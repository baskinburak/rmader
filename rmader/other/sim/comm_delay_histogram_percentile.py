#!/usr/bin/env python  
# Kota Kondo

#  Commands: Open three terminals and execute this:
#  python comm_delay_histogram_percentile.py
#  Ex. python comm_delay_histogram_percentile.py

# change cd and dc

import bagpy
from bagpy import bagreader
import pandas as pd

import rosbag
import rospy
import math
import tf2_ros
import geometry_msgs.msg
import tf
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys
import scipy
import numpy

if __name__ == '__main__':

    ##### parameters
    is_docker = True
    is_oldmader = False # always False bc oldmader doesn't have comm_delay
    num_of_agents = 10
    cd_list = [0, 50, 100, 200, 300]

    for cd in cd_list:

        is_oldmader=False
        if cd == 0: 
            dc_list = [25] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 50:
            dc_list = [60] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 100:
            dc_list = [200] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 200:
            dc_list = [300]
        elif cd == 300:
            dc_list = [400]
            
        for dc in dc_list:
            
            # comm_delay you use
            input_comm_delay = dc/1000
            str_dc = str(dc)

            if is_docker:
                source_dir = "/home/data/" # change the source dir accordingly #10 agents 
            else:
                source_dir = "/home/kota/test/data" # change the source dir accordingly #10 agents 

            figname = 'cd'+str(cd)+'dc'+str_dc+'_rmader_comm_delay_histogram.png'
            source_bags = source_dir + "/rmader/bags/cd"+str(cd)+"ms/dc"+str_dc+"ms/*.bag" # change the source dir accordingly #10 agents

            rosbag_list = glob.glob(source_bags)
            rosbag_list.sort() #alphabetically order
            rosbag = []
            comm_delay = []

            for bag in rosbag_list:
                rosbag.append(bag)

            # print(rosbag)

            for i in range(len(rosbag)):
            # for i in range(10):

                b = bagreader(rosbag[i], verbose=False);
                
                for i in range(1,num_of_agents+1):
                    if i < 10:
                        log_data = b.message_by_topic("/SQ0" + str(i) + "s/rmader/comm_delay")
                        print("log_data", log_data)
                    else:
                        log_data = b.message_by_topic("/SQ" + str(i) + "s/rmader/comm_delay")

                    try:
                        log = pd.read_csv(log_data)

                        for j in range(len(log.comm_delay)):
                            comm_delay.append(log.comm_delay[j])
                    except:
                        pass

            # print percentile

            comm_delay_arr = numpy.array(comm_delay)

            percentile = scipy.stats.percentileofscore(comm_delay_arr, input_comm_delay, kind='mean')
            os.system('echo "----------------------------------------------------------------------------------" >> '+source_dir+'/comm_delay_percentile.txt')
            os.system('echo "'+source_bags+'" >> '+source_dir+'/comm_delay_percentile.txt')
            os.system('echo "cd='+str(cd)+', dc='+str(dc)+':   '+str(input_comm_delay) + ' is ' + str(round(percentile,1)) + '-th percentile" >> '+source_dir+'/comm_delay_percentile.txt')
            # print(comm_delay)

            try:
                max_comm_delay = max(comm_delay)

                fig = plt.figure()
                ax = fig.add_subplot()
                n, bins, patches = plt.hist(x=comm_delay, color="blue", edgecolor = 'black')
                plt.axvline(x=dc/1000, color="red")
                if cd == 50:
                    ax.set_xticks(np.arange(0,0.125,0.025))
                    ax.set_xticklabels(np.arange(0,125,25))
                elif cd == 100:
                    ax.set_xticks(np.arange(0,0.175,0.025))
                    ax.set_xticklabels(np.arange(0,175,25))
                elif cd == 200:
                    ax.set_xticks(np.arange(0,0.250,0.025))
                    ax.set_xticklabels(np.arange(0,250,25))
                elif cd == 300:
                    ax.set_xticks(np.arange(0,0.375,0.025))
                    ax.set_xticklabels(np.arange(0,375,25))
                # plt.rcParams["font.family"] = "Times New Roman"
                plt.grid(axis='y', color='black', alpha=0.2)
                plt.title('Comm delay histogram \n max comm_delay is '+str(round(max_comm_delay*1000))+' [ms] and '+str(dc)+'ms delay check')
                plt.xlabel("comm delay [ms]")
                plt.ylabel("count")
                plt.savefig(source_dir+'/'+figname)
                plt.close('all')
                # plt.show()
            except:
                pass

            # in case you wanna calculate the value of q-th percentile
            # print("----------------------------------------------------------------------------------")
            for q in range(100,0,-25):
                try:
                    os.system('echo "'+str(q)+'-th : '+ str(round(numpy.percentile(comm_delay_arr, q)*1000,2)) + 'ms" >> '+source_dir+'/comm_delay_percentile.txt')
                except:
                    pass
