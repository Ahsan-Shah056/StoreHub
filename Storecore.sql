use store;

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
    base_product_id VARCHAR(255),
    category_id INT NOT NULL,
    price DECIMAL(10 , 2 ) NOT NULL CHECK (price > 0),
    stock INT NOT NULL CHECK (stock >= 0),
    low_stock_threshold INT DEFAULT 5,
    supplier_id INT,
    color VARCHAR(50),
    size VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id)
        REFERENCES Suppliers (supplier_id),
    FOREIGN KEY (category_id)
        REFERENCES Categories (category_id)
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
    total DECIMAL(10 , 2 ) NOT NULL CHECK (total >= 0),
    employee_id INT NOT NULL,
    customer_id INT NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id)
        REFERENCES Employees (employee_id),
    FOREIGN KEY (customer_id)
        REFERENCES Customers (customer_id)
);

-- Sale Items
CREATE TABLE SaleItems (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    SKU VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10 , 2 ) NOT NULL CHECK (price >= 0),
    FOREIGN KEY (sale_id)
        REFERENCES Sales (sale_id),
    FOREIGN KEY (SKU)
        REFERENCES Products (SKU)
);

-- Purchases
CREATE TABLE Purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_datetime DATETIME NOT NULL,
    shipping_cost DECIMAL(10 , 2 ) DEFAULT 0,
    delivery_status ENUM('pending', 'received') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id)
        REFERENCES Suppliers (supplier_id)
);

-- Purchase Items
CREATE TABLE PurchaseItems (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    SKU VARCHAR(255) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_cost DECIMAL(10 , 2 ) NOT NULL CHECK (unit_cost >= 0),
    FOREIGN KEY (purchase_id)
        REFERENCES Purchases (purchase_id),
    FOREIGN KEY (SKU)
        REFERENCES Products (SKU)
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
    FOREIGN KEY (SKU)
        REFERENCES Products (SKU),
    FOREIGN KEY (employee_id)
        REFERENCES Employees (employee_id)
);

-- Create default anonymous customer
INSERT INTO Customers (customer_id, name, is_anonymous) 
VALUES (0, 'Cash_sales', TRUE);
SELECT 
    *
FROM
    customers;


-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Clear existing data
DELETE FROM Suppliers;
DELETE FROM Customers 
WHERE
    customer_id != 0;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;


-- Insert Employees
INSERT INTO Employees (name) VALUES
('Ahmed Khan'),
('Ayesha Siddiqui'),
('Bilal Hassan');

-- Insert Suppliers (Pakistani Companies)
INSERT INTO Suppliers (name, contact_info, address) VALUES
('Lahore Crockery House', 'contact@lahorecrockery.pk', 'Mall Road, Lahore'),
('Karachi Tableware Mart', 'info@karachitableware.pk', 'Tariq Road, Karachi'),
('Islamabad Ceramics', 'sales@islamabadceramics.pk', 'Blue Area, Islamabad'),
('Peshawar Pottery Palace', 'info@potterypeshawar.pk', 'Saddar, Peshawar'),
('Multan Clay Crafts', 'contact@multanclay.pk', 'Hussain Agahi, Multan'),
('Faisalabad Porcelain Center', 'info@porcelainfaisalabad.pk', 'D Ground, Faisalabad'),
('Rawalpindi Crockery Store', 'sales@rawalcrockery.pk', 'Commercial Market, Rawalpindi'),
('Sialkot Table Tops', 'hello@sialkottops.pk', 'Cantt Bazaar, Sialkot'),
('Quetta Dinnerware Depot', 'info@quettadinnerware.pk', 'Jinnah Road, Quetta'),
('Hyderabad Kitchenware Hub', 'contact@hyderabadkitchenware.pk', 'Auto Bhan Road, Hyderabad');

-- Insert Categories
INSERT INTO Categories (name) VALUES
('Plates'),
('Bowls'),
('Cups'),
('Cutlery'),
('Serving Dishes');


SELECT 
    *
FROM
    products;
-- Insert Customers
INSERT INTO Customers (name, contact_info, address) VALUES
('Alice Brown', 'alice.brown@email.com', '12 Oak St, Anytown'),
('Bob Green', 'bob.green@email.com', '34 Pine Ave, Springfield'),
('Carol White', 'carol.white@email.com', '56 Maple Dr, Riverdale');

-- Sample Purchase Entry
INSERT INTO Purchases (supplier_id, purchase_datetime, delivery_status) VALUES
(1, NOW(), 'received');
SELECT 
    *
