#/bin/python3
import os
import os.path
import tempfile
import sys
import math
import random
import time
import pyqtgraph as pg
import numpy as np
import geopandas 

from datetime import timedelta

from objects import *
from picosglobals import *
from picoscolores import *

from picos_psql_config import load_config
from scipy.interpolate import griddata

import psycopg
from picos_psql_config import load_config
from scipy.interpolate import griddata
from sqlalchemy import create_engine, inspect


from PyQt6.QtWidgets import QSpacerItem, QGraphicsBlurEffect, QGraphicsOpacityEffect, QHBoxLayout,QListWidget, QListWidgetItem, QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter, QStackedWidget

from PyQt6.QtSvgWidgets import QSvgWidget

from PyQt6.QtGui import QColor, QBrush, QFont, QFontDatabase

from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup, pyqtSignal, QEasingCurve

from layout_colorwidget import Color





#selected_sensor_values = [["local","BME680","Barometer"],["local","GENERATORS","SineWave"],["local","BME680","Thermometer"],["local","GENERATORS","CosWave"],["local","BME680","Hygrometer"],["local","BME680","VOC"]]
selected_sensor_values = [["local","BME680","Barometer"],["local","BME680","Thermometer"],["local","BME680","VOC"],["local","BME680","Hygrometer"]]
#selected_sensor_values = [["local","BME680","Barometer"]]

def styling():
    global _placeholder
    global bottom_elbow_css
    global top_elbow_css
    global startup_label
    global bar_css
    global mask
    global top_label
    global build_label
    global top_bar_css
    global bottom_bar
    global bottom_bar_css
    global left_elbow_css
    global bar_css_sharp
    global bar_css_right
    global list_widget_css

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
                    
    left_elbow_css = """
                    background-color:black;
                    border-top-left-radius: 10px; 
                    border-bottom-left-radius: 10px;
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
                    
    bar_css_right = """
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bbff, stop:1 #5566ff);
                    border: 5px solid black;
                    border-left: none;
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                    border-bottom-right-radius: 5px; 
                    border-top-right-radius: 5px; 
                    """                
                    
                    
                    
    
    bar_css_sharp = """
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bbff, stop:1 #5566ff);
                    border: 5px solid black;
                    border-left: none;
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                    border-bottom-left-radius: 5px;  
                    border-top-left-radius: 5px; 
                    """                   
                    
    mask = """
                    background-color: black;
                    border: 5px solid black;
                    border-style: solid;
                    """
                    
                    
    top_label =     f"""
                    border: 5px solid black;
                    border-left: none;
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                    background-color: black;
                    color: #5566ff;
                    font-size: 14px;
                    font: bold;
                    """
                    
                    
    startup_label = f"""
                    border: 5px solid black;
                    border-left: none;
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                    background-color: black;
                    font-family: {font_families['../fonts/babs.otf']};
                    font-size: 30px;
                    color: #cc4444;
                    """              

    build_label = f"""
                    border: 5px solid black;
                    border-left: none;
                    border-right: none;
                    border-top: none;
                    border-bottom: none;
                    background-color: black;
                    font-family: {font_families['../fonts/babs.otf']};
                    font-size: 20px;
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
        self.setFont(QFont("../fonts/babs.otf", 28, QFont.Weight.Bold)) 
        
    
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
     

