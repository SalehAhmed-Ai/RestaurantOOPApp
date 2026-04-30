import tkinter as tk
from tkinter import messagebox
from Models import MenuItem, Order
from Models.database import MenuRepository, CustomerRepository
from Gui.checkout_window import CheckoutWindow



class LoginWindow:

    def __init__(self):
        self.customer = None
        self.repo     = CustomerRepository()

        self.root = tk.Tk()
        self.root.title("Restaurant — Login")
        self.root.geometry("320x380")
        self.root.resizable(False, False)

        self._build()

    def _build(self):
        tk.Label(self.root, text="Restaurant System",
                 font=("Arial", 14, "bold")).pack(pady=12)

        tk.Label(self.root, text="Phone").pack()
        self.phone_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.phone_var, width=28).pack(pady=2)

        tk.Label(self.root, text="Password").pack()
        self.pass_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.pass_var, show="*", width=28).pack(pady=2)

        tk.Label(self.root, text="Name (Register only)").pack()
        self.name_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.name_var, width=28).pack(pady=2)

        tk.Button(self.root, text="Login",    width=20, command=self._login).pack(pady=6)
        tk.Button(self.root, text="Register", width=20, command=self._register).pack()
        tk.Button(self.root, text="Continue as Guest", width=20,
                  fg="gray", command=self._guest).pack(pady=10)

    def _login(self):
        phone    = self.phone_var.get().strip()
        password = self.pass_var.get().strip()
        if not phone or not password:
            messagebox.showwarning("Input", "Enter phone and password.")
            return
        try:
            customer = self.repo.login(phone, password)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return
        if customer:
            self.customer = customer
            self.root.destroy()
        else:
            messagebox.showerror("Login Failed", "Wrong phone or password.")

    def _register(self):
        phone    = self.phone_var.get().strip()
        password = self.pass_var.get().strip()
        name     = self.name_var.get().strip()
        if not phone or not password or not name:
            messagebox.showwarning("Input", "Fill all fields to register.")
            return
        try:
            customer = self.repo.register(name, phone, password)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return
        if customer:
            messagebox.showinfo("Success", f"Welcome, {customer['Name']}!")
            self.customer = customer
            self.root.destroy()
        else:
            messagebox.showerror("Register Failed", "Phone already registered.")

    def _guest(self):
        self.customer = None
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.customer



class MainWindow:
    def __init__(self):
        # ① Login أول
        self.customer = LoginWindow().run()      # dict أو None لو Guest

        self.order     = Order()
        self.menu_repo = MenuRepository()

        self.window = tk.Tk()
        self.window.title("Restaurant System")
        self.window.geometry("400x520")

        self.menu_items = self._load_menu()
        self.build_ui()

    def _load_menu(self) -> list:
        try:
            rows = self.menu_repo.get_all()
            return [MenuItem(r["Name"], float(r["Price"])) for r in rows]
        except Exception:
            
            return [
                MenuItem("Burger", 80),
                MenuItem("Pizza",  120),
                MenuItem("Pasta",  100),
                MenuItem("Cola",   20),
            ]

    # ── UI ──────────────────────────────────────
   
    def build_ui(self):
        name = self.customer["Name"] if self.customer else "Guest"
        tk.Label(self.window, text=f"Welcome, {name}",
                 font=("Arial", 10), fg="gray").pack(anchor="e", padx=10, pady=4)

        tk.Label(self.window, text="Menu", font=("Arial", 14)).pack()

        for item in self.menu_items:
            tk.Button(
                self.window,
                text=item.get_info(),
                command=lambda i=item: self.add_to_order(i)
            ).pack()

        tk.Label(self.window, text="Cart", font=("Arial", 14)).pack(pady=10)

        self.cart_list = tk.Listbox(self.window, width=30)
        self.cart_list.pack()

        self.total_label = tk.Label(self.window, text="Total: 0")
        self.total_label.pack(pady=5)

        tk.Button(self.window, text="Remove Selected", command=self.remove_selected).pack(pady=5)
        tk.Button(self.window, text="Checkout",        command=self.open_checkout).pack(pady=10)

   
    def add_to_order(self, item):
        self.order.add_item(item)
        self.update_cart()

    def update_cart(self):
        self.cart_list.delete(0, tk.END)
        for line in self.order.get_items_summary():
            self.cart_list.insert(tk.END, line)
        self.total_label.config(text=f"Total: {self.order.calculate_total()}")

    def remove_selected(self):
        selected = self.cart_list.get(tk.ACTIVE)
        if not selected:
            return
        item_name = selected.split(" x")[0]
        self.order.remove_item(item_name)
        self.update_cart()

    def open_checkout(self):
        if not self.order.items:
            return
        customer_id = self.customer["CustomerID"] if self.customer else None
        CheckoutWindow(self.window, self.order, customer_id)   # ← customer_id

    def run(self):
        self.window.mainloop()
