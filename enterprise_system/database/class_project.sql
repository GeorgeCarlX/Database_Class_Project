/*
 Navicat Premium Data Transfer

 Source Server         : web_security
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : class_project

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 02/06/2025 15:21:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for attendance_records
-- ----------------------------
DROP TABLE IF EXISTS `attendance_records`;
CREATE TABLE `attendance_records`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NULL DEFAULT NULL,
  `date` date NULL DEFAULT NULL,
  `check_in` time(0) NULL DEFAULT NULL,
  `check_out` time(0) NULL DEFAULT NULL,
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attendance_records
-- ----------------------------
INSERT INTO `attendance_records` VALUES (1, 1, '2025-05-10', '09:00:00', '18:00:00', '前往法院出庭');
INSERT INTO `attendance_records` VALUES (2, 2, '2025-05-10', '09:05:00', '17:55:00', '案件资料准备');
INSERT INTO `attendance_records` VALUES (3, 3, '2025-05-10', '09:00:00', '19:00:00', '企业顾问咨询会议');
INSERT INTO `attendance_records` VALUES (4, 6, '2025-06-01', '22:39:36', '22:39:52', NULL);

-- ----------------------------
-- Table structure for leave_requests
-- ----------------------------
DROP TABLE IF EXISTS `leave_requests`;
CREATE TABLE `leave_requests`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NULL DEFAULT NULL,
  `leave_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `start_date` date NULL DEFAULT NULL,
  `end_date` date NULL DEFAULT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `status` enum('pending','approved','rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'pending',
  `submitted_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` int(11) NULL DEFAULT NULL,
  `approved_at` timestamp(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `approved_by`(`approved_by`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of leave_requests
-- ----------------------------
INSERT INTO `leave_requests` VALUES (1, 2, '事假', '2025-05-05', '2025-05-06', '家中有事需请假两日', 'approved', '2025-05-17 14:21:20', 3, '2025-05-17 14:21:20');
INSERT INTO `leave_requests` VALUES (2, 1, '病假', '2025-05-08', '2025-05-09', '突发感冒', 'approved', '2025-05-17 14:21:20', 6, '2025-06-02 06:45:15');

-- ----------------------------
-- Table structure for mails
-- ----------------------------
DROP TABLE IF EXISTS `mails`;
CREATE TABLE `mails`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender_id` int(11) NULL DEFAULT NULL,
  `receiver_id` int(11) NULL DEFAULT NULL,
  `subject` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `is_read` tinyint(1) NULL DEFAULT 0,
  `is_reply` tinyint(1) NULL DEFAULT 0,
  `sent_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `sender_id`(`sender_id`) USING BTREE,
  INDEX `receiver_id`(`receiver_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of mails
-- ----------------------------
INSERT INTO `mails` VALUES (1, 2, 1, '证据材料整理完成', '已整理张三案相关证据清单，请查收并准备交叉询问提纲。', 0, 0, '2025-05-17 14:21:20');
INSERT INTO `mails` VALUES (2, 1, 2, '收到，谢谢', '好的，我这边会在今天下午完成提纲准备。', 0, 1, '2025-05-17 14:21:20');
INSERT INTO `mails` VALUES (3, 3, 4, '顾问服务合同归档', '请将已签订的科技公司顾问合同扫描并归档至系统。', 0, 0, '2025-05-17 14:21:20');
INSERT INTO `mails` VALUES (4, 6, 6, '测试邮件', '这是一封测试邮件', 0, 0, '2025-06-01 13:39:48');
INSERT INTO `mails` VALUES (5, 6, 1, '测试邮件', '这是一封测试邮件', 0, 0, '2025-06-01 13:39:54');
INSERT INTO `mails` VALUES (6, 6, 1, '测试邮', '这是一封测试邮件', 0, 0, '2025-06-01 13:40:01');
INSERT INTO `mails` VALUES (7, 6, 6, '第二封自己发给自己的测试邮件', '这是一封测试邮件', 1, 1, '2025-06-01 13:46:43');
INSERT INTO `mails` VALUES (9, 6, 6, 'Re: 第二封自己发给自己的测试邮件', '收到测试，谢谢！', 0, 0, '2025-06-01 14:11:54');

-- ----------------------------
-- Table structure for notices
-- ----------------------------
DROP TABLE IF EXISTS `notices`;
CREATE TABLE `notices`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_by` int(11) NULL DEFAULT NULL,
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `created_by`(`created_by`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of notices
-- ----------------------------
INSERT INTO `notices` VALUES (1, '关于“五一”假期安排', '本所将于5月1日至5月3日放假，5月4日恢复办公，请各位律师提前协调案件安排。', 5, '2025-05-17 14:21:20');
INSERT INTO `notices` VALUES (2, '新员工入职流程更新', '为提高入职效率，新增线上文档系统，请于5月10日前学习完毕。', 5, '2025-05-17 14:21:20');
INSERT INTO `notices` VALUES (3, '[全体员工]系统升级通知', '本周五晚20:00-24:00进行系统升级，期间暂停服务...', 6, '2025-06-01 14:33:23');

-- ----------------------------
-- Table structure for project_members
-- ----------------------------
DROP TABLE IF EXISTS `project_members`;
CREATE TABLE `project_members`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NULL DEFAULT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `project_id`(`project_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of project_members
-- ----------------------------
INSERT INTO `project_members` VALUES (1, 1, 1, '主辩律师');
INSERT INTO `project_members` VALUES (2, 1, 2, '助理律师');
INSERT INTO `project_members` VALUES (3, 1, 3, '指导合伙人');
INSERT INTO `project_members` VALUES (4, 2, 3, '首席顾问');
INSERT INTO `project_members` VALUES (5, 2, 4, '行政协调');

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_by` int(11) NULL DEFAULT NULL,
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `created_by`(`created_by`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of projects
-- ----------------------------
INSERT INTO `projects` VALUES (1, '张三涉嫌诈骗案', '为当事人张三提供刑事辩护服务，已进入法庭审理阶段', 1, '2025-05-17 14:21:20');
INSERT INTO `projects` VALUES (2, '某科技公司常年法律顾问', '提供合同审核、合规咨询、知识产权保护等服务', 3, '2025-05-17 14:21:20');

-- ----------------------------
-- Table structure for reimbursements
-- ----------------------------
DROP TABLE IF EXISTS `reimbursements`;
CREATE TABLE `reimbursements`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NULL DEFAULT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL,
  `purpose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `status` enum('pending','approved','rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'pending',
  `submitted_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` int(11) NULL DEFAULT NULL,
  `approved_at` timestamp(0) NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `project_id`(`project_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `approved_by`(`approved_by`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of reimbursements
-- ----------------------------
INSERT INTO `reimbursements` VALUES (1, 1, 1, 560.00, '前往法院的交通与工作餐费用', 'approved', '2025-05-17 14:21:20', 3, '2025-05-17 14:21:20');
INSERT INTO `reimbursements` VALUES (2, 2, 4, 200.00, '打印顾问服务材料', 'approved', '2025-05-17 14:21:20', 6, '2025-06-02 06:51:59');
INSERT INTO `reimbursements` VALUES (3, 1, 6, 1250.50, '项目差旅费', 'pending', '2025-06-02 06:52:54', NULL, NULL);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `role` enum('employee','manager','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'employee',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  UNIQUE INDEX `email`(`email`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '李明', '123456', 'li.ming@lawfirm.com', '刑事部', 'employee', '专注于刑事辩护，参与多起重大案件', '2025-05-17 14:21:20');
INSERT INTO `users` VALUES (2, '张伟', 'abc123', 'zhang.wei@lawfirm.com', '民事部', 'employee', '处理合同纠纷、婚姻继承等民事案件', '2025-05-17 14:21:20');
INSERT INTO `users` VALUES (3, '孙立', 'abcdefg', 'sun.li@lawfirm.com', '合伙人', 'manager', '合伙人律师，擅长企业合规与顾问服务', '2025-05-17 14:21:20');
INSERT INTO `users` VALUES (4, '刘原', '123456', 'liu.yan@lawfirm.com', '行政部', 'employee', '负责考勤、公告发布、文书归档', '2025-05-17 14:21:20');
INSERT INTO `users` VALUES (5, 'admin', 'admin123', 'admin@lawfirm.com', '系统管理', 'admin', '系统维护人员，管理权限与账号', '2025-05-17 14:21:20');
INSERT INTO `users` VALUES (6, 'testman', '123456', 'alice@example.com', '研发部', 'admin', NULL, '2025-06-01 13:11:52');

-- ----------------------------
-- Table structure for work_logs
-- ----------------------------
DROP TABLE IF EXISTS `work_logs`;
CREATE TABLE `work_logs`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NULL DEFAULT NULL,
  `log_date` date NULL DEFAULT NULL,
  `duration_hours` decimal(4, 2) NULL DEFAULT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of work_logs
-- ----------------------------
INSERT INTO `work_logs` VALUES (1, 1, '2025-05-10', 8.00, '出庭为张三辩护，庭后与家属沟通案件进展', '2025-05-17 14:21:20');
INSERT INTO `work_logs` VALUES (2, 2, '2025-05-10', 7.50, '协助准备案件文件，整理证据目录', '2025-05-17 14:21:20');
INSERT INTO `work_logs` VALUES (3, 3, '2025-05-10', 9.00, '参与企业客户法律顾问服务会议，拟定顾问报告', '2025-05-17 14:21:20');
INSERT INTO `work_logs` VALUES (4, 6, '2025-06-02', 8.50, '完成项目模块开发和单元测试', '2025-06-02 06:56:31');

SET FOREIGN_KEY_CHECKS = 1;
