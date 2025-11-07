-- Autocare Database Initialization Script
-- This script creates the database schema and populates it with sample data

USE autocare_db;

-- Drop tables if they exist to ensure clean setup
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS maintenance_schedule;
DROP TABLE IF EXISTS service_records;

-- Create service_records table if it doesn't exist
CREATE TABLE service_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    service_date DATE NOT NULL,
    description TEXT,
    mileage INT,
    cost DECIMAL(10,2),
    technician VARCHAR(100),
    next_service_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_service_date (service_date),
    INDEX idx_service_type (service_type)
);

-- Create maintenance_schedule table for preventive maintenance
CREATE TABLE maintenance_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(50) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    interval_miles INT,
    interval_months INT,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_vehicle_type (vehicle_type)
);

-- Create appointments table for booking service slots
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50),
    vehicle_id VARCHAR(50) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    status ENUM('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'scheduled',
    technician VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_time (appointment_time),
    INDEX idx_status (status),
    INDEX idx_vehicle_id (vehicle_id),
    UNIQUE KEY unique_slot (appointment_date, appointment_time, technician)
);

-- Create indexes for better performance
-- ALTER TABLE maintenance_schedule ADD INDEX IF NOT EXISTS idx_priority (priority);

-- Insert sample service records
INSERT INTO service_records (vehicle_id, service_type, service_date, description, mileage, cost, technician, next_service_date) VALUES
('ABC123', 'Oil Change', '2024-01-15', 'Changed oil and oil filter, checked all fluid levels', 15000, 45.99, 'John Smith', '2024-04-15'),
('ABC123', 'Tire Rotation', '2024-01-15', 'Rotated tires for even wear, balanced wheels', 15000, 25.00, 'John Smith', '2024-07-15'),
('ABC123', 'Brake Inspection', '2024-02-20', 'Inspected brake pads and rotors, replaced front pads', 16500, 89.99, 'Mike Johnson', '2024-08-20'),
('XYZ789', 'Oil Change', '2024-03-10', 'Synthetic oil change, replaced air filter', 22000, 52.50, 'Sarah Davis', '2024-06-10'),
('XYZ789', 'Battery Test', '2024-03-10', 'Battery tested at 12.6V, performing well', 22000, 0.00, 'Sarah Davis', '2025-03-10'),
('DEF456', 'Transmission Service', '2024-04-05', 'Changed transmission fluid and filter', 35000, 125.00, 'Tom Wilson', '2025-04-05'),
('DEF456', 'Cooling System Flush', '2024-04-05', 'Flushed radiator and replaced coolant', 35000, 75.50, 'Tom Wilson', '2026-04-05'),
('GHI012', 'Spark Plugs', '2024-05-12', 'Replaced all 4 spark plugs', 18000, 95.99, 'Lisa Brown', '2026-05-12'),
('GHI012', 'Air Filter', '2024-05-12', 'Replaced engine air filter', 18000, 15.99, 'Lisa Brown', '2025-05-12'),
('JKL345', 'Wheel Alignment', '2024-06-18', 'Four-wheel alignment, adjusted camber and toe', 28000, 79.99, 'David Lee', '2025-06-18'),
('JKL345', 'Tire Replacement', '2024-06-18', 'Replaced all four tires with Michelin Pilot Sport 4S', 28000, 599.99, 'David Lee', '2027-06-18'),
('MNO678', 'AC Recharge', '2024-07-25', 'Recharged AC system, checked for leaks', 32000, 129.99, 'Anna Garcia', '2025-07-25'),
('PQR901', 'Fuel System Clean', '2024-08-08', 'Fuel injection cleaning service', 25000, 89.99, 'Robert Taylor', '2025-08-08'),
('STU234', 'Timing Belt', '2024-09-14', 'Replaced timing belt and water pump', 60000, 450.00, 'Karen White', '2028-09-14'),
('VWX567', 'Brake Replacement', '2024-10-02', 'Complete brake job - pads, rotors, calipers', 42000, 349.99, 'Chris Martinez', '2026-10-02');

