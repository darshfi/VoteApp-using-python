from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGroupBox, QRadioButton, QButtonGroup, QStackedWidget, QLineEdit, QMessageBox,
    QFormLayout, QMenuBar, QMenu, QComboBox, QListWidget, QListWidgetItem, QStyleFactory
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
import pandas as pd
import sys
from pathlib import Path
import json

class VotingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voting App")
        self.showFullScreen()
        self.file_path = Path("votes.xlsx")
        self.order_path = Path("role_order.json")
        self.df_roles = self.load_data()
        self.role_order = self.load_role_order()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = None
        self.home_screen()
        self.menu_bar()

    def load_data(self):
        if not self.file_path.exists():
            df = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
            df.to_excel(self.file_path, sheet_name='Roles', index=False)
        else:
            df = pd.read_excel(self.file_path, sheet_name='Roles')
        return df

    def load_role_order(self):
        if self.order_path.exists():
            with open(self.order_path, "r") as f:
                return json.load(f)
        return list(self.df_roles['Role'].unique())

    def save_role_order(self):
        with open(self.order_path, "w") as f:
            json.dump(self.role_order, f)

    def save_data(self):
        self.df_roles.to_excel(self.file_path, sheet_name='Roles', index=False)

    def menu_bar(self):
        menu_bar = QMenuBar(self)
        admin_menu = QMenu("Admin", self)

        manage_action = QAction("Manage Candidates", self)
        manage_action.triggered.connect(lambda: self.auth_screen("admin"))
        results_action = QAction("View Results", self)
        results_action.triggered.connect(lambda: self.auth_screen("results"))
        back_action = QAction("Back to Home", self)
        back_action.triggered.connect(self.home_screen)

        admin_menu.addAction(manage_action)
        admin_menu.addAction(results_action)
        admin_menu.addAction(back_action)
        menu_bar.addMenu(admin_menu)
        self.setMenuBar(menu_bar)

    def home_screen(self):
        self.home = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Voting App")
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start Voting")
        start_button.setFont(QFont("Arial", 14))
        start_button.clicked.connect(self.voting_screen)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        watermark = QLabel("Made by Darsh")
        watermark.setFont(QFont("Arial", 8))
        watermark.setStyleSheet("color: #888888;")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(watermark, alignment=Qt.AlignmentFlag.AlignBottom)

        self.showFullScreen()
        self.home.setLayout(layout)
        self.stack.addWidget(self.home)
        self.stack.setCurrentWidget(self.home)

    def voting_screen(self):
        self.voting = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        self.vote_boxes = {}

        for role in self.role_order:
            role_group = QGroupBox(role)
            role_group.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            group_layout = QVBoxLayout()

            contestants = self.df_roles[self.df_roles['Role'] == role]['Contestant'].tolist()
            button_group = QButtonGroup(self.voting)
            button_group.setExclusive(True)
            buttons = []

            row_layout = QHBoxLayout()
            for name in contestants:
                rb = QRadioButton(name)
                rb.setFont(QFont("Arial", 13))
                rb.setMinimumHeight(50)
                rb.setStyleSheet("""
                    QRadioButton {
                        background-color: #e2dfe9;
                        color: black;
                        padding: 12px;
                        border-radius: 8px;
                    }
                    QRadioButton::indicator {
                        width: 20px;
                        height: 20px;
                    }
                    QRadioButton:checked {
                        background-color: #7e7e7e;
                        color: white;
                        font-weight: bold;
                        border: 2px solid #505080;
                    }
                """)
                row_layout.addWidget(rb)
                button_group.addButton(rb)
                buttons.append(rb)

            group_layout.addLayout(row_layout)
            role_group.setLayout(group_layout)
            scroll_layout.addWidget(role_group)
            self.vote_boxes[role] = buttons

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        submit_btn = QPushButton("Submit Vote")
        submit_btn.setFont(QFont("Arial", 14))
        submit_btn.clicked.connect(self.submit_votes)
        layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.showFullScreen()
        self.voting.setLayout(layout)
        self.stack.addWidget(self.voting)
        self.stack.setCurrentWidget(self.voting)

    def submit_votes(self):
        for role, widgets in self.vote_boxes.items():
            selected = [rb for rb in widgets if rb.isChecked()]
            if not selected:
                QMessageBox.warning(self, "Missing Selection", f"Please select a candidate for the role: {role}.")
                return
            name = selected[0].text()
            self.df_roles.loc[
                (self.df_roles['Role'] == role) & (self.df_roles['Contestant'] == name), 'Votes'] += 1

        self.save_data()
        QMessageBox.information(self, "Success", "Your votes have been submitted.")
        self.stack.setCurrentWidget(self.home)

    def auth_screen(self, ok: str):
        auth = QWidget()
        layout = QFormLayout()

        self.admin_password = QLineEdit()
        layout.addRow("Admin Password:", self.admin_password)

        chk_btn = QPushButton("Check")
        chk_btn.clicked.connect(lambda: self.check_pass(ok))
        layout.addRow(chk_btn)

        self.showNormal()
        auth.setLayout(layout)
        self.stack.addWidget(auth)
        self.stack.setCurrentWidget(auth)

    def check_pass(self, ok: str):
        if self.admin_password.text() == "avadmingsc":
            if ok == "results":
                self.results_screen()
            elif ok == "admin":
                self.admin_screen()
        else:
            self.home_screen()

    def admin_screen(self):
        admin = QWidget()
        layout = QFormLayout()

        self.role_input = QLineEdit()
        self.contestant_input = QLineEdit()
        layout.addRow("Role:", self.role_input)
        layout.addRow("Contestant:", self.contestant_input)

        add_btn = QPushButton("Add Contestant")
        add_btn.clicked.connect(self.add_contestant)
        layout.addWidget(add_btn)

        # --- Delete Role Section ---
        layout.addRow(QLabel("Delete Role:"))
        self.role_delete_combo = QComboBox()
        self.role_delete_combo.addItems(self.df_roles['Role'].unique())
        layout.addRow(self.role_delete_combo)
        delete_role_btn = QPushButton("Delete Role")
        delete_role_btn.clicked.connect(self.delete_role)
        layout.addWidget(delete_role_btn)

        # --- Delete Candidate Section ---
        layout.addRow(QLabel("Delete Candidate:"))
        self.role_select_for_candidate = QComboBox()
        self.role_select_for_candidate.addItems(self.df_roles['Role'].unique())
        self.role_select_for_candidate.currentTextChanged.connect(self.update_candidate_list)
        layout.addRow(self.role_select_for_candidate)

        self.candidate_select_combo = QComboBox()
        self.update_candidate_list()
        layout.addRow(self.candidate_select_combo)

        delete_candidate_btn = QPushButton("Delete Candidate")
        delete_candidate_btn.clicked.connect(self.delete_candidate)
        layout.addWidget(delete_candidate_btn)

        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)

        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(self.ask_reorder_or_not)
        layout.addWidget(back_btn)

        watermark = QLabel("Made by Darsh")
        watermark.setFont(QFont("Arial", 8))
        watermark.setStyleSheet("color: #888888;")
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addRow("", watermark)

        admin.setLayout(layout)
        self.stack.addWidget(admin)
        self.stack.setCurrentWidget(admin)

    # Function to update candidate list dropdown based on selected role
    def update_candidate_list(self):
        role = self.role_select_for_candidate.currentText()
        candidates = self.df_roles[self.df_roles['Role'] == role]['Contestant'].tolist()
        self.candidate_select_combo.clear()
        self.candidate_select_combo.addItems(candidates)

    # Function to delete a role
    def delete_role(self):
        role = self.role_delete_combo.currentText()
        self.df_roles = self.df_roles[self.df_roles['Role'] != role]
        if role in self.role_order:
            self.role_order.remove(role)
        self.save_data()
        self.save_role_order()
        QMessageBox.information(self, "Deleted", f"Role '{role}' deleted.")
        self.admin_screen()  # Refresh UI

    # Function to delete a candidate
    def delete_candidate(self):
        role = self.role_select_for_candidate.currentText()
        candidate = self.candidate_select_combo.currentText()

        if candidate == "NOTA":
            QMessageBox.warning(self, "Blocked", "NOTA cannot be deleted.")
            return

        self.df_roles = self.df_roles[
            ~((self.df_roles['Role'] == role) & (self.df_roles['Contestant'] == candidate))]
        self.save_data()
        QMessageBox.information(self, "Deleted", f"Candidate '{candidate}' from '{role}' deleted.")
        self.admin_screen()  # Refresh UI

    # Update `add_contestant()` to auto-add NOTA if not already there and always last
    def add_contestant(self):
        role = self.role_input.text().strip().title()
        contestant = self.contestant_input.text().strip().title()

        if not role:
            QMessageBox.critical(self, "Error", "Role cannot be empty.")
            return

        if role not in self.role_order:
            self.role_order.append(role)

        if contestant:
            exists = self.df_roles[
                (self.df_roles['Role'] == role) &
                (self.df_roles['Contestant'].str.lower() == contestant.lower())]
            if exists.empty:
                self.df_roles = pd.concat([
                    self.df_roles,
                    pd.DataFrame([[role, contestant, 0]], columns=["Role", "Contestant", "Votes"])
                ], ignore_index=True)
                QMessageBox.information(self, "Added", f"{contestant} added to {role}.")
            else:
                QMessageBox.warning(self, "Duplicate", "Contestant already exists.")

        # Ensure NOTA is present and last
        if "NOTA" not in self.df_roles[self.df_roles['Role'] == role]['Contestant'].str.upper().tolist():
            self.df_roles = pd.concat([
                self.df_roles,
                pd.DataFrame([[role, "NOTA", 0]], columns=["Role", "Contestant", "Votes"])
            ], ignore_index=True)

        # Ensure NOTA is last in visual order (important for radio layout)
        self.df_roles = self.df_roles.sort_values(
            by=["Role", "Contestant"], key=lambda x: x.str.upper().ne("NOTA"), ignore_index=True)

        self.save_data()
        self.role_input.clear()
        self.contestant_input.clear()

    def reset_all(self):
        self.df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
        self.role_order = []
        self.save_data()
        if self.order_path.exists():
            self.order_path.unlink()
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

    def ask_reorder_or_not(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Role Order")
        msg.setText("Do you want to reorder the roles?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        response = msg.exec()

        if response == QMessageBox.StandardButton.Yes:
            self.reorder_screen()
        elif response == QMessageBox.StandardButton.No:
            self.save_role_order()
            self.stack.setCurrentWidget(self.home)
        # Cancel does nothing

    def reorder_screen(self):
        self.reorder = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Reorder Roles (Drag and Drop)")
        label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(label)

        self.role_list_widget = QListWidget()
        self.role_list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.role_list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)

        for role in self.role_order:
            item = QListWidgetItem(role)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsDragEnabled)
            self.role_list_widget.addItem(item)

        layout.addWidget(self.role_list_widget)

        save_btn = QPushButton("Save Order")
        save_btn.clicked.connect(self.save_new_order)
        layout.addWidget(save_btn)

        back_btn = QPushButton("Cancel and Go Back")
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.home))
        layout.addWidget(back_btn)

        self.showNormal()
        self.reorder.setLayout(layout)
        self.stack.addWidget(self.reorder)
        self.stack.setCurrentWidget(self.reorder)

    def save_new_order(self):
        new_order = []
        for i in range(self.role_list_widget.count()):
            item = self.role_list_widget.item(i)
            new_order.append(item.text())
        self.role_order = new_order
        self.save_role_order()
        QMessageBox.information(self, "Saved", "Role order updated.")
        self.stack.setCurrentWidget(self.home)

if __name__ == "__main__":
    HIDDEN_SIGNATURE = "Made by Darsh Patel - 2025fi"

    app = QApplication(sys.argv)

    app.setStyle(QStyleFactory.create("Fusion"))

    # Apply global stylesheet
    app.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            QPushButton {
                background-color: #333;
                color: white;
                padding: 8px 14px;
                border: 1px solid #555;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QLineEdit, QComboBox {
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 4px;
            }
            QLabel {
                color: white;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding: 8px;
            }
            QScrollArea {
                background-color: #1e1e1e;
            }
            QMenuBar, QMenu {
                background-color: #2d2d2d;
                color: white;
            }
            QMenu::item:selected {
                background-color: #444;
            }
        """)

    window = VotingApp()
    window.show()
    sys.exit(app.exec())
