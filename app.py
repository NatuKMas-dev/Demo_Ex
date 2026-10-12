import os
import random
import tkinter as tk
from tkinter import messagebox, ttk
from models import *

CURRENT_USER = None
ENTRY_LOGIN = None

BG = "#f9f1e5"
FIELD_BG = "#ffffff"
FIELD_FG = "#22262b"

FONT_TITLE = ("Arial", 16, "bold")
FONT_LABEL = ("Arial", 11, "bold")
FONT_BUTTON = ("Arial", 12, "bold")

root = tk.Tk()
root.title("Учебное приложение")
root.geometry("720x640")
root.configure(bg=BG)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True, padx=20, pady=20)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTCHA_DIR = os.path.join(BASE_DIR, "captcha")
CORRECT_ORDER = [1, 2, 3, 4]
PIECE_SIZE = 90

captcha_images = {}
for piece in CORRECT_ORDER:
    path = os.path.join(CAPTCHA_DIR, f"{piece}.png")
    captcha_images[piece] = tk.PhotoImage(file=path).subsample(8)
captcha_empty = tk.PhotoImage(width=PIECE_SIZE, height=PIECE_SIZE)

captcha_host = None
captcha_slots = []
captcha_placed = []
captcha_passed = False


def clear_screen():
    for w in container.winfo_children():
        w.destroy()


def make_title(text):
    return tk.Label(container, text=text, bg=BG, fg=FIELD_FG, font=FONT_TITLE)


def make_label(text):
    return tk.Label(container, text=text, bg=BG, fg=FIELD_FG,
                    font=FONT_LABEL, anchor="w")


def make_entry(password=False):
    entry = tk.Entry(container, font=FONT_BUTTON, bg=FIELD_BG, fg=FIELD_FG,
                     insertbackground=FIELD_FG, relief="solid", borderwidth=1)
    if password:
        entry.configure(show="*")
    return entry


def make_button(text, command, parent=None):
    host = container if parent is None else parent
    return tk.Button(host, text=text, command=command, font=FONT_BUTTON)


