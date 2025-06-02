-- 创建数据库
DROP DATABASE IF EXISTS class_project;
CREATE DATABASE class_project DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;
USE class_project;

-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(100),
    role ENUM('employee', 'manager', 'admin') DEFAULT 'employee',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 邮件表
CREATE TABLE mails (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT,
    receiver_id INT,
    subject VARCHAR(200),
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    is_reply BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

-- 公告通知
CREATE TABLE notices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200),
    content TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 项目表
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    description TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 项目成员表（多对多）
CREATE TABLE project_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT,
    user_id INT,
    role VARCHAR(50),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 报销申请
CREATE TABLE reimbursements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT,
    user_id INT,
    amount DECIMAL(10, 2),
    purpose TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- 请假申请表
CREATE TABLE leave_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    leave_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    reason TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INT,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- 考勤记录（可扩展迟到等字段）
CREATE TABLE attendance_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    date DATE,
    check_in TIME,
    check_out TIME,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 工作日志
CREATE TABLE work_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    log_date DATE,
    duration_hours DECIMAL(4,2),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
