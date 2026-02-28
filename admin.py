import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
connection = sqlite3.connect('todolist.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS todolist (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
)
''')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES todolist(user_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
''')
connection.commit()

root = Tk()
root.title('admin - panel')
root.geometry('1000x1000')
frame = Frame(root)
frame.pack(pady=20)

def adduser():
    add = Toplevel(root)
    add.title('Добавить пользователя')
    add.geometry('500x300')
    add.grab_set()
    add.transient(root)
    frameadd = Frame(add)
    ad = ttk.Label(frameadd, text="Ведите логин:")
    ad.pack(pady=20)
    addlog = ttk.Entry(frameadd, width=50)
    addlog.pack(pady=20)
    def insertuser():
        user = addlog.get()
        cursor.execute("INSERT INTO todolist(username) VALUES (?)", (user,))
        connection.commit()
        messagebox.showinfo("Удача!", "Пользователь успешно добавлен!")
        listbox.insert(END, user)
        add.destroy()
    addbtn = ttk.Button(frameadd,text='Добавить',command=insertuser)
    addbtn.pack(pady=20)

    frameadd.pack(pady=20)

def loaduser():
    cursor.execute("SELECT username FROM todolist")
    users = cursor.fetchall()
    for user in users:
        listbox.insert(END, user)

listbox = Listbox(frame, selectmode=SINGLE, width=80, height=50)

def deleteuser():
    user = listbox.curselection()
    if user:
        selected = user[0]
        service = listbox.get(selected)
        username = service[0]
        listbox.delete(0, END)
        cursor.execute("DELETE FROM todolist WHERE username = ?", (username,))
        connection.commit()
        loaduser()

def addtask():
    user_selection = listbox.curselection()
    if user_selection:
        selected_index = user_selection[0]
        user_data = listbox.get(selected_index)
        if isinstance(user_data, tuple):
            username = user_data[0]
        else:
            username = user_data

        addt = Toplevel(root)
        addt.geometry('500x400')
        addt.title(f"Задача для {username}")
        addt.grab_set()
        addt.transient(root)

        frameaddt = Frame(addt)

        namet = Label(frameaddt, text='Название задачи:')
        namet.pack(pady=10)
        nametask = ttk.Entry(frameaddt, width=20)
        nametask.pack(pady=20)

        datet = Label(frameaddt, text='Время выполнения:')
        datet.pack(pady=10)
        datetask = ttk.Entry(frameaddt, width=20)
        datetask.pack(pady=20)

        def add_task_to_db():
            task_title = nametask.get()
            task_date = datetask.get()

            if task_title and task_date:
                cursor.execute("SELECT user_id FROM todolist WHERE username = ?", (username,))
                user_id = cursor.fetchone()[0]
                cursor.execute('''
                               INSERT INTO tasks (user_id, title, date)
                               VALUES (?, ?, ?)
                               ''', (user_id, task_title, task_date))
                connection.commit()

                messagebox.showinfo("Успех", "Задача успешно добавлена!")
                addt.destroy()
            else:
                messagebox.showwarning("Ошибка", "Заполните все поля!")

        add_btn = ttk.Button(frameaddt, text='Добавить', command=add_task_to_db)
        add_btn.pack(pady=20)

        frameaddt.pack(pady=20)


def checkuser():
    main_selection = listbox.curselection()

    if not main_selection:
        messagebox.showwarning("Ошибка", "Выберите пользователя!")
        return

    selected_index = main_selection[0]
    user_data = listbox.get(selected_index)

    if isinstance(user_data, tuple):
        username = user_data[0]
    else:
        username = user_data

    cursor.execute("SELECT user_id FROM todolist WHERE username = ?", (username,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Ошибка", "Пользователь не найден!")
        return

    user_id = result[0]

    check = Toplevel(root)
    check.geometry('600x500')
    check.title(f'Задачи пользователя: {username}')
    check.grab_set()
    check.transient(root)

    main_frame = Frame(check)
    main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    list_frame = Frame(main_frame)
    list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

    tasks_listbox = Listbox(list_frame, selectmode=SINGLE)
    tasks_listbox.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=tasks_listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    tasks_listbox.config(yscrollcommand=scrollbar.set)

    button_frame = Frame(main_frame)
    button_frame.pack(fill=X, pady=5)

    cursor.execute("SELECT title, date, status FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()

    if tasks:
        for task in tasks:
            if task[2] == 'выполнено':
                task_str = f"{task[0]} | {task[1]} | Статус: Выполнено"
                tasks_listbox.insert(END, task_str)
                tasks_listbox.itemconfig(END, {'bg': 'lightgreen', 'fg': 'black'})
            else:
                task_str = f"{task[0]} | {task[1]} | Статус: Не выполнено"
                tasks_listbox.insert(END, task_str)
    else:
        tasks_listbox.insert(END, "У пользователя нет задач")
    def delete_task():
        selected = tasks_listbox.curselection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу!")
            return

        task_index = selected[0]
        selected_task = tasks[task_index]
        task_title = selected_task[0]

        if messagebox.askyesno("Подтверждение", f"Удалить задачу '{task_title}'?"):
            cursor.execute('''
                           DELETE
                           FROM tasks
                           WHERE user_id = ?
                             AND title = ?
                             AND date = ?
                           ''', (user_id, task_title, selected_task[1]))
            connection.commit()

            messagebox.showinfo("Успех", "Задача удалена!")
            check.destroy()
            checkuser()


    delete_btn = ttk.Button(button_frame, text="Удалить задачу", command=delete_task)
    delete_btn.pack(side=LEFT, padx=5)

checktasks = ttk.Button(frame, text='Задачи', command=checkuser)
checktasks.pack(pady=20)
addtask = ttk.Button(frame, text='Создать задачу', command=addtask)
addtask.pack(pady=20)
addu = ttk.Button(frame,text='Добавить пользователя', command=adduser)
delu = ttk.Button(frame,text='Удалить пользователя', command=deleteuser)
delu.pack(pady=20)
addu.pack(pady=20)
listbox.pack(pady=20)
loaduser()
root.mainloop()