class LCARS_C_Widget(QWidget):
    shown = pyqtSignal()
    def __init__(self, parent=None,name=None):
        super().__init__(parent)   
        
        # Main widget
        self.background_widget = QWidget(self)  
        
        self.ziel = QPoint(0, 0)
        self.ziel_mask = QPoint(round(size.width()*0.10), round(size.height()*0.05))
        
        # Backcolor set to bottom as i want to overblend a mask
        self.main_bar = QLabel("", self.background_widget)
        self.main_bar.setGeometry(round(size.width()*0.60), 0, round(size.width()*0.25), size.height())
        self.main_bar.setStyleSheet(bar_css_sharp)
        self.main_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_bar_opacity = QGraphicsOpacityEffect(self.main_bar)
        self.main_bar.setGraphicsEffect(self.main_bar_opacity)
        self.main_bar_opacity.setOpacity(0.0)       

        # Overlay Mask Top
        self.main_mask = QLabel("",self.background_widget)
        self.main_mask.setGeometry(round(size.width()*0.70),  round(size.height()*0.05),  round(size.width()*0.15), round(size.height()*0.90))
        self.main_mask.setStyleSheet(left_elbow_css)
        
        # top_bar label
        self.top_bar = QLabel("", self.background_widget)
        self.top_bar.setGeometry(round(size.width()*0.27), 0, size.width()-round(size.width()*0.25), round(size.height()*0.05))
        self.top_bar.setStyleSheet(bar_css_right)
        self.top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_bar_opacity = QGraphicsOpacityEffect(self.top_bar)
        self.top_bar.setGraphicsEffect(self.top_bar_opacity)
        self.top_bar_opacity.setOpacity(0.0)       

        # bottom_bar label
        self.bottom_bar = QLabel("", self.background_widget)
        self.bottom_bar.setGeometry(round(size.width()*0.27), size.height()-round(size.height()*0.05), size.width()-round(size.width()*0.25), round(size.height()*0.05))
        self.bottom_bar.setStyleSheet(bar_css_right)
        self.bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_bar_opacity = QGraphicsOpacityEffect(self.bottom_bar)
        self.bottom_bar.setGraphicsEffect(self.bottom_bar_opacity)
        self.bottom_bar_opacity.setOpacity(0.0)       
        
        # Overlay Mask Bottom
        self.Rtop_mask = QLabel(self.background_widget)
        self.Rtop_mask.setGeometry(round(size.width()-(size.width()*0.065)), 0, round(size.width()*0.015), round(size.height()*1.00))
        self.Rtop_mask.setStyleSheet(mask)
        
        # Overlay Mask Top
        self.label_text = f"{name}"
        self.top_label = QLabel(self.label_text,self.background_widget)
        self.font_calc = round((size.width()/25)*(len(self.label_text)))
        self.top_label.setGeometry(round(size.width()*0.45), 0, self.font_calc, round(size.height()*0.05))
        self.top_label.setStyleSheet(top_label)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_label_opacity = QGraphicsOpacityEffect(self.bottom_bar)
        self.top_label.setGraphicsEffect(self.top_label_opacity)
        self.top_label_opacity.setOpacity(0.0)    
        
        self.fade_main_bar = QPropertyAnimation(self.main_bar_opacity, b"opacity", self)
        self.fade_main_bar.setDuration(1000)
        self.fade_main_bar.setStartValue(0.0)
        self.fade_main_bar.setEndValue(1.0)
        
        self.fade_top_bar = QPropertyAnimation(self.top_bar_opacity, b"opacity", self)
        self.fade_top_bar.setDuration(1000)
        self.fade_top_bar.setStartValue(0.0)
        self.fade_top_bar.setEndValue(1.0)

        self.fade_bottom_bar = QPropertyAnimation(self.bottom_bar_opacity, b"opacity", self)
        self.fade_bottom_bar.setDuration(1000)
        self.fade_bottom_bar.setStartValue(0.0)
        self.fade_bottom_bar.setEndValue(1.0)
        
        self.fade_top_label = QPropertyAnimation(self.top_label_opacity, b"opacity", self)
        self.fade_top_label.setDuration(1000)
        self.fade_top_label.setStartValue(0.0)
        self.fade_top_label.setEndValue(1.0)
           
        self.label_slide = QPropertyAnimation(self.main_bar, b"pos", self)
        self.label_slide.setDuration(800)
        self.label_slide.setStartValue(QPoint(round(size.width()*0.60), 0))
        self.label_slide.setEndValue(self.ziel)
        self.label_slide.setEasingCurve(QEasingCurve.Type.Linear)
        
        self.mask_slide = QPropertyAnimation(self.main_mask, b"pos", self)
        self.mask_slide.setDuration(800)
        self.mask_slide.setStartValue(QPoint(round(size.width()*0.70), round(size.height()*0.05)))
        self.mask_slide.setEndValue(self.ziel_mask)
        self.mask_slide.setEasingCurve(QEasingCurve.Type.Linear)
        
        self.main_mask.setGeometry(round(size.width()*0.70),  round(size.height()*0.05),  round(size.width()*0.15), round(size.height()*0.90))
        
        self.fade_main_bar.finished.connect(self.label_slide.start)
        self.fade_main_bar.finished.connect(self.mask_slide.start)
        self.mask_slide.finished.connect(self.fade_bottom_bar.start)
        self.mask_slide.finished.connect(self.fade_top_bar.start)
        self.mask_slide.finished.connect(self.fade_top_label.start)
        
        self._shown_once = False
        
    def showEvent(self, event):
        super().showEvent(event)

        if not self._shown_once:
            self._shown_once = True
            QTimer.singleShot(0, self.shown.emit)    
               
        
    # Animation 
    def start_animation(self):
        self.fade_main_bar.start()
    
     
     
     

