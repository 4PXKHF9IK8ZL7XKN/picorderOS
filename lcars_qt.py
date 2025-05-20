#/bin/python3
import sys

from PyQt6.QtWidgets import QGraphicsBlurEffect, QGraphicsOpacityEffect, QHBoxLayout,QListWidget, QListWidgetItem, QLabel, QLineEdit, QGridLayout, QFormLayout, QGraphicsProxyWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QToolBar, QWidget, QVBoxLayout, QApplication, QMainWindow, QTabWidget, QPushButton, QLCDNumber, QStylePainter

from PyQt6.QtGui import QColor

from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup

from layout_colorwidget import Color

_placeholder = "Ganz statisch text weil im tutorial etwas verlinkt wurde, was es in der welt von python ohne einen editor dazu einfach nicht giebt"

class element_elbow_widget(QWidget):    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        

        


class costume_tab_widget(QTabWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
    def addTab_rotatet(self,layout,name):
        self.addTab(layout,name)
        print(name)

class tab_form_widget(QWidget):
    def __init__(self, parent):
        #super().__init__()
        super(QWidget, self).__init__(parent)
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
        
        
        
        
        scene = QGraphicsScene(0, 0, 400, 200)

        rect = QGraphicsRectItem(0, 0, 200, 50)
        rect.setPos(50, 20)

        scene.addItem(rect)

        self.view = QGraphicsView(scene)
        self.view.show()
        
        
        
        main_widget = QWidget()
    
        list_widget = QListWidget()
       
        vector_image = self.view
        
        for i in range(5):
            item = QListWidgetItem(f"0{i}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom )
            list_widget.addItem(item)
            
     
        
        text_widget = QLabel(_placeholder)
        button = QPushButton("Something")

        # layout section

        layout = QHBoxLayout()
        content_layout = QVBoxLayout()
               
        layout.addWidget(list_widget, 1) # list object
        layout.addWidget(main_widget, 4) # empty
        
        content_layout.addWidget(vector_image)   
        content_layout.addWidget(text_widget)
        content_layout.addWidget(button) 
           
        
        # abstraction
        
        main_widget.setLayout(content_layout) # population of empty main widget
              
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LCARS")
        self.showFullScreen()
        
        #window = QLabel("This is a placeholder text")
        #window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #window.setStyleSheet("""
        #background-color: #262626;
        #color: #FFFFFF;
        #font-family: Titillium;
        #font-size: 18px;
        #""")
        
        

        self.table_widget = list_form_widget(self)

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
    # Start the event loop.
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    
    
    
    sys.exit(app.exec())
