import sys
from PyQt5 import sip
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSystemTrayIcon
from PyQt5.QtGui import QPixmap, QIntValidator, QDoubleValidator, QRegExpValidator, QIcon
from PyQt5.QtCore import Qt
import MainUI
from numba import jit
import os.path
from fpdf import FPDF

import webbrowser
import resources_rc

import matplotlib.pyplot as plt
from math import ceil, erf, floor
from numpy import log, square, sqrt, random, mean, inf, loadtxt, array
from prettytable import PrettyTable
from scipy.integrate import quad
from scipy.stats import norm, binom, poisson

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainCode(QMainWindow,MainUI.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        MainUI.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        logo=QPixmap(r"resources/Logo.png")
        self.UNCLogo_Label.setPixmap(logo.scaled(81,81))

### Connection
        self.ED_LOS_Mean_Edit.editingFinished.connect(self.edlosmeanvaluechange)
        self.ED_LOS_Std_Edit.editingFinished.connect(self.edlosstdvaluechange)
        self.ED_Census_Edit.editingFinished.connect(self.edcensusvaluechange)

        self.Hospital_LOS_Mean_Edit.editingFinished.connect(self.hospitallosmeanvaluechange)
        self.Hospital_LOS_Std_Edit.editingFinished.connect(self.hospitallosstdvaluechange)
        self.Hospital_Census_Edit.editingFinished.connect(self.hospitalcensusvaluechange)

        self.ICU_LOS_Mean_Edit.editingFinished.connect(self.iculosmeanvaluechange)
        self.ICU_LOS_Std_Edit.editingFinished.connect(self.iculosstdvaluechange)
        self.ICU_Census_Edit.editingFinished.connect(self.icucensusvaluechange)

        self.Percentage_Hospitalized_Edit.editingFinished.connect(self.percentagehospitalizedvaluechange)
        self.Percentage_ICU_Edit.editingFinished.connect(self.percentageicuvaluechange)

        self.Update_Arrival_Button.clicked.connect(self.on_open_daily)
        self.Update_Pattern_Button.clicked.connect(self.on_open_hourly)

        self.Run_Button.clicked.connect(self.run)
        self.See_Report_Button.clicked.connect(self.seereporthospital)

        self.Run_Button_ED.clicked.connect(self.runed)
        self.See_Report_Button_ED.clicked.connect(self.seereported)
### Initialization
        self.ED_length_of_stay_mean=7.56667
        self.ED_length_of_stay_std=8.266667
        self.ED_initial_condition=8

        self.Hospital_length_of_stay_mean=8
        self.Hospital_length_of_stay_std=6
        self.Hospital_initial_condition=15

        self.ICU_length_of_stay_mean=13
        self.ICU_length_of_stay_std=8
        self.ICU_initial_condition=3

        self.Percentage_hospitalized=0.3
        self.Percentage_icu = 0.06

        self.Daily_arrival_rate = []
        self.Hourly_pattern=[]

        self.Maximum_Hospital_stay=40
        self.Maximum_ICU_stay=40
        self.Maximum_ED_stay=48



### Edit Value Change function
    ### ED
    def edlosmeanvaluechange(self):
        try:
            float(self.ED_LOS_Mean_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ED_LOS_Mean_Edit.setText("0")
            self.ED_length_of_stay_mean = 0
        else:
            if float(self.ED_LOS_Mean_Edit.text()) != self.ED_length_of_stay_mean:
                self.ED_length_of_stay_mean = float(self.ED_LOS_Mean_Edit.text())

    def edlosstdvaluechange(self):
        try:
            float(self.ED_LOS_Std_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ED_LOS_Std_Edit.setText("0")
            self.ED_length_of_stay_std = 0
        else:
            if float(self.ED_LOS_Std_Edit.text()) != self.ED_length_of_stay_std:
                self.ED_length_of_stay_std = float(self.ED_LOS_Std_Edit.text())

    def edcensusvaluechange(self):
        try:
            float(self.ED_Census_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ED_Census_Edit.setText("0")
            self.ED_initial_condition = 0
        else:
            if float(self.ED_Census_Edit.text()) != self.ED_initial_condition:
                self.ED_initial_condition = float(self.ED_Census_Edit.text())
    ### Hospital:
    def hospitallosmeanvaluechange(self):
        try:
            float(self.Hospital_LOS_Mean_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.Hospital_LOS_Mean_Edit.setText("0")
            self.Hospital_length_of_stay_mean = 0
        else:
            if float(self.Hospital_LOS_Mean_Edit.text()) != self.Hospital_length_of_stay_mean:
                self.Hospital_length_of_stay_mean = float(self.Hospital_LOS_Mean_Edit.text())

    def hospitallosstdvaluechange(self):
        try:
            float(self.Hospital_LOS_Std_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.Hospital_LOS_Std_Edit.setText("0")
            self.Hospital_length_of_stay_std = 0
        else:
            if float(self.Hospital_LOS_Std_Edit.text()) != self.Hospital_length_of_stay_std:
                self.Hospital_length_of_stay_std = float(self.Hospital_LOS_Std_Edit.text())

    def hospitalcensusvaluechange(self):
        try:
            float(self.Hospital_Census_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.Hospital_Census_Edit.setText("0")
            self.Hospital_initial_condition = 0
        else:
            if float(self.Hospital_Census_Edit.text()) != self.Hospital_initial_condition:
                self.Hospital_initial_condition = float(self.Hospital_Census_Edit.text())
    ### ICU:
    def iculosmeanvaluechange(self):
        try:
            float(self.ICU_LOS_Mean_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ICU_LOS_Mean_Edit.setText("0")
            self.ICU_length_of_stay_mean = 0
        else:
            if float(self.ICU_LOS_Mean_Edit.text()) != self.ICU_length_of_stay_mean:
                self.ICU_length_of_stay_mean = float(self.ICU_LOS_Mean_Edit.text())

    def iculosstdvaluechange(self):
        try:
            float(self.ICU_LOS_Std_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ICU_LOS_Std_Edit.setText("0")
            self.ICU_length_of_stay_std = 0
        else:
            if float(self.ICU_LOS_Std_Edit.text()) != self.ICU_length_of_stay_std:
                self.ICU_length_of_stay_std = float(self.ICU_LOS_Std_Edit.text())

    def icucensusvaluechange(self):
        try:
            float(self.ICU_Census_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.ICU_Census_Edit.setText("0")
            self.ICU_initial_condition = 0
        else:
            if float(self.ICU_Census_Edit.text()) != self.ICU_initial_condition:
                self.ICU_initial_condition = float(self.ICU_Census_Edit.text())

    def percentagehospitalizedvaluechange(self):
        try:
            float(self.Percentage_Hospitalized_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.Percentage_Hospitalized_Edit.setText("0")
            self.Percentage_hospitalized = 0
        else:
            if float(self.Percentage_Hospitalized_Edit.text()) != self.Percentage_hospitalized:
                if float(self.Percentage_Hospitalized_Edit.text())>=0 and float(self.Percentage_Hospitalized_Edit.text()) <=100:
                    self.Percentage_hospitalized = float(self.Percentage_Hospitalized_Edit.text())/100
                else:
                    QMessageBox.warning(self, "Wrong Input", "Please put an number between 0 and 100")
                    self.Percentage_Hospitalized_Edit.setText("0")
                    self.Percentage_hospitalized=0

    def percentageicuvaluechange(self):
        try:
            float(self.Percentage_ICU_Edit.text())
        except:
            QMessageBox.warning(self, "Invalid Input", "Not a number")
            self.Percentage_ICU_Edit.setText("0")
            self.Percentage_icu = 0
        else:
            if float(self.Percentage_ICU_Edit.text())/100 != self.Percentage_icu:
                if float(self.Percentage_ICU_Edit.text())>=0 and float(self.Percentage_ICU_Edit.text()) <=100:
                    self.Percentage_icu = float(self.Percentage_ICU_Edit.text())/100
                else:
                    QMessageBox.warning(self, "Wrong Input", "Please put an number between 0 and 100")
                    self.Percentage_ICU_Edit.setText("0")
                    self.Percentage_icu=0

    def on_open_daily(self):
        txtstr = ""
        FullFileName, _ = QFileDialog.getOpenFileName(self, '打开', r'./', 'TXT (*.txt)')
        try:
            with open(FullFileName, 'rt') as f:
                lines = f.readlines()
        except IOError:
            QMessageBox.warning(self, "Error", "No File")
            self.Arrival_Status_Label.setText("No File")
            self.Arrival_Status_Label.setStyleSheet("color:Red")
            self.Daily_arrival_rate = []
        except Warning:
            QMessageBox.warning(self, "Error", "Warning")
            self.Arrival_Status_Label.setText("Warning")
            self.Arrival_Status_Label.setStyleSheet("color:Red")
        except:
            QMessageBox.warning(self, "Error", "Exception")
            self.Arrival_Status_Label.setText("Exception")
            self.Arrival_Status_Label.setStyleSheet("color:Red")
        else:
            self.Daily_arrival_rate = []
            try:
                for line in lines:
                    txtstr = txtstr + line
                    line = line.strip('\n')  # 将\n去掉
                    self.Daily_arrival_rate.extend(line.split(' '))  # 将空格作为分隔符将一个字符切割成一个字符数组
                self.Arrival_Status_Label.setStyleSheet("color:Green")
                self.Arrival_Status_Label.setText("Stored")
            except:
                QMessageBox.warning(self, "Error", "Incorrect Format")
                self.Arrival_Status_Label.setText("Exception")
                self.Arrival_Status_Label.setStyleSheet("color:Red")

    def on_open_hourly(self):
        txtstr = ""
        FullFileName, _ = QFileDialog.getOpenFileName(self, '打开', r'./', 'TXT (*.txt)')
        try:
            with open(FullFileName, 'rt') as f:
                lines = f.readlines()
        except IOError:
            QMessageBox.warning(self, "Error", "No File")
            self.Pattern_Status_Label.setText("No File")
            self.Pattern_Status_Label.setStyleSheet("color:Red")
            self.Hourly_pattern = []
        except Warning:
            QMessageBox.warning(self, "Error", "Warning")
            self.Pattern_Status_Label.setText("Warning")
            self.Pattern_Status_Label.setStyleSheet("color:Red")
            self.Hourly_pattern = []
        except:
            QMessageBox.warning(self, "Error", "Exception")
            self.Pattern_Status_Label.setText("Exception")
            self.Pattern_Status_Label.setStyleSheet("color:Red")
            self.Hourly_pattern = []
        else:
            self.Hourly_pattern = []
            try:
                for line in lines:
                    txtstr = txtstr + line
                    line = line.strip('\n')  # 将\n去掉
                    self.Hourly_pattern.extend(line.split(' '))  # 将空格作为分隔符将一个字符切割成一个字符数组
                if len(self.Hourly_pattern)==24 and round((sum(float(i) for i in self.Hourly_pattern)),2)==1:
                    self.Pattern_Status_Label.setStyleSheet("color:Green")
                    self.Pattern_Status_Label.setText("Stored")
                else:
                    QMessageBox.warning(self, "Error", "Should have 24 lines and add up to one")
                    self.Pattern_Status_Label.setText("Wrong")
                    self.Pattern_Status_Label.setStyleSheet("color:Red")
                    self.Hourly_pattern=[]
            except:
                QMessageBox.warning(self, "Error", "Incorrect Format")
                self.Pattern_Status_Label.setText("Exception")
                self.Pattern_Status_Label.setStyleSheet("color:Red")

    def run(self):
        # See if the data is complete:
        flag2=False
        flag3=False

        if self.Hospital_length_of_stay_mean!=0 and self.Hospital_length_of_stay_std!=0 and self.Daily_arrival_rate!=[] and self.Percentage_hospitalized!=0:
            flag2=True
        if self.Hospital_length_of_stay_mean!=0 and self.Hospital_length_of_stay_std!=0  and self.Daily_arrival_rate!=[] and self.Percentage_icu!=0:
            flag3=True

        processbartotallength=flag2*len(self.Daily_arrival_rate)+flag3*len(self.Daily_arrival_rate)

        if flag2==True:
            mu = log(square(self.Hospital_length_of_stay_mean) / sqrt(square(self.Hospital_length_of_stay_mean) + square(self.Hospital_length_of_stay_mean)))
            stddev = sqrt(log(1 + square(self.Hospital_length_of_stay_mean) / square(self.Hospital_length_of_stay_mean)))
            ArrivalRate = array(self.Daily_arrival_rate, dtype=float)
            ArrivalRate=ArrivalRate*self.Percentage_hospitalized
            TotalTimeLength = ArrivalRate.size
            initial_condition=self.Hospital_initial_condition

            step = 1
            t = 1
            tlist = []
            tlist = range(1, TotalTimeLength + 1)
            mt = []
            mt5=[]
            mt95=[]
            pt25=[]
            pt50=[]
            pt75=[]
            pt100=[]
            pt125=[]
            pt150=[]
            pt175=[]
            error = []
            st = []
            stl = []

            while t <= TotalTimeLength:
                ans, err = quad(f, 0, t, args=(t,mu,stddev,ArrivalRate), limit=400)
                total_probability = 0
                probability_still_in_system = 1 - rs(t,mu,stddev,self.Hospital_length_of_stay_mean)
                # Calculate the mean
                mttemp = initial_condition * probability_still_in_system + ans
                mt.append(mttemp)
                # Calculate the numerical distribution:
                temptotal = 0
                flag = [False, False]
                tempcdf = 0
                while tempcdf <= 0.99:
                    i = 0
                    if t <=self.Maximum_Hospital_stay:
                        while i <= temptotal and i <= initial_condition:
                            if i <= initial_condition:
                                tempcdf = tempcdf + binom.pmf(i, initial_condition,probability_still_in_system) * poisson.pmf((temptotal - i),ans)
                            i = i + 1
                    else:
                        tempcdf=poisson.cdf(temptotal,ans)
                    if tempcdf >= 0.05 and flag[0] == False:
                        if temptotal - 1 > 0:
                            tempq = temptotal - 1
                        else:
                            tempq = 0
                        mt5.append(tempq)
                        flag[0] = True
                    if tempcdf >= 0.95 and flag[1] == False:
                        mt95.append(temptotal)
                        flag[1] = True
                    QApplication.processEvents()
                    if temptotal==25:
                        pt25.append(1-tempcdf)
                    if temptotal == 50:
                        pt50.append(1 - tempcdf)
                    if temptotal == 75:
                        pt75.append(1 - tempcdf)
                    if temptotal == 100:
                        pt100.append(1 - tempcdf)
                    if temptotal == 125:
                        pt125.append(1 - tempcdf)
                    if temptotal == 150:
                        pt150.append(1 - tempcdf)
                    if temptotal == 175:
                        pt175.append(1 - tempcdf)
                    temptotal = temptotal + 1
                temptotal = temptotal - 1
                if temptotal < 25:
                    pt25.append(float(0))
                if temptotal < 50:
                    pt50.append(float(0))
                if temptotal < 75:
                    pt75.append(float(0))
                if temptotal < 100:
                    pt100.append(float(0))
                if temptotal < 125:
                    pt125.append(float(0))
                if temptotal < 150:
                    pt150.append(float(0))
                if temptotal < 175:
                    pt175.append(float(0))
                t = t + step
                QApplication.processEvents()
                self.ProgressBar.setValue(ceil((t)/processbartotallength*100))


            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(tlist, mt)
            ax.set_title('Expected Number and 95% Band')
            ax.fill_between(tlist,mt5,mt95,color='b', alpha=0.1)
            ax.set_ylabel("Hospital Census")
            ax.set_xlabel("Days")
            fig.savefig('temp2.png')

            temp2=QPixmap("temp2.png")
            self.Hospital_Graph_Label.setPixmap(temp2.scaled(480,360))

            TableData=PrettyTable()
            TableData.field_names=["Num Pts","10 Days","20 Days","30 Days","40 Days","50 Days","60 Days","70 Days","80 Days","90 Days"]
            TableData.add_row(["25 pts",maxc(pt25[0:10]),maxc(pt25[0:20]),maxc(pt25[0:30]),maxc(pt25[0:40]),maxc(pt25[0:50]),maxc(pt25[0:60]),maxc(pt25[0:70]),maxc(pt25[0:80]),maxc(pt25[0:90])])
            TableData.add_row(["50 pts",maxc(pt50[0:10]),maxc(pt50[0:20]),maxc(pt50[0:30]),maxc(pt50[0:40]),maxc(pt50[0:50]),maxc(pt50[0:60]),maxc(pt50[0:70]),maxc(pt50[0:80]),maxc(pt50[0:90])])
            TableData.add_row(["75 pts", maxc(pt75[0:10]), maxc(pt75[0:20]), maxc(pt75[0:30]), maxc(pt75[0:40]), maxc(pt75[0:50]),maxc(pt75[0:60]), maxc(pt75[0:70]), maxc(pt75[0:80]),maxc(pt75[0:90])])
            TableData.add_row(["100 pts", maxc(pt100[0:10]), maxc(pt100[0:20]), maxc(pt100[0:30]), maxc(pt100[0:40]), maxc(pt100[0:50]),maxc(pt100[0:60]), maxc(pt100[0:70]), maxc(pt100[0:80]),maxc(pt100[0:90])])
            TableData.add_row(["125 pts", maxc(pt125[0:10]), maxc(pt125[0:20]), maxc(pt125[0:30]), maxc(pt125[0:40]), maxc(pt125[0:50]),maxc(pt125[0:60]), maxc(pt125[0:70]), maxc(pt125[0:80]),maxc(pt125[0:90])])
            TableData.add_row(["150 pts", maxc(pt150[0:10]), maxc(pt150[0:20]), maxc(pt150[0:30]), maxc(pt150[0:40]), maxc(pt150[0:50]),maxc(pt150[0:60]), maxc(pt150[0:70]), maxc(pt150[0:80]),maxc(pt150[0:90])])
            TableData.add_row(["175 pts", maxc(pt175[0:10]), maxc(pt175[0:20]), maxc(pt175[0:30]), maxc(pt175[0:40]), maxc(pt175[0:50]),maxc(pt175[0:60]), maxc(pt175[0:70]), maxc(pt175[0:80]),maxc(pt175[0:90])])

            header,data=get_data_from_prettytable(TableData)

            pdf = FPDF()
              # Font style
            pdf.set_font("Arial", size=9)
            epw = pdf.w - 2 * pdf.l_margin  # Witdh of document
            col_width = pdf.w / 10.5  # Column width in table
            row_height = pdf.font_size * 1.5  # Row height in table
            spacing = 1.3

            pdf.add_page()
            pdf.set_font("Arial", size=20)
            pdf.cell(epw, 0.0, 'COVID-CAT Report for Hospital', align='C')  # create title cell
            pdf.ln(row_height * spacing)  # Define title line style

            pdf.image("temp2.png",w=epw,h=epw*0.75)

            pdf.set_font("Arial", size=15)
            pdf.cell(epw, pdf.font_size * spacing, 'Probability of exceeding a given number of patients within:',0,1, align='L')

            pdf.set_font("Arial", size=9)
            # Add header
            for item in header:  # for each column
                pdf.cell(col_width, row_height * spacing,  # Add a new cell
                         txt=item, border=1)
            pdf.ln(row_height * spacing)  # New line after header

            for row in data:  # For each row of the table
                for item in row:  # For each cell in row
                    pdf.cell(col_width, row_height * spacing,  # Add cell
                             txt=item, border=1)
                pdf.ln(row_height * spacing)  # Add line at the end of row

        if flag3==True:
            mu = log(square(self.ICU_length_of_stay_mean) / sqrt(
                square(self.ICU_length_of_stay_mean) + square(self.ICU_length_of_stay_mean)))
            stddev = sqrt(
                log(1 + square(self.ICU_length_of_stay_mean) / square(self.ICU_length_of_stay_mean)))
            ArrivalRate = array(self.Daily_arrival_rate, dtype=float)
            ArrivalRate = ArrivalRate * self.Percentage_icu
            TotalTimeLength = ArrivalRate.size
            initial_condition = self.ICU_initial_condition

            step = 1
            t = 1
            tlist = []
            tlist = range(1, TotalTimeLength + 1)
            zeros= [0 for i in tlist]
            mt = []
            mt5=[]
            mt95=[]
            pt15=[]
            pt20=[]
            pt25=[]
            pt30=[]
            pt35=[]
            pt40=[]
            pt45=[]
            error = []
            st = []
            stl = []

            while t <= TotalTimeLength:
                ans, err = quad(f, 0, t, args=(t,mu,stddev,ArrivalRate), limit=500)
                total_probability = 0
                probability_still_in_system = 1 - rs(t,mu,stddev,self.ICU_length_of_stay_mean)
                # Calculate the mean
                mttemp = initial_condition * probability_still_in_system + ans
                mt.append(mttemp)
                # Calculate the numerical distribution:
                temptotal = 0
                flag = [False, False]
                tempcdf = 0
                while tempcdf <= 0.99:
                    i = 0
                    if t <=self.Maximum_ICU_stay:
                        while i <= temptotal and i <= initial_condition:
                            if i <= initial_condition:
                                tempcdf = tempcdf + binom.pmf(i, initial_condition,probability_still_in_system) * poisson.pmf((temptotal - i),ans)
                            i = i + 1
                    else:
                        tempcdf=poisson.cdf(temptotal,ans)
                    if tempcdf >= 0.05 and flag[0] == False:
                        if temptotal-1>0:
                            tempq=temptotal-1
                        else:
                            tempq=0
                        mt5.append(tempq)
                        flag[0] = True
                    if tempcdf >= 0.95 and flag[1] == False:
                        mt95.append(temptotal)
                        flag[1] = True
                    QApplication.processEvents()
                    if temptotal==15:
                        pt15.append(1-tempcdf)
                    if temptotal == 20:
                        pt20.append(1 - tempcdf)
                    if temptotal == 25:
                        pt25.append(1 - tempcdf)
                    if temptotal == 30:
                        pt30.append(1 - tempcdf)
                    if temptotal == 35:
                        pt35.append(1 - tempcdf)
                    if temptotal ==40:
                        pt40.append(1 - tempcdf)
                    if temptotal == 45:
                        pt45.append(1 - tempcdf)
                    temptotal = temptotal + 1
                temptotal = temptotal - 1
                if temptotal < 15:
                    pt15.append(float(0))
                if temptotal <20:
                    pt20.append(float(0))
                if temptotal < 25:
                    pt25.append(float(0))
                if temptotal < 30:
                    pt30.append(float(0))
                if temptotal < 35:
                    pt35.append(float(0))
                if temptotal < 40:
                    pt40.append(float(0))
                if temptotal < 45:
                    pt45.append(float(0))
                t = t + step
                QApplication.processEvents()
                self.ProgressBar.setValue(ceil((t+flag2*len(self.Daily_arrival_rate)) / processbartotallength * 100))


            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(tlist, mt)
            ax.set_title('Expected Number and 95% Band')
            ax.fill_between(tlist,mt5,mt95,color='b', alpha=0.1)
            ax.set_ylabel("ICU Census")
            ax.set_xlabel("Days")
            fig.savefig('temp3.png')

            temp3=QPixmap("temp3.png")
            self.ICU_Graph_Label.setPixmap(temp3.scaled(480,360))

            TableData=PrettyTable()
            TableData.field_names=["Num Pts","10 Days","20 Days","30 Days","40 Days","50 Days","60 Days","70 Days","80 Days","90 Days"]
            TableData.add_row(["15 pts",maxc(pt15[0:10]),maxc(pt15[0:20]),maxc(pt15[0:30]),maxc(pt15[0:40]),maxc(pt15[0:50]),maxc(pt15[0:60]),maxc(pt15[0:70]),maxc(pt15[0:80]),maxc(pt15[0:90])])
            TableData.add_row(["20 pts", maxc(pt20[0:10]), maxc(pt20[0:20]), maxc(pt20[0:30]), maxc(pt20[0:40]), maxc(pt20[0:50]),maxc(pt20[0:60]), maxc(pt20[0:70]), maxc(pt20[0:80]),maxc(pt20[0:90])])
            TableData.add_row(["25 pts", maxc(pt25[0:10]), maxc(pt25[0:20]), maxc(pt25[0:30]), maxc(pt25[0:40]), maxc(pt25[0:50]),maxc(pt25[0:60]), maxc(pt25[0:70]), maxc(pt25[0:80]),maxc(pt25[0:90])])
            TableData.add_row(["30 pts", maxc(pt30[0:10]), maxc(pt30[0:20]), maxc(pt30[0:30]), maxc(pt30[0:40]), maxc(pt30[0:50]),maxc(pt30[0:60]), maxc(pt30[0:70]), maxc(pt30[0:80]),maxc(pt30[0:90])])
            TableData.add_row(["35 pts", maxc(pt35[0:10]), maxc(pt35[0:20]), maxc(pt35[0:30]), maxc(pt35[0:40]), maxc(pt35[0:50]),maxc(pt35[0:60]), maxc(pt35[0:70]), maxc(pt35[0:80]),maxc(pt35[0:90])])
            TableData.add_row(["40 pts", maxc(pt40[0:10]), maxc(pt40[0:20]), maxc(pt40[0:30]), maxc(pt40[0:40]), maxc(pt40[0:50]),maxc(pt40[0:60]), maxc(pt40[0:70]), maxc(pt40[0:80]),maxc(pt40[0:90])])
            TableData.add_row(["45 pts", maxc(pt45[0:10]), maxc(pt45[0:20]), maxc(pt45[0:30]), maxc(pt45[0:40]), maxc(pt45[0:50]),maxc(pt45[0:60]), maxc(pt45[0:70]), maxc(pt45[0:80]),maxc(pt45[0:90])])
            header,data=get_data_from_prettytable(TableData)

              # Font style
            pdf.set_font("Arial", size=9)
            epw = pdf.w - 2 * pdf.l_margin  # Witdh of document
            col_width = pdf.w / 10.5  # Column width in table
            row_height = pdf.font_size * 1.5  # Row height in table
            spacing = 1.3

            pdf.add_page()
            pdf.set_font("Arial", size=20)
            pdf.cell(epw, 0.0, 'COVID-CAT Report for ICU', align='C')  # create title cell
            pdf.ln(row_height * spacing)  # Define title line style

            pdf.image("temp3.png",w=epw,h=epw*0.75)

            pdf.set_font("Arial", size=15)
            pdf.cell(epw, pdf.font_size * spacing, 'Probability of exceeding a given number of patients within:',0,1, align='L')

            pdf.set_font("Arial", size=9)
            # Add header
            for item in header:  # for each column
                pdf.cell(col_width, row_height * spacing,  # Add a new cell
                         txt=item, border=1)
            pdf.ln(row_height * spacing)  # New line after header

            for row in data:  # For each row of the table
                for item in row:  # For each cell in row
                    pdf.cell(col_width, row_height * spacing,  # Add cell
                             txt=item, border=1)
                pdf.ln(row_height * spacing)  # Add line at the end of row

        if flag2==True or flag3==True:
            try:
                pdf.output('Report_Hospital_and_ICU.pdf')  # Create pdf file
                pdf.close()  # Close file
            except:
                QMessageBox.warning(self, "Error", "Couldn't Create PDF. Please close the PDF file of report")
        else:
            QMessageBox.warning(self, "Error", "Not Enough Data")

    def seereporthospital(self):
        try:
            attempt=open("Report_Hospital_and_ICU.pdf")
            attempt.close()
            webbrowser.open_new(r"Report_Hospital_and_ICU.pdf")
        except:
            QMessageBox.warning(self, "Error", "Cannot find any report. Please first run the analysis")

    def runed(self):
        flag1 = False
        if self.ED_length_of_stay_mean != 0 and self.ED_length_of_stay_std != 0 and self.Daily_arrival_rate != [] and self.Hourly_pattern != []:
            flag1 = True

        processbartotallength = flag1 * len(self.Hourly_pattern) * len(self.Daily_arrival_rate)

        if flag1==True:
            mu = log(square(self.ED_length_of_stay_mean) / sqrt(
                square(self.ED_length_of_stay_mean) + square(self.ED_length_of_stay_mean)))
            stddev = sqrt(
                log(1 + square(self.ED_length_of_stay_mean) / square(self.ED_length_of_stay_mean)))

            ArrivalRate=[]
            for j in range(len(self.Daily_arrival_rate)):
                for k in range(24):
                    ArrivalRate.append(float(self.Daily_arrival_rate[j])*float(self.Hourly_pattern[k]))
            ArrivalRate = array(ArrivalRate, dtype=float)
            TotalTimeLength = ArrivalRate.size
            initial_condition = self.ED_initial_condition

            step = 1
            t = 1
            tlist = []
            tlist = range(1, TotalTimeLength + 1)
            mt = []
            mt5 = []
            mt95 = []
            pt10 = []
            pt15 = []
            pt20 = []
            pt25 = []
            pt30 = []
            pt35 = []
            pt40 = []
            error = []
            st = []
            stl = []

            while t <= TotalTimeLength:
                ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
                total_probability = 0
                probability_still_in_system = 1 - rs(t, mu, stddev, self.ED_length_of_stay_mean)
                # Calculate the mean
                mttemp = initial_condition * probability_still_in_system + ans
                mt.append(mttemp)
                # Calculate the numerical distribution:
                temptotal = 0
                flag = [False, False]
                tempcdf = 0
                while tempcdf <= 0.99:
                    i = 0
                    if t <= self.Maximum_ED_stay:
                        while i <= temptotal and i <= initial_condition:
                            if i <= initial_condition:
                                tempcdf = tempcdf + binom.pmf(i, initial_condition,
                                                              probability_still_in_system) * poisson.pmf(
                                    (temptotal - i), ans)
                            i = i + 1
                    else:
                        tempcdf = poisson.cdf(temptotal, ans)
                    if tempcdf >= 0.05 and flag[0] == False:
                        if temptotal - 1 > 0:
                            tempq = temptotal - 1
                        else:
                            tempq = 0
                        mt5.append(tempq)
                        flag[0] = True
                    if tempcdf >= 0.95 and flag[1] == False:
                        mt95.append(temptotal)
                        flag[1] = True
                    QApplication.processEvents()
                    if temptotal == 10:
                        pt10.append(1 - tempcdf)
                    if temptotal == 15:
                        pt15.append(1 - tempcdf)
                    if temptotal == 20:
                        pt20.append(1 - tempcdf)
                    if temptotal == 25:
                        pt25.append(1 - tempcdf)
                    if temptotal == 30:
                        pt30.append(1 - tempcdf)
                    if temptotal == 35:
                        pt35.append(1 - tempcdf)
                    if temptotal == 40:
                        pt40.append(1 - tempcdf)
                    temptotal = temptotal + 1
                temptotal=temptotal-1
                if temptotal < 10:
                    pt10.append(float(0))
                if temptotal < 15:
                    pt15.append(float(0))
                if temptotal < 20:
                    pt20.append(float(0))
                if temptotal < 25:
                    pt25.append(float(0))
                if temptotal < 30:
                    pt30.append(float(0))
                if temptotal < 35:
                    pt35.append(float(0))
                if temptotal < 40:
                    pt40.append(float(0))
                t = t + step
                QApplication.processEvents()
                self.ProgressBar.setValue(ceil((t) / processbartotallength * 100))

            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(tlist, mt)
            ax.set_title('Expected Number and 95% Band')
            ax.fill_between(tlist, mt5, mt95, color='b', alpha=0.1)
            ax.set_ylabel("ED Census")
            ax.set_xlabel("Hours")
            fig.savefig('temp1.png')

            temp1 = QPixmap("temp1.png")
            self.ED_Graph_Label.setPixmap(temp1.scaled(480, 360))

            TableData = PrettyTable()
            TableData.field_names = ["Num Pts", "10 Days", "20 Days", "30 Days", "40 Days", "50 Days", "60 Days",
                                        "70 Days", "80 Days","90 Days"]
            TableData.add_row(
                ["10 pts", maxc(pt10[0:240]), maxc(pt10[0:480]), maxc(pt10[0:720]), maxc(pt10[0:960]), maxc(pt10[0:1200]),
                 maxc(pt10[0:1440]), maxc(pt10[0:1680]), maxc(pt10[0:1920]),maxc(pt10[0:2160])])
            TableData.add_row(
                ["15 pts", maxc(pt15[0:240]), maxc(pt15[0:480]), maxc(pt15[0:720]), maxc(pt15[0:960]), maxc(pt15[0:1200]),
                 maxc(pt15[0:1440]), maxc(pt15[0:1680]), maxc(pt15[0:1920]),maxc(pt15[0:2160])])
            TableData.add_row(
                ["20 pts", maxc(pt20[0:240]), maxc(pt20[0:480]), maxc(pt20[0:720]), maxc(pt20[0:960]), maxc(pt20[0:1200]),
                 maxc(pt20[0:1440]), maxc(pt20[0:1680]), maxc(pt20[0:1920]),maxc(pt20[0:2160])])
            TableData.add_row(
                ["25 pts", maxc(pt25[0:240]), maxc(pt25[0:480]), maxc(pt25[0:720]), maxc(pt25[0:960]), maxc(pt25[0:1200]),
                 maxc(pt25[0:1440]), maxc(pt25[0:1680]), maxc(pt25[0:1920]),maxc(pt25[0:2160])])
            TableData.add_row(
                ["15 pts", maxc(pt30[0:240]), maxc(pt30[0:480]), maxc(pt30[0:720]), maxc(pt30[0:960]), maxc(pt30[0:1200]),
                 maxc(pt30[0:1440]), maxc(pt30[0:1680]), maxc(pt30[0:1920]),maxc(pt30[0:2160])])
            TableData.add_row(
                ["35 pts", maxc(pt35[0:240]), maxc(pt35[0:480]), maxc(pt35[0:720]), maxc(pt35[0:960]), maxc(pt35[0:1200]),
                 maxc(pt35[0:1440]), maxc(pt35[0:1680]), maxc(pt35[0:1920]),maxc(pt35[0:2160])])
            TableData.add_row(
                ["40 pts", maxc(pt40[0:240]), maxc(pt40[0:480]), maxc(pt40[0:720]), maxc(pt40[0:960]), maxc(pt40[0:1200]),
                 maxc(pt40[0:1440]), maxc(pt40[0:1680]), maxc(pt40[0:1920]),maxc(pt40[0:2160])])

            header, data = get_data_from_prettytable(TableData)

            pdf = FPDF()
            # Font style
            pdf.set_font("Arial", size=9)
            epw = pdf.w - 2 * pdf.l_margin  # Witdh of document
            col_width = pdf.w / 10.5  # Column width in table
            row_height = pdf.font_size * 1.5  # Row height in table
            spacing = 1.3

            pdf.add_page()
            pdf.set_font("Arial", size=20)
            pdf.cell(epw, 0.0, 'COVID-CAT Report for ED', align='C')  # create title cell
            pdf.ln(row_height * spacing)  # Define title line style

            pdf.image("temp1.png", w=epw, h=epw * 0.75)

            pdf.set_font("Arial", size=15)
            pdf.cell(epw, pdf.font_size * spacing, 'Probability of exceeding a given number of patients within:', 0, 1,
                     align='L')

            pdf.set_font("Arial", size=9)
            # Add header
            for item in header:  # for each column
                pdf.cell(col_width, row_height * spacing,  # Add a new cell
                         txt=item, border=1)
            pdf.ln(row_height * spacing)  # New line after header

            for row in data:  # For each row of the table
                for item in row:  # For each cell in row
                    pdf.cell(col_width, row_height * spacing,  # Add cell
                             txt=item, border=1)
                pdf.ln(row_height * spacing)

        if flag1==True:
            try:
                pdf.output('Report_ED.pdf')  # Create pdf file
                pdf.close()  # Close file
            except:
                QMessageBox.warning(self, "Error", "Couldn't Create PDF. Please close the PDF file of report")
        else:
            QMessageBox.warning(self, "Error", "Not Enough Data")

    def seereported(self):
        try:
            attempt=open("Report_ED.pdf")
            attempt.close()
            webbrowser.open_new(r"Report_ED.pdf")
        except:
            QMessageBox.warning(self, "Error", "Cannot find any report. Please first run the analysis")

    global lognorm
    @jit
    def lognorm(x, mu, sigma):
        a = (log(x) - mu) / sqrt(2 * sigma ** 2)
        p = 0.5 + 0.5 * erf(a)
        return p

    global lognormc
    @jit
    def lognormc(x, mu, sigma):
        return (1 - lognorm(x, mu, sigma))

    global flambda
    @jit
    def flambda(x, Arrival_rate):
        p = floor(x)
        return Arrival_rate[p]

    global f
    @jit
    def f(s, t, mu, stddev, Arrival_rate):
        hourofday = floor((t - s) % 24)
        p = flambda(t - s,Arrival_rate) * (1 - lognorm(s, mu, stddev))
        return p

    global rs
    def rs(x,mu,stddev,length_of_stay_mean):
        temp_int, temp_err = quad(lognormc, 0, x, args=(mu, stddev), limit=500)
        return temp_int / length_of_stay_mean

    global get_data_from_prettytable
    def get_data_from_prettytable(data):
        """
        Get a list of list from pretty_data table
        Arguments:
            :param data: data table to process
            :type data: PrettyTable
        """

        def remove_space(liste):
            """
            Remove space for each word in a list
            Arguments:
                :param liste: list of strings
            """
            list_without_space = []
            for mot in liste:  # For each word in list
                word_without_space = mot.replace(' ', '')  # word without space
                list_without_space.append(word_without_space)  # list of word without space
            return list_without_space

        # Get each row of the table
        string_x = str(data).split('\n')  # Get a list of row
        header = string_x[1].split('|')[1: -1]  # Columns names
        rows = string_x[3:len(string_x) - 1]  # List of rows

        list_word_per_row = []
        for row in rows:  # For each word in a row
            row_resize = row.split('|')[1:-1]  # Remove first and last arguments
            list_word_per_row.append(remove_space(row_resize))  # Remove spaces

        return header, list_word_per_row

    global maxc
    @jit
    def maxc(datalist):
        temp=max(datalist)
        if temp<=0:
            return round(0,2)
        else:
            return round(temp,2)

if __name__=='__main__':
    app = QApplication(sys.argv)
    md = MainCode()
    md.setWindowTitle("Queue Analyzer")
    md.show()
    tray = QSystemTrayIcon(md)
    tray.setIcon(QIcon(r"resources/ico.png"))
    tray.show()
    tray.showMessage("Message", "Queue Analyzer is Running", icon=0)
    md.setWindowIcon(QIcon(r"resources/ico.png"))


    temp1 = QPixmap(r"resources/InitialTemp1.png")
    md.ED_Graph_Label.setPixmap(temp1.scaled(480, 360))



    temp2 = QPixmap(r"resources/InitialTemp2.png")
    md.Hospital_Graph_Label.setPixmap(temp2.scaled(480, 360))



    temp3=QPixmap(r"resources/InitialTemp3.png")
    md.ICU_Graph_Label.setPixmap(temp3.scaled(480,360))


    sys.exit(app.exec_())

