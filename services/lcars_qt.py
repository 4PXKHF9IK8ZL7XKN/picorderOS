#/bin/python3
import os
import os.path
import tempfile
import sys
import math
import random
import time
import psycopg2
import pyqtgraph as pg
import numpy as np

from datetime import timedelta

from objects import *
from picosglobals import *
from picoscolores import *

from picos_psql_config import load_config
from scipy.interpolate import griddata


from PyQt6.QtWidgets import QSpacerItem, QGraphicsBlurEffect, QGraphicsOpacityEffect, QHBoxLayout,QListWidget, QListWidgetItem, QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter, QStackedWidget

from PyQt6.QtGui import QColor, QBrush, QFont

from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup

from layout_colorwidget import Color

#selected_sensor_values = [["local","BME680","Barometer"],["local","GENERATORS","SineWave"],["local","BME680","Thermometer"],["local","GENERATORS","CosWave"],["local","BME680","Hygrometer"],["local","BME680","VOC"]]
selected_sensor_values = [["local","BME680","Barometer"],["local","BME680","Thermometer"],["local","BME680","VOC"],["local","BME680","Hygrometer"]]
#selected_sensor_values = [["local","BME680","Barometer"]]

_placeholder = """Ganz statisch text 
weil im tutorial etwas verlinkt wurde, 
was es in der welt von python 
ohne einen editor dazu einfach nicht giebt"""

top_elbow_css = """
                background-color:black;
                border-bottom-left-radius: 10px; 
                border-style: solid;
                """

bottom_elbow_css = """
                background-color:black;
                border-top-left-radius: 10px; 
                border-style: solid;
                """
                
list_widget_css = """
                QListWidget {
                background-color: black;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                font: bold 14px;
                padding-top: 0px;
                padding-bottom: 0px;
                }
                
                QListWidget::item:selected {        
                background-color: #f5f6fa;
                border-style: solid;
                border-width:0px;
                color: #000000;
                max-height:50px;
                min-height:50px;
                font: bold 14px;
                }
                
                QListWidget::item {
                background-color: #666688;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                margin-top: 2px;
                margin-bottom: 2px;
                margin-right: 75px;
                }
                """  
top_bar_css = """
                background-color: #5566ff;
                border: 5px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                border-bottom-left-radius: 25px; 
                """    
bottom_bar_css = """
                border: 5px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                background-color:#cc4444;
                border-top-left-radius: 25px; 
                """    

bar_css = """
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bbff, stop:1 #5566ff);
                border: 5px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                border-bottom-left-radius: 5px; 
                border-bottom-right-radius: 5px; 
                border-top-left-radius: 5px; 
                border-top-right-radius: 5px; 
                """
                
mask = """
                background-color: solid black;
                border: 5px solid black;
                border-style: solid;
                """
                
                
top_label = """
                border: 5px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                background-color: black;
                color: #5566ff;
                """
                
                
startup_label = """
                border: 5px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                background-color: black;
                font: bold 14px;
                color: #cc4444;
                """              


button_css = """
                background-color: #C5E566;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """      
                
button_css_bar_lvl1 = """
                background-color: #cccc66;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """  
                
button_css_bar_lvl2 = """
                background-color: #cc5599;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """                   
 
button_css_bar_lvl3 = """
                background-color: #5566ff;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """                                     
                
button_css_voc_lvl1 = """
                background-color: #38e428;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """
                                              
button_css_voc_lvl2 = """
                background-color: #95d057;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """         
                
                
button_css_voc_lvl3 = """
                background-color: #feff30;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """     
                
button_css_voc_lvl4 = """
                background-color: #f98115;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """                      
                                                  
button_css_voc_lvl5 = """
                background-color: #f81d05;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """  

button_css_voc_lvl6 = """
                background-color: #950a4b;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """  

button_css_voc_lvl7 = """
                background-color: #643404;
                border-style: solid;
                border-width:0px;
                border-color: #000000;
                max-height:50px;
                min-height:50px;
                color: #000000;
                font: bold 14px;
                border-radius: 25px; 
                margin-left: 500px;
                padding-right: 10px;
                """  


