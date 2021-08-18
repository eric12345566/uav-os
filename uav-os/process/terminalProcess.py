import tkinter
import time

class Begueradj():
    '''
    Constructor
    '''
    def __init__(self, terminalService):
        self.terminalService = terminalService
        # Frame set
        self.align_mode = 'nswe'
        self.pad = 5
        self.div_size = 250
        self.img_size = self.div_size * 2
        self.general_font = ('Arial', 16)
        self.pad_font = 10
        # init
        self.window = tkinter.Tk()
        self.initialize_user_interface()
        self.split_user_frame()
        self.split_div1_frame()

        # Init frame update
        self.getTime()
        self.window.mainloop()

    def initialize_user_interface(self):
        # Draw a user interface
        self.window.geometry('800x600')
        self.window.title('Window')
        # Split div frame
        self.div1 = tkinter.Frame(self.window, width=self.img_size, height=self.img_size)
        self.div2 = tkinter.Frame(self.window, width=self.div_size, height=self.div_size, bg='orange')
        self.div3 = tkinter.Frame(self.window, width=self.div_size, height=self.div_size, bg='green')

        self.div1_temp = tkinter.Frame(self.div1, width=self.img_size / 3, height=self.img_size / 3, bg='#6CABE7')
        self.div1_body = tkinter.Frame(self.div1, width=self.img_size / 3, height=self.img_size / 3, bg='#93BFEB')
        self.div1_battery = tkinter.Frame(self.div1, width=self.img_size / 3, height=self.img_size / 3, bg='#6CABE7')

        self.div1.grid(column=0, row=0, padx=self.pad, pady=self.pad, rowspan=3, sticky=self.align_mode)
        self.div2.grid(column=1, row=0, padx=self.pad, pady=self.pad, sticky=self.align_mode)
        self.div3.grid(column=1, row=1, padx=self.pad, pady=self.pad, sticky=self.align_mode)

        self.div1_temp.grid(column=0, row=0, padx=self.pad, pady=self.pad, rowspan=3, sticky=self.align_mode)
        self.div1_body.grid(column=0, row=1, padx=self.pad, pady=self.pad, rowspan=3, sticky=self.align_mode)
        self.div1_battery.grid(column=0, row=2, padx=self.pad, pady=self.pad, rowspan=3, sticky=self.align_mode)

    def split_user_frame(self):
        # div2
        self.time_title = tkinter.Label(self.div2, text=time.strftime("%H:%M:%S"), bg='orange', fg='white', font=self.general_font)
        self.lbl_title2 = tkinter.Label(self.div2, text="Tello", bg='orange', fg='white', font=self.general_font)

        self.time_title.grid(column=0, row=0, sticky=self.align_mode)
        self.lbl_title2.grid(column=0, row=1, sticky=self.align_mode)
        # TODO:加入Button
        # div3
        self.bt1 = tkinter.Button(self.div3, text='Force land', command=self.auto_landing, bg='green', fg='white', font=self.general_font)
        self.bt2 = tkinter.Button(self.div3, text='Take off', command=self.ready_takeOff, bg='green', fg='white', font=self.general_font)
        self.bt3 = tkinter.Button(self.div3, text='Trigger Keyboard', command=self.keyboard_trigger, bg='green', fg='white', font=self.general_font)
        self.bt4 = tkinter.Button(self.div3, text='Button 4', bg='green', fg='white', font=self.general_font)

        self.bt1.grid(column=0, row=0, sticky=self.align_mode)
        self.bt2.grid(column=0, row=1, sticky=self.align_mode)
        self.bt3.grid(column=0, row=2, sticky=self.align_mode)
        self.bt4.grid(column=0, row=3, sticky=self.align_mode)

        self.define_layout(self.window, cols=2, rows=2)
        self.define_layout(self.div1, rows=2)
        self.define_layout(self.div2, rows=2)
        self.define_layout(self.div3, rows=4)

    def split_div1_frame(self):
        # Split div1 frame
        # div1 temp
        self.lbl_high_temp = tkinter.Label(self.div1_temp, text='', bg='#6CABE7',
                                 fg='#263238', font=self.general_font)
        self.lbl_low_temp = tkinter.Label(self.div1_temp, text='', bg='#6CABE7',
                                fg='#263238', font=self.general_font)
        self.lbl_avg_temp = tkinter.Label(self.div1_temp, text='', bg='#6CABE7',
                                fg='#263238', font=self.general_font)

        self.lbl_high_temp.grid(column=0, row=0, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_low_temp.grid(column=0, row=1, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_avg_temp.grid(column=0, row=2, padx=self.pad_font, pady=self.pad_font, sticky='w')

        # div1 body
        self.lbl_pitch = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                             font=self.general_font)
        self.lbl_roll = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                            font=self.general_font)
        self.lbl_yaw = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                           font=self.general_font)
        self.lbl_barometer = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                                 font=self.general_font)
        self.lbl_rotate = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                                           font=self.general_font)
        self.lbl_high = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                                           font=self.general_font)
        self.lbl_position_x = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                                        font=self.general_font)
        self.lbl_position_y = tkinter.Label(self.div1_body, text='', bg='#93BFEB', fg='#263238',
                                        font=self.general_font)

        self.lbl_pitch.grid(column=0, row=0, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_roll.grid(column=0, row=1, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_yaw.grid(column=0, row=2, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_barometer.grid(column=0, row=3, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_rotate.grid(column=0, row=4, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_high.grid(column=0, row=5, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_position_x.grid(column=0, row=6, padx=self.pad_font, pady=self.pad_font, sticky='w')
        self.lbl_position_y.grid(column=0, row=7, padx=self.pad_font, pady=self.pad_font, sticky='w')

        # div1 battery
        self.lbl_battery_percentage = tkinter.Label(self.div1_battery, text='',
                                                    bg='#6CABE7', fg='#263238', font=self.general_font)

        self.lbl_battery_percentage.grid(column=0, row=1, padx=self.pad_font, pady=self.pad_font, sticky='w')

    def auto_landing(self):
        self.terminalService.setForceLanding(True)

    def ready_takeOff(self):
        self.terminalService.setForceLanding(False)

    def keyboard_trigger(self):
        print('trigger!!!')
        if self.terminalService.getKeyboardTrigger():
            self.terminalService.setKeyboardTrigger(False)
        else:
            self.terminalService.setKeyboardTrigger(True)

    def getTime(self):
        self.tello_pitch = self.terminalService.getInfo('pitch')
        self.tello_roll = self.terminalService.getInfo('roll')
        self.tello_yaw = self.terminalService.getInfo('yaw')
        self.tello_battery_percentage = self.terminalService.getInfo('battery')
        self.lowest_temperature = self.terminalService.getInfo('low_temperature')
        self.highest_temperature = self.terminalService.getInfo('high_temperature')
        self.average_temperature = self.terminalService.getInfo('temperature')
        self.tello_barometer = self.terminalService.getInfo('barometer')
        self.position_rotate = self.terminalService.getInfo('rotate')
        self.tello_high = self.terminalService.getInfo('high')
        self.position_x = self.terminalService.getInfo('position_X')
        self.position_y = self.terminalService.getInfo('position_Y')
        self.time_title.config(text=time.strftime("%H:%M:%S"))  # 获取当前时间
        self.lbl_yaw.config(text='Tello yaw: ' + str(self.tello_yaw))
        self.lbl_roll.config(text='Tello roll: ' + str(self.tello_roll))
        self.lbl_pitch.config(text='Tello pitch: ' + str(self.tello_pitch))
        self.lbl_barometer.config(text='Tello barometer: ' + str(int(self.tello_barometer)))
        self.lbl_rotate.config(text='Tello rotate: ' + str(int(self.position_rotate)))
        self.lbl_high.config(text='Tello High: ' + str(int(self.tello_high)))
        self.lbl_position_x.config(text='Tello Position X: ' + str(int(self.position_x)))
        self.lbl_position_y.config(text='Tello Position Y: ' + str(int(self.position_y)))
        self.lbl_high_temp.config(text='Highest temperature: ' + str(self.highest_temperature))
        self.lbl_low_temp.config(text='Lowest temperature: ' + str(self.lowest_temperature))
        self.lbl_avg_temp.config(text='Average temperature: ' + str(self.average_temperature))
        self.lbl_battery_percentage.config(text='Battery percentage: ' + str(self.tello_battery_percentage) + '%')

        self.window.after(5, self.getTime)  # 每隔5ms调用函数 gettime 自身获取时间

    def define_layout(self, obj, cols=1, rows=1):
        def method(trg, col, row):

            for c in range(cols):
                trg.columnconfigure(c, weight=1)
            for r in range(rows):
                trg.rowconfigure(r, weight=1)

        if type(obj) == list:
            [method(trg, cols, rows) for trg in obj]
        else:
            trg = obj
            method(trg, cols, rows)
def terminalProcess(terminalService):
    Begueradj(terminalService)