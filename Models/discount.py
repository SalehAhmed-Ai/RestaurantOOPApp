from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total):
        pass


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage):
        self.percentage = percentage

    def apply_discount(self, total):
        return total - (total * self.percentage)


class FlatDiscount(DiscountStrategy):
    def __init__(self, discount):
        self.discount = discount

    def apply_discount(self, total):
        return total - self.discount