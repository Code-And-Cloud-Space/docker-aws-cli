-- MySQL Schema for Salesforce OAuth Session & Token Expiry Management
CREATE DATABASE IF NOT EXISTS salesforce_integration CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE salesforce_integration;

-- 1. Salesforce OAuth Tokens Table (Tracks tokens, instance URL, session ID, and expiration timestamps)
CREATE TABLE IF NOT EXISTS salesforce_oauth_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NULL,
    salesforce_user_id VARCHAR(100) NULL,
    salesforce_org_id VARCHAR(100) NULL,
    salesforce_username VARCHAR(255) NULL,
    instance_url VARCHAR(255) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token_secret_arn VARCHAR(255) NOT NULL COMMENT 'Secret Name / ARN in AWS Secrets Manager',
    token_type VARCHAR(50) DEFAULT 'Bearer',
    issued_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL COMMENT 'Expiration timestamp calculated from OAuth response',
    last_refreshed_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_session_active (session_id, is_active),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;

-- 2. Salesforce Accounts Table
CREATE TABLE IF NOT EXISTS salesforce_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salesforce_id VARCHAR(18) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NULL,
    industry VARCHAR(100) NULL,
    phone VARCHAR(50) NULL,
    website VARCHAR(255) NULL,
    annual_revenue VARCHAR(50) NULL,
    billing_street VARCHAR(255) NULL,
    billing_city VARCHAR(100) NULL,
    billing_state VARCHAR(100) NULL,
    billing_postal_code VARCHAR(50) NULL,
    billing_country VARCHAR(100) NULL,
    raw_payload LONGTEXT NULL,
    sync_status VARCHAR(50) DEFAULT 'SYNCED',
    salesforce_created_date DATETIME NULL,
    salesforce_last_modified_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sf_account_name (name),
    INDEX idx_sf_account_sync (sync_status)
) ENGINE=InnoDB;

-- 3. Salesforce Contacts Table
CREATE TABLE IF NOT EXISTS salesforce_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salesforce_id VARCHAR(18) NOT NULL UNIQUE,
    account_salesforce_id VARCHAR(18) NULL,
    account_id INT NULL,
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NOT NULL,
    name VARCHAR(255) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(50) NULL,
    mobile_phone VARCHAR(50) NULL,
    title VARCHAR(150) NULL,
    department VARCHAR(100) NULL,
    raw_payload LONGTEXT NULL,
    sync_status VARCHAR(50) DEFAULT 'SYNCED',
    salesforce_created_date DATETIME NULL,
    salesforce_last_modified_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES salesforce_accounts(id) ON DELETE SET NULL,
    INDEX idx_sf_contact_email (email),
    INDEX idx_sf_contact_last_name (last_name),
    INDEX idx_sf_contact_account (account_salesforce_id)
) ENGINE=InnoDB;

-- 4. Salesforce Opportunities Table
CREATE TABLE IF NOT EXISTS salesforce_opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salesforce_id VARCHAR(18) NOT NULL UNIQUE,
    account_salesforce_id VARCHAR(18) NULL,
    account_id INT NULL,
    name VARCHAR(255) NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    amount VARCHAR(50) NULL,
    probability VARCHAR(50) NULL,
    close_date DATETIME NULL,
    type VARCHAR(100) NULL,
    lead_source VARCHAR(100) NULL,
    raw_payload LONGTEXT NULL,
    sync_status VARCHAR(50) DEFAULT 'SYNCED',
    salesforce_created_date DATETIME NULL,
    salesforce_last_modified_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES salesforce_accounts(id) ON DELETE SET NULL,
    INDEX idx_sf_opp_name (name),
    INDEX idx_sf_opp_stage (stage_name),
    INDEX idx_sf_opp_account (account_salesforce_id)
) ENGINE=InnoDB;
