CREATE DATABASE IF NOT EXISTS smartpaydb;

USE smartpaydb;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_name VARCHAR(100),

    receiver_name VARCHAR(100),

    amount DECIMAL(10,2),

    transaction_id VARCHAR(255),

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);