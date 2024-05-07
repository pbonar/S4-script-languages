from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QPushButton, QWidget, QLineEdit, QLabel, QGridLayout, QScrollArea
import sys
from functools import partial

from lib import parse_line, get_ipv4s_from_log, get_user_from_log


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
    STYLES = {
        "unselected_line": "border: 1px solid black; padding: 5px; margin: 0px; background-color: white; text-align: left;",
        "selected_line": "border: 1px solid black; padding: 5px; margin: 0px; background-color: #f0f0f0; text-align: left; font-weight: bold;",
        
        "details_container": "background-color: #f0f0f0; border: 1px solid black; padding: 10px; margin: 0px",
        "details_first_column": "font-weight: bold; border: none; padding: 5px; margin: 0px; background-color: #f0f0f0;",
        "details_second_column": "border: 1px solid black; padding: 5px; margin: 0px; background-color: white;"
    }
    
    lines: list[str]
    log_display: QVBoxLayout
    middle_right_layout: QGridLayout
    
    selected_line: int = -1
    
    def __init__(self):
        super().__init__()
        self.lines = []
        
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
        self.middle_right_layout = QGridLayout()
        
        details_container = QWidget()
        details_container.setLayout(self.middle_right_layout)
        
        details_container.setFixedHeight(300)
        details_container.setStyleSheet(self.STYLES["details_container"])
        
        data_widgets = [
            "Remote host", "User", "Date", "Time", "Status Code", "Method", "Size"
        ]
        
        # fist column
        for i, label in enumerate(data_widgets):
            x = QLabel(label)
            x.setStyleSheet(self.STYLES["details_first_column"])
            self.middle_right_layout.addWidget(x, i, 0)
        
        # second column
        for i in range(len(data_widgets)):
            x = QLabel("-")
            x.setStyleSheet(self.STYLES["details_second_column"])
            self.middle_right_layout.addWidget(x, i, 1)
            
        # minimum width
        self.middle_right_layout.setColumnMinimumWidth(0, 100)
        self.middle_right_layout.setColumnMinimumWidth(1, 200)
        
        # combine both
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(scroll)
        middle_layout.addWidget(details_container)
        
        self.setLayout(middle_layout)

    def set_lines(self, lines):
        self.lines = lines
        self.selected_line = -1
        
        while self.log_display.count():
            self.log_display.takeAt(0).widget().deleteLater()
        
        for i, line in enumerate(lines):
            label = QPushButton(line[:50] + "..." if len(line) > 50 else line)
            label.setStyleSheet(self.STYLES["unselected_line"])
            
            label.clicked.connect(partial(self.select_line, i))

            self.log_display.addWidget(label)

    def select_line(self, i):
        # reset color for previously selected line
        if self.selected_line != -1:
            self.log_display.itemAt(self.selected_line).widget().setStyleSheet(self.STYLES["unselected_line"])
        
        # set color for selected line
        self.log_display.itemAt(i).widget().setStyleSheet(self.STYLES["selected_line"])
        
        # update details
        details = parse_line(self.lines[i])
        ipv4s = get_ipv4s_from_log(details)
        user = get_user_from_log(details)
        
        # clear middle_right_layout right column
        COLUMN_START = 7
        self.middle_right_layout.itemAt(COLUMN_START).widget().setText(ipv4s[0] if ipv4s else "-")
        self.middle_right_layout.itemAt(COLUMN_START + 1).widget().setText(user or "-")
        self.middle_right_layout.itemAt(COLUMN_START + 2).widget().setText(details["date"].strftime("%b %d"))
        self.middle_right_layout.itemAt(COLUMN_START + 3).widget().setText(details["date"].strftime("%H:%M:%S"))
        
        # set
        self.selected_line = i
    
    def jump_relative(self, n):
        if self.selected_line == -1:
            return
        
        new_line = self.selected_line + n
        if new_line < 0 or new_line >= len(self.lines):
            return
        
        self.select_line(new_line)


class BottomSection(QWidget):
    def __init__(self, jump_relative):
        super().__init__()
        
        # bottom section - previous and next buttons
        bottom_layout = QHBoxLayout()
        
        previous = QPushButton("Previous")
        next = QPushButton("Next")
        
        previous.clicked.connect(partial(jump_relative, -1))
        next.clicked.connect(partial(jump_relative, 1))
        
        bottom_layout.addWidget(previous)
        bottom_layout.addWidget(next)
        
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
        self.bottom_section = BottomSection(self.middle_section.jump_relative)
        
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

