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
    votes_to_add = []

    for idx, role in enumerate(df_roles['Role'].unique()):
        contestant = comboboxes[idx].get().strip()
        if contestant:
            votes_to_add.append((role.lower(), contestant))  # Store the valid vote
        else:
            valid_vote = False
            break

    if valid_vote:
        for role, contestant in votes_to_add:
            df_roles.loc[
                (df_roles['Role'].str.lower() == role) & (df_roles['Contestant'] == contestant), 'Votes'] += 1

        with pd.ExcelWriter('votes.xlsx') as writer:
            df_roles.to_excel(writer, sheet_name='Roles', index=False)

        messagebox.showinfo("Success", "Your votes have been submitted.")
        voting_screen.destroy()
    else:
        messagebox.showerror("Error", "You must vote for a contestant in every role.")


# Function to apply color theme to the UI
def apply_color_theme(bg_color, fg_color, button_color, combobox_color):
    root.configure(bg=bg_color)

    # Update the home screen if it exists
    if 'home_screen' in globals():
        home_screen.configure(bg=bg_color)
        start_button.configure(bg=button_color, fg=fg_color)

    # Update the admin screen if it exists
    if 'admin_screen' in globals():
        admin_screen.configure(bg=bg_color)
        entry_role.configure(bg=combobox_color, fg=fg_color)
        entry_contestant.configure(bg=combobox_color, fg=fg_color)
        add_button.configure(bg=button_color, fg=fg_color)
        reset_button.configure(bg=button_color, fg=fg_color)

    # Update the voting screen if it exists
    if 'voting_screen' in globals():
        voting_screen.configure(bg=bg_color)
        for combobox in comboboxes:
            combobox.configure(bg=combobox_color, fg=fg_color)
        vote_button.configure(bg=button_color, fg=fg_color)

    # Update the menu
    menu_bar.configure(bg=bg_color, fg=fg_color)
    admin_menu.configure(bg=bg_color, fg=fg_color)

    # Update labels and other widgets dynamically
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
            widget.configure(bg=bg_color, fg=fg_color)


# Admin screen for adding candidates
def open_admin_screen():
    global admin_screen, entry_role, entry_contestant, add_button, reset_button
    admin_screen = tk.Toplevel(root)
    admin_screen.title("Admin - Manage Roles & Contestants")

    tk.Label(admin_screen, text="Role:").grid(row=0, column=0, padx=5, pady=5)
    entry_role = tk.Entry(admin_screen)
    entry_role.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(admin_screen, text="Contestant:").grid(row=1, column=0, padx=5, pady=5)
    entry_contestant = tk.Entry(admin_screen)
    entry_contestant.grid(row=1, column=1, padx=5, pady=5)

    add_button = tk.Button(admin_screen, text="Add Contestant", command=add_role_contestant)
    add_button.grid(row=2, column=0, pady=10)

    reset_button = tk.Button(admin_screen, text="Reset All", command=reset_roles_contestants)
    reset_button.grid(row=2, column=1, pady=10)

    # Apply the current theme to the new admin screen
    apply_color_theme(bg_color='#2D9C56', fg_color='#FF7F00', button_color='#FFFFFF', combobox_color='#A3D99A')


global vote_button, voting_screen, comboboxes


# Voting screen
def open_voting_screen():
    voting_screen = tk.Toplevel(root)
    voting_screen.title("Voting")

    comboboxes = []
    roles = df_roles['Role'].unique()

    for idx, role in enumerate(roles):
        tk.Label(voting_screen, text=f"{role.capitalize()}:").grid(row=idx, column=0, padx=5, pady=5)
        contestants = df_roles[df_roles['Role'].str.lower() == role.lower()]['Contestant'].tolist()
        combobox = ttk.Combobox(voting_screen, values=contestants)
        combobox.grid(row=idx, column=1, padx=5, pady=5)
        comboboxes.append(combobox)

    tk.Button(voting_screen, text="Submit Votes", command=submit_votes)
    vote_button.grid(row=len(roles), column=0, columnspan=2, pady=10)
    vote_button.configure(bg_color='#000000', fg_color='#FFFFFF')

    # Apply the current theme to the new voting screen
    apply_color_theme(bg_color='#2D9C56', fg_color='#FF7F00', button_color='#FFFFFF', combobox_color='#A3D99A')


# Main window
root = tk.Tk()
root.title("Voting App")

global menu_bar, admin_menu
menu_bar = Menu(root, bg='#2D9C56', fg='#FF7F00')
admin_menu = Menu(menu_bar, tearoff=0, bg='#2D9C56', fg='#FF7F00')

# Apply color theme
apply_color_theme(
    bg_color='#2D9C56',
    fg_color='#000000',
    button_color='#000000',
    combobox_color='#A3D99A'
)


# Home Page
def open_home_page():
    global home_screen, start_button
    home_screen = tk.Frame(root, bg='#2D9C56')
    home_screen.pack(padx=10, pady=10, fill="x")

    start_button = tk.Button(home_screen, text="Start Voting", command=open_voting_screen, bg='#FFFFFF', fg='#FF7F00')
    start_button.pack(pady=20)


open_home_page()

# Admin Menu
root.config(menu=menu_bar)
menu_bar.add_cascade(label="Admin", menu=admin_menu)
admin_menu.add_command(label="Manage Candidates", command=open_admin_screen)

# Start the GUI event loop
root.mainloop()
