

-- Create RawMaterials table
CREATE TABLE RawMaterials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Create Products table
ALTER TABLE Products
ADD COLUMN material_id INT Not null;
ALTER TABLE Products
ADD CONSTRAINT fk_material_id
FOREIGN KEY (material_id) REFERENCES RawMaterials(material_id);


-- Create WheatProduction table
CREATE TABLE WheatProduction (
    wheat_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    timestamp DATETIME,
    expected_condition TEXT,
    category VARCHAR(50),
    original_production DECIMAL(10,2),
    delay_percent DECIMAL(5,2),
    expected_production DECIMAL(10,2),
    FOREIGN KEY (material_id) REFERENCES RawMaterials(material_id)
);

-- Create CottonProduction table
CREATE TABLE CottonProduction (
    cotton_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    timestamp DATETIME,
    expected_condition TEXT,
    category VARCHAR(50),
    original_production DECIMAL(10,2),
    delay_percent DECIMAL(5,2),
    expected_production DECIMAL(10,2),
    FOREIGN KEY (material_id) REFERENCES RawMaterials(material_id)
);

-- Create RiceProduction table
CREATE TABLE RiceProduction (
    rice_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    timestamp DATETIME,
    expected_condition TEXT,
    category VARCHAR(50),
    original_production DECIMAL(10,2),
    delay_percent DECIMAL(5,2),
    expected_production DECIMAL(10,2),
    FOREIGN KEY (material_id) REFERENCES RawMaterials(material_id)
);

-- Create SugarcaneProduction table
CREATE TABLE SugarcaneProduction (
    sugarcane_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    timestamp DATETIME,
    expected_condition TEXT,
    category VARCHAR(50),
    original_production DECIMAL(10,2),
    delay_percent DECIMAL(5,2),
    expected_production DECIMAL(10,2),
    FOREIGN KEY (material_id) REFERENCES RawMaterials(material_id)
);