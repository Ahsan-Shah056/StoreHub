# 🚀 Storecore: Modern POS System for Retail & Inventory

**Python Tkinter | MySQL**

---

## 📝 Overview

Storecore is a robust, user-friendly Point-of-Sale (POS) and inventory management system for retail businesses. Built with Python and Tkinter, it features a modern interface, real-time inventory tracking, customer and supplier management, and a suite of business reports. Storecore is designed for reliability, clarity, and ease of use in any retail environment.

---

## ✨ Features

- **Intuitive GUI:** Clean, responsive interface with tabbed navigation (Sales, Customers, Inventory, Suppliers, Reports).
- **Sales Management:**
  - Add items to cart, update/remove, and checkout with receipt display.
  - Customer selection and purchase history lookup.
- **Inventory Management:**
  - Add, delete, and adjust stock for products.
  - View inventory with real-time stock and value.
- **Customer & Supplier Management:**
  - Add, delete, and view customers and suppliers.
  - Supplier search and purchase history.
- **Employee Management:**
  - Add, update, delete, and view employees.
- **Comprehensive Reports:**
  - Low Stock Report
  - Sales by Employee
  - Supplier Purchase Report
  - Inventory Adjustment History
  - Inventory Value Report (SKU, Product Name, Stock, Price, Total Value)
  - Customer Purchase History (select customer, see all purchases)
- **Consistent, Compact UI:**
  - All reports and dropdowns are easy to use and auto-populated.
- **Robust Error Handling:**
  - User-friendly error popups for all operations.

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone [https://github.com/Ahsan-Shah056/Storecore.git]
cd Storecore

# 2. Set up a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Set up the MySQL database
- Create database and tables (see schema.sql)
- Edit database.py with your MySQL credentials

# 5. (Optional) Populate with sample data
python sample_data.py

# 6. Run the application
python main.py
```

---

## 🖥️ How the App Operates

### For Sales Staff

- **Start the Application:** Launch `main.py`.
- **Add to Cart:** Enter SKU and quantity, click 'Add to Cart'.
- **Select Customer:** Use the dropdown to select a customer.
- **Checkout:** Click 'Checkout' to complete the sale and view the receipt.

### For Managers/Admins

- **Inventory:** Add/delete products, adjust stock, and view inventory value.
- **Customers/Suppliers:** Add, delete, and view all records.
- **Reports:**
  - Use the Reports tab to generate business insights (low stock, sales by employee, inventory value, customer purchase history, etc.).
  - Use dropdowns to filter by employee, supplier, or customer as needed.

---

## 📊 Example: Inventory Value Report

| SKU      | Product Name   | Stock | Price   | Total Value |
|----------|---------------|-------|---------|-------------|
| 1001     | Widget A       |  20   | $5.00   | $100.00     |
| 1002     | Widget B       |  10   | $8.00   | $80.00      |

---

## 🗂️ Project Structure

```
Storecore/
├── main.py                # Main application (Tkinter GUI)
├── Ui.py                  # All UI classes and logic
├── database.py            # Database connection logic
├── inventory.py           # Inventory management logic
├── sales.py               # Sales/cart logic
├── customers.py           # Customer management
├── suppliers.py           # Supplier management
├── employees.py           # Employee management
├── reporting.py           # Business reports logic
├── sample_data.py         # Script to populate sample data
├── schema.sql             # MySQL schema
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Configuration

- Edit `database.py` to set your MySQL username, password, and database name (`store`).
- Ensure MySQL server is running before launching the app.

---

## 🛠️ Requirements

- Python 3.x
- Tkinter (usually included with Python)
- MySQL Server

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📬 Contact

For questions or feedback, contact the maintainer: [ahsanxhah056@gmail.com]