def build_captcha():
    global captcha_slots, captcha_placed, captcha_passed
    for w in captcha_host.winfo_children():
        w.destroy()
    captcha_slots = []
    captcha_placed = []
    captcha_passed = False
    text = ("Соберите картинку: кликайте фрагменты по порядку. "
            "Лишний фрагмент уберите кликом по нему.")
    tk.Label(captcha_host, text=text, bg=BG, fg=FIELD_FG, font=FONT_LABEL,
             anchor="w", wraplength=640, justify="left").pack(fill="x")
    board = tk.Frame(captcha_host, bg=BG)
    board.pack(pady=6)
    for i in range(4):
        slot = tk.Button(board, image=captcha_empty, relief="solid", borderwidth=1,
                         cursor="hand2", command=lambda i=i: remove_piece(i))
        slot.grid(row=i // 2, column=i % 2)
        captcha_slots.append(slot)
    order = CORRECT_ORDER[:]
    while order == CORRECT_ORDER:
        random.shuffle(order)
    pieces = tk.Frame(captcha_host, bg=BG)
    pieces.pack(pady=(0, 6))
    for piece in order:
        btn = tk.Button(pieces, image=captcha_images[piece], relief="solid",
                        borderwidth=1, cursor="hand2", command=lambda p=piece: place_piece(p))
        btn.pack(side="left", padx=3)


def redraw_captcha():
    for i in range(4):
        img = captcha_images[captcha_placed[i]] if i < len(captcha_placed) else captcha_empty
        captcha_slots[i].configure(image=img)


def place_piece(piece):
    if captcha_passed or piece in captcha_placed:
        return
    captcha_placed.append(piece)
    redraw_captcha()
    if len(captcha_placed) == 4:
        check_captcha()


def remove_piece(index):
    if captcha_passed or index >= len(captcha_placed):
        return
    captcha_placed.pop(index)
    redraw_captcha()


def check_captcha():
    global captcha_passed
    if captcha_placed == CORRECT_ORDER:
        captcha_passed = True
        messagebox.showinfo("Капча",
                            "Картинка собрана верно. Теперь можно нажимать «Войти».")
        return
    if register_fail(ENTRY_LOGIN.get().strip()):
        messagebox.showerror("Блокировка",
                             "Вы заблокированы. Обратитесь к администратору")
    else:
        messagebox.showerror("Капча", "Картинка собрана неверно. Попробуйте ещё раз.")
    build_captcha()


def try_login(login, password):
    global CURRENT_USER
    login = login.strip()
    password = password.strip()
    if not login or not password:
        messagebox.showwarning("Внимание", "Заполните логин и пароль.")
        return
    if not captcha_passed:
        messagebox.showwarning("Капча",
                               "Сначала соберите капчу, затем нажимайте «Войти».")
        return
    user = find_user(login, password)
    if user is None:
        if register_fail(login):
            messagebox.showerror("Блокировка",
                                 "Вы заблокированы. Обратитесь к администратору")
        else:
            messagebox.showerror(
                "Ошибка входа",
                "Вы ввели неверный логин или пароль. "
                "Пожалуйста проверьте ещё раз введенные данные")
        return
    if user["locked"]:
        messagebox.showerror("Блокировка",
                             "Вы заблокированы. Обратитесь к администратору")
        return
    reset_attempts(login)
    CURRENT_USER = user
    messagebox.showinfo("Авторизация", "Вы успешно авторизовались")
    if user["role"] == "Администратор":
        open_admin()
    else:
        open_user()


def open_login():
    global ENTRY_LOGIN, captcha_host
    clear_screen()
    make_title("Вход в систему").pack(pady=(0, 10))

    make_label("Логин").pack(fill="x")
    ENTRY_LOGIN = make_entry()
    ENTRY_LOGIN.pack(fill="x", pady=(0, 8))
    make_label("Пароль").pack(fill="x")
    entry_pass = make_entry(password=True)
    entry_pass.pack(fill="x", pady=(0, 4))

    show_var = tk.BooleanVar(value=False)

    def toggle_password():
        entry_pass.configure(show="" if show_var.get() else "*")

    tk.Checkbutton(container, text="Показать пароль", variable=show_var,
                   command=toggle_password,
                   bg=BG, fg=FIELD_FG, activebackground=BG,
                   activeforeground=FIELD_FG, selectcolor=FIELD_BG,
                   font=FONT_LABEL, anchor="w").pack(fill="x", pady=(0, 10))

    captcha_host = tk.Frame(container, bg=BG)
    captcha_host.pack(fill="x", pady=(0, 10))
    build_captcha()

    make_button("Войти",
                lambda: try_login(ENTRY_LOGIN.get(), entry_pass.get())
                ).pack(fill="x", ipady=6)


def open_user():
    clear_screen()
    make_title("Рабочее место пользователя").pack(pady=(0, 10))
    make_label(f"Вы вошли как: {CURRENT_USER['login']}").pack(fill="x", pady=(0, 6))
    make_label(f"Роль: {CURRENT_USER['role']}").pack(fill="x", pady=(0, 20))
    make_button("Выйти", open_login).pack(ipadx=24, ipady=4)


def open_edit_user(login):
    user = user_by_login(login)
    clear_screen()
    make_title("Изменение пользователя").pack(pady=(0, 10))
    make_label(f"Логин: {login}").pack(fill="x", pady=(0, 10))

    make_label("ФИО").pack(fill="x")
    e_name = make_entry()
    e_name.insert(0, user["full_name"])
    e_name.pack(fill="x", pady=(0, 8))

    make_label("Пароль").pack(fill="x")
    e_pass = make_entry()
    e_pass.insert(0, user["password"])
    e_pass.pack(fill="x", pady=(0, 8))

    make_label("Роль").pack(fill="x")
    combo_role = ttk.Combobox(container, values=["Пользователь", "Администратор"],
                              state="readonly", font=FONT_BUTTON)
    combo_role.set(user["role"])
    combo_role.pack(fill="x", pady=(0, 10))

    lock_label = make_label("Заблокирован: да" if user["locked"] else "Заблокирован: нет")
    lock_label.pack(fill="x", pady=(0, 10))

    def do_save():
        name = e_name.get().strip()
        password = e_pass.get().strip()
        if not name or not password:
            messagebox.showwarning("Внимание", "ФИО и пароль не могут быть пустыми.")
            return
        update_user(login, password, combo_role.get(), name)
        messagebox.showinfo("Готово", "Данные пользователя сохранены.")
        open_admin()

    def do_unlock():
        unlock_user(login)
        lock_label.configure(text="Заблокирован: нет")
        messagebox.showinfo("Готово", f"Пользователь {login} разблокирован.")

    def do_delete():
        if login == "admin":
            messagebox.showerror("Ошибка", "Администратора удалять нельзя.")
            return
        if messagebox.askyesno("Удаление", f"Удалить пользователя {login}?"):
            delete_user(login)
            messagebox.showinfo("Готово", "Пользователь удалён.")
            open_admin()

    row = tk.Frame(container, bg=BG)
    row.pack(fill="x")
    make_button("Сохранить", do_save, parent=row).pack(side="left", padx=(0, 6))
    make_button("Разблокировать", do_unlock, parent=row).pack(side="left", padx=(0, 6))
    make_button("Удалить", do_delete, parent=row).pack(side="left", padx=(0, 6))
    make_button("Отмена", open_admin, parent=row).pack(side="right")


def open_admin():
    clear_screen()
    make_title("Панель администратора").pack(pady=(0, 5))
    make_label(f"Вы вошли как: {CURRENT_USER['login']}").pack(fill="x", pady=(0, 10))

    tree = ttk.Treeview(container,
                        columns=("login", "full_name", "role", "locked"),
                        show="headings", height=8)
    tree.heading("login", text="Логин")
    tree.heading("full_name", text="ФИО")
    tree.heading("role", text="Роль")
    tree.heading("locked", text="Заблокирован")
    tree.column("login", width=120, anchor="w")
    tree.column("full_name", width=180, anchor="w")
    tree.column("role", width=130, anchor="w")
    tree.column("locked", width=110, anchor="center")
    for u in all_users():
        tree.insert("", "end", values=(u["login"], u["full_name"], u["role"],
                                       "да" if u["locked"] else "нет"))
    tree.pack(fill="both", expand=True, pady=(0, 10))

    def edit_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите строку в таблице.")
            return
        open_edit_user(tree.item(selected[0])["values"][0])

    row = tk.Frame(container, bg=BG)
    row.pack(fill="x")
    make_button("Добавить", open_add_user, parent=row).pack(side="left", padx=(0, 6))
    make_button("Изменить", edit_selected, parent=row).pack(side="left", padx=(0, 6))
    make_button("Выйти", open_login, parent=row).pack(side="right")


def save_user(login, password, role, full_name):
    login = login.strip()
    password = password.strip()
    full_name = full_name.strip()
    if not login or not password or not full_name:
        messagebox.showwarning("Внимание", "Логин, пароль и ФИО не могут быть пустыми.")
        return
    if login_exists(login):
        messagebox.showerror("Ошибка", "Такой логин уже существует.")
        return
    add_user(login, password, role, full_name)
    messagebox.showinfo("Готово", f"Пользователь {login} добавлен.")
    open_admin()


def open_add_user():
    clear_screen()
    make_title("Новый пользователь").pack(pady=(0, 15))
    make_label("Логин").pack(fill="x")
    e_login = make_entry()
    e_login.pack(fill="x", pady=(0, 10))
    make_label("ФИО").pack(fill="x")
    e_name = make_entry()
    e_name.pack(fill="x", pady=(0, 10))
    make_label("Пароль").pack(fill="x")
    e_pass = make_entry()
    e_pass.pack(fill="x", pady=(0, 10))
    make_label("Роль").pack(fill="x")
    combo_role = ttk.Combobox(container, values=["Пользователь", "Администратор"],
                              state="readonly", font=FONT_BUTTON)
    combo_role.current(0)
    combo_role.pack(fill="x", pady=(0, 15))
    make_button("Сохранить",
                lambda: save_user(e_login.get(), e_pass.get(),
                                  combo_role.get(), e_name.get())
                ).pack(fill="x", ipady=6)
    make_button("Отмена", open_admin).pack(fill="x", pady=(8, 0), ipady=4)


open_login()
root.mainloop()