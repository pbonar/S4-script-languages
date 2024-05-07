from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QPushButton, QWidget, QLineEdit, QLabel, QGridLayout, QScrollArea
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
    log_display: QVBoxLayout
    
    def __init__(self):
        super().__init__()
        
        # main section - log display
        self.log_display = QVBoxLayout()
        self.log_display.setSpacing(5)
        
        # make it scrollable
        scroll = QScrollArea()
        log_container = QWidget()
        log_container.setLayout(self.log_display)
        scroll.setWidget(log_container)
        scroll.setWidgetResizable(True)
        
        # on the right - specific log details
        middle_right_layout = QGridLayout()
        
        details_container = QWidget()
        details_container.setLayout(middle_right_layout)
        
        details_container.setFixedHeight(200)
        details_container.setStyleSheet("background-color: #f0f0f0; border: 1px solid black; padding: 10px; margin: 0px")
        
        data_widgets = [
            "hostname", "username", "date", "time", "status code", "method", "size"
        ]
        
        # fist column
        for i, label in enumerate(data_widgets):
            x = QLabel(label)
            x.setStyleSheet("font-weight: bold; border: none; padding: 5px; margin: 0px; background-color: #f0f0f0;")
            middle_right_layout.addWidget(x, i, 0)
        
        # second column
        for i in range(len(data_widgets)):
            x = QLabel("-")
            x.setStyleSheet("border: 1px solid black; padding: 5px; margin: 0px; background-color: white;")
            middle_right_layout.addWidget(x, i, 1)
            
        # minimum width
        middle_right_layout.setColumnMinimumWidth(0, 100)
        middle_right_layout.setColumnMinimumWidth(1, 100)
        
        # combine both
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(scroll)
        middle_layout.addWidget(details_container)
        
        self.setLayout(middle_layout)

    def set_lines(self, lines):
        while self.log_display.count():
            self.log_display.takeAt(0).widget().deleteLater()
        
        for line in lines:
            label = QLabel(line[:50] + "..." if len(line) > 50 else line)
            label.setStyleSheet("border: 1px solid black; padding: 5px; margin: 0px; background-color: white;")
            self.log_display.addWidget(label)


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
        
        # default window size
        self.resize(800, 600)
        
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
            self.middle_section.set_lines(self.lines)
        except FileNotFoundError:
            self.top_section.filename_input.clear()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

