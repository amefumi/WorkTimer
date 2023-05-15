import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)


class TimerWidget(QWidget):
    def __init__(self):
        super(TimerWidget, self).__init__()
        self.setFixedSize(300, 150)

        self.total_time_label = QLabel("Total 0 days 0 hours 0 minutes")
        self.timer_label = QLabel("00:00:00")
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("End")
        self.exit_button = QPushButton("Exit")
        self.timer_running = False
        self.start_time = None
        self.end_time = None
        self.weekly_elapsed_time = 0
        self.total_elapsed_time = 0
        self.last_start_week = 0

        font_total_timer = QFont("Arial")
        font = QFont("Arial", 16)
        font_timer = QFont("Arial", 40)
        self.total_time_label.setFont(font_total_timer)
        self.timer_label.setFont(font_timer)
        self.start_button.setFont(font)
        self.pause_button.setFont(font)
        self.exit_button.setFont(font)

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.exit_button.clicked.connect(self.exit_program)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_label)

        layout = QVBoxLayout()
        layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.total_time_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setWindowTitle("Worker's Timer")
        self.load_timer_data()
        self.update_total_timer_label()
        self.timer_label.setText(format_time(self.weekly_elapsed_time))

    def start_timer(self):
        if not self.timer_running:
            self.load_timer_data()  # 加载计时数据
            self.timer_running = True
            self.start_time = QDateTime.currentDateTime()
            current_week = self.start_time.date().weekNumber()
            if current_week[0] != self.last_start_week:
                self.weekly_elapsed_time = 0
                self.last_start_week = current_week[0]
            self.timer.start(100)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()

            self.end_time = QDateTime.currentDateTime()
            elapsed_time = self.start_time.secsTo(self.end_time)
            self.weekly_elapsed_time += elapsed_time
            self.total_elapsed_time += elapsed_time
            self.save_timer_data()  # 保存计时数据

            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.update_total_timer_label()

    def exit_program(self):
        self.pause_timer()
        sys.exit()

    def update_timer_label(self):
        current_time = QDateTime.currentDateTime()
        elapsed_time = self.start_time.secsTo(current_time) + self.weekly_elapsed_time
        self.timer_label.setText(format_time(elapsed_time))

    def update_total_timer_label(self):
        t = self.total_elapsed_time
        minutes = t//60
        hours = (t // 3600) % 24
        days = t // (3600 * 24)
        self.total_time_label.setText(f"Total {days} days {hours} hours {minutes} minutes")

    def load_timer_data(self):
        try:
            with open("timer_data.json", "r") as file:
                data = json.load(file)
                self.total_elapsed_time = data["elapsed_times"]
                self.weekly_elapsed_time = data["weekly_elapsed_times"]
                self.last_start_week = data["last_start_week"]
        except FileNotFoundError:
            pass

    def save_timer_data(self):
        try:
            with open("timer_data.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"elapsed_times": 0, "weekly_elapsed_times": 0, "last_start_week": 0, "time_stamps": []}

        data["weekly_elapsed_times"] = self.weekly_elapsed_time
        data["elapsed_times"] = self.total_elapsed_time
        data["last_start_week"] = self.last_start_week
        data["time_stamps"].append({"start_time": self.start_time.toString(Qt.DefaultLocaleShortDate),
                                    "end_time": self.end_time.toString(Qt.DefaultLocaleShortDate)})
        with open("timer_data.json", "w") as file:
            json.dump(data, file, indent=4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer_widget = TimerWidget()
    timer_widget.show()
    sys.exit(app.exec_())
