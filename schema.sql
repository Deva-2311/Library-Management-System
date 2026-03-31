-- ============================================
-- Library Management System - Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'member') DEFAULT 'member',
    phone VARCHAR(20),
    address TEXT,
    joined_date DATE DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(150) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    genre VARCHAR(80),
    publisher VARCHAR(150),
    year_published YEAR,
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1,
    description TEXT,
    cover_url VARCHAR(500),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    reserved_date DATE DEFAULT (CURRENT_DATE),
    due_date DATE,
    return_date DATE,
    status ENUM('reserved', 'borrowed', 'returned', 'overdue', 'cancelled') DEFAULT 'reserved',
    fine_amount DECIMAL(6,2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- ============================================
-- Seed Data
-- ============================================

-- Admin user (password: admin123)
INSERT INTO users (name, email, password, role, phone) VALUES
('Admin User', 'admin@library.com', 'pbkdf2:sha256:600000$salt$hashedpassword', 'admin', '9876543210'),
('Arjun Kumar', 'arjun@email.com', 'pbkdf2:sha256:600000$salt$hashedpassword2', 'member', '9123456780'),
('Priya Sharma', 'priya@email.com', 'pbkdf2:sha256:600000$salt$hashedpassword3', 'member', '9234567891'),
('Ravi Nair', 'ravi@email.com', 'pbkdf2:sha256:600000$salt$hashedpassword4', 'member', '9345678902');

-- Books
INSERT INTO books (title, author, isbn, genre, publisher, year_published, total_copies, available_copies, description) VALUES
('The Pragmatic Programmer', 'David Thomas, Andrew Hunt', '978-0135957059', 'Technology', 'Addison-Wesley', 2019, 3, 2, 'Your journey to mastery in software development.'),
('Clean Code', 'Robert C. Martin', '978-0132350884', 'Technology', 'Prentice Hall', 2008, 2, 1, 'A handbook of agile software craftsmanship.'),
('Wings of Fire', 'A.P.J. Abdul Kalam', '978-8173711466', 'Autobiography', 'Universities Press', 1999, 5, 5, 'Autobiography of the missile man of India.'),
('The Alchemist', 'Paulo Coelho', '978-0062315007', 'Fiction', 'HarperOne', 1988, 4, 3, 'A journey of self-discovery and destiny.'),
('Design Patterns', 'Gang of Four', '978-0201633610', 'Technology', 'Addison-Wesley', 1994, 2, 2, 'Elements of reusable object-oriented software.'),
('Sapiens', 'Yuval Noah Harari', '978-0062316097', 'History', 'Harper', 2011, 3, 2, 'A brief history of humankind.'),
('Introduction to Algorithms', 'Cormen, Leiserson, Rivest', '978-0262033848', 'Technology', 'MIT Press', 2009, 3, 1, 'The classic algorithms textbook.'),
('Atomic Habits', 'James Clear', '978-0735211292', 'Self-Help', 'Avery', 2018, 4, 4, 'Tiny changes, remarkable results.'),
('Python Crash Course', 'Eric Matthes', '978-1593279288', 'Technology', 'No Starch Press', 2019, 3, 3, 'A hands-on, project-based introduction to Python.'),
('Rich Dad Poor Dad', 'Robert T. Kiyosaki', '978-1612680194', 'Finance', 'Plata Publishing', 1997, 2, 2, 'What the rich teach their kids about money.');

-- Reservations
INSERT INTO reservations (user_id, book_id, reserved_date, due_date, return_date, status) VALUES
(2, 1, '2025-11-01', '2025-11-15', '2025-11-13', 'returned'),
(3, 2, '2025-11-10', '2025-11-24', NULL, 'borrowed'),
(4, 7, '2025-11-05', '2025-11-19', NULL, 'overdue'),
(2, 4, '2025-11-20', '2025-12-04', NULL, 'borrowed');
