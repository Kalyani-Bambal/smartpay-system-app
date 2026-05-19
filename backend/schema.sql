CREATE DATABASE IF NOT EXISTS smartpaydb;

USE smartpaydb;

CREATE TABLE transactions (

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_name VARCHAR(100),

    receiver_name VARCHAR(100),

    amount DECIMAL(10,2),

    transaction_id VARCHAR(255),

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);