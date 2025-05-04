# 🚀 Storecore: Modern POS & Inventory Management System

**Python Tkinter | MySQL | Modular Architecture**

---

## 📝 Overview

Storecore is a comprehensive, modular Point-of-Sale (POS) and inventory management solution tailored for retail businesses, warehouses, and small enterprises. Built with Python and Tkinter for the GUI and MySQL for persistent data storage, Storecore offers a seamless experience for both end-users and developers. The system supports real-time inventory tracking, robust sales workflows, customer and supplier management, and a suite of actionable business reports. Its codebase is structured for maintainability, extensibility, and ease of integration with other systems.

---

## ✨ Features

- **Intuitive GUI:**
  - Responsive, tabbed interface (Sales, Customers, Inventory, Suppliers, Reports).
  - Consistent look and feel across all modules.
- **Sales Management:**
  - Add items to cart, update/remove, and checkout with real-time receipt generation.
  - Customer selection and purchase history lookup.
  - Transactional integrity: all sales are atomic and rollback on error.
- **Inventory Management:**
  - Add, delete, and adjust stock for products.
  - View inventory with real-time stock, price, and computed value.
  - Inventory adjustments are logged for auditability.
- **Customer & Supplier Management:**
  - Add, delete, and view customers and suppliers.
  - Supplier search and purchase history.
  - Referential integrity: prevents orphaned sales or purchases.
- **Employee Management:**
  - Add, update, delete, and view employees.
  - Role-based access patterns possible with minor extension.
- **Comprehensive Reports:**
  - Low Stock Report: Instantly identify products needing restock.
  - Sales by Employee: Analyze staff performance.
  - Supplier Purchase Report: Track procurement and supplier reliability.
  - Inventory Adjustment History: Full audit trail of stock changes.
  - Inventory Value Report: SKU, Product Name, Stock, Price, Total Value.
  - Customer Purchase History: Select customer, see all purchases.
- **Consistent, Compact UI:**
  - All reports and dropdowns are easy to use and auto-populated.
  - Horizontal scrollbars and column widths are optimized for clarity.
- **Robust Error Handling:**
  - User-friendly error popups for all operations.
  - Defensive programming: all DB operations wrapped in try/except.
- **Extensible Codebase:**
  - Modular Python files for each domain (sales, inventory, reporting, etc.).
  - Easy to add new reports, business logic, or integrations.
- **Technical Highlights:**
  - Uses parameterized SQL queries to prevent SQL injection.
  - Follows MVC-like separation: UI, business logic, and data access are decoupled.
  - Supports multi-user workflows and concurrent access (with proper DB config).

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Ahsan-Shah056/Storecore.git
cd Storecore

# 2. Set up a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Set up the MySQL database
- Use storecore.sql to create all tables and relationships:
- mysql -u <username> -p < storecore.sql
- Edit database.py with your MySQL credentials

# 4. (Optional) Populate with sample data
python sample_data.py

# 5. Run the application
python main.py
```

---

## 🖥️ How the App Operates

### For Sales Staff

- **Start the Application:** Launch `main.py`.
- **Add to Cart:** Enter SKU and quantity, click 'Add to Cart'.
- **Select Customer:** Use the dropdown to select a customer.
- **Checkout:** Click 'Checkout' to complete the sale and view the receipt.
- **Error Handling:** Any invalid input or DB error is shown in a popup, and the operation is safely rolled back.

### For Managers/Admins

- **Inventory:** Add/delete products, adjust stock, and view inventory value.
- **Customers/Suppliers:** Add, delete, and view all records. Supplier and customer dropdowns are always up-to-date.
- **Reports:**
  - Use the Reports tab to generate business insights (low stock, sales by employee, inventory value, customer purchase history, etc.).
  - Use dropdowns to filter by employee, supplier, or customer as needed.
  - All reports are generated via optimized SQL queries for performance.

### For Developers

- **Codebase Structure:**
  - Each business domain (sales, inventory, etc.) is encapsulated in its own Python module.
  - UI logic is separated from business logic and data access.
  - All DB access uses parameterized queries and context management.
- **Adding New Features:**
  - To add a new report, create a function in `reporting.py`, add a callback in `main.py`, and wire a button/dropdown in `Ui.py`.
  - To extend the UI, subclass or modify the relevant UI class in `Ui.py`.
- **Testing & Debugging:**
- **Testing & Debugging:**
  - All exceptions are caught and surfaced to the user.
  - Use print statements or logging for deeper debugging.

---

## 📊 Example: Inventory Value Report

| SKU      | Product Name  | Stock | Price   | Total Value |
|----------|---------------|-------|---------|-------------|
| 1001     | china_bowl    |  20   | $5.00   | $100.00     |
| 1002     | Cupsaucer     |  10   | $8.00   | $80.00      |

---

## 🗂️ Project Structure

```
Storecore/
├── main.py                # Main application (Tkinter GUI, app entrypoint)
├── Ui.py                  # All UI classes and logic (modular, extensible)
├── database.py            # Database connection logic (MySQL, parameterized)
├── inventory.py           # Inventory management logic (CRUD, adjustments)
├── sales.py               # Sales/cart logic (transactional, atomic)
├── customers.py           # Customer management (CRUD)
├── suppliers.py           # Supplier management (CRUD, search)
├── employees.py           # Employee management (CRUD)
├── reporting.py           # Business reports logic (optimized SQL)
├── sample_data.py         # Script to populate sample data
├── schema.sql             # (Legacy) MySQL schema
├── storecore.sql          # **Recommended**: Full SQL schema for Storecore DB setup
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## ⚙️ Configuration

- Use `storecore.sql` to set up your MySQL database schema. This file contains all necessary CREATE TABLE and relationship statements for Storecore.
- Edit `database.py` to set your MySQL username, password, and database name (`store`).
- Ensure MySQL server is running before launching the app.
- All DB credentials are kept in code for simplicity; for production, use environment variables or a config file.

---

## 🛠️ Requirements

- Python 3.x
- Tkinter (usually included with Python)
- MySQL Server (with InnoDB for transactions)
- (Optional) MySQL Workbench for DB management

---

## 🧑‍💻 Example: Adding a New Report (Developer Guide)

```python
# In reporting.py
def top_selling_products(cursor):
    query = """
        SELECT SKU, name, SUM(quantity) as total_sold
        FROM SaleItems
        JOIN Products USING(SKU)
        GROUP BY SKU, name
        ORDER BY total_sold DESC
        LIMIT 10;
    """
    cursor.execute(query)
    return cursor.fetchall()

# In main.py
def top_selling_products_callback():
    data = reporting.top_selling_products(cursor)
    columns = ("SKU", "Product Name", "Total Sold")
    rows = [(d['SKU'], d['name'], d['total_sold']) for d in data]
    pos_app.reports_ui.display_report(columns, rows)

# In Ui.py
# Add a button in ReportsUI and wire it to the callback
```

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## 📬 Contact

For questions or feedback, contact the maintainer: [ahsanxhah056@gmail.com]