def rnd_colore():
	r = random.randint(0, 254)
	g = random.randint(0, 254)
	b = random.randint(0, 254)
	return (r,g,b)


def update_label():
        print("update")


class LCARS_Title(QLabel):
    def __init__(self, parent):
        super(LCARS_Title, self).__init__(parent)   
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
        background-color:transparent;
        color:#ffaa00;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("babs.otf", 28, QFont.Weight.Bold)) 
        
    
# A Spacer Class 
class empty_label(QLabel):
    def __init__(self, parent):
        super(empty_label, self).__init__(parent)   
        
        self.hight = 200
        
        self.setStyleSheet(f"""
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: none;
        border-style: solid;
        border-width:0px;
        border-color: blue;
        background-color:none;
        max-width:0px;
        max-height: {self.hight} px;
        min-width:0 px;
        min-height: {self.hight} px;
        """)
        
    def arrange(self,hight):
    
        self.hight = hight
    
        self.setStyleSheet(f"""
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: none;
        border-style: solid;
        border-width:0px;
        border-color: blue;
        background-color:none;
        max-width:0px;
        max-height: {self.hight} px;
        min-width:0 px;
        min-height: {self.hight} px;
        """)

        
class draw_line_widget(QLabel):
    def __init__(self):
        #super().__init__()
        super(QLabel, self).__init__()
        self.setAutoFillBackground(True)
        self.setStyleSheet(
        """min-height:50px;
        background-color: #2255ff;
        border-style: solid;
        color: #2255ff;
        margin: 5px;
        max-height:50px;
        min-width:100px;
        min-height:50px;
        border-radius: 25px;  
        font: bold 14px;
        padding-right: 15px;
        """)
        
class LCARS_MASK_Widget(QWidget):
    def __init__(self, parent):
        super(LCARS_MASK_Widget, self).__init__(parent)  
        
        print(size.width(), size.height())     
        mask_widget = QWidget(self)
        
        # Overlay Mask Top
        self.top_mask = QLabel(mask_widget)
        self.top_mask.setGeometry(0, 0, size.width(), size.height())
        self.top_mask.setStyleSheet(mask)
     

class LCARS_SPLIT2_Widget(QWidget):
    def __init__(self, parent):
        super(LCARS_GRAPH_Widget, self).__init__(parent)  
        
        print(size.width(), size.height())
         
        # Main widget
        # we need a canvas to draw oure LCARS Shapes first
        # this should be a stacked widget
        background_widget = QWidget(self)  
        
        # This Widgets are used to create a Layout on Top with Functunal Elements
       
        left_widget = QWidget() # empty object
        right_widget = QWidget() # empty object 
        
        # top_bar label
        top_bar = QLabel("Background Content", background_widget)
        top_bar.setGeometry(0, 0, size.width(), round(size.height()*0.25))
        top_bar.setStyleSheet(top_bar_css)
        top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # bottom_bar label
        bottom_bar = QLabel("Background Content",background_widget)
        bottom_bar.setGeometry(0, round(size.height()*0.26), size.width(), size.height())
        bottom_bar.setStyleSheet(bottom_bar_css)
        bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Overlay Mask Top
        self.top_mask = QLabel(background_widget)
        self.top_mask.setGeometry(round(size.width()*0.10), 0, size.width(), round(size.height()*0.23))
        self.top_mask.setStyleSheet(top_elbow_css)
 
        # Overlay Mask Bottom
        #self.bottom_mask = QLabel(background_widget)
        #self.bottom_mask.setGeometry(round(size.width()*0.10), round(size.height()*0.28), size.width(), size.height())
        #self.bottom_mask.setStyleSheet(bottom_elbow_css)
        
        # i want to write some text in the box here so i init the block
        #self.top_mask.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        #self.top_mask.setAlignment(Qt.AlignmentFlag.AlignTop)  
        
        #list_widget = QListWidget(background_widget)
        #list_widget.setGeometry(0, 300, 205, 230)
        #list_widget.setStyleSheet(list_widget_css)
        
