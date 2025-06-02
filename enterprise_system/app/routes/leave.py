# 请假申请与审批
# app/routes/leave.py
from flask import Blueprint, request, jsonify, session
from app.models import db, LeaveRequest, User
from datetime import datetime, date
from sqlalchemy import or_

bp = Blueprint('leave', __name__, url_prefix='/leave')

# 辅助函数：检查用户是否为管理员或部门经理
def is_manager_or_admin(user_id):
    user = User.query.get(user_id)
    return user and (user.role == 'admin' or user.role == 'manager')

# 1. 提交请假申请
@bp.route('/submit', methods=['POST'])
def submit_leave_request():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    data = request.json
    leave_type = data.get('leave_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason')
    
    if not all([leave_type, start_date, end_date, reason]):
        return jsonify({'status': 'error', 'message': '请填写完整的请假信息'}), 400
    
    # 日期格式转换
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'status': 'error', 'message': '日期格式错误，应为YYYY-MM-DD'}), 400
    
    # 检查结束日期是否早于开始日期
    if end_date < start_date:
        return jsonify({'status': 'error', 'message': '结束日期不能早于开始日期'}), 400
    
    new_leave = LeaveRequest(
        user_id=user_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status='pending',
        submitted_at=datetime.utcnow()
    )
    
    db.session.add(new_leave)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '请假申请已提交',
        'leave_id': new_leave.id
    })

# 2. 获取当前用户的请假记录
@bp.route('/my_requests', methods=['GET'])
def get_my_leave_requests():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取用户的所有请假记录，按提交时间降序排列
    leave_requests = LeaveRequest.query.filter_by(user_id=user_id).order_by(
        LeaveRequest.submitted_at.desc()
    ).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_leave_request(req) for req in leave_requests]
    })

# 3. 管理员/经理获取待审批的请假申请
@bp.route('/pending', methods=['GET'])
def get_pending_leave_requests():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员或经理可以查看待审批的请假申请
    if not is_manager_or_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取所有待审批的请假申请
    pending_requests = LeaveRequest.query.filter_by(
        status='pending'
    ).order_by(
        LeaveRequest.submitted_at.asc()
    ).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_leave_request(req) for req in pending_requests]
    })

# 4. 审批请假申请
@bp.route('/approve/<int:leave_id>', methods=['POST'])
def approve_leave_request(leave_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员或经理可以审批请假申请
    if not is_manager_or_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限审批'}), 403
    
    leave_request = LeaveRequest.query.get(leave_id)
    if not leave_request:
        return jsonify({'status': 'error', 'message': '请假申请不存在'}), 404
    
    # 只能审批待处理的申请
    if leave_request.status != 'pending':
        return jsonify({'status': 'error', 'message': '该申请已处理'}), 400
    
    data = request.json
    action = data.get('action')  # 'approve' 或 'reject'
    comment = data.get('comment', '')
    
    if action == 'approve':
        leave_request.status = 'approved'
    elif action == 'reject':
        leave_request.status = 'rejected'
    else:
        return jsonify({'status': 'error', 'message': '无效的审批动作'}), 400
    
    leave_request.approved_by = user_id
    leave_request.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'请假申请已{action}通过',
        'status': leave_request.status
    })

# 5. 获取所有请假记录（管理员/经理）
@bp.route('/all', methods=['GET'])
def get_all_leave_requests():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员或经理可以查看所有请假记录
    if not is_manager_or_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取所有请假记录，按提交时间降序排列
    all_requests = LeaveRequest.query.order_by(
        LeaveRequest.submitted_at.desc()
    ).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_leave_request(req) for req in all_requests]
    })

# 6. 获取单个请假记录详情
@bp.route('/detail/<int:leave_id>', methods=['GET'])
def get_leave_request_detail(leave_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    leave_request = LeaveRequest.query.get(leave_id)
    if not leave_request:
        return jsonify({'status': 'error', 'message': '请假申请不存在'}), 404
    
    # 普通用户只能查看自己的请假记录
    if leave_request.user_id != user_id and not is_manager_or_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限查看'}), 403
    
    return jsonify({
        'status': 'success',
        'request': _format_leave_request(leave_request)
    })

# 辅助函数：格式化请假申请数据
def _format_leave_request(req):
    user = User.query.get(req.user_id)
    approver = User.query.get(req.approved_by) if req.approved_by else None
    
    return {
        'id': req.id,
        'user_id': req.user_id,
        'username': user.username if user else '未知',
        'leave_type': req.leave_type,
        'start_date': req.start_date.strftime('%Y-%m-%d'),
        'end_date': req.end_date.strftime('%Y-%m-%d'),
        'duration': (req.end_date - req.start_date).days + 1,  # 计算请假天数
        'reason': req.reason,
        'status': req.status,
        'submitted_at': req.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        'approved_by': approver.username if approver else '未审批',
        'approved_at': req.approved_at.strftime('%Y-%m-%d %H:%M:%S') if req.approved_at else '未审批'
    }