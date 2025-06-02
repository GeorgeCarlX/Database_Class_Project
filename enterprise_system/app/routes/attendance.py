# 考勤记录
# app/routes/attendance.py
from flask import Blueprint, request, jsonify, session
from app.models import db, AttendanceRecord, User
from datetime import datetime, time, timedelta
import calendar

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

# 辅助函数：检查用户是否为管理员
def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

# 1. 打卡（签到/签退）
@bp.route('/check', methods=['POST'])
def check_attendance():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    today = datetime.now().date()
    now_time = datetime.now().time()
    
    # 检查今天是否已有打卡记录
    today_record = AttendanceRecord.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    
    if not today_record:
        # 第一次打卡：签到
        new_record = AttendanceRecord(
            user_id=user_id,
            date=today,
            check_in=now_time
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '签到成功', 'check_in': now_time.strftime('%H:%M:%S')})
    
    elif today_record.check_in and not today_record.check_out:
        # 已有签到记录：签退
        today_record.check_out = now_time
        db.session.commit()
        return jsonify({
            'status': 'success', 
            'message': '签退成功', 
            'check_out': now_time.strftime('%H:%M:%S')
        })
    
    else:
        return jsonify({'status': 'error', 'message': '今日已完成签到和签退'}), 400

# 2. 获取个人考勤记录（支持按月份筛选）
@bp.route('/personal', methods=['GET'])
def get_personal_attendance():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # 获取当月第一天和最后一天
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
    
    records = AttendanceRecord.query.filter(
        AttendanceRecord.user_id == user_id,
        AttendanceRecord.date.between(first_day, last_day)
    ).order_by(AttendanceRecord.date).all()
    
    record_list = []
    for record in records:
        record_list.append({
            'date': record.date.strftime('%Y-%m-%d'),
            'check_in': record.check_in.strftime('%H:%M:%S') if record.check_in else None,
            'check_out': record.check_out.strftime('%H:%M:%S') if record.check_out else None,
            'note': record.note,
            'status': _get_attendance_status(record)  # 迟到、早退等状态
        })
    
    return jsonify({'status': 'success', 'records': record_list})

# 3. 管理员获取部门考勤记录
@bp.route('/department', methods=['GET'])
def get_department_attendance():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    if not is_admin(user_id):
        return jsonify({'status': 'error', 'message': '只有管理员可查看部门考勤'}), 403
    
    department = request.args.get('department')
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    if not department:
        return jsonify({'status': 'error', 'message': '请指定部门'}), 400
    
    # 获取部门所有用户
    users = User.query.filter_by(department=department).all()
    user_ids = [user.id for user in users]
    
    # 获取考勤记录
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
    
    records = AttendanceRecord.query.filter(
        AttendanceRecord.user_id.in_(user_ids),
        AttendanceRecord.date.between(first_day, last_day)
    ).order_by(AttendanceRecord.user_id, AttendanceRecord.date).all()
    
    # 按用户分组
    result = {}
    for user in users:
        user_records = [record for record in records if record.user_id == user.id]
        result[user.username] = [{
            'date': record.date.strftime('%Y-%m-%d'),
            'check_in': record.check_in.strftime('%H:%M:%S') if record.check_in else None,
            'check_out': record.check_out.strftime('%H:%M:%S') if record.check_out else None,
            'note': record.note,
            'status': _get_attendance_status(record)
        } for record in user_records]
    
    return jsonify({'status': 'success', 'attendance': result})

# 4. 管理员添加考勤备注
@bp.route('/add_note/<int:record_id>', methods=['POST'])
def add_attendance_note(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    if not is_admin(user_id):
        return jsonify({'status': 'error', 'message': '只有管理员可添加备注'}), 403
    
    data = request.json
    note = data.get('note')
    
    if not note:
        return jsonify({'status': 'error', 'message': '备注不能为空'}), 400
    
    record = AttendanceRecord.query.get(record_id)
    if not record:
        return jsonify({'status': 'error', 'message': '考勤记录不存在'}), 404
    
    record.note = note
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '备注添加成功'})

# 辅助函数：判断考勤状态
def _get_attendance_status(record):
    # 假设上班时间 9:00，下班时间 18:00
    work_start = time(9, 0)  # 9:00
    work_end = time(18, 0)   # 18:00
    
    status = '正常'
    
    if record.check_in and record.check_in > work_start:
        status = '迟到'
    
    if record.check_out and record.check_out < work_end:
        if status == '迟到':
            status = '迟到+早退'
        else:
            status = '早退'
    
    if not record.check_in or not record.check_out:
        status = '缺勤'
    
    return status