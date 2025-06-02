from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    department = db.Column(db.String(100))
    role = db.Column(db.Enum('employee', 'manager', 'admin'), default='employee')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sent_mails = db.relationship('Mail', backref='sender', foreign_keys='Mail.sender_id')
    received_mails = db.relationship('Mail', backref='receiver', foreign_keys='Mail.receiver_id')

class Mail(db.Model):
    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject = db.Column(db.String(200))
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    is_reply = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('ProjectMember', backref='project')

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role = db.Column(db.String(50))

class Reimbursement(db.Model):
    __tablename__ = 'reimbursements'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Numeric(10, 2))
    purpose = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    note = db.Column(db.Text)

class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    log_date = db.Column(db.Date)
    duration_hours = db.Column(db.Numeric(4, 2))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
