class MenuItem:
    def __init__(self, name, price):
        self._name = name
        self._price = price

    def get_info(self):
        return f"{self._name} - {self._price} EGP"