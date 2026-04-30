-- Migration script for existing RestaurantDB.

USE RestaurantDB;
GO

-- Add customers table.
CREATE TABLE Customers (
    CustomerID   INT IDENTITY(1,1) PRIMARY KEY,
    Name         NVARCHAR(150)  NOT NULL,
    Phone        NVARCHAR(20)   NOT NULL UNIQUE,
    PasswordHash NVARCHAR(256)  NOT NULL,
    CreatedAt    DATETIME       NOT NULL DEFAULT GETDATE()
);
GO

-- Link orders to customers (nullable for guest checkout).
ALTER TABLE Orders
    ADD CustomerID INT NULL REFERENCES Customers(CustomerID);
GO
