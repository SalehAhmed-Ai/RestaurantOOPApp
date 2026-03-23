class Order:
    def __init__(self):
        self.items = {}  # {name: {"item": MenuItem, "qty": number}}

    def add_item(self, item):
        if item._name in self.items:
            self.items[item._name]["qty"] += 1
        else:
            self.items[item._name] = {"item": item, "qty": 1}

    def remove_item(self, item_name):
        if item_name in self.items:
            self.items[item_name]["qty"] -= 1
            if self.items[item_name]["qty"] <= 0:
                del self.items[item_name]

    def calculate_total(self):
        total = 0
        for data in self.items.values():
            total += data["item"]._price * data["qty"]
        return total

    def get_items_summary(self):
        result = []
        for name, data in self.items.items():
            qty = data["qty"]
            price = data["item"]._price
            result.append(f"{name} x{qty} = {qty * price}")
        return result