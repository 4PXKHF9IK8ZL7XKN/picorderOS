#/bin/python3
import sys

from PyQt6.QtWidgets import QGraphicsBlurEffect, QGraphicsOpacityEffect, QHBoxLayout,QListWidget, QListWidgetItem, QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter

from PyQt6.QtGui import QColor, QBrush, QFont

from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup

from layout_colorwidget import Color

_placeholder = """Ganz statisch text 
weil im tutorial etwas verlinkt wurde, 
was es in der welt von python 
ohne einen editor dazu einfach nicht giebt"""















def draw_line_scene(posx,posy,lengh,hight):

        scene = QGraphicsScene(0,0,lengh,50)
        scene.setBackgroundBrush(QBrush(QColor("#2255ff")))
        
        return scene
        
        
def draw_end_scene(posx,posy,lengh,hight):

        scene = QGraphicsScene(0,0,lengh,50)
        scene.setBackgroundBrush(QBrush(QColor("#2255ff")))
        
        return scene


def draw_elbow_scene(posx,posy,lengh,hight):

        scene = QGraphicsScene(posx,posy,lengh,hight)
        scene.setBackgroundBrush(QBrush(QColor("#ffffff")))

        rect = QGraphicsRectItem(0, 0, 200, 50)
        rect_2 = QGraphicsRectItem(0, 0, 200, 50)
        
        rect.setPos(-100, 0)
        rect_2.setPos(0, 80)

        scene.addItem(rect)
        scene.addItem(rect_2)
        
        return scene

        
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
        max-width:25px;
        max-height:50px;
        min-width:750px;
        min-height:50px;
        border-radius: 25px;  
        font: bold 14px;
        padding-right: 15px;
        """)
     

      

class tab_form_widget(QWidget):
    def __init__(self, parent):
        super().__init__()
        #super(QWidget, self).__init__(parent)
        #background = (245, 245, 245)

        #main_layout = QGridLayout(self)
        #self.setLayout(main_layout)

        #contact_layout = QFormLayout()
        #personal_layout = QFormLayout()


        #tab = costume_tab_widget(self)
        #tab.resize(600,400)

        #tab.setTabPosition(QTabWidget.TabPosition.West)

        #contact_page = QWidget(self)
        #contact_page.setLayout(contact_layout)
        #contact_layout.addRow('First Name:', QLineEdit(self))
        #contact_layout.setBackground("blue")


        #personal_page = QWidget(self)
        #personal_page.setLayout(personal_layout)
        #personal_layout.addRow('Phone Number:', QLineEdit(self))


        #tab.addTab_rotatet(personal_page, 'Personal Info')
        #tab.addTab_rotatet(contact_page, 'Contact Info')
        
class list_form_widget(QWidget):
    def __init__(self, parent):
        super(list_form_widget, self).__init__(parent)    
             
             
        # widget section
        
        vector_image = draw_elbow_widget()
        
        vector_image_2 = draw_line_widget()
        
        vector_image_3 = draw_line_widget()
        
        
        main_widget = QWidget()
        sec_widget = QWidget()

        list_widget = QListWidget()

        
        for i in range(6):
            item = QListWidgetItem(f"0{i}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            list_widget.addItem(item)
            
     
        
        text_widget = QLabel(_placeholder)
        button = QPushButton("Something")

        # layout section

        
        layout = QHBoxLayout()
        content_layout_1 = QVBoxLayout()
        content_layout_2 = QVBoxLayout()
                      
        layout.addWidget(main_widget,0) # empty
        layout.addWidget(sec_widget,2) # empty
        
        content_layout_1.addWidget(vector_image,0)   
        content_layout_1.addWidget(list_widget,8)    
        
        content_layout_2.addWidget(vector_image_2,0)   
        content_layout_2.addWidget(text_widget,8)
        content_layout_2.addWidget(button,1) 
        content_layout_2.addWidget(vector_image_3,0)   
        
        

           
        
        # abstraction
        
        main_widget.setLayout(content_layout_1) # population of empty main widget
        sec_widget.setLayout(content_layout_2) # population of empty main widget
              
        # engage
            
        self.setLayout(layout)

        effect = QGraphicsOpacityEffect(list_widget)
        list_widget.setGraphicsEffect(effect)

        # animation

        list_widget.anim_1 = QPropertyAnimation(effect, b"opacity")
        list_widget.anim_1.setStartValue(0)
        list_widget.anim_1.setEndValue(1)
        list_widget.anim_1.setDuration(1200)
        
        list_widget.anim_2 = QPropertyAnimation(effect, b"opacity")
        list_widget.anim_2.setStartValue(1)
        list_widget.anim_2.setEndValue(0)
        list_widget.anim_2.setDuration(1200)

        #list_widget.anim.start()
        
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(list_widget.anim_1)
        self.anim_group.addAnimation(list_widget.anim_2)
        self.anim_group.start()
        
        self.anim_group.finished.connect(self.anim_group.start)
        
        
class stacked_form_widget(QWidget):
    def __init__(self, parent):
        super(stacked_form_widget, self).__init__(parent)   
        
        
        # Main widget
        main_widget = QWidget(self)
        #self.setCentralWidget(main_widget)

        
        # top_bar label
        top_bar = QLabel("Background Content", main_widget)
        top_bar.setGeometry(5, 0, 1015, 200)
        top_bar.setStyleSheet("""
        background-color: blue;
        border: 1px solid black;
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: none;
        border-bottom-left-radius: 100px; 
        """)
        top_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Overlay label
        bottom_bar = QLabel(main_widget)
        bottom_bar.setGeometry(5, 205, 1015, 400)
        bottom_bar.setStyleSheet("""
        border: 1px solid black;
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: none;
        background-color:red;
        border-top-left-radius: 100px; 
        """)
        
        #bottom_bar.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        #bottom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)      
        
        # Overlay Mask Bottom
        bottom_mask = QLabel(main_widget)
        bottom_mask.setGeometry(200, 230, 1015, 390)
        bottom_mask.setStyleSheet("""
        background-color:black;
        border-top-left-radius: 50px; 
        """)

        # Overlay Mask Top
        bottom_mask = QLabel(main_widget)
        bottom_mask.setGeometry(200, 0, 1015, 170)
        bottom_mask.setStyleSheet("""
        background-color:black;
        border-bottom-left-radius: 50px; 
        """)
        
        list_widget = QListWidget(main_widget)
        list_widget.setGeometry(0, 300, 205, 230)
        list_widget.setStyleSheet("""
        QListWidget {
        background-color: black;
        border-style: solid;
        border-width:0px;
        border-color: #000000;
        font: bold 14px;
        margin: 5px;
        padding-top: 5px;
        padding-bottom: 5px;
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
        margin-top: 1px;
        margin-bottom: 1px;
        }
        """)

        
        for i in range(4):
            item = QListWidgetItem(f"0{i}")

            
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            list_widget.addItem(item)
          
        
        button_group_widget = QListWidget(main_widget)
        button_group_widget.setGeometry(1024-205, 90, 205, 80)
        button_group_widget.setStyleSheet("""
        QListWidget {
        background-color: black;
        border-style: solid;
        border-width:0px;
        border-color: #000000;
        font: bold 14px;
        margin: 5px;
        padding-top: 5px;
        padding-bottom: 5px;
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
        background-color: blue;
        border-style: solid;
        border-width:0px;
        border-color: #000000;
        max-height:50px;
        min-height:50px;
        color: #000000;
        font: bold 14px;
        margin-top: 1px;
        margin-bottom: 1px;
        border-radius: 25px;
        }
        """)

        
        for i in range(1):
            item = QListWidgetItem(f"0{i}")

            
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            button_group_widget.addItem(item)
            
            
            
        button_group2_widget = QListWidget(main_widget)
        button_group2_widget.setGeometry(1024-410, 90, 205, 80)
        button_group2_widget.setStyleSheet("""
        QListWidget {
        background-color: black;
        border-style: solid;
        border-width:0px;
        border-color: #000000;
        font: bold 14px;
        margin: 5px;
        padding-top: 5px;
        padding-bottom: 5px;
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
        background-color: blue;
        border-style: solid;
        border-width:0px;
        border-color: #000000;
        max-height:50px;
        min-height:50px;
        color: #000000;
        font: bold 14px;
        margin-top: 1px;
        margin-bottom: 1px;
        border-radius: 25px;
        }
        """)

        
        for i in range(1):
            item = QListWidgetItem(f"0{i}")

            
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            button_group2_widget.addItem(item)
          
        
        
        
        
        
 
        
        # Overlay Top Right Lable
        labelHeader = QLabel("LCARS • Test Form",main_widget)
        labelHeader.setGeometry(1024-405, 0, 400, 80)
        labelHeader.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        labelHeader.setFont(QFont("Arial", 28, QFont.Weight.Bold)) 
        labelHeader.setStyleSheet("""
        background-color:black;
        color:gold;
        """)
        
        
         # Overlay Header Right Lable
        labelTilel = QLabel("Titel Section",main_widget)
        labelTilel.setGeometry(1024-405, 240, 400, 80)
        labelTilel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        labelTilel.setFont(QFont("Arial", 28, QFont.Weight.Bold)) 
        labelTilel.setStyleSheet("""
        background-color:black;
        color:Blue;
        """)
        
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
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LCARS")
        
        #self.resize(448,368)
        
        self.showFullScreen()

        self.setStyleSheet("""
        background-color: #000000;
        """)
        
        
        self.table_widget = stacked_form_widget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


if __name__ == "__main__":
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show() # IMPORTANT!!!!! Windows are hidden by default.

    sys.exit(app.exec())
