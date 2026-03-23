from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass


class CashPayment(Payment):
    def process_payment(self, amount):
        return f"Paid {amount} EGP using Cash"


class CardPayment(Payment):
    def process_payment(self, amount):
        return f"Paid {amount} EGP using Card"