FROM
    customers;


-- Sample Purchase Item
INSERT INTO PurchaseItems (purchase_id, SKU, quantity, unit_cost) VALUES
(LAST_INSERT_ID(), 'DINNER_PLATE_WHITE', 10, 12.99);

INSERT ignore INTO Suppliers (name, contact_info, address) VALUES 
('Lahore Crockery House', 'contact@lahorecrockery.pk', 'Mall Road, Lahore'),
('Karachi Tableware Mart', 'info@karachitableware.pk', 'Tariq Road, Karachi'),
('Islamabad Ceramics', 'sales@islamabadceramics.pk', 'Blue Area, Islamabad'),
('Multan Clay Crafts', 'info@multanclay.pk', 'Hussain Agahi, Multan'),
('Rawalpindi Crockery Center', 'support@rawalcrockery.pk', 'Commercial Market, Rawalpindi'),
('Hyderabad Kitchenware Hub', 'sales@hyderabadkitchen.pk', 'Auto Bhan Road, Hyderabad'),
('Sialkot Porcelain Traders', 'info@sialkotporcelain.pk', 'Cantt Bazaar, Sialkot'),
('Quetta Dinnerware Depot', 'help@quettadinnerware.pk', 'Jinnah Road, Quetta'),
('Faisalabad Table Tops', 'sales@faisalabadtops.pk', 'D Ground, Faisalabad'),
('Peshawar Pottery Plaza', 'info@peshawarpottery.pk', 'Saddar Road, Peshawar'),
('Bahawalpur Crockery Mall', 'bahawalpur@crockerymall.pk', 'Model Town, Bahawalpur'),
('Gujranwala Glassware Traders', 'info@gujranwalaglass.pk', 'Railway Road, Gujranwala'),
('Sargodha Ceramics Mart', 'sales@sargodhaceramics.pk', 'Satellite Town, Sargodha'),
('Sukkur Crockery Point', 'info@sukkurcrockery.pk', 'Shahbaz Road, Sukkur'),
('Abbottabad Fine Crockery', 'contact@abbottabadcrockery.pk', 'Main Bazaar, Abbottabad');

INSERT INTO Categories (name) VALUES 
('Dinner Plates'),
('Soup Bowls'),
('Serving Bowls'),
('Tea Sets'),
('Coffee Mugs'),
('Cutlery'),
('Water Glasses'),
('Serving Platters'),
('Salad Bowls'),
('Dessert Plates'),
('Rice Plates'),
('Gravy Boats'),
('Cake Stands'),
('Casseroles'),
('Tea Saucers');

INSERT INTO Products (SKU, name, base_product_id, category_id, price, stock, supplier_id, color, size) VALUES 
('DPLATE_WHITE', 'Dinner Plate White', NULL, 1, 450.00, 100, 1, 'White', 'Large'),
('SOUPBOWL_BLUE', 'Soup Bowl Blue', NULL, 2, 320.00, 80, 2, 'Blue', 'Medium'),
('SERVBOWL_GREEN', 'Serving Bowl Green', NULL, 3, 600.00, 50, 3, 'Green', 'Large'),
('TEASET_GOLD', 'Tea Set Golden', NULL, 4, 2200.00, 20, 4, 'Golden', 'Set of 6'),
('COFFEEMUG_RED', 'Coffee Mug Red', NULL, 5, 250.00, 200, 5, 'Red', 'Medium'),
('CUTLERY_SET', 'Cutlery Set 24 pcs', NULL, 6, 1800.00, 30, 6, NULL, 'Set of 24'),
('WATERGLASS_CLEAR', 'Clear Water Glass', NULL, 7, 150.00, 120, 7, 'Transparent', 'Medium'),
('SERVPLATTER_BLACK', 'Serving Platter Black', NULL, 8, 900.00, 40, 8, 'Black', 'Large'),
('SALADBOWL_WHITE', 'Salad Bowl White', NULL, 9, 500.00, 60, 9, 'White', 'Medium'),
('DESSERTPLATE', 'Dessert Plate Small', NULL, 10, 350.00, 100, 10, 'Floral', 'Small'),
('RICEPLATE', 'Rice Plate', NULL, 11, 550.00, 70, 11, 'White', 'Large'),
('GRAVYBOAT', 'Gravy Boat Ceramic', NULL, 12, 850.00, 30, 12, 'White', 'Medium'),
('CAKESTAND', 'Cake Stand Marble', NULL, 13, 1200.00, 15, 13, 'White', 'Large'),
('CASSEROLE', 'Casserole Dish', NULL, 14, 950.00, 25, 14, 'White', 'Large'),
('TEASAUCER', 'Tea Saucer', NULL, 15, 200.00, 150, 15, 'White', 'Small');


