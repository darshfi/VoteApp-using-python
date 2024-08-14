import tkinter as tk
from tkinter import ttk, messagebox, Menu
import pandas as pd
import os

# Initialize or load the Excel file
if not os.path.exists('votes.xlsx'):
    df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
    with pd.ExcelWriter('votes.xlsx') as writer:
        df_roles.to_excel(writer, sheet_name='Roles', index=False)
else:
    with pd.ExcelFile('votes.xlsx') as reader:
        df_roles = pd.read_excel(reader, sheet_name='Roles')


# Function to add a new role or contestant
def add_role_contestant():
    role = entry_role.get().strip().lower()  # Normalize case and strip whitespace
    contestant = entry_contestant.get().strip()

    if role and contestant:
        global df_roles
        if not ((df_roles['Role'].str.lower() == role) & (df_roles['Contestant'] == contestant)).any():
            new_entry = pd.DataFrame([[role.capitalize(), contestant, 0]], columns=["Role", "Contestant", "Votes"])
            df_roles = pd.concat([df_roles, new_entry], ignore_index=True)
            with pd.ExcelWriter('votes.xlsx') as writer:
                df_roles.to_excel(writer, sheet_name='Roles', index=False)

            messagebox.showinfo("Success", f"Contestant '{contestant}' added to role '{role.capitalize()}'.")
            entry_role.delete(0, tk.END)
            entry_contestant.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "This contestant already exists in this role.")
    else:
        messagebox.showerror("Error", "Please fill in both Role and Contestant fields.")


# Function to reset roles and contestants
def reset_roles_contestants():
    global df_roles
    df_roles = pd.DataFrame(columns=["Role", "Contestant", "Votes"])
    with pd.ExcelWriter('votes.xlsx') as writer:
        df_roles.to_excel(writer, sheet_name='Roles', index=False)
    messagebox.showinfo("Reset", "All roles and contestants have been reset.")


# Function to submit votes
def submit_votes():
    global df_roles
    valid_vote = True
    for idx, role in enumerate(df_roles['Role'].unique()):
        contestant = comboboxes[idx].get().strip()
        if contestant:
            df_roles.loc[
                (df_roles['Role'].str.lower() == role.lower()) & (df_roles['Contestant'] == contestant), 'Votes'] += 1
        else:
            valid_vote = False
            break

    if valid_vote:
        with pd.ExcelWriter('votes.xlsx') as writer:
            df_roles.to_excel(writer, sheet_name='Roles', index=False)
        messagebox.showinfo("Success", "Your votes have been submitted.")
        voting_screen.destroy()
    else:
        messagebox.showerror("Error", "You must vote for at least one contestant in each role.")


# Admin screen for adding candidates
def open_admin_screen():
    admin_screen = tk.Toplevel(root)
    admin_screen.title("Admin - Manage Roles & Contestants")

    tk.Label(admin_screen, text="Role:").grid(row=0, column=0, padx=5, pady=5)
    global entry_role
    entry_role = tk.Entry(admin_screen)
    entry_role.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(admin_screen, text="Contestant:").grid(row=1, column=0, padx=5, pady=5)
    global entry_contestant
    entry_contestant = tk.Entry(admin_screen)
    entry_contestant.grid(row=1, column=1, padx=5, pady=5)

    add_button = tk.Button(admin_screen, text="Add Contestant", command=add_role_contestant)
    add_button.grid(row=2, column=0, pady=10)

    reset_button = tk.Button(admin_screen, text="Reset All", command=reset_roles_contestants)
    reset_button.grid(row=2, column=1, pady=10)


# Voting screen
def open_voting_screen():
    global voting_screen
    voting_screen = tk.Toplevel(root)
    voting_screen.title("Voting")

    global comboboxes
    comboboxes = []
    roles = df_roles['Role'].unique()

    for idx, role in enumerate(roles):
        tk.Label(voting_screen, text=f"{role.capitalize()}:").grid(row=idx, column=0, padx=5, pady=5)
        contestants = df_roles[df_roles['Role'].str.lower() == role.lower()]['Contestant'].tolist()
        combobox = ttk.Combobox(voting_screen, values=contestants)
        combobox.grid(row=idx, column=1, padx=5, pady=5)
        comboboxes.append(combobox)

    vote_button = tk.Button(voting_screen, text="Submit Votes", command=submit_votes)
    vote_button.grid(row=len(roles), column=0, columnspan=2, pady=10)


# Main window
root = tk.Tk()
root.title("Voting App")


# Home Page
def open_home_page():
    home_screen = tk.Frame(root)
    home_screen.pack(padx=100, pady=100, fill="x")

    start_button = tk.Button(home_screen, text="Start Voting", command=open_voting_screen)
    start_button.pack(pady=20)


open_home_page()

# Admin Menu
menu_bar = Menu(root)
root.config(menu=menu_bar)
admin_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Admin", menu=admin_menu)
admin_menu.add_command(label="Manage Candidates", command=open_admin_screen)

# Start the GUI event loop
root.mainloop()
