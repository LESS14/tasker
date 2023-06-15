import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QDateTimeEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime, QTimer, Qt
from plyer import notification

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tasker")
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setGeometry(200, 200, 400, 400)
        self.setStyleSheet("background-color: #2C2F33; color: #FFFFFF;")
        flags = Qt.WindowFlags()
        self.setWindowFlags(flags)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Tarefas")
        self.label.setStyleSheet("font-size: 18px;")
        self.layout.addWidget(self.label)

        self.task_input = QLineEdit()
        self.task_input.setStyleSheet("background-color: #40444B; color: #FFFFFF; padding: 5px;")
        self.layout.addWidget(self.task_input)

        self.description_input = QLineEdit()
        self.description_input.setStyleSheet("background-color: #40444B; color: #FFFFFF; padding: 5px;")
        self.description_input.setPlaceholderText("Descrição da Tarefa")
        self.layout.addWidget(self.description_input)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setStyleSheet("background-color: #40444B; color: #FFFFFF; padding: 5px;")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.layout.addWidget(self.datetime_edit)

        self.add_button = QPushButton("Adicionar")
        self.add_button.setStyleSheet("background-color: #7289DA; color: #FFFFFF; padding: 5px; border-radius: 5px;")
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background-color: #40444B; color: #FFFFFF; padding: 5px;")
        self.layout.addWidget(self.task_list)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_tasks)

        # Carrega as tarefas salvas
        self.load_tasks()

    def add_task(self):
        task = self.task_input.text().strip()
        description = self.description_input.text().strip()
        if task:
            deadline = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            item_text = f"{task} - {deadline}"
            if description:
                item_text += f"\nDescrição: {description}"
            self.task_list.addItem(item_text)
            self.task_input.clear()
            self.description_input.clear()
            self.save_tasks()

    def save_tasks(self):
        with open("tasks.txt", "w") as file:
            tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
            file.write("\n".join(tasks))

    def load_tasks(self):
        try:
            with open("tasks.txt", "r") as file:
                tasks = file.read().splitlines()
                for task in tasks:
                    if " - " in task:
                        self.task_list.addItem(task)
        except FileNotFoundError:
            pass

        self.start_timer()

    def start_timer(self):
        current_datetime = QDateTime.currentDateTime()
        for i in range(self.task_list.count()):
            task = self.task_list.item(i).text()
            _, deadline = task.split(" - ")
            datetime = QDateTime.fromString(deadline, "yyyy-MM-dd HH:mm:ss")
            if datetime <= current_datetime:
                self.show_notification(task)

        self.timer.start(1000)  # Verifica a cada segundo

    def stop_timer(self):
        self.timer.stop()

    def check_tasks(self):
        current_datetime = QDateTime.currentDateTime()
        tasks_to_notify = []
        for i in range(self.task_list.count()):
            task = self.task_list.item(i).text()
            _, deadline = task.split(" - ")
            datetime = QDateTime.fromString(deadline, "yyyy-MM-dd HH:mm:ss")
            if datetime <= current_datetime:
                tasks_to_notify.append(task)

        for task in tasks_to_notify:
            self.show_notification(task)
            item = self.task_list.findItems(task, Qt.MatchExactly)[0]
            self.task_list.takeItem(self.task_list.row(item))

        if self.task_list.count() == 0:
            self.stop_timer()

    def show_notification(self, task):
        notification.notify(
            title="Tarefa",
            message=task,
            timeout=10
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
