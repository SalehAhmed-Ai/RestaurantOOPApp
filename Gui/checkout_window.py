import tkinter as tk
from tkinter import messagebox
from Models import PercentageDiscount, FlatDiscount, CashPayment, CardPayment
from Models.database import OrderRepository, PaymentRepository


class CheckoutWindow:


    def __init__(self, parent, order, customer_id: int = None):
        self.order        = order
        self.customer_id  = customer_id           # ← جديد
        self.order_repo   = OrderRepository()     # ← جديد
        self.payment_repo = PaymentRepository()   # ← جديد

        self.window = tk.Toplevel(parent)
        self.window.title("Checkout")
        self.window.geometry("300x350")

        self.build_ui()

    def build_ui(self):
       
        tk.Label(self.window, text="Checkout", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.window, text="Payment Method").pack()
        self.payment_var = tk.StringVar(value="cash")
        tk.Radiobutton(self.window, text="Cash", variable=self.payment_var, value="cash").pack()
        tk.Radiobutton(self.window, text="Visa", variable=self.payment_var, value="card").pack()

        tk.Label(self.window, text="Discount").pack(pady=10)
        self.discount_var = tk.StringVar(value="none")
        tk.Radiobutton(self.window, text="No Discount", variable=self.discount_var, value="none").pack()
        tk.Radiobutton(self.window, text="10% Off",     variable=self.discount_var, value="percent").pack()
        tk.Radiobutton(self.window, text="50 EGP Off",  variable=self.discount_var, value="flat").pack()

        tk.Button(self.window, text="Pay", command=self.process_payment).pack(pady=15)

    def process_payment(self):
       
        original_total = self.order.calculate_total()
        final_total    = original_total
        discount_value = 0
        discount_type  = self.discount_var.get()

        if discount_type == "percent":
            final_total    = PercentageDiscount(0.1).apply_discount(original_total)
            discount_value = original_total - final_total
        elif discount_type == "flat":
            final_total    = FlatDiscount(50).apply_discount(original_total)
            discount_value = original_total - final_total

        
        method_key = self.payment_var.get()
        if method_key == "cash":
            payment      = CashPayment()
            method_label = "Cash"
        else:
            payment      = CardPayment()
            method_label = "Card"

        result = payment.process_payment(final_total)

    
        db_note = ""
        try:
            order_id   = self.order_repo.save_order(self.order, self.customer_id)
            payment_id = self.payment_repo.save_payment(
                order_id       = order_id,
                original_total = original_total,
                discount_type  = discount_type,
                discount_value = discount_value,
                final_total    = final_total,
                method         = method_label
            )
            db_note = f"\nOrder ID : #{order_id}\nPayment ID: #{payment_id}"
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Payment was not saved in database.\n{e}"
            )
            return
        # ───────────────────────────────────────────────

        details = "\n".join(self.order.get_items_summary())

        messagebox.showinfo(
            "Receipt",
            f"{details}\n"
            f"─────────────────\n"
            f"Original : {original_total} EGP\n"
            f"Discount : {discount_value} EGP\n"
            f"Total    : {final_total} EGP\n"
            f"─────────────────\n"
            f"{result}"
            f"{db_note}"
        )

        self.window.destroy()
