-- Restaurant schema bootstrap.

CREATE DATABASE RestaurantDB;
GO

USE RestaurantDB;
GO

-- Core menu data.
CREATE TABLE MenuItems (
    ItemID    INT IDENTITY(1,1) PRIMARY KEY,
    Name      NVARCHAR(150)  NOT NULL UNIQUE,
    Price     DECIMAL(10,2)  NOT NULL CHECK (Price >= 0)
);
GO

-- Customer accounts for login/register.
CREATE TABLE Customers (
    CustomerID   INT IDENTITY(1,1) PRIMARY KEY,
    Name         NVARCHAR(150)  NOT NULL,
    Phone        NVARCHAR(20)   NOT NULL UNIQUE,
    PasswordHash NVARCHAR(256)  NOT NULL,
    CreatedAt    DATETIME       NOT NULL DEFAULT GETDATE()
);
GO

-- Order header.
CREATE TABLE Orders (
    OrderID     INT IDENTITY(1,1) PRIMARY KEY,
    OrderDate   DATETIME       NOT NULL DEFAULT GETDATE(),
    TotalAmount DECIMAL(10,2)  NOT NULL DEFAULT 0,
    CustomerID  INT NULL REFERENCES Customers(CustomerID)
);
GO

-- Order line items.
CREATE TABLE OrderDetails (
    DetailID  INT IDENTITY(1,1) PRIMARY KEY,
    OrderID   INT           NOT NULL REFERENCES Orders(OrderID) ON DELETE CASCADE,
    ItemID    INT           NOT NULL REFERENCES MenuItems(ItemID),
    Quantity  INT           NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(10,2) NOT NULL,
    Subtotal  AS (Quantity * UnitPrice) PERSISTED
);
GO

-- Payment records.
CREATE TABLE Payments (
    PaymentID     INT IDENTITY(1,1) PRIMARY KEY,
    OrderID       INT            NOT NULL REFERENCES Orders(OrderID),
    PaymentDate   DATETIME       NOT NULL DEFAULT GETDATE(),
    OriginalTotal DECIMAL(10,2)  NOT NULL,
    DiscountType  NVARCHAR(50)   NOT NULL DEFAULT 'none'
                                 CHECK (DiscountType IN ('none', 'percent', 'flat')),
    DiscountValue DECIMAL(10,2)  NOT NULL DEFAULT 0,
    FinalTotal    DECIMAL(10,2)  NOT NULL,
    Method        NVARCHAR(50)   NOT NULL DEFAULT 'Cash'
                                 CHECK (Method IN ('Cash', 'Card'))
);
GO

-- Seed menu records.
INSERT INTO MenuItems (Name, Price) VALUES
('Burger', 80),
('Pizza',  120),
('Pasta',  100),
('Cola',   20);
GO