class LCARS_SPLIT2_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
         
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
        self.bottom_mask = QLabel(background_widget)
        self.bottom_mask.setGeometry(round(size.width()*0.10), round(size.height()*0.28), size.width(), size.height())
        self.bottom_mask.setStyleSheet(bottom_elbow_css)
        
        # i want to write some text in the box here so i init the block
        #self.top_mask.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        #self.top_mask.setAlignment(Qt.AlignmentFlag.AlignTop)  
        
        #list_widget = QListWidget(background_widget)
        #list_widget.setGeometry(0, 300, 205, 230)
        #list_widget.setStyleSheet(list_widget_css)
        
# Draws 2 Line Top Bottom         
class LCARS_twoLines_Widget(QWidget):
    def __init__(self, parent=None, name="SYSTEM 47"):
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
        self.label_text = f"{name}"
        self.top_label = QLabel(self.label_text,twoLines_Widget)
        self.font_calc = round((size.width()/25)*(len(self.label_text)))
        self.top_label.setGeometry(round(size.width()*0.10), 0, self.font_calc, round(size.height()*0.05))
        self.top_label.setStyleSheet(top_label)
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        

        
        
        
class GraphScreen(QWidget):
    shown = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
               
        # Rahmen-Widget speichern, statt nur eine lokale Variable anzulegen
        self.graph_Widget = LCARS_C_Widget(self, name="Multi Graph")
        self.graph_Widget.setGeometry(0, 0, size.width(), size.height())   
        
        self.graph_Widget.shown.connect(
            self.graph_Widget.start_animation
        )
        
        background_widget = QWidget(self)  
        
        # This Widgets are used to create a Layout on Top with Functunal Elements
       
        left_widget = QWidget() # empty object
        right_widget = QWidget() # empty object 
        
        list_widget = QListWidget(background_widget)
        list_widget.setGeometry(0, 300, 205, 230)
        list_widget.setStyleSheet(list_widget_css)
        
               
        # Init Plot item
        # Implementing this example https://github.com/pyqtgraph/pyqtgraph/blob/master/pyqtgraph/examples/MultiplePlotAxes.py
        # kudos and prais to https://github.com/pyqtgraph/pyqtgraph/commits?author=j9ac9k
                   
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.setGeometry(round(size.height()*0.20), round(size.width()*0.10), round(size.width()*0.8), round(size.height()*0.80))

        self.graph_Widget.fade_top_label.finished.connect(self.plotWidget.show)
        
        self.plot = []
        self.plot_ax = []
        self.pen = []
        
        # Building Multi Graph
        for index_a, sensors_to_read in enumerate(selected_sensor_values):
            diced_colore = rnd_colore()
            diced_colore_hex = '#%02x%02x%02x' % diced_colore
            if index_a == 0:
                #print("First")
                self.plot.append(self.plotWidget.plotItem)
                self.plot_ax.append(pg.AxisItem('right'))
                self.plot[0].setLabels(left=f'{sensors_to_read}')
                self.plot[0].setZValue(-10000)
            elif index_a >= 1:
                if index_a == 1:
                    #print("Second")
                    self.plot.append(pg.ViewBox())
                    self.plot_ax.append(pg.AxisItem('right'))
                    self.plot[0].showAxis('right')
                    self.plot[0].scene().addItem(self.plot[1])
                    self.plot[0].getAxis('right').linkToView(self.plot[1])
                    self.plot[1].setXLink(self.plot[0])
                    self.plot[0].getAxis('right').setLabel(sensors_to_read, color=diced_colore_hex)
             
                else:
                    #print("Odd third Variant")
                    self.plot.append(pg.ViewBox())
                    self.plot_ax.append(pg.AxisItem('right'))
                    self.plot[0].layout.addItem(self.plot_ax[index_a], 2, index_a+1)
                    self.plot[0].scene().addItem(self.plot[index_a])
                    self.plot_ax[index_a].linkToView(self.plot[index_a])
                    self.plot[index_a].setXLink(self.plot[0])
                    self.plot_ax[index_a].setZValue(-10000)
                    self.plot_ax[index_a].setLabel(sensors_to_read, color=diced_colore_hex)
            self.plot[index_a].invertX(True)
            if index_a == 0:
                self.pen.append('#999999')
            else:
                self.pen.append(diced_colore)
                       
        text_widget = QLabel(_placeholder)
        lcars_tile_element = LCARS_Title("Multi Graph")  
        
        lcars_text_element = LCARS_Title("Multi Graph") 
        
        SpacerwidgetL = empty_label("")
        SpacerwidgetL.arrange(280)
        
        SpacerwidgetR = empty_label("")
        SpacerwidgetR.arrange(80)

        #list_widget.setStyleSheet(list_widget_css)
        #list_widget.setGeometry(0, 300, 205, 230)
        
        # some loops for drawing elements
        
        #for i in range(4):
        #    item = QListWidgetItem(f"0{i}")
        ##
        ##    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
        #    list_widget.addItem(item)
                      
   

        # Overlay Header Right Lable
        labelTilel = QLabel("Scan in Progress",right_widget)
        labelTilel.setGeometry(1024-405, 240, 400, 80)
        labelTilel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        labelTilel.setFont(QFont("Arial", 28, QFont.Weight.Bold)) 
        labelTilel.setStyleSheet("""
        background-color:black;
        color:#cc55ff;
        """)   
        
        # layout section // now i start to arrange the elements
       
        # here are the classes that allow to arrange in horizontal or vertical form
        # i do a stacking from both to get the abillity to attach witdget top o bottom and sidways
        main_layout = QVBoxLayout()
        main_Hlayout = QHBoxLayout()
                                 
        main_layout.addWidget(background_widget) # empty        
   
        content_layout_left = QVBoxLayout()
        content_layout_right = QVBoxLayout()
        
 
        main_Hlayout.addWidget(left_widget,0) # empty
        main_Hlayout.addWidget(right_widget,2) # empty
        
        content_layout_left.addWidget(SpacerwidgetL,0)
        content_layout_left.addWidget(list_widget,0) 
                   
        
        #content_layout_right.addWidget(lcars_tile_element,0)
        #content_layout_right.addWidget(self.voc_label,0)
        #content_layout_right.addWidget(self.wetter_label,0)
        #content_layout_right.addWidget(SpacerwidgetR,0) 
        #content_layout_right.addWidget(labelTilel)
        content_layout_right.addWidget(self.plotWidget,2)
               
        # abstraction
        
        background_widget.setLayout(main_Hlayout) # population of empty background widget
        left_widget.setLayout(content_layout_left) # population of empty main widget
        right_widget.setLayout(content_layout_right) # population of empty main widget

              
        # engage
            
        self.setLayout(main_layout)
        
        
        # animation
        effect = QGraphicsOpacityEffect(list_widget)
        labelTilel.setGraphicsEffect(effect)
        

        labelTilel.anim_1 = QPropertyAnimation(effect, b"opacity")
        labelTilel.anim_1.setStartValue(0)
        labelTilel.anim_1.setEndValue(0)
        labelTilel.anim_1.setDuration(360)
        
        labelTilel.anim_2 = QPropertyAnimation(effect, b"opacity")
        labelTilel.anim_2.setStartValue(1)
        labelTilel.anim_2.setEndValue(1)
        labelTilel.anim_2.setDuration(360)

        #list_widget.anim.start()
        
        # Blink Text
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(labelTilel.anim_1)
        self.anim_group.addAnimation(labelTilel.anim_2)
        self.anim_group.start()
        
        self.anim_group.finished.connect(self.anim_group.start)
        
        # Update Graph
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Set interval to 1 second
        self.timer.timeout.connect(self.update_label)
        self.timer.start()
        
        # Update VOC and Wetter
        #self.timer2 = QTimer(self)
        #self.timer2.setInterval(1000)  # Set interval to 1 second
        #self.timer2.timeout.connect(self.update_voc_wetter_label)
        #self.timer2.start()
        
    def updateViews(self):
        ## view has resized; update auxiliary views to match
        for index_b, plot_item in enumerate(self.plot):
            if index_b > 0:
                self.plot[index_b].setGeometry(self.plot[0].vb.sceneBoundingRect())
                ## need to re-update linked axes since this was called
                ## incorrectly while views had different shapes.
                ## (probably this should be handled in ViewBox.resizeEvent)
                self.plot[index_b].linkedViewChanged(self.plot[0].vb, self.plot[index_b].XAxis)
                
                
    def update_label(self):

        debug_line = ""
        
        self.updateViews()
    
        # Unpacking the array with with array
      
        for index_c, sensors_to_read in enumerate(selected_sensor_values):

        # dev is the Pi dsc the cpu, location_tag is a name of the sending device like local remote or tric2351

            # by setting up all sensor values with a timestamp , can we now select the time section to watch , and ask get recent for example for the last minute
            location_tag,sensor_dev,sensor_dsc = sensors_to_read   
            recent, elements_forgieventime = get_recent(location_tag, sensor_dev, sensor_dsc, 60)
            print(recent)
            if type(recent) != bool and len(recent) != 0: 
                x = [*range(elements_forgieventime)]
                
                table_string = '%s_%s_%s' % (location_tag,sensor_dev,sensor_dsc)
                
                debug = f"{recent} \n"
                #debug = f"{table_string}:{recent} \n"
                debug_line = debug_line + debug

                self.plot[index_c].clear()
                self.plot[index_c].addItem(pg.PlotCurveItem(recent, pen=self.pen[index_c]))

                                                       
            
       
       
                
class StartupScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
                
        # Rahmen-Widget speichern, statt nur eine lokale Variable anzulegen
        self.start_Widget = LCARS_twoLines_Widget(self)
        self.start_Widget.setGeometry(0, 0, size.width(), size.height())
        
        self.frame_opacity = QGraphicsOpacityEffect(self.start_Widget)
        self.start_Widget.setGraphicsEffect(self.frame_opacity)
        self.frame_opacity.setOpacity(0.0)
        
        # Logo Element
        self.picorder_logo = QSvgWidget("../assets/picorderOS_logo_splash.svg", self)
        self.picorder_logo.setMinimumSize(80, 100)
        self.picorder_logo.setGeometry(round(size.width()*0.38), round(size.height()*0.15), round(size.width()*0.1), round(size.height()*0.1))
        self.logo_opacity = QGraphicsOpacityEffect(self.picorder_logo)
        self.picorder_logo.setGraphicsEffect(self.logo_opacity)
        self.logo_opacity.setOpacity(0.0)
        

        #Text Element
        self.startup_text = "INITIATING START-UP SEQUENCE"
        self.startup_label = QLabel(self.startup_text, self)
        self.startup_label.setGeometry(0, round(size.height()*0.65), size.width(), round(size.height()*0.15))
        self.startup_label.setStyleSheet(startup_label)       
        self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_opacity = QGraphicsOpacityEffect(self.startup_label)
        self.startup_label.setGraphicsEffect(self.label_opacity)
        self.label_opacity.setOpacity(0.0)
        
        #Text Element Build Number
        self.build_text = f"PicorderOS {configure.version}"
        self.build_label = QLabel(self.build_text, self)
        self.build_label.setGeometry(0, round(size.height()*0.8), size.width(), round(size.height()*0.15))
        self.build_label.setStyleSheet(build_label)       
        self.build_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.build_opacity = QGraphicsOpacityEffect(self.build_label)
        self.build_label.setGraphicsEffect(self.build_opacity)
        self.build_opacity.setOpacity(0.0)
        
        
        # Animation Sequenzing and Timing
        self.fade = QPropertyAnimation(self.label_opacity, b"opacity", self)
        self.fade.setDuration(1000)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        
        self.fade_se = QPropertyAnimation(self.label_opacity, b"opacity", self)
        self.fade_se.setDuration(1000)
        self.fade_se.setStartValue(0.0)
        self.fade_se.setEndValue(1.0)
        
        self.fade_off = QPropertyAnimation(self.label_opacity, b"opacity", self)
        self.fade_off.setDuration(1000)
        self.fade_off.setStartValue(1.0)
        self.fade_off.setEndValue(0.0)
        
        self.fade_main = QPropertyAnimation(self.frame_opacity, b"opacity", self)
        self.fade_main.setDuration(1000)
        self.fade_main.setStartValue(0.0)
        self.fade_main.setEndValue(1.0)
        
        self.fade_main_off = QPropertyAnimation(self.frame_opacity, b"opacity", self)
        self.fade_main_off.setDuration(1000)
        self.fade_main_off.setStartValue(1.0)
        self.fade_main_off.setEndValue(0.0)
        
        self.fade_logo = QPropertyAnimation(self.logo_opacity, b"opacity", self)
        self.fade_logo.setDuration(1000)
        self.fade_logo.setStartValue(0.0)
        self.fade_logo.setEndValue(1.0)
        
        self.fade_logo_off = QPropertyAnimation(self.logo_opacity, b"opacity", self)
        self.fade_logo_off.setDuration(1000)
        self.fade_logo_off.setStartValue(1.0)
        self.fade_logo_off.setEndValue(0.0)
        
        
        self.fade_build = QPropertyAnimation(self.build_opacity, b"opacity", self)
        self.fade_build.setDuration(1000)
        self.fade_build.setStartValue(0.0)
        self.fade_build.setEndValue(1.0)
        
        self.fade_build_off = QPropertyAnimation(self.build_opacity, b"opacity", self)
        self.fade_build_off.setDuration(1000)
        self.fade_build_off.setStartValue(1.0)
        self.fade_build_off.setEndValue(0.0)
        

        self.fade_main.finished.connect(self.fade_logo.start)
        self.fade_logo.finished.connect(self.fade.start)
        self.fade_logo.finished.connect(self.fade_build.start)
        self.fade_build.finished.connect(self.fade_off.start)
        self.fade_off.finished.connect(self.fade_se.start)
        self.fade_se.finished.connect(self.fade_off.start)
        
        self.fade_off.finished.connect(
            lambda: self.startup_label.setText("READY")
        )
        
        self.fade_se.finished.connect(
            lambda: QTimer.singleShot(2000, self.fade_off_startscreen)
        )

        self._started = False

    def showEvent(self, event):
        super().showEvent(event)
        if not self._started:
            self._started = True
            self.fade_main.start()
            
    def fade_off_startscreen(self):
        self.fade_off.start()
        self.fade_main_off.start()
        self.fade_logo_off.start()
        self.fade_build_off.start()
        self.fade_build_off.finished.connect(self.finished.emit)
        
        


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

        self.setFixedSize(size.width(), size.height())
        self.showFullScreen()
        
        # Setup StackedWidget for memü
        self.setWindowTitle("LCARS")
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        
        # defining Pages
        self.startup_Widget = StartupScreen() 
        self.graph_Widget = GraphScreen() 

        # menü elements  
        self.pages.addWidget(self.startup_Widget)
        self.pages.addWidget(self.graph_Widget)

        # Side Rotation
        self.pages.setCurrentWidget(self.startup_Widget)
        #self.pages.setCurrentWidget(self.graph_Widget)
        
        self.startup_Widget.finished.connect(self.show_graph)
        
    def show_graph(self):
        self.pages.setCurrentWidget(self.graph_Widget)

