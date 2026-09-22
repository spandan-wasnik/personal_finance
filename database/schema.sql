
CREATE DATABASE IF NOT EXISTS personal_finance;
USE personal_finance;

-- Users table: stores login information for each user
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table: every income/expense record
CREATE TABLE IF NOT EXISTS transactions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    date            DATE NOT NULL,
    description     VARCHAR(255),
    amount          DECIMAL(12,2) NOT NULL,
    type            ENUM('income','expense') NOT NULL,
    category        VARCHAR(100) DEFAULT 'Other',
    expense_type    ENUM('fixed','recurring_variable','variable') DEFAULT 'variable',
    payment_mode    ENUM('UPI','Card','Bank Transfer','Cash','Other') DEFAULT 'Other',
    source          VARCHAR(100) DEFAULT 'Manual',
    notes           TEXT,
    is_unusual      TINYINT(1) DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Budgets table: monthly overall budget per user
CREATE TABLE IF NOT EXISTS budgets (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    month   INT NOT NULL,
    year    INT NOT NULL,
    amount  DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_budget (user_id, month, year)
);

-- Category budgets: per-category spending limits
CREATE TABLE IF NOT EXISTS category_budgets (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    category      VARCHAR(100) NOT NULL,
    month         INT NOT NULL,
    year          INT NOT NULL,
    budget_amount DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cat_budget (user_id, category, month, year)
);

-- Financial goals table
CREATE TABLE IF NOT EXISTS financial_goals (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT NOT NULL,
    goal_name            VARCHAR(200) NOT NULL,
    target_amount        DECIMAL(12,2) NOT NULL,
    current_amount       DECIMAL(12,2) DEFAULT 0,
    monthly_contribution DECIMAL(12,2) DEFAULT 0,
    target_date          DATE,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
