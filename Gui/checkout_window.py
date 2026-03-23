import tkinter as tk
from tkinter import messagebox
from Models import PercentageDiscount, FlatDiscount, CashPayment, CardPayment


class CheckoutWindow:
    def __init__(self, parent, order):
        self.order = order

        self.window = tk.Toplevel(parent)
        self.window.title("Checkout")
        self.window.geometry("300x350")

        self.build_ui()

    def build_ui(self):
        tk.Label(self.window, text="Checkout", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.window, text="Payment Method").pack()

        self.payment_var = tk.StringVar(value="cash")

        tk.Radiobutton(self.window, text="Cash", variable=self.payment_var, value="cash").pack()
        tk.Radiobutton(self.window, text="Card", variable=self.payment_var, value="card").pack()

        tk.Label(self.window, text="Discount").pack(pady=10)

        self.discount_var = tk.StringVar(value="none")

        tk.Radiobutton(self.window, text="No Discount", variable=self.discount_var, value="none").pack()
        tk.Radiobutton(self.window, text="10% Off", variable=self.discount_var, value="percent").pack()
        tk.Radiobutton(self.window, text="50 EGP Off", variable=self.discount_var, value="flat").pack()

        tk.Button(self.window, text="Pay", command=self.process_payment).pack(pady=15)

    def process_payment(self):
        original_total = self.order.calculate_total()
        final_total = original_total
        discount_value = 0

        # Apply Discount
        if self.discount_var.get() == "percent":
            final_total = PercentageDiscount(0.1).apply_discount(original_total)
            discount_value = original_total - final_total

        elif self.discount_var.get() == "flat":
            final_total = FlatDiscount(50).apply_discount(original_total)
            discount_value = original_total - final_total

        # Payment Method
        if self.payment_var.get() == "cash":
            payment = CashPayment()
        else:
            payment = CardPayment()

        result = payment.process_payment(final_total)

        details = "\n".join(self.order.get_items_summary())

        messagebox.showinfo(
            "Receipt",
            f"{details}\n\n"
            f"Original Total: {original_total}\n"
            f"Discount: {discount_value}\n"
            f"Final Total: {final_total}\n\n"
            f"{result}"
        )

        self.window.destroy()