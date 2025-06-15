import tkinter as tk
from tkinter import ttk, messagebox, Menu
import pandas as pd
from pathlib import Path


class VotingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voting App")
        self.file_path = Path("votes.xlsx")
        self.df_roles = self.load_data()
        self.create_menu()
        self.open_home_page()

    def load_data(self):
        """Load data from Excel or create a new file if not found."""
        if not self.file_path.exists():
            df = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
            df.to_excel(self.file_path, sheet_name='Roles', index=False)
        else:
            df = pd.read_excel(self.file_path, sheet_name='Roles')
        return df

    def save_data(self):
        """Save the DataFrame to the Excel file."""
        with pd.ExcelWriter(self.file_path, mode="w") as writer:
            self.df_roles.to_excel(writer, sheet_name='Roles', index=False)

    def add_role_contestant(self, event=None):
        """Add a new role and contestant with default NOTA."""
        role = self.entry_role.get().strip().title()
        contestant = self.entry_contestant.get().strip().title()

        if role:
            existing_roles = self.df_roles['Role'].str.lower().unique()
            if role.lower() not in existing_roles:
                # Add NOTA option if new role
                self.df_roles = pd.concat([
                    self.df_roles,
                    pd.DataFrame([[role, "NOTA", 0]], columns=["Role", "Contestant", "Votes"])
                ], ignore_index=True)

            if contestant and contestant.lower() != "nota":
                existing_combination = self.df_roles[
                    (self.df_roles['Role'].str.lower() == role.lower()) &
                    (self.df_roles['Contestant'].str.lower() == contestant.lower())
                    ]
                if existing_combination.empty:
                    self.df_roles = pd.concat([
                        self.df_roles,
                        pd.DataFrame([[role, contestant, 0]], columns=["Role", "Contestant", "Votes"])
                    ], ignore_index=True)
                    messagebox.showinfo("Success", f"'{contestant}' added to '{role}'.")
                else:
                    messagebox.showerror("Error", "Contestant already exists for this role.")
        else:
            messagebox.showerror("Error", "Role cannot be empty.")

        self.save_data()
        self.entry_role.delete(0, tk.END)
        self.entry_contestant.delete(0, tk.END)
        self.entry_role.focus_set()

    def reset_roles_contestants(self):
        """Reset the entire roles and contestants list."""
        self.df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
        self.save_data()
        messagebox.showinfo("Reset", "All roles and contestants have been reset.")

    def submit_votes(self):
        """Submit votes for selected contestants."""
        for idx, role in enumerate(self.df_roles['Role'].unique()):
            contestant = self.comboboxes[idx].get().strip()
            self.df_roles.loc[
                (self.df_roles['Role'].str.lower() == role.lower()) & (
                            self.df_roles['Contestant'] == contestant), 'Votes'
            ] += 1
        self.save_data()
        messagebox.showinfo("Success", "Your votes have been submitted.")
        self.voting_screen.destroy()

    def open_admin_screen(self):
        """Open the admin panel."""
        admin_screen = tk.Toplevel(self.root)
        admin_screen.title("Admin - Manage Roles & Contestants")

        tk.Label(admin_screen, text="Role:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_role = tk.Entry(admin_screen)
        self.entry_role.grid(row=0, column=1, padx=5, pady=5)
        self.entry_role.bind("<Return>", lambda e: self.entry_contestant.focus_set())  # Move focus to contestant

        tk.Label(admin_screen, text="Contestant:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_contestant = tk.Entry(admin_screen)
        self.entry_contestant.grid(row=1, column=1, padx=5, pady=5)
        self.entry_contestant.bind("<Return>", self.add_role_contestant)  # Auto-add on Enter

        tk.Button(admin_screen, text="Add Contestant", command=self.add_role_contestant).grid(row=2, column=0, pady=10)
        tk.Button(admin_screen, text="Reset All", command=self.reset_roles_contestants).grid(row=2, column=1, pady=10)
        self.entry_role.focus_set()

    def open_voting_screen(self):
        """Open the voting interface."""
        self.voting_screen = tk.Toplevel(self.root)
        self.voting_screen.title("Voting")
        self.comboboxes = []

        for idx, role in enumerate(self.df_roles['Role'].unique()):
            tk.Label(self.voting_screen, text=f"{role}: ").grid(row=idx, column=0, padx=5, pady=5, sticky="w")
            contestants = self.df_roles[self.df_roles['Role'].str.lower() == role.lower()]['Contestant'].tolist()
            combobox = ttk.Combobox(self.voting_screen, values=contestants, state="readonly")
            combobox.grid(row=idx, column=1, padx=5, pady=5)
            combobox.current(0)
            self.comboboxes.append(combobox)

        tk.Button(self.voting_screen, text="Submit Votes", command=self.submit_votes).grid(
            row=len(self.df_roles['Role'].unique()), column=0, columnspan=2, pady=10
        )

    def open_home_page(self):
        """Display the home screen."""
        home_screen = tk.Frame(self.root)
        home_screen.pack(padx=100, pady=200, fill="x")
        tk.Button(home_screen, text="Start Voting", command=self.open_voting_screen).pack(pady=20)

    def create_menu(self):
        """Create an admin menu."""
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        admin_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Admin", menu=admin_menu)
        admin_menu.add_command(label="Manage Candidates", command=self.open_admin_screen)


if __name__ == "__main__":
    root = tk.Tk()
    app = VotingApp(root)
    root.mainloop()
