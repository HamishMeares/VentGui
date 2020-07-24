#from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout
from pyqtgraph import PlotWidget, plot

import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint


# import board
import time
# import busio
# import digitalio
# import adafruit_bmp280
import array as arr
import matplotlib.pyplot as plt
import numpy as np
import math
import statistics

#1
# alarmBuzzer = digitalio.DigitalInOut(board.D12)
# alarmBuzzer.direction = digitalio.Direction.OUTPUT
# alarmBuzzer.value = False

# plt.style.use('ggplot')
# print('set up sensors...')
# spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# print('init sensor 1')
# cs1 = digitalio.DigitalInOut(board.D5)
# print('init sensor 2')
# cs2 = digitalio.DigitalInOut(board.D6)
# sensor1 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs1)
# sensor2 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, cs2)



# print('test sensors')
# print('sensor1 pressure: ', sensor1.pressure)
# print('sensor2 pressure: ', sensor2.pressure)


#constants used in flow calculation
print('set up constants for flow...')
beta = 0.54545 #ratio of d/D little diameter to big diameter
beta_thing = 1.047432587 #saves recalculating
coeff = 1.0
area = 0.0001130973
rho = 1.204

time_now = 0
time_last = 0
volume = 0.0
d = 9.0
cal_1 = 0.0
cal_2 = 0.0
av_press = 0.0

tidal_volume = 0.0
THRESHOLD = 1000.0
old_flow = 0.0

current_milli_time = lambda: int(round(time.time() * 1000))


def calibratePressureSensors(numValues):
    dummyTime = 0
    print('calibrating sensors...')
    p1_sum = 0
    p2_sum = 0
    p_sum = 0
    global cal_1, cal_2, av_press
    num = numValues
    # for i in range(num):
    #     p1_sum += sensor1.pressure
    #     p2_sum += sensor2.pressure

    av_press = (p1_sum + p2_sum )/(2*num)
    cal_1 = p1_sum/num - av_press
    cal_2 = p2_sum/num - av_press
    print('Done!')
    
