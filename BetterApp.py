import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QRadioButton, QScrollArea,
    QGroupBox, QMessageBox, QMenuBar, QMenu, QStackedWidget, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import pandas as pd
from pathlib import Path


class VotingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voting App")
        self.showFullScreen()

        self.file_path = Path("votes.xlsx")
        self.df_roles = self.load_data()
        self.selected_votes = {}

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.create_menu()
        self.show_home_page()

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

    def show_home_page(self):
        home = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Welcome to the Voting App")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)

        btn_start = QPushButton("Start Voting")
        btn_start.clicked.connect(self.show_voting_screen)
        layout.addWidget(btn_start)

        home.setLayout(layout)
        self.stack.addWidget(home)
        self.stack.setCurrentWidget(home)

    def show_voting_screen(self):
        voting = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Cast Your Vote")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        scroll_layout.addWidget(title)

        self.selected_votes.clear()

        for role in self.df_roles['Role'].unique():
            box = QGroupBox(role)
            box_layout = QHBoxLayout()

            var = {}
            for contestant in self.df_roles[self.df_roles['Role'] == role]['Contestant']:
                rb = QRadioButton(contestant)
                rb.toggled.connect(lambda checked, r=role, c=contestant: self.select_vote(r, c, checked))
                box_layout.addWidget(rb)

            box.setLayout(box_layout)
            scroll_layout.addWidget(box)

        submit_btn = QPushButton("Submit Votes")
        submit_btn.clicked.connect(self.submit_votes)
        scroll_layout.addWidget(submit_btn)

        scroll.setWidget(scroll_content)
        layout = QVBoxLayout()
        layout.addWidget(scroll)
        voting.setLayout(layout)

        self.stack.addWidget(voting)
        self.stack.setCurrentWidget(voting)

    def select_vote(self, role, contestant, checked):
        if checked:
            self.selected_votes[role] = contestant

    def submit_votes(self):
        for role, contestant in self.selected_votes.items():
            self.df_roles.loc[
                (self.df_roles['Role'] == role) &
                (self.df_roles['Contestant'] == contestant), 'Votes'] += 1
        self.save_data()
        QMessageBox.information(self, "Success", "Your votes have been submitted.")
        self.show_home_page()

    def show_results(self):
        results = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        grouped = self.df_roles.groupby("Role")
        for role, group in grouped:
            title = QLabel(f"{role}")
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            layout.addWidget(title)
            for _, row in group.iterrows():
                layout.addWidget(QLabel(f"{row['Contestant']} - {row['Votes']} votes"))

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.show_home_page)
        layout.addWidget(back_btn)

        results.setLayout(layout)
        self.stack.addWidget(results)
        self.stack.setCurrentWidget(results)

    def show_admin_panel(self):
        admin = QWidget()
        layout = QFormLayout()

        self.input_role = QLineEdit()
        self.input_contestant = QLineEdit()
        layout.addRow("Role:", self.input_role)
        layout.addRow("Contestant:", self.input_contestant)

        btn_add = QPushButton("Add Contestant")
        btn_add.clicked.connect(self.add_contestant)
        layout.addRow(btn_add)

        btn_reset = QPushButton("Reset All")
        btn_reset.clicked.connect(self.reset_all)
        layout.addRow(btn_reset)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.show_home_page)
        layout.addRow(back_btn)

        admin.setLayout(layout)
        self.stack.addWidget(admin)
        self.stack.setCurrentWidget(admin)

    def add_contestant(self):
        role = self.input_role.text().strip().title()
        contestant = self.input_contestant.text().strip().title()

        if not role:
            QMessageBox.warning(self, "Error", "Role cannot be empty.")
            return

        if role.lower() not in self.df_roles['Role'].str.lower().unique():
            self.df_roles = pd.concat([
                self.df_roles,
                pd.DataFrame([[role, "NOTA", 0]], columns=["Role", "Contestant", "Votes"])
            ], ignore_index=True)

        if contestant and contestant.lower() != "nota":
            exists = self.df_roles[
                (self.df_roles['Role'].str.lower() == role.lower()) &
                (self.df_roles['Contestant'].str.lower() == contestant.lower())]
            if exists.empty:
                self.df_roles = pd.concat([
                    self.df_roles,
                    pd.DataFrame([[role, contestant, 0]], columns=["Role", "Contestant", "Votes"])
                ], ignore_index=True)
                QMessageBox.information(self, "Success", f"'{contestant}' added to '{role}'.")
            else:
                QMessageBox.warning(self, "Error", "Contestant already exists for this role.")
        self.save_data()
        self.input_role.clear()
        self.input_contestant.clear()

    def reset_all(self):
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to reset all roles and contestants?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
            self.save_data()
            QMessageBox.information(self, "Reset", "All roles and contestants have been reset.")

    def create_menu(self):
        menu_bar = self.menuBar()
        admin_menu = menu_bar.addMenu("Admin")

        manage_action = QAction("Manage Candidates", self)
        manage_action.triggered.connect(self.show_admin_panel)
        admin_menu.addAction(manage_action)

        results_action = QAction("View Results", self)
        results_action.triggered.connect(self.show_results)
        admin_menu.addAction(results_action)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VotingApp()
    window.show()
    sys.exit(app.exec())
