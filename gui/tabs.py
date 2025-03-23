from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from solvers.equations import chord_method, newton_method, simple_iteration_method
from solvers.systems import system_simple_iteration
from utils.config import EQUATIONS, SYSTEMS
from utils.validation import validate_interval
import numpy as np


class EquationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_equation = None
        self.current_method = None

        self.update_equation()

    def init_ui(self):
        layout = QVBoxLayout()

        # Choice equation
        self.eq_combo = QComboBox()
        self.eq_combo.addItems(EQUATIONS.keys())
        self.eq_combo.currentIndexChanged.connect(self.update_equation)
        layout.addWidget(QLabel("Выберите уравнение:"))
        layout.addWidget(self.eq_combo)

        # Input interval and accuracy
        self.a_input = QLineEdit()
        self.b_input = QLineEdit()
        self.eps_input = QLineEdit("1e-6")
        layout.addWidget(QLabel("Интервал [a, b]:"))
        layout.addWidget(self.a_input)
        layout.addWidget(self.b_input)
        layout.addWidget(QLabel("Точность:"))
        layout.addWidget(self.eps_input)

        # Choice method
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Метод хорд", "Метод Ньютона", "Метод простой итерации"])
        layout.addWidget(QLabel("Выберите метод:"))
        layout.addWidget(self.method_combo)

        # Solve button
        self.solve_btn = QPushButton("Решить")
        self.solve_btn.clicked.connect(self.solve_equation)
        layout.addWidget(self.solve_btn)

        # Output results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Graph
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_equation(self):
        self.current_equation = self.eq_combo.currentText()

    def solve_equation(self):
        try:
            a = float(self.a_input.text())
            b = float(self.b_input.text())
            eps = float(self.eps_input.text())
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректный ввод данных")
            return

        # Checking interval
        is_valid, msg = validate_interval(a, b, EQUATIONS[self.current_equation]["f"])
        if not is_valid:
            QMessageBox.critical(self, "Ошибка", msg)
            return

        # Choice method
        method = self.method_combo.currentText()
        f = EQUATIONS[self.current_equation]["f"]
        result = None

        if method == "Метод хорд":
            result = chord_method(f, a, b, eps)
        elif method == "Метод Ньютона":
            df = EQUATIONS[self.current_equation]["df"]
            x0 = a if abs(f(a)) < abs(f(b)) else b
            result = newton_method(f, df, x0, eps)
        elif method == "Метод простой итерации":
            phi = EQUATIONS[self.current_equation]["phi"]
            x0 = (a + b) / 2
            result = simple_iteration_method(phi, x0, eps)

        # Output results
        if result:
            x, fx, iterations = result
            self.result_text.setText(
                f"Корень: {x:.6f}\nЗначение функции: {fx:.2e}\nИтераций: {iterations}"
            )
            self.plot_function(a, b, f, x)

    def plot_function(self, a, b, f, root_x):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_vals = np.linspace(a, b, 1000)
        y_vals = [f(x) for x in x_vals]
        ax.plot(x_vals, y_vals, label="Функция")
        ax.axhline(0, color='black', linewidth=0.5)
        ax.axvline(root_x, color='red', linestyle='--', label="Корень")
        ax.legend()
        self.canvas.draw()


class SystemTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Choice system
        self.sys_combo = QComboBox()
        self.sys_combo.addItems(SYSTEMS.keys())
        layout.addWidget(QLabel("Выберите систему:"))
        layout.addWidget(self.sys_combo)

        # Input start data
        self.x0_input = QLineEdit()
        self.y0_input = QLineEdit()
        self.eps_input = QLineEdit("1e-6")
        layout.addWidget(QLabel("Начальные приближения x0, y0:"))
        layout.addWidget(self.x0_input)
        layout.addWidget(self.y0_input)
        layout.addWidget(QLabel("Точность:"))
        layout.addWidget(self.eps_input)

        # Solve button
        self.solve_btn = QPushButton("Решить")
        self.solve_btn.clicked.connect(self.solve_system)
        layout.addWidget(self.solve_btn)

        # Output results
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def solve_system(self):
        try:
            x0 = float(self.x0_input.text())
            y0 = float(self.y0_input.text())
            eps = float(self.eps_input.text())
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректный ввод данных")
            return

        system_name = self.sys_combo.currentText()
        system = SYSTEMS[system_name]

        # System solving
        (x, y), iterations, errors = system_simple_iteration(
            system["phi1"], system["phi2"], x0, y0, eps
        )

        # Output result
        result_text = (
            f"Решение:\n"
            f"x = {x:.6f}\n"
            f"y = {y:.6f}\n"
            f"Итераций: {iterations}\n"
            "Погрешности:\n"
        )
        for i, (err_x, err_y) in enumerate(errors):
            result_text += f"Шаг {i + 1}: Δx={err_x:.2e}, Δy={err_y:.2e}\n"

        self.result_text.setText(result_text)
