import tkinter as tk
from tkinter import ttk, messagebox, Menu
import pandas as pd
from pathlib import Path
import ttkbootstrap as tb


class VotingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voting App")
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        self.style = tb.Style("morph")
        self.file_path = Path("votes.xlsx")
        self.df_roles = self.load_data()

        self.create_menu()
        self.open_home_page()

    def open_results_screen(self):
        """ Display voting results grouped by role. """
        results_screen = tk.Toplevel(self.root)
        results_screen.title("Voting Results")
        results_screen.geometry("600x500")

        canvas = tk.Canvas(results_screen)
        scrollbar = ttk.Scrollbar(results_screen, orient="vertical", command=canvas.yview)
        scroll_frame = tb.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        grouped = self.df_roles.groupby("Role")

        for role, group in grouped:
            tb.Label(scroll_frame, text=f"{role}", font=("Arial", 14, "bold")).pack(pady=(10, 5))
            for _, row in group.iterrows():
                tb.Label(scroll_frame, text=f"{row['Contestant']} - {row['Votes']} votes", font=("Arial", 12)).pack(
                    pady=2)

    def load_data(self):
        """ Load or create an Excel file for roles and contestants. """
        if not self.file_path.exists():
            df = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
            df.to_excel(self.file_path, sheet_name='Roles', index=False)
        else:
            df = pd.read_excel(self.file_path, sheet_name='Roles')
            df.sort_values(by=["Role", "Contestant"], inplace=True, ignore_index=True)
        return df

    def save_data(self):
        """ Save updated data back to the Excel file, sorted by Role and Contestant. """
        self.df_roles.sort_values(by=["Role", "Contestant"], inplace=True, ignore_index=True)
        with pd.ExcelWriter(self.file_path, mode="w", engine="openpyxl") as writer:
            self.df_roles.to_excel(writer, sheet_name='Roles', index=False)

    def add_role_contestant(self, event=None):
        """ Add a new role and/or contestant to the system. """
        role = self.entry_role.get().strip().title()
        contestant = self.entry_contestant.get().strip().title()

        if not role:
            messagebox.showerror("Error", "Role cannot be empty.")
            return

        existing_roles = self.df_roles['Role'].str.lower().unique()
        if role.lower() not in existing_roles:
            self.df_roles = pd.concat([self.df_roles, pd.DataFrame([[role, "NOTA", 0]],
                                                                   columns=["Role", "Contestant", "Votes"])],
                                      ignore_index=True)

        if contestant and contestant.lower() != "nota":
            existing_combination = self.df_roles[
                (self.df_roles['Role'].str.lower() == role.lower()) &
                (self.df_roles['Contestant'].str.lower() == contestant.lower())
            ]
            if existing_combination.empty:
                self.df_roles = pd.concat([self.df_roles, pd.DataFrame([[role, contestant, 0]],
                                                                       columns=["Role", "Contestant", "Votes"])],
                                          ignore_index=True)
                messagebox.showinfo("Success", f"'{contestant}' added to '{role}'.")
            else:
                messagebox.showerror("Error", "Contestant already exists for this role.")

        self.save_data()
        self.entry_role.delete(0, tk.END)
        self.entry_contestant.delete(0, tk.END)
        self.entry_role.focus_set()

    def reset_roles_contestants(self):
        """ Reset all roles and contestants. """
        self.df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
        self.save_data()
        messagebox.showinfo("Reset", "All roles and contestants have been reset.")

    def submit_votes(self):
        """ Submit votes and update Excel file. """
        for idx, role in enumerate(self.df_roles['Role'].unique()):
            contestant = self.comboboxes[idx].get().strip()
            self.df_roles.loc[
                (self.df_roles['Role'].str.lower() == role.lower()) &
                (self.df_roles['Contestant'] == contestant), 'Votes'
            ] += 1
        self.save_data()
        messagebox.showinfo("Success", "Your votes have been submitted.")
        self.voting_screen.destroy()

    def open_confirmation_screen(self):
        """ Open a confirmation popup before resetting roles. """
        confirmation_screen = tk.Toplevel(self.root)
        confirmation_screen.title("Confirmation")
        confirmation_screen.geometry("320x180")

        tb.Label(confirmation_screen, text="Are you sure you want to reset?", font=("Arial", 14, "bold")).pack(pady=10)
        tb.Button(confirmation_screen, text="Yes", bootstyle="success",
                  command=lambda: [self.reset_roles_contestants(), confirmation_screen.destroy()]).pack(pady=10)
        tb.Button(confirmation_screen, text="No", bootstyle="danger", command=confirmation_screen.destroy).pack(pady=5)

    def open_admin_screen(self):
        """ Open admin panel for adding roles & contestants. """
        admin_screen = tk.Toplevel(self.root)
        admin_screen.title("Admin - Manage Roles & Contestants")
        admin_screen.geometry("420x240")

        tb.Label(admin_screen, text="Role:", font=("Arial", 12)).pack(pady=5)
        self.entry_role = tb.Entry(admin_screen, font=("Arial", 12))
        self.entry_role.pack()
        self.entry_role.bind("<Return>", lambda e: self.entry_contestant.focus_set())

        tb.Label(admin_screen, text="Contestant:", font=("Arial", 12)).pack(pady=5)
        self.entry_contestant = tb.Entry(admin_screen, font=("Arial", 12))
        self.entry_contestant.pack()
        self.entry_contestant.bind("<Return>", self.add_role_contestant)

        tb.Button(admin_screen, text="Add Contestant", bootstyle="success", command=self.add_role_contestant).pack(
            pady=10)
        tb.Button(admin_screen, text="Reset All", bootstyle="danger", command=self.open_confirmation_screen).pack(
            pady=5)

    def open_voting_screen(self):
        """ Open the voting screen with scrollable, modern-grouped layout and horizontal radio buttons. """
        self.voting_screen = tk.Toplevel(self.root)
        self.voting_screen.title("Voting")
        self.voting_screen.attributes("-fullscreen", True)

        self.selected_votes = {}

        # Scrollable canvas setup
        canvas = tk.Canvas(self.voting_screen, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.voting_screen, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas, padding=30)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title
        tb.Label(
            scrollable_frame,
            text="Cast Your Vote",
            font=("Arial", 32, "bold"),
            foreground="black"
        ).pack(pady=(0, 20))

        # Custom style for radio buttons
        rb_style = "Voting.TRadiobutton"
        self.style.configure(rb_style, font=("Arial", 16), foreground="black")

        # Display each role inside a modern translucent box
        for i, role in enumerate(self.df_roles['Role'].unique()):
            box = tb.Frame(
                scrollable_frame,
                padding=20,
                bootstyle="light" if i % 2 == 0 else "secondary",  # Alternate color themes
                relief="ridge"
            )
            box.pack(fill="x", pady=15, padx=10)

            tb.Label(box, text=role, font=("Arial", 22, "bold"), foreground="black").pack(anchor="w", pady=(0, 10))

            # Container for horizontal layout
            row_frame = tb.Frame(box)
            row_frame.pack(fill="x")

            contestants = self.df_roles[self.df_roles['Role'].str.lower() == role.lower()]['Contestant'].tolist()
            var = tk.StringVar(value="NOTA")
            self.selected_votes[role] = var

            for contestant in contestants:
                card = tb.Frame(row_frame, padding=(10, 5), bootstyle="info", relief="groove")
                card.pack(side="left", padx=10)

                tb.Radiobutton(
                    card,
                    text=contestant,
                    variable=var,
                    value=contestant,
                    style=rb_style
                ).pack()

        # Submit Button
        tb.Button(
            scrollable_frame,
            text="Submit Votes",
            bootstyle="success",
            command=self.submit_votes_radio
        ).pack(pady=30)

        # Exit Button
        tb.Button(
            scrollable_frame,
            text="Exit Fullscreen",
            bootstyle="danger-outline",
            command=self.voting_screen.destroy
        ).pack(pady=(0, 20))

    def submit_votes_radio(self):
        """ Collect radio button votes and save them. """
        for role, var in self.selected_votes.items():
            selected = var.get().strip()
            self.df_roles.loc[
                (self.df_roles['Role'].str.lower() == role.lower()) &
                (self.df_roles['Contestant'] == selected), 'Votes'
            ] += 1

        self.save_data()
        messagebox.showinfo("Success", "Your votes have been submitted.")
        self.voting_screen.destroy()

    def open_home_page(self):
        """ Open the home screen. """
        home_screen = tb.Frame(self.root)
        home_screen.pack(padx=50, pady=80, fill="both", expand=True)

        tb.Label(home_screen, text="Welcome to the Voting App", font=("Arial", 14, "bold")).pack(pady=10)
        tb.Button(home_screen, text="Start Voting", bootstyle="primary", command=self.open_voting_screen).pack(pady=20)

    def create_menu(self):
        """ Create admin menu. """
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        admin_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Admin", menu=admin_menu)
        admin_menu.add_command(label="Manage Candidates", command=self.open_admin_screen)
        admin_menu.add_command(label="View Results", command=self.open_results_screen)


if __name__ == "__main__":
    root = tb.Window(themename="morph")
    app = VotingApp(root)
    root.mainloop()
