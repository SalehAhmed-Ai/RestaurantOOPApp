import tkinter as tk
from Models import MenuItem, Order
from Gui.checkout_window import CheckoutWindow


class MainWindow:
    def __init__(self):
        self.order = Order()

        self.window = tk.Tk()
        self.window.title("Restaurant System")
        self.window.geometry("400x500")

        self.menu_items = [
            MenuItem("Burger", 80),
            MenuItem("Pizza", 120),
            MenuItem("Pasta", 100),
            MenuItem("Cola", 20),
        ]

        self.build_ui()

    def build_ui(self):
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

        tk.Button(self.window, text="Checkout", command=self.open_checkout).pack(pady=10)

    def add_to_order(self, item):
        self.order.add_item(item)
        self.update_cart()

    def update_cart(self):
        self.cart_list.delete(0, tk.END)

        for line in self.order.get_items_summary():
            self.cart_list.insert(tk.END, line)

        total = self.order.calculate_total()
        self.total_label.config(text=f"Total: {total}")

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

        CheckoutWindow(self.window, self.order)

    def run(self):
        self.window.mainloop()