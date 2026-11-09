from tkinter import *
from tkinter import ttk, messagebox
import pymysql as m


# -------------------------------------------------
# Main Window
# -------------------------------------------------

w = Tk()
w.title("Registration Management System")
w.geometry("900x650")
w.configure(bg="red")


# -------------------------------------------------
# Database Connection
# -------------------------------------------------

def connect_db():
    return m.connect(
        host="localhost",
        user="root",
        password="1522",
        database="register"
    )


# -------------------------------------------------
# Display all records
# -------------------------------------------------

def display_data():

    # Clear existing rows
    for row in table.get_children():
        table.delete(row)

    try:
        db = connect_db()
        cur = db.cursor()

        cur.execute("SELECT * FROM re")

        rows = cur.fetchall()

        for row in rows:
            table.insert("", END, values=row)

        db.close()

    except Exception as ex:
        messagebox.showerror("Database Error", str(ex))


# -------------------------------------------------
# Insert
# -------------------------------------------------

def insert_data():

    name = e.get()
    email = e1.get()
    ph = e2.get()
    passw = e3.get()

    if name == "" or email == "" or ph == "" or passw == "":
        messagebox.showerror("Error", "Fill all the details")
        return

    try:
        db = connect_db()
        cur = db.cursor()

        query = """
        INSERT INTO re (name, email, ph, passw)
        VALUES (%s, %s, %s, %s)
        """

        values = (name, email, ph, passw)

        cur.execute(query, values)
        db.commit()

        db.close()

        messagebox.showinfo("Success", "Record inserted successfully")

        clear_data()
        display_data()

    except Exception as ex:
        messagebox.showerror("Database Error", str(ex))


# -------------------------------------------------
# Select row from table
# -------------------------------------------------

def select_row(event):

    selected = table.focus()

    if selected == "":
        return

    values = table.item(selected, "values")

    # Clear entry boxes
    e.delete(0, END)
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)

    # Put selected data into Entry boxes
    e.insert(0, values[0])
    e1.insert(0, values[1])
    e2.insert(0, values[2])
    e3.insert(0, values[3])


# -------------------------------------------------
# Update
# -------------------------------------------------

def update_data():

    selected = table.focus()

    if selected == "":
        messagebox.showerror("Error", "Select a record from the table")
        return

    name = e.get()
    email = e1.get()
    ph = e2.get()
    passw = e3.get()

    if name == "" or email == "" or ph == "" or passw == "":
        messagebox.showerror("Error", "Fill all the details")
        return

    old_values = table.item(selected, "values")

    old_name = old_values[0]

    try:
        db = connect_db()
        cur = db.cursor()

        query = """
        UPDATE re
        SET name=%s, email=%s, ph=%s, passw=%s
        WHERE name=%s
        """

        values = (name, email, ph, passw, old_name)

        cur.execute(query, values)
        db.commit()

        db.close()

        messagebox.showinfo("Success", "Record updated successfully")

        clear_data()
        display_data()

    except Exception as ex:
        messagebox.showerror("Database Error", str(ex))


# -------------------------------------------------
# Delete
# -------------------------------------------------

def delete_data():

    selected = table.focus()

    if selected == "":
        messagebox.showerror("Error", "Select a record from the table")
        return

    values = table.item(selected, "values")

    name = values[0]

    answer = messagebox.askyesno(
        "Confirm Delete",
        "Do you want to delete this record?"
    )

    if answer:

        try:
            db = connect_db()
            cur = db.cursor()

            query = "DELETE FROM re WHERE name=%s"

            cur.execute(query, (name,))

            db.commit()
            db.close()

            messagebox.showinfo(
                "Success",
                "Record deleted successfully"
            )

            clear_data()
            display_data()

        except Exception as ex:
            messagebox.showerror("Database Error", str(ex))


# -------------------------------------------------
# Clear
# -------------------------------------------------

def clear_data():

    e.delete(0, END)
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)

    table.selection_remove(table.selection())


# -------------------------------------------------
# Heading
# -------------------------------------------------

heading = Label(
    w,
    text="REGISTRATION MANAGEMENT SYSTEM",
    bg="skyblue",
    fg="yellow",
    font=("Times New Roman", 24)
)

heading.place(x=190, y=20)


# -------------------------------------------------
# Labels
# -------------------------------------------------

Label(
    w,
    text="Name",
    font=("Times New Roman", 18)
).place(x=80, y=90)

Label(
    w,
    text="Email",
    font=("Times New Roman", 18)
).place(x=80, y=140)

Label(
    w,
    text="Phone",
    font=("Times New Roman", 18)
).place(x=80, y=190)

Label(
    w,
    text="Password",
    font=("Times New Roman", 18)
).place(x=80, y=240)


# -------------------------------------------------
# Entry boxes
# -------------------------------------------------

e = Entry(
    w,
    width=30,
    font=("Times New Roman", 18)
)

e.place(x=220, y=90)


e1 = Entry(
    w,
    width=30,
    font=("Times New Roman", 18)
)

e1.place(x=220, y=140)


e2 = Entry(
    w,
    width=30,
    font=("Times New Roman", 18)
)

e2.place(x=220, y=190)


e3 = Entry(
    w,
    width=30,
    font=("Times New Roman", 18),
    show="*"
)

e3.place(x=220, y=240)


# -------------------------------------------------
# Buttons
# -------------------------------------------------

Button(
    w,
    text="INSERT",
    command=insert_data,
    font=("Times New Roman", 15),
    bg="lightgreen",
    width=10
).place(x=100, y=290)


Button(
    w,
    text="UPDATE",
    command=update_data,
    font=("Times New Roman", 15),
    bg="skyblue",
    width=10
).place(x=250, y=290)


Button(
    w,
    text="DELETE",
    command=delete_data,
    font=("Times New Roman", 15),
    bg="orange",
    width=10
).place(x=400, y=290)


Button(
    w,
    text="CLEAR",
    command=clear_data,
    font=("Times New Roman", 15),
    bg="white",
    width=10
).place(x=550, y=290)


# -------------------------------------------------
# Table
# -------------------------------------------------

table = ttk.Treeview(
    w,
    columns=("name", "email", "ph", "passw"),
    show="headings"
)


# Headings

table.heading("name", text="Name")
table.heading("email", text="Email")
table.heading("ph", text="Phone")
table.heading("passw", text="Password")


# Column sizes

table.column("name", width=180)
table.column("email", width=250)
table.column("ph", width=150)
table.column("passw", width=150)


table.place(
    x=50,
    y=350,
    width=800,
    height=250
)


# -------------------------------------------------
# When user clicks a row
# -------------------------------------------------

table.bind(
    "<ButtonRelease-1>",
    select_row
)


# -------------------------------------------------
# Initially load database records
# -------------------------------------------------

display_data()


# -------------------------------------------------
# Start
# -------------------------------------------------

w.mainloop()