# return a list of n most recent data from specific sensor defined by keys
# gets Called from pilgraph
def get_recent(tag, dsc, dev, time_ing):	
	timelength = 0
	clean_slices = []
	slices = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql(psql_connection_lcars, table_string, time_ing)
	slices = table_data
	if type(table_data) != bool:
		timelength = len(table_data)
		for item in table_data:
			item_clean = float(str(item).strip("(, )"))
			clean_slices.append(item_clean)
		slices = clean_slices
	return slices, timelength    
	
def get_recent_text(tag, dsc, dev, time_ing):	
	timelength = 0
	clean_slices = []
	slices = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql(psql_connection_lcars, table_string, time_ing)
	slices = table_data
	if type(table_data) != bool:
		timelength = len(table_data)
		for item in table_data:
			item_clean = str(str(item).strip("(, )"))
			clean_slices.append(item_clean)
		slices = clean_slices
	return slices, timelength  
	
def get_recent_termal(tag, dsc, dev):	
	items_count = 0
	clean_slices = []
	array_data = False

	table_string = '%s_%s_%s' % (tag,dsc,dev)
	table_data = return_data_from_sql_termal_adv(psql_connection_lcars, table_string, dev)	
	if type(table_data) != bool and len(table_data) != 0:
		array_data = ast.literal_eval(str(table_data[0]).strip("( )"))
		items_count = len(array_data)
	return array_data, items_count  
		
        
        
