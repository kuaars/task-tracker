from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from plyer import notification
import sqlite3

root = Tk()
root.title("список задач")
root.geometry("700x700")

connection = sqlite3.connect('todolist.db')
cursor = connection.cursor()


c = 0
tasked = []

current_user_id = None

def adduser():
    global current_user_id

    verificate = Toplevel(root)
    verificate.geometry("400x200")
    verificate.title("Проверка")
    verificate.grab_set()
    verificate.transient(root)

    label = Label(verificate, text='Введите логин')
    label.pack(pady=10)

    username_entry = Entry(verificate, width=30, font=("Arial", 12))
    username_entry.pack(pady=5)

    def user():
        global current_user_id
        username = username_entry.get().strip()

        if username:
            cursor.execute("SELECT user_id FROM todolist WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                current_user_id = existing_user[0]
                verificate.destroy()
                messagebox.showinfo('Успех', f'Добро пожаловать, {username}!')
                load_tasks()
            else:
                messagebox.showerror('Ошибка!','Логин не найден, обратитесь к администратору')
        else:
            messagebox.showinfo('Ошибка', 'Введите username')

    add = ttk.Button(verificate, text='Проверить', command=user)
    add.pack(pady=5)


def load_tasks():
    global current_user_id, tasked, c
    if current_user_id is not None:
        listbox.delete(0, END)
        tasked.clear()
        c = 0

        cursor.execute("SELECT task_id, title, date, status FROM tasks WHERE user_id = ?", (current_user_id,))
        tasks = cursor.fetchall()

        for task_row in tasks:
            c += 1
            task_id, title, date, status = task_row
            tasked.append({
                'task_id': task_id,
                'title': title,
                'date': date
            })

            listbox.insert(END, f"{title} - {date}")


            if status == "выполнено":
                listbox.itemconfig(c - 1, {'bg': 'lightgreen', 'fg': 'black'})


def done_task():
    global current_user_id
    selected_task = listbox.curselection()
    if selected_task:
        task = selected_task[0]
        listbox.itemconfig(task, {'bg': 'lightgreen', 'fg': 'black'})
        cursor.execute("UPDATE tasks SET status = 'выполнено' WHERE task_id = ?", (task,))
        connection.commit()


frame = Frame(root)
frame.pack(pady=20)

done = ttk.Button(frame, text='Выполнено', command=done_task)
done.grid(row=2, column=0, columnspan=1, pady=10)

refresh = ttk.Button(frame, text='Обновить задачи', command=load_tasks)
refresh.grid(row=3, column=0, columnspan=1, pady=10)

listbox = Listbox(
    root,
    width=60,
    height=30,
    font=("Arial", 12),
    selectmode=SINGLE
)
def show_notification():
    notification.notify(
        title='Новая задача',
        message='Былв добавлена новая задача',
        app_name='task traker',
        timeout=5
    )
cnow = 0
listbox.pack(pady=20)


def check():
    global c, current_user_id

    if current_user_id:
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (current_user_id,))
        current_count = cursor.fetchone()[0]

        if current_count > c:
            show_notification()
            load_tasks()

        c = current_count

    root.after(1000, check)

root.after(1000, check)
adduser()
root.mainloop()
connection.close()
