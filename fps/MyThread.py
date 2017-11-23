# coding=utf-8
import threading
import os
import time
import subprocess
from Tkinter import *
import xlsxwriter
#from uiautomator import Device
from fps_test import SurfaceFlinger
import re

date = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))

file_path=os.path.abspath(sys.argv[0])  
path_list=file_path.split('\\')
path_list.pop()
path='\\'.join(path_list)

path=path+'\\result\\'
log_path=path+'\\'

path=unicode(path,"gb2312")
log_path=unicode(log_path,"gb2312")

if not os.path.exists(path): os.makedirs(path)
if not os.path.exists(log_path): os.makedirs(log_path)

flag = False
Time = []  # 获取数据时间点
frame_count = []  # 更新的SurfaceFlinger数据数量
frame_rate = []  # 数据计算得到的fps
jank_count = []  # 丢帧率代表持续卡顿
fps = []  # 真实fps=计算得到的fps-掉帧数
max_delay = []  # 最大帧间隔代表最大卡顿持续时长,单位毫秒。


class myThread1(threading.Thread):  # 继承父类threading.Thread

    def __init__(self, threadID, device, direction, speed, ratio, max_steps,test_type,auto,text_msglist):

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.device = device
        self.direction = direction
        self.speed = int(speed[:-2])
        self.ratio = float(ratio)
        self.max_steps = int(max_steps)
        self.test_type = test_type
        self.text_msglist = text_msglist
        self.auto=auto
        self.i=0

    @staticmethod
    def set_flag(f):
        global flag
        if f == "False":
            flag = False
        else:
            flag = True
            print 'True'

    def swipe(self, x, y, x1, x2, y1, y2):

        if self.direction == u'水平方向':
            if self.i < self.max_steps:
                subprocess.call('adb -s %s shell input swipe %f %f %f %f %d' % \
                                (self.device, x2, y, x1, y, self.speed), shell=True)
                self.i += 1
            elif self.max_steps <= self.i < 2*self.max_steps:
                subprocess.call('adb -s %s shell input swipe %f %f %f %f %d' % \
                                (self.device, x1, y, x2, y, self.speed), shell=True)
                self.i += 1
                if self.i == (2*self.max_steps):
                    self.i = 0
        else:
            if self.i < self.max_steps:
                subprocess.call('adb -s %s shell input swipe %f %f %f %f %d' % \
                                (self.device, x, y1, x, y2, self.speed), shell=True)
                self.i += 1
            elif self.max_steps <= self.i < 2*self.max_steps:
                subprocess.call('adb -s %s shell input swipe %f %f %f %f %d' % \
                                (self.device, x, y2, x, y1, self.speed), shell=True)
                self.i += 1
                if self.i == (2*self.max_steps):
                    self.i = 0

    def run(self):

        Time[:] = []
        frame_count[:] = []
        frame_rate[:] = []
        jank_count[:] = []
        fps[:] = []
        max_delay[:] = []

        activity_name = self.get_focused_package_and_activity()
        if self.test_type == u'UI页面':
            sf = SurfaceFlinger(activity_name, self.device)
        else:
            sf = SurfaceFlinger('SurfaceView', self.device)

        subprocess.call("adb -s %s shell mkdir -p /sdcard/screenshot/" % self.device, shell=True)

        if self.auto == u'开启':
            display_info = os.popen("adb -s %s shell dumpsys window displays | findstr init" % self.device).read()
            display = display_info[9:18].split('x')
            Width = int(display[0])
            Height = int(display[1])
            x = Width / 2
            y = Height / 2
            x1 = self.ratio * Width
            x2 = Width - self.ratio * Width
            y1 = Height - self.ratio * Width
            y2 = self.ratio * Width

        while not flag:
            if sf.clear_buffer():
                if self.auto == u'开启':
                    self.swipe(x, y, x1, x2, y1, y2)
                    time.sleep(0.5)
                else:
                    time.sleep(1.5)
                sf.start_dump_latency_data()
                frame = sf.get_frame_rate()
                jankiness = sf.get_Vsync_jankiness()
                delay = sf.get_max_delay()
                frame_data_size = sf.get_frame_latency_data_size()
                real_fps = frame - jankiness
                if frame != -1:
                    t = time.strftime('%H-%M-%S', time.localtime())
                    if self.test_type == u'UI页面':
                        if real_fps < 30 or jankiness > 6:  # fps<30或者大于6帧时才会截图。
                            self.screenshot(t)
                    Time.append(t)
                    frame_count.append(frame_data_size)
                    frame_rate.append(frame)
                    jank_count.append(jankiness)
                    fps.append(real_fps)
                    max_delay.append(delay)
                    self.text_msglist.insert(END, 'fps: %s  ' % real_fps, 'blue')
                    self.text_msglist.insert(END, 'jank_count: %s\n' % jankiness, 'blue')
                    self.text_msglist.see(END)
                    self.text_msglist.insert(END, '--------------------------\n', 'green')
                sf.stop_dump_latency_data()

        self.write_xlsx(activity_name)
        self.text_msglist.insert(END, '测试完成,等待传输截图文件到本地..\n', 'green')
        self.text_msglist.see(END)
        self.pull_screenshot()
        self.text_msglist.insert(END, '传输完成！\n', 'green')

    def get_focused_package_and_activity(self):
        pattern = re.compile(r"[a-zA-Z0-9_\.]+/.[a-zA-Z0-9_\.]+")
        out = os.popen("adb -s %s shell dumpsys window w | findstr \/ | findstr name=" % self.device).read()
        component = pattern.findall(out)[-1]
        return component

    def screenshot(self, t):
        subprocess.call("adb -s %s shell screencap -p /sdcard/screenshot/%s.png" % (self.device, t),shell=True)

    def pull_screenshot(self):
        print path + 'screenshot/'
        subprocess.call("adb -s %s pull /sdcard/screenshot %s" % (self.device, path + 'screenshot/'), shell=True)
        subprocess.call('adb -s %s shell rm -r /sdcard/screenshot/' % self.device, shell=True)

    def write_xlsx(self, activity_name):
        w = xlsxwriter.Workbook(path + 'fps_' + date + '.xlsx')
        ws = w.add_worksheet('data')
        title_list=['Time','frame_count','frame_rate','jank_count','fps','max_delay(ms)']
        ws.write_row('A1', title_list)
        result_list = [Time, frame_count, frame_rate, jank_count, fps, max_delay]
        col_char = 65 #字母A ascii 码
        for result in result_list:
            result.pop(0)
            result.pop(-1)
            ws.write_column(chr(col_char)+'2', result)
            col_char += 1
        length = len(Time)
        chart = w.add_chart({'type': 'line'})
        chart.add_series(
            {'name': '=data!$D$1'
                , 'categories': '=data!$A$2:$A$%d' % length
                , 'values': '=data!$D$2:$D$%d' % length
                , 'line': {'width': 1.25, 'color': 'green'}
             })
        chart.add_series(
            {'name': '=data!$E$1'
                , 'values': '=data!$E$2:$E$%d' % length
                , 'line': {'width': 1.25, 'color': 'red'}
             })
        chart.set_title({'name': activity_name})  # 图标名称
        chart.set_size({'width': 1200, 'height': 800})
        ws.insert_chart('G7', chart, {'x_offset': 40, 'y_offset': 10})
        w.close()