-- Insert maintenance schedule data
INSERT INTO maintenance_schedule (vehicle_type, service_type, interval_miles, interval_months, description, priority) VALUES
('sedan', 'Oil Change', 5000, 6, 'Regular oil and filter change', 'high'),
('sedan', 'Tire Rotation', 6000, 6, 'Rotate tires for even wear', 'medium'),
('sedan', 'Brake Inspection', 10000, 12, 'Check brake pads and rotors', 'high'),
('sedan', 'Air Filter', 15000, 12, 'Replace engine air filter', 'medium'),
('sedan', 'Cabin Filter', 15000, 12, 'Replace cabin air filter', 'low'),
('sedan', 'Battery Test', 20000, 24, 'Test battery voltage and condition', 'medium'),
('sedan', 'Transmission Service', 30000, 24, 'Change transmission fluid', 'high'),
('sedan', 'Cooling System', 30000, 24, 'Flush coolant system', 'high'),
('sedan', 'Spark Plugs', 30000, 36, 'Replace spark plugs', 'medium'),
('sedan', 'Fuel Filter', 30000, 24, 'Replace fuel filter', 'medium'),
('sedan', 'Wheel Alignment', 12000, 12, 'Check and adjust wheel alignment', 'medium'),
('sedan', 'Tire Replacement', 40000, 36, 'Replace tires based on wear', 'medium'),
('SUV', 'Oil Change', 5000, 6, 'Regular oil and filter change', 'high'),
('SUV', 'Tire Rotation', 6000, 6, 'Rotate tires for even wear', 'medium'),
('SUV', 'Brake Inspection', 10000, 12, 'Check brake pads and rotors', 'high'),
('truck', 'Oil Change', 5000, 6, 'Regular oil and filter change', 'high'),
('truck', 'Tire Rotation', 6000, 6, 'Rotate tires for even wear', 'medium'),
('truck', 'Brake Inspection', 10000, 12, 'Check brake pads and rotors', 'high');

-- Insert sample appointment data
INSERT INTO appointments (customer_id, vehicle_id, service_type, appointment_date, appointment_time, duration_minutes, status, technician, notes) VALUES
('CUST001', 'ABC123', 'Oil Change', '2024-12-01', '09:00:00', 30, 'scheduled', 'John Smith', 'Regular maintenance'),
('CUST002', 'XYZ789', 'Brake Inspection', '2024-12-01', '10:00:00', 45, 'confirmed', 'Mike Johnson', 'Customer requested early morning'),
('CUST003', 'DEF456', 'Tire Rotation', '2024-12-02', '14:00:00', 30, 'scheduled', 'Sarah Davis', 'Include alignment check'),
('CUST001', 'ABC123', 'Complete Service', '2024-12-15', '11:00:00', 120, 'scheduled', 'Tom Wilson', 'Full service package');

-- Additional dummy data for testing and development
INSERT INTO service_records (vehicle_id, service_type, service_date, description, mileage, cost, technician) VALUES
('SAMPLE001', 'Oil Change', '2024-11-01', '10W-30 conventional oil change', 12500, 29.99, 'Tech A'),
('SAMPLE001', 'Tire Rotation', '2024-11-01', 'Standard tire rotation service', 12500, 19.99, 'Tech A'),
('SAMPLE002', 'Brake Service', '2024-10-15', 'Front brake pad replacement', 45000, 149.99, 'Tech B'),
('SAMPLE002', 'Battery Replacement', '2024-09-20', 'Replaced 12V battery', 42000, 89.99, 'Tech C'),
('SAMPLE003', 'AC Service', '2024-08-10', 'AC recharge and leak test', 38000, 99.99, 'Tech D'),
('SAMPLE004', 'Transmission Flush', '2024-07-05', 'Complete transmission fluid flush', 55000, 179.99, 'Tech E'),
('SAMPLE005', 'Spark Plug Replacement', '2024-06-12', 'Replaced all spark plugs', 30000, 119.99, 'Tech F'),
('SAMPLE006', 'Wheel Alignment', '2024-05-08', 'Full wheel alignment service', 25000, 69.99, 'Tech G'),
('SAMPLE007', 'Fuel System Cleaning', '2024-04-15', 'Fuel injection cleaning', 35000, 79.99, 'Tech H'),
('SAMPLE008', 'Coolant Flush', '2024-03-20', 'Radiator coolant flush and refill', 40000, 59.99, 'Tech I');

