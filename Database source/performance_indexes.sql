-- Performance Optimization Indexes for DigiClimate Store Hub
-- These indexes will dramatically improve dashboard and filter performance

-- Sales table indexes (most critical for dashboard performance)
CREATE INDEX idx_sales_datetime ON Sales(sale_datetime);
CREATE INDEX idx_sales_employee_datetime ON Sales(employee_id, sale_datetime);
CREATE INDEX idx_sales_customer_datetime ON Sales(customer_id, sale_datetime);
CREATE INDEX idx_sales_total_datetime ON Sales(total, sale_datetime);

-- SaleItems table indexes (for transaction details and product analysis)
CREATE INDEX idx_saleitems_sale_id ON SaleItems(sale_id);
CREATE INDEX idx_saleitems_sku_datetime ON SaleItems(SKU, sale_id);
CREATE INDEX idx_saleitems_price_quantity ON SaleItems(price, quantity);

-- Products table indexes (for inventory and category filtering)
CREATE INDEX idx_products_category_id ON Products(category_id);
CREATE INDEX idx_products_supplier_id ON Products(supplier_id);
CREATE INDEX idx_products_stock_threshold ON Products(stock, low_stock_threshold);
CREATE INDEX idx_products_price ON Products(price);
CREATE INDEX idx_products_name ON Products(name);

-- Purchases table indexes (for supplier analysis)
CREATE INDEX idx_purchases_supplier_datetime ON Purchases(supplier_id, purchase_datetime);
CREATE INDEX idx_purchases_datetime ON Purchases(purchase_datetime);
CREATE INDEX idx_purchases_status ON Purchases(delivery_status);

-- PurchaseItems table indexes (for purchase analysis)
CREATE INDEX idx_purchaseitems_purchase_id ON PurchaseItems(purchase_id);
CREATE INDEX idx_purchaseitems_sku ON PurchaseItems(SKU);
CREATE INDEX idx_purchaseitems_cost ON PurchaseItems(unit_cost);

-- InventoryAdjustments table indexes (for adjustment history)
CREATE INDEX idx_adjustments_sku_datetime ON InventoryAdjustments(SKU, adjustment_datetime);
CREATE INDEX idx_adjustments_employee_datetime ON InventoryAdjustments(employee_id, adjustment_datetime);
CREATE INDEX idx_adjustments_datetime ON InventoryAdjustments(adjustment_datetime);

-- Composite indexes for common dashboard queries
CREATE INDEX idx_sales_comprehensive ON Sales(sale_datetime, employee_id, customer_id, total);
CREATE INDEX idx_saleitems_comprehensive ON SaleItems(sale_id, SKU, quantity, price);

-- Covering indexes for frequently accessed data
CREATE INDEX idx_products_dashboard_info ON Products(SKU, name, category_id, price, stock, supplier_id);
CREATE INDEX idx_sales_dashboard_summary ON Sales(sale_datetime, total, employee_id);

-- Text indexes for search functionality
CREATE INDEX idx_products_name_search ON Products(name(50));
CREATE INDEX idx_suppliers_name_search ON Suppliers(name(50));
CREATE INDEX idx_customers_name_search ON Customers(name(50));
CREATE INDEX idx_customers_contact_search ON Customers(contact_info(50));

-- Performance monitoring query
-- Use this to check index usage: SHOW INDEX FROM table_name;
-- Use this to analyze queries: EXPLAIN SELECT ...;