# Draws 2 Line Top Bottom         
class LCARS_twoLines_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main widget
        twoLines_Widget = QWidget(self)  
    
        
        # top_bar label
        self.top_bar = QLabel("", twoLines_Widget)
        self.top_bar.setGeometry(0, 0, size.width(), round(size.height()*0.05))
        self.top_bar.setStyleSheet(bar_css)
        self.top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # bottom_bar label
        self.bottom_bar = QLabel("",twoLines_Widget)
        self.bottom_bar.setGeometry(0, size.height()-round(size.height()*0.05), size.width(), round(size.height()*0.05))
        self.bottom_bar.setStyleSheet(bar_css)
        self.bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Top Down Lines
        self.Ltop_mask = QLabel(twoLines_Widget)
        self.Ltop_mask.setGeometry(round(size.width()*0.05), 0, round(size.width()*0.015), round(size.height()*1.00))
        self.Ltop_mask.setStyleSheet(mask)
 
        # Overlay Mask Bottom
        self.Rtop_mask = QLabel(twoLines_Widget)
        self.Rtop_mask.setGeometry(round(size.width()-(size.width()*0.065)), 0, round(size.width()*0.015), round(size.height()*1.00))
        self.Rtop_mask.setStyleSheet(mask)
        
        # Overlay Mask Top
        self.label_text = "SYSTEM 47"
        self.top_label = QLabel(self.label_text,twoLines_Widget)
        self.font_calc = round((size.width()/25)*(len(self.label_text)))
        self.top_label.setGeometry(round(size.width()*0.10), 0, self.font_calc, round(size.height()*0.05))
        self.top_label.setStyleSheet(top_label)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
                
                
class StartupScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
                
        # Rahmen-Widget speichern, statt nur eine lokale Variable anzulegen
        self.start_Widget = LCARS_twoLines_Widget(self)
        self.start_Widget.setGeometry(0, 0, size.width(), size.height())
        
        self.frame_opacity = QGraphicsOpacityEffect(self.start_Widget)
        self.start_Widget.setGraphicsEffect(self.frame_opacity)
        self.frame_opacity.setOpacity(0.0)

        #Text Element
        self.startup_text = "INITIATING START-UP SEQUENCE"
        self.startup_label = QLabel(self.startup_text, self)
        self.startup_label.setFont(QFont("babs.otf", 28, QFont.Weight.Bold)) 
        self.startup_label.setGeometry(0, round(size.height()*0.7), size.width(), round(size.height()*0.05))
        self.startup_label.setStyleSheet(startup_label)
        self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_opacity = QGraphicsOpacityEffect(self.startup_label)
        self.startup_label.setGraphicsEffect(self.label_opacity)
        self.label_opacity.setOpacity(0.0)
        
        self.fade = QPropertyAnimation(self.label_opacity, b"opacity", self)
        self.fade.setDuration(1000)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        
        self.fade_main = QPropertyAnimation(self.frame_opacity, b"opacity", self)
        self.fade_main.setDuration(1000)
        self.fade_main.setStartValue(0.0)
        self.fade_main.setEndValue(1.0)

        self.fade_main.finished.connect(self.fade.start)

        self._started = False

    def showEvent(self, event):
        super().showEvent(event)
        if not self._started:
            self._started = True
            self.fade_main.start()
          
            

        


class MenuScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.menu_label = QLabel("Hauptmenü")
        self.content_layout.addWidget(self.menu_label)        
            
            
            

            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("LCARS")                      
        self.setStyleSheet("""
        background-color: black;
        """)

        self.showFullScreen()
       
       
        # Setup StackedWidget for memü
        self.setWindowTitle("LCARS")
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        # defining Pages
        self.startup_Widget = StartupScreen()  # erbt von LCARS_twoLines_Widget
        

        # menü elements  
        self.pages.addWidget(self.startup_Widget)

        # Side Rotation
        self.pages.setCurrentWidget(self.startup_Widget)


if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    
    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default.

    sys.exit(app.exec())
