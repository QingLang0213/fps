#coding=utf-8
from Tkinter import *
import tkMessageBox
import os
import MyThread
import tkFileDialog
from ttk import Combobox



def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)



class Application(Frame):

        def __init__(self,master):
                Frame.__init__(self,master)
                self.root = master
                self.root.title('FPS(v1.0.0,qing.guo)')
                self.root.geometry('650x400')
                self.root.resizable(0, 0)  # 禁止调整窗口大小
                self.root.protocol("WM_DELETE_WINDOW",self.close)
                self.root.iconbitmap(get_path('fps.ico'))
                
        def creatWidgets(self):
                frame_left_top= Frame(self.root, width=410, height=220,bg='#C1CDCD')
                frame_left_center=Frame(self.root,width=410, height=80,bg='#C1CDCD')
                frame_left_bottom=Frame(self.root,width=410, height=100,bg='#C1CDCD')
                frame_right=Frame(self.root,width=240,height=400,bg='#C1CDCD')

                frame_left_top.grid_propagate(0)
                frame_left_center.grid_propagate(0)
                frame_left_bottom.grid_propagate(0)
                frame_right.propagate(0)
                frame_right.grid_propagate(0)

                frame_left_top.grid(row=0,column=0)
                frame_left_center.grid(row=1,column=0)
                frame_left_bottom.grid(row=2,column=0)
                frame_right.grid(row=0,column=1,rowspan=3)

                self.v1 = StringVar()
                self.v2 = StringVar()
                self.v3 = StringVar()
                self.v4 = StringVar()
                self.v5 = StringVar()
                self.v6 = StringVar()
                self.v7 = StringVar()
                self.v8 = StringVar()
                self.v4.set('0.2')


                type_list = [u'UI页面', u'视频/电影']
                swipe_list = [u'竖直方向', u'水平方向']
                swipe_config = [u'开启', u'关闭']
                swipe_speed = ['25ms', '50ms',  '75ms', '100ms', '150ms', '200ms', '300ms', '400ms',\
                               '500ms', '600ms', '700ms', '800ms']

                Label(frame_left_top, text=u"测试类型:",bg='#C1CDCD').grid(row=0, column=0, pady=20, sticky=NW, padx=5)
                self.cb1 = Combobox(frame_left_top, width=11, textvariable=self.v1, values=type_list)
                self.cb1.grid(row=0, column=1, ipady=1, padx=5)
                # cb1.set(u'Activity页面')
                self.cb1.current(0)
                #Label
                Button(frame_left_top, text=u"获取设备id:", command=self.set_device,bg='#C1CDCD').grid(row=0, column=2, pady=20, padx=13)
                Entry(frame_left_top, width=15, textvariable=self.v2).grid(row=0, column=3, padx=5, ipady=1)

                Label(frame_left_top, text=u"滑动方向:",bg='#C1CDCD').grid(row=1, column=0, pady=20, sticky=NW, padx=5)
                self.cb2 = Combobox(frame_left_top, width=11, textvariable=self.v3, values=swipe_list)
                self.cb2.grid(row=1, column=1, ipady=1, padx=5)
                self.cb2.current(0)
                Button(frame_left_top, text=u"设置滑动系数:", command=self.set_precent,bg='#C1CDCD').grid(row=1, column=2, pady=20, sticky=NW, padx=13)
                Entry(frame_left_top, width=15, textvariable=self.v4).grid(row=1,column=3, padx=5, ipady=1)

                Label(frame_left_top, text=u"滑动速度:",bg='#C1CDCD').grid(row=2, column=0, pady=20, sticky=NW, padx=5)
                self.cb3 = Combobox(frame_left_top, width=11, textvariable=self.v5, values=swipe_speed)
                self.cb3.grid(row=2, column=1, padx=5, ipady=1)
                self.cb3.current(8)

                Button(frame_left_top, text=u"最大滑动次数:", command=self.set_max_steps,bg='#C1CDCD').grid(row=2, column=2, pady=20, sticky=NW, padx=13)
                Entry(frame_left_top, width=15, textvariable=self.v6).grid(row=2, column=3, padx=5, ipady=1)

                Label(frame_left_center, text=u"自动滑动",bg='#C1CDCD').grid(row=0, column=0, padx=5, sticky=NW, pady=15)
                self.cb4 = Combobox(frame_left_center, width=6, textvariable=self.v7, values=swipe_config)
                self.cb4.grid(row=0, column=1, ipady=1, padx=5)
                self.cb4.current(0)

                self.b1=Button(frame_left_center, text=u"开始测试",command=self.start_test,bg='#C1CDCD')
                self.b1.grid(row=0,column=2,padx=30,pady=15)
                self.b2=Button(frame_left_center, text=u"结束测试",command=self.end_test,bg='#C1CDCD')
                self.b2.grid(row=0,column=3,padx=30,pady=15)
                Button(frame_left_bottom, text=u"测试结果",command=self.open_file,bg='#C1CDCD').grid(row=0,column=0,padx=13,pady=15)
                Entry(frame_left_bottom, width=49, textvariable=self.v8).grid(row=0, column=1, ipady=1, padx=10,pady=15)
                self.v8.set(MyThread.path)
                #Scrollbar
                scrollbar=Scrollbar(frame_right)
                scrollbar.pack(side=RIGHT, fill=Y)
                self.text_msglist=Text(frame_right, yscrollcommand = scrollbar.set,bg='#C1CDCD')
                self.text_msglist.pack(side = RIGHT, fill =BOTH)

                scrollbar['command'] = self.text_msglist.yview

                self.text_msglist.tag_config('green', foreground='#008B00')
                self.text_msglist.tag_config('blue', foreground='#0000FF')
                self.text_msglist.tag_config('red', foreground='#FF3030')
                self.text_msglist.tag_config('purple', foreground='#CD00CD')

                self.cb1.bind('<<ComboboxSelected>>', self.cb1_select)
                self.cb2.bind('<<ComboboxSelected>>', self.cb2_select)
                text_message = u"测试前请打开需要测试的页面,测试过程中需保持在同一Activity界面中,切换到其他Activity则无数据输出\n\n"
                self.text_msglist.insert(END,text_message,'green')

        def cb1_select(self, event):
                if self.v1.get() == u'视频/电影':
                        self.cb4.current(1)
                else:
                        self.cb4.current(0)

        def cb2_select(self, event):
                if self.v3.get() == u'水平方向':
                        self.cb3.current(2)
                else:
                        self.cb3.current(8)

        def start_test(self):

                MyThread.myThread1.set_flag('False')
                self.b1.config(state=DISABLED)
                self.b2.config(state=NORMAL)
                test_type=self.v1.get()
                device=self.v2.get()
                direction=self.v3.get()
                ratio=self.v4.get()
                speed=self.v5.get()
                max_steps=self.v6.get()
                auto=self.v7.get()

                if device == '' or device.isspace():
                        self.text_msglist.insert(END, 'please input device id\n', 'red')
                        self.b1.config(state=NORMAL)
                        return -1
                elif auto == u'开启':
                        try:
                                ratio = float(ratio)
                        except ValueError:
                                self.text_msglist.insert(END, 'please input swipe precent\n', 'red')
                                self.b1.config(state=NORMAL)
                                return -1
                        if ratio<0 or ratio>=0.5:
                                self.text_msglist.insert(END, 'precent range is [0,0.5)\n', 'red')
                                self.b1.config(state=NORMAL)
                                return -1
                        elif max_steps == '' or  max_steps.isspace() or not max_steps.isdigit():
                                self.text_msglist.insert(END, 'please input swipe precent\n', 'red')
                                self.b1.config(state=NORMAL)
                                return -1
                if auto == u'关闭':
                        ratio = 0
                        max_steps = 0
                thread1 = MyThread.myThread1(1, device, direction, speed, ratio, max_steps,test_type,auto,self.text_msglist)
                thread1.setDaemon(True)
                thread1.start()

        def end_test(self):
                self.b1.config(state=NORMAL)
                MyThread.myThread1.set_flag('True')
                self.b2.config(state=DISABLED)

        def set_device(self):
                device_info=os.popen('adb devices').readlines()
                device=device_info[-2]
                device_id=device.split('\t')[0]
                self.v2.set(device_id)
                self.text_msglist.insert(END, u'请确认获取的设备id正确，默认获取最新连接的设备\n\n', 'green')
                self.text_msglist.see(END)

        def set_precent(self):
                self.text_msglist.insert(END, u'滑动系数n（0>=n<0.5,表示屏幕两端各减去n倍屏宽或长）,剩下的区域即为实际滑动的区域。\n', 'green')
                self.text_msglist.insert(END, u'当UI布局为全屏时，可以设置0表示全屏滑动\n\n', 'green')
                self.text_msglist.see(END)

        def set_max_steps(self):
                self.text_msglist.insert(END, u'最大滑动次数max，表示滑动达到最大次数后，反向滑动，如此循环\n\n', 'green')
                self.text_msglist.see(END)

        def open_file(self):
                filename = tkFileDialog.askopenfilename(initialdir=MyThread.path)
                if filename == '':
                        return 0
                os.startfile(filename)

        def close(self):
                if MyThread.flag:
                    print MyThread.flag
                    result = tkMessageBox.askokcancel(title=u"退出", message=u"确定退出程序？")
                else:
                    result = tkMessageBox.askokcancel(title=u"警告", message=u"测试还未完成，确定要退出程序？")
                if result:
                        self.root.quit()
                        self.root.destroy()


if __name__ == "__main__":

        f=open(MyThread.log_path+'fps_log.txt','w')
        sys.stderr=f
        root=Tk()
        app=Application(root)
        app.creatWidgets()
        app.mainloop()
        f.close()
   