INSERT INTO maintenance_schedule (vehicle_type, service_type, interval_miles, interval_months, description, priority) VALUES
('hatchback', 'Oil Change', 5000, 6, 'Regular oil and filter change for hatchback', 'high'),
('hatchback', 'Tire Rotation', 6000, 6, 'Rotate tires for even wear on hatchback', 'medium'),
('coupe', 'Oil Change', 5000, 6, 'Regular oil and filter change for coupe', 'high'),
('coupe', 'Brake Inspection', 10000, 12, 'Check brake system for sports coupe', 'high'),
('convertible', 'Oil Change', 5000, 6, 'Regular oil and filter change for convertible', 'high'),
('convertible', 'Soft Top Care', 12000, 12, 'Clean and condition convertible top', 'medium'),
('minivan', 'Oil Change', 5000, 6, 'Regular oil and filter change for minivan', 'high'),
('minivan', 'Multi-Point Inspection', 6000, 6, 'Comprehensive vehicle inspection', 'high'),
('crossover', 'Oil Change', 5000, 6, 'Regular oil and filter change for crossover', 'high'),
('crossover', 'All-Wheel Drive Service', 10000, 12, 'Service AWD system components', 'medium');

INSERT INTO appointments (customer_id, vehicle_id, service_type, appointment_date, appointment_time, duration_minutes, status, technician, notes) VALUES
('CUST004', 'TEST001', 'Oil Change', '2025-11-12', '09:00:00', 30, 'scheduled', 'Tech A', 'Test booking - fully booked day'),
('CUST005', 'TEST002', 'Brake Service', '2025-11-12', '09:30:00', 30, 'confirmed', 'Tech B', 'Test booking - fully booked day'),
('CUST006', 'TEST003', 'Tire Rotation', '2025-11-12', '10:00:00', 30, 'scheduled', 'Tech C', 'Test booking - fully booked day'),
('CUST007', 'TEST004', 'Battery Check', '2025-11-12', '10:30:00', 30, 'confirmed', 'Tech A', 'Test booking - fully booked day'),
('CUST008', 'TEST005', 'Oil Change', '2025-11-14', '11:00:00', 30, 'scheduled', 'Tech B', 'Test booking - fully booked day'),
('CUST009', 'TEST006', 'Maintenance', '2025-11-14', '11:30:00', 30, 'confirmed', 'Tech C', 'Test booking - fully booked day'),
('CUST010', 'TEST007', 'Inspection', '2025-11-12', '13:00:00', 30, 'scheduled', 'Tech A', 'Test booking - fully booked day'),
('CUST011', 'TEST008', 'Oil Change', '2025-11-12', '13:30:00', 30, 'confirmed', 'Tech B', 'Test booking - fully booked day'),
('CUST012', 'TEST009', 'Brake Service', '2025-11-14', '14:00:00', 30, 'scheduled', 'Tech C', 'Test booking - fully booked day'),
('CUST013', 'TEST010', 'Tire Service', '2025-11-14', '14:30:00', 30, 'confirmed', 'Tech A', 'Test booking - fully booked day'),
('CUST014', 'TEST011', 'Oil Change', '2025-11-14', '15:00:00', 30, 'scheduled', 'Tech B', 'Test booking - fully booked day'),
('CUST015', 'TEST012', 'Maintenance', '2025-11-12', '15:30:00', 30, 'confirmed', 'Tech C', 'Test booking - fully booked day'),
('CUST016', 'TEST013', 'Inspection', '2025-11-12', '16:00:00', 30, 'scheduled', 'Tech A', 'Test booking - fully booked day'),
('CUST017', 'TEST014', 'Oil Change', '2025-11-14', '16:30:00', 30, 'confirmed', 'Tech B', 'Test booking - fully booked day');

-- Create view for upcoming services
DROP VIEW IF EXISTS upcoming_services;
CREATE VIEW upcoming_services AS
SELECT
    sr.vehicle_id,
    sr.service_type,
    sr.service_date as last_service_date,
    sr.mileage as last_mileage,
    DATE_ADD(sr.service_date, INTERVAL ms.interval_months MONTH) as next_due_date,
    (sr.mileage + ms.interval_miles) as next_due_mileage,
    ms.description,
    ms.priority,
    DATEDIFF(DATE_ADD(sr.service_date, INTERVAL ms.interval_months MONTH), CURDATE()) as days_until_due
FROM service_records sr
JOIN maintenance_schedule ms ON sr.service_type = ms.service_type
WHERE DATE_ADD(sr.service_date, INTERVAL ms.interval_months MONTH) >= CURDATE()
ORDER BY next_due_date ASC;