def return_data_from_sql(con, table_str, time_lengh_sec):
	ret = False
	now_time = time.time()
	time_past = now_time - time_lengh_sec 
	try:	
		cur = con.cursor()
		query = f'SELECT value FROM "{table_str}" where timestamp > {time_past} order by timestamp desc'
		cur.execute(query)
		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg.Error as e:
		print(f"{type(e).__name__}: {e}")
		return False
	return ret	
		

def return_data_from_sql_termal_adv(con, table_str, dev):
	ret = False
	now_time = time.time()
	time_past = now_time - 30
	
	if dev == "MLX90640_ARRAY":
		lenght = 768
	elif dev == "ARRAY":
		lenght = 64
	else:
		return ret
	
	construct = 'select '
	end = " order by timestamp desc LIMIT 1"
	mid = 'from "' + table_str + '"  where timestamp > ' + str(time_past) 
	for i in range(lenght-1):
		construct = construct + "val" + str(i) + ", "
	construct = construct + "val" + str(lenght-1) + " "
	construct = construct + mid
	construct = construct + end

	#print("construct", construct)
	
	try:
		cur = con.cursor()
		cur.execute(construct)

		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret	    
        
 
	
def connect_psql(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        conn = psycopg.connect(**config)
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg.DatabaseError, Exception) as error:
        print(error) 	

# Prepare connection to PSQL
config = load_config()

psql_connection_lcars = connect_psql(config)
psql_connection_lcars.autocommit = True

config_gis = load_config('database_gisdata.ini')
con_param = "postgresql+psycopg://%s:%s@%s:5432/%s" % (config_gis['user'] , config_gis['password'], config_gis['host'], config_gis['database'] )
gis_engine = create_engine(con_param)	



if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()   
    
    # Font Loading
    font_families = {}

    for path in [
        "../fonts/babs.otf",
        "../fonts/C&C Red Alert.ttf",
        "../fonts/klingon font.ttf",
    ]:

        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            raise RuntimeError(f"Error loading Font: {path}")

        for family in QFontDatabase.applicationFontFamilies(font_id):
            font_families[path] = family
            
    styling()

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default.

    sys.exit(app.exec())
