-- Suppliers
CREATE TABLE Suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255),
    address VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Categories
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);


-- Products
CREATE TABLE Products (
    SKU VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10 , 2 ) NOT NULL CHECK (price > 0),
    stock INT NOT NULL CHECK (stock >= 0),
    low_stock_threshold INT DEFAULT 5,
    supplier_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id)
        REFERENCES Suppliers (supplier_id),
    FOREIGN KEY (category_id)
        REFERENCES Categories (category_id),
        cost DECIMAL(10,2) DEFAULT 0.00
);



-- Employees
CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
);

-- Customers
CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'Anonymous',
    contact_info VARCHAR(255),
    address VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sales
CREATE TABLE Sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_datetime DATETIME NOT NULL,
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    employee_id INT NOT NULL,
    customer_id INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- Sale Items
CREATE TABLE SaleItems (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    SKU VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    FOREIGN KEY (sale_id) REFERENCES Sales(sale_id),
    FOREIGN KEY (SKU) REFERENCES Products(SKU)
);

-- Purchases
CREATE TABLE Purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_datetime DATETIME NOT NULL,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    delivery_status ENUM('pending', 'received') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);

-- Purchase Items
CREATE TABLE PurchaseItems (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    SKU VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_cost DECIMAL(10, 2) NOT NULL CHECK (unit_cost >= 0),
    FOREIGN KEY (purchase_id) REFERENCES Purchases(purchase_id),
    FOREIGN KEY (SKU) REFERENCES Products(SKU)
);

-- Inventory Adjustments
CREATE TABLE InventoryAdjustments (
    adjustment_id INT AUTO_INCREMENT PRIMARY KEY,
    SKU VARCHAR(255) NOT NULL,
    adjustment_datetime DATETIME NOT NULL,
    quantity_change INT NOT NULL,
    reason VARCHAR(255),
    employee_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SKU) REFERENCES Products(SKU),
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);

-- Create default anonymous customer
INSERT INTO Customers (customer_id, name, is_anonymous) 
VALUES (0, 'Anonymous', TRUE);