INSERT INTO Employees (name) VALUES 
('Ahmed Raza'),
('Sara Khan'),
('Bilal Qureshi'),
('Fatima Sheikh'),
('Zain Ahmed'),
('Ayesha Malik'),
('Hamza Shah'),
('Nida Usman'),
('Waleed Rauf'),
('Mehwish Asif'),
('Fahad Jamil'),
('Hira Aftab'),
('Saad Farooq'),
('Rimsha Nadeem'),
('Imran Haider');


INSERT INTO Customers (name, contact_info, address) VALUES
('Ali Raza', 'ali.raza@email.com', 'DHA, Lahore'),
('Fatima Khan', 'fatima.khan@email.com', 'Gulshan-e-Iqbal, Karachi'),
('Bilal Ahmad', 'bilal.ahmad@email.com', 'F-8 Markaz, Islamabad'),
('Zainab Siddiqui', 'zainab.sid@email.com', 'Model Town, Lahore'),
('Hamza Javed', 'hamza.javed@email.com', 'G-11 Sector, Islamabad'),
('Ayesha Malik', 'ayesha.malik@email.com', 'Clifton, Karachi'),
('Umar Farooq', 'umar.farooq@email.com', 'Saddar, Rawalpindi'),
('Maria Shah', 'maria.shah@email.com', 'Cantt, Multan'),
('Ahmad Nadeem', 'ahmad.nadeem@email.com', 'Satellite Town, Sargodha'),
('Noor Fatima', 'noor.fatima@email.com', 'Auto Bhan Road, Hyderabad'),
('Saad Qureshi', 'saad.qureshi@email.com', 'Jinnah Road, Quetta'),
('Hiba Ali', 'hiba.ali@email.com', 'Blue Area, Islamabad'),
('Daniyal Sheikh', 'daniyal.sheikh@email.com', 'Main Bazaar, Peshawar'),
('Laiba Hassan', 'laiba.hassan@email.com', 'Sadar, Faisalabad'),
('Hasnain Raza', 'hasnain.raza@email.com', 'Model Town, Bahawalpur');

INSERT INTO Purchases (supplier_id, purchase_datetime, shipping_cost, delivery_status) VALUES
(1, NOW(), 500.00, 'received'),
(2, NOW(), 300.00, 'received'),
(3, NOW(), 450.00, 'pending'),
(4, NOW(), 600.00, 'received'),
(5, NOW(), 350.00, 'received');

INSERT INTO PurchaseItems (purchase_id, SKU, quantity, unit_cost) VALUES
(1, 'DPLATE_WHITE', 20, 400.00),
(1, 'SOUPBOWL_BLUE', 15, 280.00),
(2, 'SERVBOWL_GREEN', 10, 550.00),
(3, 'TEASET_GOLD', 5, 2000.00),
(4, 'COFFEEMUG_RED', 30, 200.00),
(5, 'CUTLERY_SET', 10, 1700.00);

INSERT INTO Sales (sale_datetime, total, employee_id, customer_id) VALUES
(NOW(), 4500.00, 2, 1),
(NOW(), 3200.00, 3, 2),
(NOW(), 2500.00, 1, 3),
(NOW(), 1800.00, 2, 4),
(NOW(), 6000.00, 3, 5);



INSERT INTO SaleItems (sale_id, SKU, quantity, price) VALUES
(1, 'DPLATE_WHITE', 5, 450.00),
(1, 'SOUPBOWL_BLUE', 3, 320.00),
(2, 'TEASET_GOLD', 2, 2200.00),
(3, 'COFFEEMUG_RED', 4, 250.00),
(4, 'CUTLERY_SET', 1, 1800.00),
(5, 'SERVPLATTER_BLACK', 2, 900.00);

INSERT INTO InventoryAdjustments (SKU, adjustment_datetime, quantity_change, reason, employee_id) VALUES
('DPLATE_WHITE', NOW(), -2, 'Breakage', 2),
('SOUPBOWL_BLUE', NOW(), 5, 'New Shipment', 3),
('TEASET_GOLD', NOW(), -1, 'Sample Damage', 1),
('COFFEEMUG_RED', NOW(), 10, 'Restock', 2),
('CUTLERY_SET', NOW(), -3, 'Theft Adjustment', 3);

SELECT 
    *
FROM
    customers;


select * from employees;


