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

from picos_psql_config import load_config
from scipy.interpolate import griddata


from PyQt6.QtWidgets import QSpacerItem, QGraphicsBlurEffect, QGraphicsOpacityEffect, QHBoxLayout,QListWidget, QListWidgetItem, QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter

from PyQt6.QtGui import QColor, QBrush, QFont

from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup

from layout_colorwidget import Color

_placeholder = """Ganz statisch text 
weil im tutorial etwas verlinkt wurde, 
was es in der welt von python 
ohne einen editor dazu einfach nicht giebt"""

top_elbow_css = """
                background-color:black;
                border-bottom-left-radius: 50px; 
                """

bottom_elbow_css = """
                background-color:black;
                border-top-left-radius: 50px; 
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
                background-color: darkred;
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
                background-color: blue;
                border: 1px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                border-bottom-left-radius: 100px; 
                """    
bottom_bar_css = """
                border: 1px solid black;
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
                background-color:red;
                border-top-left-radius: 100px; 
                """                          

def update_label():
        print("update")


class LCARS_Title(QLabel):
    def __init__(self, parent):
        super(LCARS_Title, self).__init__(parent)   
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
        background-color:transparent;
        color:Gold;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 28, QFont.Weight.Bold)) 
        
    
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
     

class LCARS_GRAPH_Widget(QWidget):
    def __init__(self, parent):
        super(LCARS_GRAPH_Widget, self).__init__(parent)  
         
        # Main widget
        # we need a canvas to draw oure LCARS Shapes first
        # this should be a stacked widget
        background_widget = QWidget(self)  
        
        # This Widgets are used to create a Layout on Top with Functunal Elements
       
        left_widget = QWidget() # empty object
        right_widget = QWidget() # empty object 
        
        # top_bar label
        top_bar = QLabel("Background Content", background_widget)
        top_bar.setGeometry(18, 0, 1015, 200)
        top_bar.setStyleSheet(top_bar_css)
        top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # bottom_bar label
        bottom_bar = QLabel("Background Content",background_widget)
        bottom_bar.setGeometry(18, 205, 1015, 400)
        bottom_bar.setStyleSheet(bottom_bar_css)
        
        #bottom_bar.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        #bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)      
        
        # Overlay Mask Bottom
        bottom_mask = QLabel(background_widget)
        bottom_mask.setGeometry(200, 230, 1015, 390)
        bottom_mask.setStyleSheet(bottom_elbow_css)

        # Overlay Mask Top
        bottom_mask = QLabel(background_widget)
        bottom_mask.setGeometry(200, 0, 1015, 170)
        bottom_mask.setStyleSheet(top_elbow_css)
        
        list_widget = QListWidget(background_widget)
        list_widget.setGeometry(0, 300, 205, 230)
        list_widget.setStyleSheet(list_widget_css)
       
        
        background_widget.setStyleSheet("""
        background-color:black;
        """)

        left_widget.setStyleSheet("""
        background-color:rgba(r, g, b, alpha);
        """) # sets the frame transparent     
           
        right_widget.setStyleSheet("""
        background-color:rgba(r, g, b, alpha);         
        """) # sets the frame transparent


        # this elements are later used for display 

        vector_image = draw_line_widget()
        list_widget = QListWidget()        
        self.plotWidget = pg.plot(title="Three plot curves")
        self.plotWidget.invertX(True)
               
        text_widget = QLabel(_placeholder)
        lcars_tile_element = LCARS_Title("Multi Graph")  
        SpacerwidgetL = empty_label("")
        SpacerwidgetL.arrange(280)
        
        SpacerwidgetR = empty_label("")

        list_widget.setStyleSheet(list_widget_css)
        list_widget.setGeometry(0, 300, 205, 230)
        
        # some loops for drawing elements
        
        for i in range(4):
            item = QListWidgetItem(f"0{i}")
      
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            list_widget.addItem(item)
            
        recent, elements_forgieventime = get_recent("local", "BME680", "Barometer", 60)
        if type(recent) != bool and len(recent) != 0:
            x = [*range(elements_forgieventime)]
            self.plotWidget.plot(x, recent, pen=(i,1))  ## setting pen=(i,3) automaticaly creates three different-colored pens             
        else:
            print("No Data Returnd")
   

        # Overlay Header Right Lable
        labelTilel = QLabel("Scan in Progress",right_widget)
        labelTilel.setGeometry(1024-405, 240, 400, 80)
        labelTilel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        labelTilel.setFont(QFont("Arial", 28, QFont.Weight.Bold)) 
        labelTilel.setStyleSheet("""
        background-color:black;
        color:Blue;
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
                   
        
        content_layout_right.addWidget(lcars_tile_element,0)
        content_layout_right.addWidget(SpacerwidgetR,0) 
        content_layout_right.addWidget(labelTilel)
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
        
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(labelTilel.anim_1)
        self.anim_group.addAnimation(labelTilel.anim_2)
        self.anim_group.start()
        
        self.anim_group.finished.connect(self.anim_group.start)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Set interval to 1 second
        self.timer.timeout.connect(self.update_label)
        self.timer.start()

    def update_label(self):
        recent, elements_forgieventime = get_recent("local", "BME680", "Barometer", 60)
        if type(recent) != bool and len(recent) != 0:
            x = [*range(elements_forgieventime)]
            self.plotWidget.clear()
            self.plotWidget.plot(x, recent, pen=(1,1))  ## setting pen=(i,3) automaticaly creates three different-colored pens             
        else:
            print("No Data Returnd")
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LCARS")
        
        #self.resize(448,368)
        
        self.showFullScreen()

        self.setStyleSheet("""
        background-color: #000000;
        """)
        
        self.table_widget = LCARS_GRAPH_Widget(self)
        self.setCentralWidget(self.table_widget)

        self.show()

	
def return_data_from_sql(con, table_str, time_lengh_sec):
	ret = False
	now_time = time.time()
	time_past = now_time - time_lengh_sec 
	

	try:
		cur = con.cursor()
		cur.execute('select value from "' + table_str + '"  where timestamp > '+ str(time_past) + ' order by timestamp desc')
		values = cur.fetchall()
		ret = values
		cur.close()
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
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
	except psycopg2.Error as e:
		if e == "no results to fetch":
			print( e )
	return ret	
	
def connect_psql(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error) 		

# Prepare connection to PSQL
config = load_config()
psql_connection_lcars = connect_psql(config)
psql_connection_lcars.autocommit = True
	
		

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

		


if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default.

    sys.exit(app.exec())
