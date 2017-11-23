#!/usr/bin/env python
# -*- coding: utf-8 -*
import os
import subprocess


class SurfaceFlinger(object):

    CLEAR_BUFFER_CMD = "dumpsys SurfaceFlinger --latency-clear"
    FRAME_LATENCY_CMD = "dumpsys SurfaceFlinger --latency"
    PAUSE_LATENCY = 20  #两个frame之间的latency大于20，则不是一个jank
    #查询某帧数据出问题的时候，系统会返回一个64位的int最大值，我们会忽略这列数据
    PENDING_FENCE_TIME = (1 << 63) - 1  #Symbol of unfinished frame time
    refresh_period = -1     #刷新周期
    frame_buffer_data = []
    frame_latency_data_size = 0    
    
    def __init__(self, activity_name,device):
        """
        :param activity_name: 当前界面的"package/activity"
        :max_Vsync=0  最大帧延时。
        """
        self.activity_name = activity_name
        self.max_Vsync = 0
        self.device = device

    def clear_buffer(self):
        '''清除SurfaceFlinger缓存数据'''       
        results = os.popen("adb -s %s shell "%self.device+'{0} {1}'.format(self.CLEAR_BUFFER_CMD, self.activity_name)).readlines()
        return not len(results)

    def start_dump_latency_data(self, ignore_pending_fence_time = False):
        '''开始获取SurfaceFlinger数据'''
        results = []

        #results = os.popen("adb -s %s shell "%self.device+'{0} {1}'.format(self.FRAME_LATENCY_CMD, self.activity_name)).readlines()
        results = os.popen("adb -s %s shell " % self.device + '{0} {1}'.format(self.FRAME_LATENCY_CMD,self.activity_name)).readlines()
        if self.activity_name=='SurfaceView':
            self.refresh_period=41666667
        else:
            self.refresh_period = int(results[0].strip())  # strip(del)去除指定字符,默认空则去除\n\r\t
        if self.refresh_period < 0:
            return False

        data_invalid_flag = False
        for line in results:
            if not line.strip():
                break
            if len(line.split()) == 1 or line.split()[0] == "0":  # 去除第一行刷新周期，去除数据为0的行
                continue
            elif line.split()[1] == str(self.PENDING_FENCE_TIME):
                if ignore_pending_fence_time:
                    data_invalid_flag = True
                else:
                    return False
            self.frame_buffer_data.append(line.split())
            if not data_invalid_flag:
                self.frame_latency_data_size += 1

        return True

    def get_frame_latency_data_size(self):
        return self.frame_latency_data_size

    def get_refresh_period(self):
        return self.refresh_period

    def get_max_delay(self):
        return round(self.max_Vsync/1e6,2)

    def __get_delta_Vsync_data(self):
        '''获取Vsync增量数据'''
        delta_Vsync_data = []
        max_Vsync = 0
        if self.frame_buffer_data:
            first_Vsync_time = long(self.frame_buffer_data[0][1])
            for i in xrange(0, self.frame_latency_data_size-1):
                cur_Vsync_time = long(self.frame_buffer_data[i+1][1])
                delta_Vsync_data.append(cur_Vsync_time - first_Vsync_time)
                first_Vsync_time = cur_Vsync_time
                if self.max_Vsync < delta_Vsync_data[i]:
                    self.max_Vsync = delta_Vsync_data[i]       
        return  delta_Vsync_data

    def __get_delta2_Vsync_data(self):
        '''在delta_Vsync_data基础上再获取增量数据'''
        delta_Vsync_data = self.__get_delta_Vsync_data()
        delta2_Vsync_data = []
        num_delta_Vsync = self.frame_latency_data_size - 1

        for i in xrange(0, num_delta_Vsync-1):
            delta2_Vsync_data.append(delta_Vsync_data[i+1] - delta_Vsync_data[i])
        return delta2_Vsync_data

    def __get_normalized_delta2_Vsync(self):
        delta2_Vsync_data = self.__get_delta2_Vsync_data()
        normalized_delta2_Vsync = []
        for i in xrange(0, self.frame_latency_data_size-2):
            normalized_delta2_Vsync.append(delta2_Vsync_data[i]/self.refresh_period)
        return normalized_delta2_Vsync

    def __get_round_normalized_delta2_Vsync(self):
        normalized_delta2_Vsync = self.__get_normalized_delta2_Vsync()
        round_normalized_delta2_Vsync = []
        for i in xrange(0, self.frame_latency_data_size-2):
            value = round(max(normalized_delta2_Vsync[i], 0.0))
            round_normalized_delta2_Vsync.append(value)
        return round_normalized_delta2_Vsync

    def get_Vsync_jankiness(self):

        '''应用绘制超时（跳帧）的次数,估算'''

        if self.refresh_period< 0:
            return -1
        round_normalized_delta2_Vsync = self.__get_round_normalized_delta2_Vsync()
        num_jankiness = 0
        for i in xrange(0, self.frame_latency_data_size-2):
            value = round_normalized_delta2_Vsync[i]
            if value > 0 and value < self.PAUSE_LATENCY:
                num_jankiness += 1

        return num_jankiness  

    def get_frame_rate(self):

        if self.refresh_period < 0:
            return -1
        if not self.frame_buffer_data:
            return -1
        start_time = long(self.frame_buffer_data[0][1])
        end_time = long(self.frame_buffer_data[-1][1])
        total_time = end_time - start_time
        buffer_len=len(self.frame_buffer_data)
        if buffer_len<2: #舍弃采样数据为1帧的样本
            return -1
        frame_rate=(self.frame_latency_data_size - 1) * 1e9 / total_time  
        return round(frame_rate,2)

    
    def stop_dump_latency_data(self):

        '''#停止数据采集'''
        self.refresh_period = -1
        self.frame_buffer_data[:] = []
        self.frame_latency_data_size = 0
        self.max_Vsync = 0