class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.lastTime = current_milli_time()
        self.currentTime = current_milli_time()
        self.lastInspiration = current_milli_time()
        self.currentInspiration = current_milli_time()

        self.respRate = 10
        self.lastPressure = 0

        self.lastExpiration = current_milli_time()
        self.lastExpTime = current_milli_time()
        self.lastExpCurrentTime = current_milli_time()
        self.tidalVol = 0.0
        self.lastTidalVol = 0.0
        self.lastFlow = 0.0
        self.tidalVolHistory = [0] * 10
        self.tidalVolHistoryCounter = 0
        self.meantidalVol = 0.0


        ### widgets ###################################################################3
        # create graph widgets
        # alarm row at top
        self.labelAlarm = QLabel("Alarms:")
        self.graphWidgetPressure = pg.PlotWidget()
        self.graphWidgetVol = pg.PlotWidget()
        self.graphWidgetFlow = pg.PlotWidget()
        
        # pressure labels
        self.labelPMax = QLabel()
        self.labelPMaxVal = QLabel()
        self.labelPAv = QLabel()
        self.labelPAvVal = QLabel()
        self.labelPMin = QLabel()
        self.labelPMinVal = QLabel()

        # resp rate labels
        self.labelRespRate = QLabel("Resp. Rate:")
        self.labelRespRateVal = QLabel("10 bpm")

        # tidal volume labels
        self.labelTidalVol = QLabel("Tidal Vol:")
        self.labelTidalVolVal = QLabel("500 ml")

        # minute volume labels
        self.labelMinuteVol = QLabel("Minute Vol:")
        self.labelMinuteVolVal = QLabel("5 L/min")
        
        self.labelAlarmPMax = QLabel("40")
        self.btnUpPMax = QPushButton("+")
        self.btnDownPMax = QPushButton("-")
        
        
        self.labelAlarmPMin = QLabel("10")
        self.btnUpPMin = QPushButton("+")
        self.btnDownPMin = QPushButton("-")
        
        self.labelFMax = QLabel("Flow_max:")
        self.labelFMin = QLabel("Flow_min:")
        self.labelFMaxVal = QLabel()
        self.labelFMinVal = QLabel()

        
        layout = QGridLayout()
        
        layout.addWidget(self.labelAlarm, 1,1)
        layout.addWidget(self.graphWidgetPressure, 2,1, 3, 3)
        layout.addWidget(self.graphWidgetVol, 5,1, 3, 3)
        layout.addWidget(self.labelPMax,2,4)
        layout.addWidget(self.labelPMaxVal, 2,5)
        layout.addWidget(self.labelPAv,3,4)
        layout.addWidget(self.labelPAvVal, 3,5)
        layout.addWidget(self.labelPMin,4,4)
        layout.addWidget(self.labelPMinVal, 4,5)
        layout.addWidget(self.labelRespRate, 5,4)
        layout.addWidget(self.labelRespRateVal, 5,5)
        layout.addWidget(self.labelTidalVol, 6,4)
        layout.addWidget(self.labelTidalVolVal, 6,5)
        layout.addWidget(self.labelMinuteVol, 7,4)
        layout.addWidget(self.labelMinuteVolVal, 7,5)
        #layout.addWidget(self.btnUpPMax, 1,2)
        #layout.addWidget(self.labelAlarmPMax, 2,2)
        #layout.addWidget(self.btnDownPMax, 3,2)
        #layout.addWidget(self.btnUpPMin, 4,2)
        #layout.addWidget(self.labelAlarmPMin, 5,2)
        #layout.addWidget(self.btnDownPMin, 6,2)
        # layout.addWidget(self.labelFMax,4,4)
        # layout.addWidget(self.labelFMaxVal, 4,5)
        # layout.addWidget(self.labelFMin,5,4)
        # layout.addWidget(self.labelFMinVal, 5,5)
        

        self.labelPMax.setText("P_peak:")
        self.labelPMaxVal.setText("20")
        self.labelPMaxVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))
        self.labelPAv.setText("P_mean:")
        self.labelPAvVal.setText("20")
        self.labelPAvVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))
        self.labelPMin.setText("P_min:")
        self.labelPMinVal.setText("20")
        self.labelPMinVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))
        self.labelAlarmPMax.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Bold))
        self.labelAlarmPMin.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Bold))

        self.labelRespRateVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))
        self.labelTidalVolVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))
        self.labelTidalVolVal.setAlignment(QtCore.Qt.AlignRight)
        self.labelMinuteVolVal.setFont(QtGui.QFont("Arial", 48, QtGui.QFont.Bold))

        self.maxX = 100
        self.x = list(range(self.maxX))
        self.y = [randint(0,100) for _ in range(100)]
        self.yRealPressure = [randint(0,100) for _ in range(100)]
        self.counter = 0
        self.fcounter = 0
        self.vcounter = 0
        self.maxPressure = 0.0
        self.minPressure = 100.0
        self.avPressure = 0.0
        
        self.alarmMaxPressure = 40.0
        self.alarmMinPressure = -5.0
        
        self.graphWidgetPressure.setBackground('w')
        #self.graphWidget.setYRange(-10 , 45, padding=0)
        styles = {'color':'b', 'font-size':'20px'}
        self.graphWidgetPressure.setLabel("left","Pressure (cmH2O)", **styles)

        pen = pg.mkPen(color=(255,0,0))
        self.data_line = self.graphWidgetPressure.plot(self.x, self.y, pen=pen, fillLevel=0.0, brush=(255,0,0,255))

        self.x2 = list(range(100))
        self.y2 = [randint(0,100) for _ in range(100)]
        
        self.graphWidgetFlow.setBackground('w')
        self.graphWidgetVol.setBackground('w')

        #self.graphWidgetFlow.setYRange(-300 , 300, padding=0)
        self.graphWidgetFlow.setLabel("left","Flow (ml/s)", **styles)
        self.graphWidgetVol.setLabel("left","Volume (ml)", **styles)

        #pen = pg.mkPen(color=(255,0,0))
        pen2 = pg.mkPen(color=(0,0,255))
        self.data_line_flow = self.graphWidgetFlow.plot(self.x2, self.y2, pen=pen2, fillLevel=0.0, brush=(0,0,255,255))
        self.data_line_vol = self.graphWidgetVol.plot(self.x2, self.y2, pen=pen2, fillLevel=0.0, brush=(0,0,255,255))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.resize(800,480)
        # self.showFullScreen()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.timeout.connect(self.update_flow_plot_data)
        self.timer.timeout.connect(self.update_vol_plot_data)
        self.timer.start()
        
    def update_plot_data(self):
        self.counter += 1
        if self.counter >= self.maxX:
            self.counter = 0
        self.nextVal1 = (self.counter + 1) % self.maxX
        self.nextVal2 = (self.counter + 2) % self.maxX
        self.nextVal3 = (self.counter + 3) % self.maxX
        self.nextVal4 = (self.counter + 4) % self.maxX
        self.nextVal5 = (self.counter + 5) % self.maxX

        #self.x[self.counter] = self.counter
        #self.x = self.x[1:]
        #self.x.append(self.x[-1] + 1)
        
        #self.y = self.y[1:]
        #1 pressure = (sensor1.pressure - cal_1 - av_press)
        if(self.counter < 25 or self.counter > 50):
            pressure = 30
        else:
            pressure = 10
        # pressure = (self.counter % 1000) * 10.0
        if(self.counter == 100):
            self.counter = 0
       


        #self.y.append(pressure)
        self.y[self.nextVal1] = 0
        self.y[self.nextVal2] = 0
        self.y[self.nextVal3] = 0
        self.y[self.nextVal4] = 0
        self.y[self.nextVal5] = 0
        self.y[self.counter] = pressure
        self.yRealPressure[self.counter] = pressure
        self.data_line.setData(self.x, self.y)
        
        
        self.maxPressure = int(max(self.y))
        self.minPressure = int(min(self.yRealPressure))

        self.avPressure = int(statistics.mean(self.y))

        if (self.lastPressure < self.avPressure) and (pressure > self.avPressure):
            #inspiration
            self.currentInspiration = current_milli_time()
            time_elapsed_secs = (self.currentInspiration - self.lastInspiration) / 1000.0
            self.respRate = 60//time_elapsed_secs
            self.lastInspiration = self.currentInspiration
            self.lastPressure = pressure


        self.labelPMaxVal.setText(f"{self.maxPressure}")
        self.labelPAvVal.setText(f"{self.avPressure}")
        self.labelPMinVal.setText(f"{self.minPressure}")

        self.labelRespRateVal.setText(f"{int(self.respRate)}")

        
        if(pressure > 40 or pressure < -5):
            #1 alarmBuzzer.value = True
            print("High Pressure Alamr")
        # 1else:
            #1 alarmBuzzer.value = False
    def update_vol_plot_data(self):
        # flow = self.getFlow()
        flow = randint(0,2000)
        if(flow > 1000 and self.lastFlow < 1000): # we are in inspiration
            self.lastTidalVol = self.tidalVol
            self.tidalVolHistoryCounter += 1
            if(self.tidalVolHistoryCounter > 9):
                self.tidalVolHistoryCounter = 0
            self.tidalVolHistory[self.tidalVolHistoryCounter] = self.lastTidalVol
            self.meanTidalVol = int(statistics.mean(self.tidalVolHistory))
        if((self.lastFlow >= 1000 and flow < 1000) or (self.lastFlow == flow)):# we are in expiration
            self.tidalVol = 0.0

        if(flow < 1000.0):# we are in expiration
            self.currentExpiration = current_milli_time()
            time_elapsed_secs = (self.currentExpiration - self.lastExpTime) / 1000.0
            self.tidalVol += time_elapsed_secs * flow
            self.lastExpTime = self.currentExpiration
        self.lastFlow = flow

        self.vcounter += 1
        if self.vcounter >= self.maxX:
            self.vcounter = 0
        self.vnextVal1 = (self.vcounter + 1) % self.maxX
        self.vnextVal2 = (self.vcounter + 2) % self.maxX
        self.vnextVal3 = (self.vcounter + 3) % self.maxX
        self.vnextVal4 = (self.vcounter + 4) % self.maxX
        self.vnextVal5 = (self.vcounter + 5) % self.maxX


        #self.x2 = self.x2[1:]
        #self.x2.append(self.x2[-1] + 1)
        
        #self.y2 = self.y2[1:]
        #self.y.append(randint(0,100))
        self.y2[self.vnextVal1] = 0
        self.y2[self.vnextVal2] = 0
        self.y2[self.vnextVal3] = 0
        self.y2[self.vnextVal4] = 0
        self.y2[self.vnextVal5] = 0
        #self.y2.append(flow)
        self.y2[self.counter] = self.tidalVol
        # print(self.tidalVol)
        self.data_line_vol.setData(self.x2, self.y2)
        
        spaces = "_" * (3 - int(np.log10(self.lastTidalVol)))
        labelText = spaces + f"{int(self.lastTidalVol)}" + " ml"


        self.labelTidalVolVal.setText(labelText)
        self.labelMinuteVolVal.setText(f"{round(self.meanTidalVol * self.respRate/1000.0, 2)} L/min")

        
            
    def update_flow_plot_data(self):
        self.fcounter += 1
        if self.fcounter >= self.maxX:
            self.fcounter = 0
        self.fnextVal1 = (self.fcounter + 1) % self.maxX
        self.fnextVal2 = (self.fcounter + 2) % self.maxX
        self.fnextVal3 = (self.fcounter + 3) % self.maxX
        self.fnextVal4 = (self.fcounter + 4) % self.maxX
        self.fnextVal5 = (self.fcounter + 5) % self.maxX


        #self.x2 = self.x2[1:]
        #self.x2.append(self.x2[-1] + 1)
        
        #self.y2 = self.y2[1:]
        #self.y.append(randint(0,100))
        self.y2[self.fnextVal1] = 0
        self.y2[self.fnextVal2] = 0
        self.y2[self.fnextVal3] = 0
        self.y2[self.fnextVal4] = 0
        self.y2[self.fnextVal5] = 0
        flow = self.getFlow()
        #self.y2.append(flow)
        self.y2[self.counter] = flow
        self.data_line_flow.setData(self.x2, self.y2)
        
        
        
        self.maxFlow= int(max(self.y))
        self.minFlow = int(min(self.y))
        
        self.labelFMaxVal.setText(f"{self.maxFlow}")
        self.labelFMinVal.setText(f"{self.minFlow}")


            
    def getFlow(self):
        # p1 = sensor1.pressure - cal_1
        # p2 = sensor2.pressure - cal_2
        p1 = 0.0
        p2 = 0.0
        
        if(p1 > p2 and not math.isnan(p1) and not math.isnan(p2)):
            press_diff = math.sqrt( 2 * (p1 - p2)/rho)
        elif (p1 <= p2 and not math.isnan(p1) and not math.isnan(p2)):
            press_diff = math.sqrt( 2 * (p2 - p1)/rho) * -1.0
        else:
            return 0
        if (math.isnan(press_diff)):
            press_diff = 0
            print("nanan")
        return coeff * area * beta_thing * press_diff

def main():
    calibratePressureSensors(5)
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
