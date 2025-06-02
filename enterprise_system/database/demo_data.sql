USE class_project;

-- 用户表（律师事务所常见角色）
INSERT INTO users (username, password, email, department, role, description) VALUES
('李明', '123456', 'li.ming@lawfirm.com', '刑事部', 'employee', '专注于刑事辩护，参与多起重大案件'),
('张伟', 'abc123', 'zhang.wei@lawfirm.com', '民事部', 'employee', '处理合同纠纷、婚姻继承等民事案件'),
('孙立', 'abcdefg', 'sun.li@lawfirm.com', '合伙人', 'manager', '合伙人律师，擅长企业合规与顾问服务'),
('刘原', '123456', 'liu.yan@lawfirm.com', '行政部', 'employee', '负责考勤、公告发布、文书归档'),
('admin', 'admin123', 'admin@lawfirm.com', '系统管理', 'admin', '系统维护人员，管理权限与账号');

-- 公告
INSERT INTO notices (title, content, created_by) VALUES
('关于“五一”假期安排', '本所将于5月1日至5月3日放假，5月4日恢复办公，请各位律师提前协调案件安排。', 4),
('新员工入职流程更新', '为提高入职效率，新增线上文档系统，请于5月10日前学习完毕。', 5);

-- 项目（律所案件/顾问项目）
INSERT INTO projects (name, description, created_by) VALUES
('张三涉嫌诈骗案', '为当事人张三提供刑事辩护服务，已进入法庭审理阶段', 1),
('某科技公司常年法律顾问', '提供合同审核、合规咨询、知识产权保护等服务', 3);

-- 项目成员
INSERT INTO project_members (project_id, user_id, role) VALUES
(1, 1, '主辩律师'),
(1, 2, '助理律师'),
(1, 3, '指导合伙人'),
(2, 3, '首席顾问'),
(2, 4, '行政协调');

-- 邮件
INSERT INTO mails (sender_id, receiver_id, subject, content, is_reply) VALUES
(2, 1, '证据材料整理完成', '已整理张三案相关证据清单，请查收并准备交叉询问提纲。', FALSE),
(1, 2, '收到，谢谢', '好的，我这边会在今天下午完成提纲准备。', TRUE),
(3, 4, '顾问服务合同归档', '请将已签订的科技公司顾问合同扫描并归档至系统。', FALSE);

-- 报销申请（贴合律师事务所场景）
INSERT INTO reimbursements (project_id, user_id, amount, purpose, status, approved_by, approved_at) VALUES
(1, 1, 560.00, '前往法院的交通与工作餐费用', 'approved', 3, NOW()),
(2, 4, 200.00, '打印顾问服务材料', 'pending', NULL, NULL);

-- 请假记录
INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status, approved_by, approved_at) VALUES
(2, '事假', '2025-05-05', '2025-05-06', '家中有事需请假两日', 'approved', 3, NOW()),
(1, '病假', '2025-05-08', '2025-05-09', '突发感冒', 'pending', NULL, NULL);

-- 考勤记录
INSERT INTO attendance_records (user_id, date, check_in, check_out, note) VALUES
(1, '2025-05-10', '09:00:00', '18:00:00', '前往法院出庭'),
(2, '2025-05-10', '09:05:00', '17:55:00', '案件资料准备'),
(3, '2025-05-10', '09:00:00', '19:00:00', '企业顾问咨询会议');

-- 工作日志
INSERT INTO work_logs (user_id, log_date, duration_hours, content) VALUES
(1, '2025-05-10', 8.0, '出庭为张三辩护，庭后与家属沟通案件进展'),
(2, '2025-05-10', 7.5, '协助准备案件文件，整理证据目录'),
(3, '2025-05-10', 9.0, '参与企业客户法律顾问服务会议，拟定顾问报告');
