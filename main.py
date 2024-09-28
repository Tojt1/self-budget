import tkinter as tk
import psycopg2
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt


connection = psycopg2.connect('dbname=budzet user=postgres password=2910')
cursor = connection.cursor()


cursor.execute("CREATE TABLE IF NOT EXISTS login (user_id SERIAL PRIMARY KEY,"
               " email VARCHAR(100),"
               " password VARCHAR(100))")

cursor.execute('CREATE TABLE IF NOT EXISTS budget '
               '(id SERIAL PRIMARY KEY,'
               ' ammount NUMERIC,'
               ' category VARCHAR(50),'
               ' transactions VARCHAR(10) DEFAULT \'expense\' CHECK (transactions IN (\'income\', \'expense\')),'
               ' user_id INTEGER REFERENCES login(user_id)'
               ')')


class Aplication:
    def __init__(self, window):
        self.window = window

        self.start_label = tk.Label(text='Logowanie')
        self.start_label.grid(row=0, column=0, padx=10)

        self.email_label = tk.Label(text="email:")
        self.email_label.grid(row=2, column=0, padx=10)

        self.email_entry = tk.Entry()
        self.email_entry.grid(row=3, column=0, padx=10)

        self.password_label = tk.Label(text="password:")
        self.password_label.grid(row=4, column=0, padx=10)

        self.password_entry = tk.Entry()
        self.password_entry.grid(row=5, column=0, padx=10)

        self.button = tk.Button(self.window, text='wprowadz', command=self.check_button)
        self.button.grid(row=6, column=0, padx=10)

        self.sign_button = tk.Button(self.window, text='Sign up', command=self.sign_up)
        self.sign_button.grid(row=7, column=0, padx=10)

        self.value = tk.StringVar()

    def sign_up(self):
        def data_sign_pre(windows):
            user_email = email_entry.get()
            user_password = password_entry.get()
            if len(user_password) >= 8 and "@" in user_email:
                self.data_sign(user_email, user_password, windows)
            else:
                messagebox.showinfo("Błąd", "Nie udało się utworzyć konta")

        sign_window = tk.Tk()
        sign_window.title("Sign up")

        email_label = tk.Label(sign_window, text='wprowadx swoj email')
        email_label.pack(padx=10)

        email_entry = tk.Entry(sign_window)
        email_entry.pack(padx=10)

        password_label = tk.Label(sign_window, text='Wprowadz swoje haslo')
        password_label.pack(padx=10)

        password_entry = tk.Entry(sign_window)
        password_entry.pack(padx=10)

        button = tk.Button(sign_window, text='Zapisz', command=lambda: data_sign_pre(sign_window))
        button.pack(padx=10)

        sign_window.mainloop()


    def data_sign(self, email, password, windows):
        cursor.execute("SELECT * FROM login WHERE email = %s", (email, ))
        login = cursor.fetchone()
        if login is None:
            cursor.execute("INSERT INTO login (email, password) VALUES(%s, %s)", (email, password))
            messagebox.showinfo("Information", 'Pomyslnie utworzono konto')
            windows.destroy()
        else:
            messagebox.showinfo("Information", 'Takie konto już istnieje')
            windows.destroy()

    def check_button(self):
        self.email = self.email_entry.get()
        self.password = self.password_entry.get()
        cursor.execute("SELECT * FROM login WHERE email = %s AND password = %s", (self.email, self.password))
        login = cursor.fetchone()
        if login is None:
            new_label = tk.Label(self.window, text='niepoprawny email lub haslo', fg='red')
            new_label.grid(row=1, column=0, padx=10)
            window.update()
        else:
            self.check_id()


    def check_id(self):
        self.window.destroy()
        cursor.execute("SELECT * FROM login WHERE email = %s AND password = %s ", (self.email, self.password))
        user_id_row = cursor.fetchone()
        if user_id_row:
            self.user_id = user_id_row[0]
        self.main_window()


    def main_window(self):
        self.new_window = tk.Tk()
        self.new_window.title("Budget")

        label = tk.Label(self.new_window, text='BUDGET')
        label.grid(row=0, column=1)

        add_button = tk.Button(self.new_window, text="Dodaj nowe", command=self.add_new)
        add_button.grid(row=0, column=2)

        stat_button = tk.Button(self.new_window, text="Pokaż statystyki", command=self.show_statistic)
        stat_button.grid(row=0, column=3)

        ammount_label = tk.Label(self.new_window, text='amoount')
        ammount_label.grid(row=1, column=0)
        self.amount_listbox = tk.Listbox(self.new_window)
        self.amount_listbox.grid(row=2, column=0)

        category_label = tk.Label(self.new_window, text='category')
        category_label.grid(row=1, column=1)
        self.category_listbox = tk.Listbox(self.new_window)
        self.category_listbox.grid(row=2, column=1)

        transtaction_label = tk.Label(self.new_window, text='transactions')
        transtaction_label.grid(row=1, column=2)
        self.transaction_listbox = tk.Listbox(self.new_window)
        self.transaction_listbox.grid(row=2, column=2)

        self.fetch_listbox()
        self.new_window.mainloop()

    def show_statistic(self):
        expense_sum = 0
        income_sum = 0
        cursor.execute("SELECT ammount, transactions FROM budget WHERE user_id = %s", (self.user_id, ))
        data = cursor.fetchall()
        print(data)
        for amount, transactions in data:
            if transactions == 'expense':
                expense_sum += amount
            elif transactions == 'income':
                income_sum += amount
            else:
                print("Cos nie dziala")
        print("expense suma ", expense_sum)
        print('income suma ', income_sum)
        transakcje = [income_sum, expense_sum]
        category = ['income', 'expense']

        # make data:
        positions = range(len(transakcje))
        plt.bar(positions,transakcje)
        plt.xticks(positions, category)

        plt.show()

    def fetch_listbox(self):
        cursor.execute("SELECT ammount, category, transactions FROM budget WHERE user_id = %s",(self.user_id, ))
        rows = cursor.fetchall()
        for row in rows:
            self.amount_listbox.insert(tk.END, row[0])
            self.category_listbox.insert(tk.END, row[1])
            self.transaction_listbox.insert(tk.END, row[2])

    def add_new(self):
        def add_to_data_pre():
            ammount = amount_entry.get()
            category = category_entry.get()
            transactions = combox.get()
            self.add_to_data(ammount, category, transactions, root)

        root = tk.Tk()
        root.title("Dodaj nowe")

        label = tk.Label(root, text='Dodawanie')
        label.grid(row=0, column=1, pady=2)

        ammount_label = tk.Label(root, text='ammount')
        ammount_label.grid(row=1, column=0, padx=2)

        amount_entry = tk.Entry(root)
        amount_entry.grid(row=2, column=0, padx=2)

        category_label = tk.Label(root, text='category')
        category_label.grid(row=1, column=1, padx=2)

        category_entry = tk.Entry(root)
        category_entry.grid(row=2, column=1, padx=2)

        transaction_label = tk.Label(root, text='transactions')
        transaction_label.grid(row=1, column=2, padx=2)

        combox = ttk.Combobox(root, textvariable=self.value)
        combox.grid(row=2, column=2, padx=2)
        combox['values'] = ['expense', 'income']
        combox.current(0)

        przycisk = tk.Button(root, text="Dodaj", command=add_to_data_pre)
        przycisk.grid(row=3, column=1, padx=5)

        root.mainloop()

    def listbox_reflesh(self):
        self.amount_listbox.delete(0, tk.END)
        self.category_listbox.delete(0, tk.END)
        self.transaction_listbox.delete(0, tk.END)

        cursor.execute("SELECT ammount, category, transactions FROM budget " )
        rows = cursor.fetchall()
        for row in rows:
            self.amount_listbox.insert(tk.END, row[0])
            self.category_listbox.insert(tk.END, row[1])
            self.transaction_listbox.insert(tk.END, row[2])


    def add_to_data(self, ammount, category, transactions, root):
        cursor.execute("SELECT * FROM login WHERE email = %s AND password = %s ", (self.email, self.password))
        user_id_row = cursor.fetchone()
        if user_id_row:
            user_id = user_id_row[0]
        cursor.execute("INSERT INTO budget(ammount, category, transactions, user_id) VALUES(%s, %s, %s, %s)",
                       (ammount, category, transactions, user_id))
        messagebox.showinfo('Pomyslnie', 'pomyslnie dodano nowe dane')
        self.new_window.update()
        root.destroy()
        self.listbox_reflesh()


if __name__ == '__main__':
    window = tk.Tk()
    window.title('Budżet osobisty')
    Aplication(window)
    window.mainloop()

connection.commit()
cursor.close()
connection.close()
