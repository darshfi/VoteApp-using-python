from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget, QLineEdit, QMessageBox,
    QFormLayout, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction, QPalette, QColor
import pandas as pd
import sys
from pathlib import Path


class VotingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voting App")
        self.showFullScreen()
        self.file_path = Path("votes.xlsx")
        self.df_roles = self.load_data()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_screen()
        self.menu_bar()

    def load_data(self):
        if not self.file_path.exists():
            df = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
            df.to_excel(self.file_path, sheet_name='Roles', index=False)
        else:
            df = pd.read_excel(self.file_path, sheet_name='Roles')
            df.sort_values(by=["Role", "Contestant"], inplace=True, ignore_index=True)
        return df

    def save_data(self):
        self.df_roles.sort_values(by=["Role", "Contestant"], inplace=True, ignore_index=True)
        with pd.ExcelWriter(self.file_path, mode="w", engine="openpyxl") as writer:
            self.df_roles.to_excel(writer, sheet_name='Roles', index=False)

    def menu_bar(self):
        menu_bar = QMenuBar(self)
        admin_menu = QMenu("Admin", self)

        manage_action = QAction("Manage Candidates", self)
        manage_action.triggered.connect(self.admin_screen)
        results_action = QAction("View Results", self)
        results_action.triggered.connect(self.results_screen)

        admin_menu.addAction(manage_action)
        admin_menu.addAction(results_action)
        menu_bar.addMenu(admin_menu)
        self.setMenuBar(menu_bar)

    def home_screen(self):
        home = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Voting App")
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start Voting")
        start_button.setFont(QFont("Arial", 14))
        start_button.clicked.connect(self.voting_screen)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        home.setLayout(layout)
        self.stack.addWidget(home)
        self.stack.setCurrentWidget(home)

    def voting_screen(self):
        self.showFullScreen()
        vote_widget = QWidget()
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.vote_vars = {}

        for role in self.df_roles['Role'].unique():
            group_box = QGroupBox(role)
            group_box.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            group_layout = QHBoxLayout()

            button_group = QButtonGroup(group_box)
            contestants = self.df_roles[self.df_roles['Role'].str.lower() == role.lower()]['Contestant'].tolist()

            for contestant in contestants:
                button = QRadioButton(contestant)
                button.setFont(QFont("Arial", 14))
                button.setStyleSheet(""
                    "QRadioButton::indicator { width: 24px; height: 24px; }"
                    "QRadioButton { padding: 12px 20px; border-radius: 10px; background-color: #e0f0ff; }"
                    "QRadioButton:hover { background-color: #cce4ff; }"
                    "QRadioButton:checked { background-color: #99ccff; }"
                "")
                button_group.addButton(button)
                group_layout.addWidget(button)

            self.vote_vars[role] = button_group
            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)

        layout.addWidget(scroll)

        submit_btn = QPushButton("Submit Votes")
        submit_btn.setFont(QFont("Arial", 14))
        submit_btn.clicked.connect(self.submit_votes)
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        vote_widget.setLayout(layout)
        self.stack.addWidget(vote_widget)
        self.stack.setCurrentWidget(vote_widget)

    def submit_votes(self):
        for role, group in self.vote_vars.items():
            selected = group.checkedButton()
            if selected:
                name = selected.text()
                self.df_roles.loc[
                    (self.df_roles['Role'].str.lower() == role.lower()) &
                    (self.df_roles['Contestant'] == name), 'Votes'
                ] += 1
        self.save_data()
        QMessageBox.information(self, "Success", "Your votes have been submitted.")
        self.stack.setCurrentIndex(0)

    def admin_screen(self):
        self.showNormal()
        admin = QWidget()
        layout = QFormLayout()

        self.role_input = QLineEdit()
        self.contestant_input = QLineEdit()

        layout.addRow("Role:", self.role_input)
        layout.addRow("Contestant:", self.contestant_input)

        add_btn = QPushButton("Add Contestant")
        add_btn.clicked.connect(self.add_contestant)
        layout.addWidget(add_btn)

        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)

        back_btn = QPushButton("Reset All")
        back_btn.clicked.connect(self.home_screen)
        layout.addWidget(back_btn)

        admin.setLayout(layout)
        self.stack.addWidget(admin)
        self.stack.setCurrentWidget(admin)

    def add_contestant(self):
        role = self.role_input.text().strip().title()
        contestant = self.contestant_input.text().strip().title()

        if not role:
            QMessageBox.critical(self, "Error", "Role cannot be empty.")
            return

        existing_roles = self.df_roles['Role'].str.lower().unique()
        if role.lower() not in existing_roles:
            self.df_roles = pd.concat([self.df_roles, pd.DataFrame([[role, "NOTA", 0]],
                                                                   columns=["Role", "Contestant", "Votes"])],
                                      ignore_index=True)

        if contestant and contestant.lower() != "nota":
            exists = self.df_roles[
                (self.df_roles['Role'].str.lower() == role.lower()) &
                (self.df_roles['Contestant'].str.lower() == contestant.lower())
            ]
            if exists.empty:
                self.df_roles = pd.concat([self.df_roles, pd.DataFrame([[role, contestant, 0]],
                                                                       columns=["Role", "Contestant", "Votes"])],
                                          ignore_index=True)
                QMessageBox.information(self, "Added", f"{contestant} added to {role}.")
            else:
                QMessageBox.warning(self, "Duplicate", "Contestant already exists.")
        self.save_data()
        self.role_input.clear()
        self.contestant_input.clear()

    def reset_all(self):
        self.df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
        self.save_data()
        QMessageBox.information(self, "Reset", "All roles and contestants reset.")

    def results_screen(self):
        results = QWidget()
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        grouped = self.df_roles.groupby("Role")

        for role, group in grouped:
            role_label = QLabel(role)
            role_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            scroll_layout.addWidget(role_label)
            for _, row in group.iterrows():
                line = QLabel(f"{row['Contestant']} - {row['Votes']} votes")
                line.setFont(QFont("Arial", 12))
                scroll_layout.addWidget(line)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        results.setLayout(layout)
        self.stack.addWidget(results)
        self.stack.setCurrentWidget(results)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VotingApp()
    window.show()
    sys.exit(app.exec())
