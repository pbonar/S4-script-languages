from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QPushButton, QWidget, QLineEdit, QLabel, QGridLayout
import sys


class TopSection(QWidget):
    def __init__(self, open_file):
        super().__init__()
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter the filename")
        
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(open_file)
        
        layout = QHBoxLayout()
        layout.addWidget(self.filename_input)
        layout.addWidget(self.open_button)
        
        self.setLayout(layout)


class MiddleSection(QWidget):
    def __init__(self):
        super().__init__()
        
        # main section - log display
        placeholder = QPushButton("Placeholder for log display", enabled=False)
        placeholder.setFixedSize(400, 400)
        
        # on the right - specific log details
        middle_right_layout = QGridLayout()
        
        data_widgets = [
            "hostname", "username", "date", "time", "status code", "method", "size"
        ]
        
        # fist column
        for i, label in enumerate(data_widgets):
            middle_right_layout.addWidget(QLabel(label), i, 0)
        
        # second column
        for i in range(len(data_widgets)):
            middle_right_layout.addWidget(QLabel("0"), i, 1)
            
        # minimum width
        middle_right_layout.setColumnMinimumWidth(0, 100)
        middle_right_layout.setColumnMinimumWidth(1, 100)
        
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(placeholder)
        middle_layout.addLayout(middle_right_layout)
        
        self.setLayout(middle_layout)


class BottomSection(QWidget):
    def __init__(self):
        super().__init__()
        
        # bottom section - previous and next buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QPushButton("Previous"))
        bottom_layout.addWidget(QPushButton("Next"))
        
        self.setLayout(bottom_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SSH Logs Viewer")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # combine all sections
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # styling
        layout.setContentsMargins(25, 25, 25, 25)
        
        self.top_section = TopSection(self.open_file)
        self.middle_section = MiddleSection()
        self.bottom_section = BottomSection()
        
        layout.addWidget(self.top_section)
        layout.addWidget(self.middle_section)
        layout.addWidget(self.bottom_section)
        
    
    def open_file(self):
        filename = self.top_section.filename_input.text()
        print(f"Opening file: {filename}")

        try:
            self.lines = open(filename, "r").readlines()
        except FileNotFoundError:
            self.top_section.filename_input.clear()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

