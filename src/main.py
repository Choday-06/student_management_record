
import sys
import sqlite3
from pathlib import Path
from datetime import date

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QStackedWidget,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QCheckBox,
    QScrollArea
)

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"
DATA_FOLDER.mkdir(exist_ok=True)

DATABASE_PATH = DATA_FOLDER / "students.db"


def connect_database():
    return sqlite3.connect(DATABASE_PATH)


def create_table():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            marks REAL NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def get_all_students():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, student_id, name, class_name,
               gender, phone, marks
        FROM students
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    return records


def add_student(student_id, name, class_name,
                gender, phone, marks):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO students
            (student_id, name, class_name,
             gender, phone, marks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            name,
            class_name,
            gender,
            phone,
            marks
        ))

        connection.commit()

        return True, "Student registered successfully."

    except sqlite3.IntegrityError:

        return False, "This Student ID already exists."

    except sqlite3.Error as error:

        return False, f"Database error: {error}"

    finally:

        connection.close()


def update_student(record_id, student_id, name,
                   class_name, gender, phone, marks):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                class_name = ?,
                gender = ?,
                phone = ?,
                marks = ?
            WHERE id = ?
        """, (
            student_id,
            name,
            class_name,
            gender,
            phone,
            marks,
            record_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Student record was not found."

        return True, "Student updated successfully."

    except sqlite3.IntegrityError:

        return False, "This Student ID is already in use."

    except sqlite3.Error as error:

        return False, f"Database error: {error}"

    finally:

        connection.close()


def delete_student(record_id):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (record_id,)
        )

        connection.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        connection.close()


# ==================================================
# PIE CHART WIDGET
# ==================================================

class PerformancePieChart(QWidget):

    def __init__(self):

        super().__init__()

        self.passed = 0
        self.failed = 0

        self.setMinimumHeight(220)

    def set_data(self, passed, failed):

        self.passed = passed
        self.failed = failed

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        total = self.passed + self.failed

        if total == 0:

            painter.setPen(QColor("#7C8BA0"))

            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "No student data available"
            )

            return

        size = min(145, self.height() - 35)

        x = 15
        y = (self.height() - size) // 2

        rect = QRectF(x, y, size, size)

        passed_angle = int(
            self.passed / total * 360 * 16
        )

        failed_angle = 360 * 16 - passed_angle

        painter.setPen(Qt.PenStyle.NoPen)

        # Passed students
        painter.setBrush(QColor("#286DE0"))

        painter.drawPie(
            rect,
            90 * 16,
            -passed_angle
        )

        # Failed students
        painter.setBrush(QColor("#F39B45"))

        painter.drawPie(
            rect,
            90 * 16 - passed_angle,
            -failed_angle
        )

        # Legend
        legend_x = x + size + 22
        legend_y = y + 30

        painter.setFont(QFont("Arial", 10))

        painter.setBrush(QColor("#286DE0"))

        painter.drawRoundedRect(
            legend_x,
            legend_y,
            12,
            12,
            3,
            3
        )

        painter.setPen(QColor("#26364F"))

        painter.drawText(
            legend_x + 20,
            legend_y + 11,
            f"Passed: {self.passed}"
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F39B45"))

        painter.drawRoundedRect(
            legend_x,
            legend_y + 35,
            12,
            12,
            3,
            3
        )

        painter.setPen(QColor("#26364F"))

        painter.drawText(
            legend_x + 20,
            legend_y + 46,
            f"Failed: {self.failed}"
        )

        painter.drawText(
            legend_x,
            legend_y + 85,
            f"Total: {total}"
        )


# ==================================================
# BAR CHART WIDGET
# ==================================================

class MarksBarChart(QWidget):

    def __init__(self):

        super().__init__()

        self.marks = []

        self.setMinimumHeight(220)

    def set_data(self, marks):

        self.marks = marks

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        categories = [
            "0-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80-89",
            "90-100"
        ]

        counts = [0] * len(categories)

        for mark in self.marks:

            if mark < 40:
                counts[0] += 1

            elif mark < 50:
                counts[1] += 1

            elif mark < 60:
                counts[2] += 1

            elif mark < 70:
                counts[3] += 1

            elif mark < 80:
                counts[4] += 1

            elif mark < 90:
                counts[5] += 1

            else:
                counts[6] += 1

        left = 38
        top = 20
        bottom = self.height() - 35

        chart_height = bottom - top
        chart_width = self.width() - 55

        maximum = max(counts) if counts else 0
        maximum = max(maximum, 1)

        painter.setPen(
            QPen(QColor("#DCE5F1"), 1)
        )

        painter.drawLine(left, top, left, bottom)

        painter.drawLine(
            left,
            bottom,
            self.width() - 10,
            bottom
        )

        bar_width = chart_width / len(categories)

        for i, count in enumerate(counts):

            bar_height = (
                count / maximum * (chart_height - 15)
            )

            x = left + i * bar_width + 5
            y = bottom - bar_height

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#286DE0"))

            painter.drawRoundedRect(
                QRectF(
                    x,
                    y,
                    max(5, bar_width - 12),
                    max(0, bar_height)
                ),
                4,
                4
            )

            painter.setPen(QColor("#26364F"))
            painter.setFont(QFont("Arial", 8))

            painter.drawText(
                QRectF(
                    x - 2,
                    bottom + 5,
                    bar_width,
                    20
                ),
                Qt.AlignmentFlag.AlignCenter,
                categories[i]
            )

            if count > 0:

                painter.drawText(
                    QRectF(
                        x - 2,
                        y - 19,
                        bar_width,
                        18
                    ),
                    Qt.AlignmentFlag.AlignCenter,
                    str(count)
                )


# ==================================================
# MAIN STUDENT MANAGEMENT APPLICATION
# ==================================================

class StudentManagementApp(QMainWindow):

    def __init__(self):

        super().__init__()

        create_table()

        self.editing_id = None

        self.setWindowTitle(
            "Student Record Management System"
        )

        self.resize(1250, 850)
        self.setMinimumSize(1000, 700)

        self.setStyleSheet("""

            QMainWindow {
                background-color: #F2F6FC;
            }

            QWidget {
                font-family: Arial;
                color: #26364F;
                font-size: 13px;
            }

            QFrame#sidebar {
                background-color: #142F50;
                border-radius: 14px;
            }

            QLabel#brand {
                color: white;
                font-size: 21px;
                font-weight: bold;
            }

            QLabel#sidebar_text {
                color: #C8D8EC;
                font-size: 12px;
            }

            QPushButton#nav_button {
                background-color: transparent;
                color: #E0EAF6;
                border: none;
                text-align: left;
                padding: 13px;
                border-radius: 8px;
                font-size: 14px;
            }

            QPushButton#nav_button:hover {
                background-color: #294B70;
            }

            QPushButton#nav_button:checked {
                background-color: #286DE0;
                color: white;
                font-weight: bold;
            }

            QPushButton#primary {
                background-color: #286DE0;
                color: white;
                border: none;
                padding: 11px 17px;
                border-radius: 7px;
                font-weight: bold;
            }

            QPushButton#primary:hover {
                background-color: #1857BD;
            }

            QPushButton#secondary {
                background-color: #E3ECFA;
                color: #244D7D;
                border: none;
                padding: 11px 17px;
                border-radius: 7px;
            }

            QPushButton#secondary:hover {
                background-color: #D3E1F5;
            }

            QPushButton#danger {
                background-color: #FCE8E8;
                color: #BD3737;
                border: none;
                padding: 10px 16px;
                border-radius: 7px;
            }

            QPushButton#danger:hover {
                background-color: #F8D5D5;
            }

            QPushButton#action_add {
                background-color: #286DE0;
                color: white;
                padding: 15px;
                border: none;
                border-radius: 9px;
                font-weight: bold;
                text-align: left;
            }

            QPushButton#action_view,
            QPushButton#action_about {
                background-color: white;
                color: #244D7D;
                padding: 15px;
                border: 1px solid #DCE5F1;
                border-radius: 9px;
                font-weight: bold;
                text-align: left;
            }

            QFrame#dashboard_card,
            QFrame#content_card {
                background-color: white;
                border: 1px solid #E3EAF3;
                border-radius: 12px;
            }

            QLabel#page_title {
                color: #183451;
                font-size: 27px;
                font-weight: bold;
            }

            QLabel#muted {
                color: #7C8BA0;
                font-size: 12px;
            }

            QLabel#stat_heading {
                color: #7C8BA0;
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#stat_value {
                color: #286DE0;
                font-size: 29px;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #D8E1ED;
                border-radius: 7px;
                padding: 9px;
                min-height: 21px;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #286DE0;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #E1E8F1;
                border-radius: 9px;
                gridline-color: #EDF1F6;
                selection-background-color: #DCE9FC;
                selection-color: #183451;
                alternate-background-color: #F8FAFD;
            }

            QHeaderView::section {
                background-color: #EAF1FA;
                color: #304B6B;
                padding: 11px;
                border: none;
                font-weight: bold;
            }

            QCheckBox {
                spacing: 8px;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

        """)

        self.build_interface()
        self.load_students()
        self.update_dashboard()

    # ==================================================
    # SIDEBAR AND NAVIGATION
    # ==================================================

    def build_interface(self):

        central_widget = QWidget()

        main_layout = QHBoxLayout(central_widget)

        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(
            18, 25, 18, 20
        )

        sidebar_layout.setSpacing(12)

        brand = QLabel("STUDENT\nMANAGEMENT")
        brand.setObjectName("brand")

        description = QLabel(
            "Record Management System"
        )
        description.setObjectName("sidebar_text")

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(description)
        sidebar_layout.addSpacing(35)

        self.dashboard_button = self.create_nav_button(
            "▦   Dashboard"
        )

        self.students_button = self.create_nav_button(
            "＋   Register Student"
        )

        self.records_button = self.create_nav_button(
            "▤   View Records"
        )

        self.about_button = self.create_nav_button(
            "ⓘ   About"
        )

        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.students_button)
        sidebar_layout.addWidget(self.records_button)
        sidebar_layout.addWidget(self.about_button)

        sidebar_layout.addStretch()

        footer = QLabel(
            "Developed using Python and PyQt6"
        )

        footer.setObjectName("sidebar_text")
        footer.setWordWrap(True)

        sidebar_layout.addWidget(footer)

        # Create pages
        self.pages = QStackedWidget()

        self.dashboard_page = self.create_dashboard_page()
        self.students_page = self.create_students_page()
        self.records_page = self.create_records_page()
        self.about_page = self.create_about_page()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.students_page)
        self.pages.addWidget(self.records_page)
        self.pages.addWidget(self.about_page)

        # Navigation connections
        self.dashboard_button.clicked.connect(
            lambda: self.navigate(0)
        )

        self.students_button.clicked.connect(
            lambda: self.navigate(1)
        )

        self.records_button.clicked.connect(
            lambda: self.navigate(2)
        )

        self.about_button.clicked.connect(
            lambda: self.navigate(3)
        )

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)

        self.setCentralWidget(central_widget)

        self.navigate(0)

    def create_nav_button(self, text):

        button = QPushButton(text)

        button.setObjectName("nav_button")
        button.setCheckable(True)

        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        return button

    def navigate(self, index):

        self.pages.setCurrentIndex(index)

        buttons = [
            self.dashboard_button,
            self.students_button,
            self.records_button,
            self.about_button
        ]

        for i, button in enumerate(buttons):
            button.setChecked(i == index)

        if index == 2:
            self.load_students()

        if index == 0:
            self.update_dashboard()

    # ==================================================
    # DASHBOARD PAGE
    # ==================================================

    def create_dashboard_page(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(17)

        # Welcome banner
        banner = QFrame()

        banner.setStyleSheet("""
            QFrame {
                background-color: #142F50;
                border-radius: 12px;
            }
        """)

        banner_layout = QHBoxLayout(banner)

        banner_layout.setContentsMargins(
            22, 18, 22, 18
        )

        welcome_layout = QVBoxLayout()

        welcome = QLabel(
            "Welcome to Student Management!"
        )

        welcome.setStyleSheet("""
            color: white;
            font-size: 21px;
            font-weight: bold;
        """)

        welcome_subtitle = QLabel(
            "Manage student information and monitor academic performance."
        )

        welcome_subtitle.setStyleSheet(
            "color: #D4E2F2; font-size: 12px;"
        )

        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(welcome_subtitle)

        date_label = QLabel(
            date.today().strftime("%d %B %Y")
        )

        date_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
        """)

        banner_layout.addLayout(welcome_layout)
        banner_layout.addStretch()
        banner_layout.addWidget(date_label)

        layout.addWidget(banner)

        # Heading
        title = QLabel("Dashboard Overview")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Here is a summary of your student records."
        )

        subtitle.setObjectName("muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Statistics
        cards = QGridLayout()
        cards.setSpacing(12)

        self.total_label = self.create_stat_card(
            cards, 0, "TOTAL STUDENTS", "0", "👥"
        )

        self.average_label = self.create_stat_card(
            cards, 1, "AVERAGE MARKS", "0%", "📊"
        )

        self.pass_label = self.create_stat_card(
            cards, 2, "PASSED STUDENTS", "0", "🎓"
        )

        self.failed_label = self.create_stat_card(
            cards, 3, "FAILED STUDENTS", "0", "⚠️"
        )

        layout.addLayout(cards)

        # Academic performance
        chart_title = QLabel("Academic Performance")

        chart_title.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
        """)

        layout.addWidget(chart_title)

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        # Pie chart card
        pie_card = QFrame()
        pie_card.setObjectName("content_card")

        pie_layout = QVBoxLayout(pie_card)

        pie_layout.setContentsMargins(
            15, 15, 15, 15
        )

        pie_heading = QLabel(
            "Pass and Fail Overview"
        )

        pie_heading.setStyleSheet(
            "font-weight: bold;"
        )

        self.performance_chart = PerformancePieChart()

        pie_layout.addWidget(pie_heading)
        pie_layout.addWidget(self.performance_chart)

        # Bar chart card
        bar_card = QFrame()
        bar_card.setObjectName("content_card")

        bar_layout = QVBoxLayout(bar_card)

        bar_layout.setContentsMargins(
            15, 15, 15, 15
        )

        bar_heading = QLabel(
            "Marks Distribution"
        )

        bar_heading.setStyleSheet(
            "font-weight: bold;"
        )

        self.marks_chart = MarksBarChart()

        bar_layout.addWidget(bar_heading)
        bar_layout.addWidget(self.marks_chart)

        charts_layout.addWidget(pie_card)
        charts_layout.addWidget(bar_card)

        layout.addLayout(charts_layout)

        # Recent records
        recent_heading = QLabel(
            "Recent Student Records"
        )

        recent_heading.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
        """)

        layout.addWidget(recent_heading)

        self.recent_table = QTableWidget()

        self.recent_table.setColumnCount(5)

        self.recent_table.setHorizontalHeaderLabels([
            "Student ID",
            "Full Name",
            "Class",
            "Gender",
            "Marks"
        ])

        self.recent_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.recent_table.verticalHeader().setVisible(False)

        self.recent_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.recent_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.recent_table.setMaximumHeight(210)

        self.recent_table.setAlternatingRowColors(True)

        layout.addWidget(self.recent_table)

        # Quick actions
        quick_heading = QLabel("Quick Actions")

        quick_heading.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
        """)

        layout.addWidget(quick_heading)

        actions = QHBoxLayout()

        add_button = QPushButton(
            "+ Register Student"
        )

        add_button.setObjectName("primary")

        add_button.clicked.connect(
            lambda: self.navigate(1)
        )

        view_button = QPushButton(
            "View All Records"
        )

        view_button.setObjectName("secondary")

        view_button.clicked.connect(
            lambda: self.navigate(2)
        )

        actions.addWidget(add_button)
        actions.addWidget(view_button)

        layout.addLayout(actions)
        layout.addStretch()

        scroll.setWidget(page)

        return scroll

    def create_stat_card(self, grid, column,
                         heading, value, emoji):

        card = QFrame()

        card.setObjectName("dashboard_card")
        card.setMinimumHeight(135)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            16, 13, 16, 13
        )

        card_layout.setSpacing(7)

        icon_label = QLabel(emoji)
        icon_label.setStyleSheet(
            "font-size: 23px;"
        )

        heading_label = QLabel(heading)
        heading_label.setObjectName("stat_heading")

        value_label = QLabel(value)
        value_label.setObjectName("stat_value")

        card_layout.addWidget(icon_label)
        card_layout.addWidget(heading_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        grid.addWidget(card, 0, column)

        return value_label

    # ==================================================
    # REGISTER STUDENT PAGE
    # ==================================================

    def create_students_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Register Student")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Enter student information below."
        )

        subtitle.setObjectName("muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        form_card = QFrame()
        form_card.setObjectName("content_card")

        form_layout = QGridLayout(form_card)

        form_layout.setContentsMargins(
            20, 20, 20, 20
        )

        form_layout.setSpacing(15)

        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText(
            "Enter student ID"
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "Enter full name"
        )

        self.class_input = QComboBox()

        self.class_input.addItems([
            "Class 5", "Class 6", "Class 7",
            "Class 8", "Class 9", "Class 10",
            "Class 11", "Class 12"
        ])

        self.gender_input = QComboBox()

        self.gender_input.addItems([
            "Select Gender",
            "Male",
            "Female",
            "Other"
        ])

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText(
            "Enter phone number"
        )

        self.marks_input = QLineEdit()
        self.marks_input.setPlaceholderText(
            "Enter marks (0-100)"
        )

        form_layout.addWidget(
            QLabel("Student ID"), 0, 0
        )

        form_layout.addWidget(
            self.student_id_input, 0, 1
        )

        form_layout.addWidget(
            QLabel("Full Name"), 0, 2
        )

        form_layout.addWidget(
            self.name_input, 0, 3
        )

        form_layout.addWidget(
            QLabel("Class"), 1, 0
        )

        form_layout.addWidget(
            self.class_input, 1, 1
        )

        form_layout.addWidget(
            QLabel("Gender"), 1, 2
        )

        form_layout.addWidget(
            self.gender_input, 1, 3
        )

        form_layout.addWidget(
            QLabel("Phone"), 2, 0
        )

        form_layout.addWidget(
            self.phone_input, 2, 1
        )

        form_layout.addWidget(
            QLabel("Marks"), 2, 2
        )

        form_layout.addWidget(
            self.marks_input, 2, 3
        )

        layout.addWidget(form_card)

        self.confirm_checkbox = QCheckBox(
            "I confirm that the student information is correct."
        )

        layout.addWidget(self.confirm_checkbox)

        buttons = QHBoxLayout()

        self.save_button = QPushButton(
            "Save Student"
        )

        self.save_button.setObjectName("primary")

        self.clear_button = QPushButton(
            "Clear Form"
        )

        self.clear_button.setObjectName("secondary")

        buttons.addWidget(self.save_button)
        buttons.addWidget(self.clear_button)
        buttons.addStretch()

        layout.addLayout(buttons)
        layout.addStretch()

        self.save_button.clicked.connect(
            self.save_student
        )

        self.clear_button.clicked.connect(
            self.clear_form
        )

        return page

    # ==================================================
    # VIEW RECORDS PAGE
    # ==================================================

    def create_records_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("Student Records")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "View, search, edit and delete registered students."
        )

        subtitle.setObjectName("muted")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addWidget(QLabel("Search Student"))

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Search by student ID, name or class..."
        )

        layout.addWidget(self.search_input)

        self.table = QTableWidget()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "Database ID",
            "Student ID",
            "Full Name",
            "Class",
            "Gender",
            "Phone",
            "Marks"
        ])

        self.table.setColumnHidden(0, True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()

        self.edit_button = QPushButton(
            "Edit Selected"
        )

        self.edit_button.setObjectName("secondary")
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton(
            "Delete Selected"
        )

        self.delete_button.setObjectName("danger")
        self.delete_button.setEnabled(False)

        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch()

        layout.addLayout(actions)

        self.search_input.textChanged.connect(
            self.search_student
        )

        self.edit_button.clicked.connect(
            self.select_student_for_edit
        )

        self.delete_button.clicked.connect(
            self.remove_student
        )

        self.table.itemSelectionChanged.connect(
            self.check_table_selection
        )

        return page

    # ==================================================
    # ABOUT PAGE
    # ==================================================

    def create_about_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("About This Application")
        title.setObjectName("page_title")

        card = QFrame()
        card.setObjectName("content_card")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            25, 25, 25, 25
        )

        information = QLabel("""
            <h2>Student Record Management System</h2>

            <p><b>Developer:</b> Dechen Choden</p>

            <p><b>Framework:</b> Python PyQt6</p>

            <p><b>Database:</b> SQLite</p>

            <p><b>Purpose:</b> To manage student information
            and academic marks efficiently.</p>

            <p>This application demonstrates GUI design,
            database management, input validation and
            event handling.</p>
        """)

        information.setWordWrap(True)

        card_layout.addWidget(information)

        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addWidget(card)
        layout.addStretch()

        return page

    # ==================================================
    # REGISTER AND UPDATE STUDENT
    # ==================================================

    def save_student(self):

        if not self.confirm_checkbox.isChecked():

            QMessageBox.warning(
                self,
                "Confirmation Required",
                "Please confirm the student information."
            )

            return

        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()
        class_name = self.class_input.currentText()
        gender = self.gender_input.currentText()
        phone = self.phone_input.text().strip()
        marks_text = self.marks_input.text().strip()

        if not student_id or not name or not marks_text:

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Student ID, Full Name and Marks."
            )

            return

        if gender == "Select Gender":

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please select the student's gender."
            )

            return

        try:

            marks = float(marks_text)

            if not 0 <= marks <= 100:
                raise ValueError

        except ValueError:

            QMessageBox.warning(
                self,
                "Invalid Marks",
                "Marks must be between 0 and 100."
            )

            return

        if self.editing_id is None:

            success, message = add_student(
                student_id,
                name,
                class_name,
                gender,
                phone,
                marks
            )

        else:

            success, message = update_student(
                self.editing_id,
                student_id,
                name,
                class_name,
                gender,
                phone,
                marks
            )

        if success:

            QMessageBox.information(
                self,
                "Success",
                message
            )

            self.clear_form()
            self.load_students()
            self.update_dashboard()

        else:

            QMessageBox.warning(
                self,
                "Error",
                message
            )

    # ==================================================
    # LOAD AND DISPLAY STUDENT RECORDS
    # ==================================================

    def load_students(self):

        self.display_students(
            get_all_students()
        )

    def display_students(self, students):

        self.table.setRowCount(0)

        for record in students:

            row = self.table.rowCount()

            self.table.insertRow(row)

            for column, value in enumerate(record):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.table.setItem(
                    row,
                    column,
                    item
                )

    # ==================================================
    # SEARCH STUDENTS
    # ==================================================

    def search_student(self, keyword):

        keyword = keyword.strip().lower()

        if not keyword:

            self.load_students()
            return

        matching_records = []

        for student in get_all_students():

            searchable_text = " ".join(
                str(value).lower()
                for value in student[1:]
            )

            if keyword in searchable_text:

                matching_records.append(student)

        self.display_students(matching_records)

    # ==================================================
    # SELECT AND EDIT STUDENT
    # ==================================================

    def check_table_selection(self):

        selected = self.table.currentRow() >= 0

        self.edit_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def select_student_for_edit(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a student first."
            )

            return

        self.editing_id = int(
            self.table.item(row, 0).text()
        )

        self.student_id_input.setText(
            self.table.item(row, 1).text()
        )

        self.name_input.setText(
            self.table.item(row, 2).text()
        )

        self.class_input.setCurrentText(
            self.table.item(row, 3).text()
        )

        self.gender_input.setCurrentText(
            self.table.item(row, 4).text()
        )

        self.phone_input.setText(
            self.table.item(row, 5).text()
        )

        self.marks_input.setText(
            self.table.item(row, 6).text()
        )

        self.confirm_checkbox.setChecked(True)

        self.save_button.setText(
            "Update Student"
        )

        self.navigate(1)

        QMessageBox.information(
            self,
            "Edit Student",
            "Update the information and click Update Student."
        )

    # ==================================================
    # DELETE STUDENT
    # ==================================================

    def remove_student(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select a student to delete."
            )

            return

        record_id = int(
            self.table.item(row, 0).text()
        )

        student_name = self.table.item(row, 2).text()

        answer = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {student_name}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:

            if delete_student(record_id):

                QMessageBox.information(
                    self,
                    "Deleted",
                    "Student record deleted successfully."
                )

                self.load_students()
                self.update_dashboard()
                self.clear_form()

            else:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to delete this student record."
                )

    # ==================================================
    # CLEAR REGISTRATION FORM
    # ==================================================

    def clear_form(self):

        self.student_id_input.clear()
        self.name_input.clear()

        self.class_input.setCurrentIndex(0)
        self.gender_input.setCurrentIndex(0)

        self.phone_input.clear()
        self.marks_input.clear()

        self.confirm_checkbox.setChecked(False)

        self.editing_id = None

        self.save_button.setText(
            "Save Student"
        )

        if hasattr(self, "table"):
            self.table.clearSelection()

    # ==================================================
    # UPDATE DASHBOARD
    # ==================================================

    def update_dashboard(self):

        students = get_all_students()

        total = len(students)

        marks = [
            float(student[6])
            for student in students
        ]

        if total > 0:

            average = sum(marks) / total

            passed = sum(
                1 for mark in marks
                if mark >= 40
            )

            failed = total - passed

        else:

            average = 0
            passed = 0
            failed = 0

        # Statistics cards
        self.total_label.setText(str(total))

        self.average_label.setText(
            f"{average:.1f}%"
        )

        self.pass_label.setText(str(passed))

        self.failed_label.setText(str(failed))

        # Charts
        self.performance_chart.set_data(
            passed,
            failed
        )

        self.marks_chart.set_data(marks)

        # Recent records
        self.recent_table.setRowCount(0)

        for student in students[:5]:

            row = self.recent_table.rowCount()

            self.recent_table.insertRow(row)

            values = [
                student[1],
                student[2],
                student[3],
                student[4],
                student[6]
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                self.recent_table.setItem(
                    row,
                    column,
                    item
                )


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = StudentManagementApp()

    window.show()

    sys.exit(app.exec())
