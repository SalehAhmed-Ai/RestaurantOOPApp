import hashlib
try:
    import pyodbc
except ImportError:  # pragma: no cover - depends on local environment
    pyodbc = None

class DatabaseConnection:
    _instance = None

    CONNECTION_STRING = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        # Use localhost\\SQLEXPRESS if you run SQL Server Express.
        "SERVER=localhost;"
        "DATABASE=RestaurantDB;"
        "Trusted_Connection=yes;"
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
        return cls._instance

    def get_connection(self):
        if self._conn is None:
            if pyodbc is None:
                raise RuntimeError(
                    "pyodbc is not installed. Install it to enable database features."
                )
            self._conn = pyodbc.connect(self.CONNECTION_STRING)
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

class _Repo:
    def __init__(self):
        self._db = DatabaseConnection()

    @property
    def _conn(self):
        return self._db.get_connection()

    def _run(self, sql, params=()):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        self._conn.commit()
        return cur

    def _all(self, sql, params=()):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def _one(self, sql, params=()):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None

class MenuRepository(_Repo):

    def get_all(self):
        return self._all("SELECT ItemID, Name, Price FROM MenuItems")

    def get_by_name(self, name: str):
        return self._one(
            "SELECT ItemID, Name, Price FROM MenuItems WHERE Name = ?", (name,)
        )

    def add_item(self, name: str, price: float):
        self._run(
            "INSERT INTO MenuItems (Name, Price) VALUES (?, ?)", (name, price)
        )

    def update_price(self, name: str, new_price: float):
        self._run(
            "UPDATE MenuItems SET Price = ? WHERE Name = ?", (new_price, name)
        )

    def delete_item(self, name: str):
        self._run("DELETE FROM MenuItems WHERE Name = ?", (name,))

class OrderRepository(_Repo):

    def save_order(self, order, customer_id: int = None) -> int:
        menu_repo  = MenuRepository()
        total      = order.calculate_total()
        cur        = self._conn.cursor()

        cur.execute(
            """
            INSERT INTO Orders (TotalAmount, CustomerID)
            OUTPUT INSERTED.OrderID
            VALUES (?, ?)
            """,
            (total, customer_id)
        )
        order_id = cur.fetchone()[0]

        for name, data in order.items.items():
            row        = menu_repo.get_by_name(name)
            if not row:
                raise ValueError(
                    f"Menu item '{name}' does not exist in database MenuItems table."
                )
            item_id    = row["ItemID"]
            unit_price = data["item"]._price
            qty        = data["qty"]

            cur.execute(
                """
                INSERT INTO OrderDetails (OrderID, ItemID, Quantity, UnitPrice)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, item_id, qty, unit_price)
            )

        self._conn.commit()
        return order_id

    def get_all_orders(self):
        return self._all(
            "SELECT OrderID, OrderDate, TotalAmount, CustomerID FROM Orders ORDER BY OrderDate DESC"
        )

    def get_order_details(self, order_id: int):
        return self._all(
            """
            SELECT mi.Name, od.Quantity, od.UnitPrice, od.Subtotal
            FROM   OrderDetails od
            JOIN   MenuItems    mi ON od.ItemID = mi.ItemID
            WHERE  od.OrderID = ?
            """,
            (order_id,)
        )

class PaymentRepository(_Repo):

    def save_payment(
        self,
        order_id: int,
        original_total: float,
        discount_type: str,
        discount_value: float,
        final_total: float,
        method: str
    ) -> int:
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO Payments
                (OrderID, OriginalTotal, DiscountType, DiscountValue, FinalTotal, Method)
            OUTPUT INSERTED.PaymentID
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, original_total, discount_type, discount_value, final_total, method)
        )
        payment_id = cur.fetchone()[0]
        self._conn.commit()
        return payment_id

    def get_all_payments(self):
        return self._all(
            """
            SELECT p.PaymentID, p.PaymentDate, p.Method,
                   p.OriginalTotal, p.DiscountType, p.DiscountValue, p.FinalTotal
            FROM   Payments p
            ORDER BY p.PaymentDate DESC
            """
        )

    def daily_revenue(self) -> float:
        row = self._one(
            """
            SELECT ISNULL(SUM(FinalTotal), 0) AS Revenue
            FROM   Payments
            WHERE  CAST(PaymentDate AS DATE) = CAST(GETDATE() AS DATE)
            """
        )
        return float(row["Revenue"]) if row else 0.0

class CustomerRepository(_Repo):

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, name: str, phone: str, password: str):
        """Return created customer dict, or None if phone already exists."""
        if self.get_by_phone(phone):
            return None
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO Customers (Name, Phone, PasswordHash)
            OUTPUT INSERTED.CustomerID, INSERTED.Name, INSERTED.Phone
            VALUES (?, ?, ?)
            """,
            (name, phone, self._hash(password))
        )
        row = cur.fetchone()
        self._conn.commit()
        return {"CustomerID": row[0], "Name": row[1], "Phone": row[2]}

    def login(self, phone: str, password: str):
        """Return customer dict on success, otherwise None."""
        return self._one(
            """
            SELECT CustomerID, Name, Phone
            FROM   Customers
            WHERE  Phone = ? AND PasswordHash = ?
            """,
            (phone, self._hash(password))
        )

    def get_by_phone(self, phone: str):
        return self._one(
            "SELECT CustomerID, Name, Phone FROM Customers WHERE Phone = ?",
            (phone,)
        )
