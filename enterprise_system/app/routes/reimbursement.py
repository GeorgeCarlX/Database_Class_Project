 # 报销申请与审批
# app/routes/reimbursement.py
from flask import Blueprint, request, jsonify, session
from app.models import db, Reimbursement, User, Project
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('reimbursement', __name__, url_prefix='/reimbursement')

# 辅助函数：检查用户是否为管理员或项目负责人
def is_manager_or_admin(user_id, project_id=None):
    user = User.query.get(user_id)
    if not user:
        return False
    
    # 管理员拥有所有权限
    if user.role == 'admin':
        return True
    
    # 项目负责人可以审批自己项目的报销
    if project_id:
        from app.routes.project import is_project_creator  # 避免循环导入
        return is_project_creator(user_id, project_id)
    
    return False

# 1. 提交报销申请
@bp.route('/submit', methods=['POST'])
def submit_reimbursement():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    data = request.json
    project_id = data.get('project_id')
    amount = data.get('amount')
    purpose = data.get('purpose')
    
    if not all([project_id, amount, purpose]):
        return jsonify({'status': 'error', 'message': '请填写完整的报销信息'}), 400
    
    # 检查项目是否存在
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'status': 'error', 'message': '项目不存在'}), 400
    
    # 检查金额是否合法
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({'status': 'error', 'message': '报销金额必须为正数'}), 400
    
    new_reimbursement = Reimbursement(
        project_id=project_id,
        user_id=user_id,
        amount=amount,
        purpose=purpose,
        status='pending',
        submitted_at=datetime.utcnow()
    )
    
    db.session.add(new_reimbursement)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '报销申请已提交',
        'reimbursement_id': new_reimbursement.id
    })

# 2. 获取当前用户的报销记录
@bp.route('/my_requests', methods=['GET'])
def get_my_reimbursements():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取用户的所有报销记录，按提交时间降序排列
    reimbursements = Reimbursement.query.filter_by(user_id=user_id).order_by(
        Reimbursement.submitted_at.desc()
    ).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_reimbursement(req) for req in reimbursements]
    })

# 3. 获取待审批的报销申请（管理员/项目负责人）
@bp.route('/pending', methods=['GET'])
def get_pending_reimbursements():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员或项目负责人可以查看待审批的报销申请
    user = User.query.get(user_id)
    if not user or (user.role != 'admin' and user.role != 'manager'):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 管理员可以查看所有待审批的报销
    if user.role == 'admin':
        pending_requests = Reimbursement.query.filter_by(status='pending').order_by(
            Reimbursement.submitted_at.asc()
        ).all()
    else:
        # 经理只能查看自己负责项目的报销
        from app.routes.project import get_user_projects  # 避免循环导入
        managed_projects = [p['project_id'] for p in get_user_projects(user_id) if p['role'] == '负责人']
        pending_requests = Reimbursement.query.filter(
            Reimbursement.status == 'pending',
            Reimbursement.project_id.in_(managed_projects)
        ).order_by(Reimbursement.submitted_at.asc()).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_reimbursement(req) for req in pending_requests]
    })

# 4. 审批报销申请
@bp.route('/approve/<int:reimbursement_id>', methods=['POST'])
def approve_reimbursement(reimbursement_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    reimbursement = Reimbursement.query.get(reimbursement_id)
    if not reimbursement:
        return jsonify({'status': 'error', 'message': '报销申请不存在'}), 404
    
    # 检查用户是否有权限审批（管理员或项目负责人）
    if not is_manager_or_admin(user_id, reimbursement.project_id):
        return jsonify({'status': 'error', 'message': '无权限审批'}), 403
    
    # 只能审批待处理的申请
    if reimbursement.status != 'pending':
        return jsonify({'status': 'error', 'message': '该申请已处理'}), 400
    
    data = request.json
    action = data.get('action')  # 'approve' 或 'reject'
    
    if action == 'approve':
        reimbursement.status = 'approved'
    elif action == 'reject':
        reimbursement.status = 'rejected'
    else:
        return jsonify({'status': 'error', 'message': '无效的审批动作'}), 400
    
    reimbursement.approved_by = user_id
    reimbursement.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'报销申请已{action}通过',
        'status': reimbursement.status
    })

# 5. 获取所有报销记录（管理员）
@bp.route('/all', methods=['GET'])
def get_all_reimbursements():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员可以查看所有报销记录
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取所有报销记录，按提交时间降序排列
    all_requests = Reimbursement.query.order_by(
        Reimbursement.submitted_at.desc()
    ).all()
    
    return jsonify({
        'status': 'success',
        'requests': [_format_reimbursement(req) for req in all_requests]
    })

# 6. 获取单个报销记录详情
@bp.route('/detail/<int:reimbursement_id>', methods=['GET'])
def get_reimbursement_detail(reimbursement_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    reimbursement = Reimbursement.query.get(reimbursement_id)
    if not reimbursement:
        return jsonify({'status': 'error', 'message': '报销申请不存在'}), 404
    
    # 普通用户只能查看自己的报销记录
    if reimbursement.user_id != user_id and not is_manager_or_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限查看'}), 403
    
    return jsonify({
        'status': 'success',
        'request': _format_reimbursement(reimbursement)
    })

# 辅助函数：格式化报销申请数据
def _format_reimbursement(req):
    user = User.query.get(req.user_id)
    approver = User.query.get(req.approved_by) if req.approved_by else None
    project = Project.query.get(req.project_id)
    
    return {
        'id': req.id,
        'project_id': req.project_id,
        'project_name': project.name if project else '未知项目',
        'user_id': req.user_id,
        'username': user.username if user else '未知',
        'amount': float(req.amount),  # 转换为浮点数便于前端处理
        'purpose': req.purpose,
        'status': req.status,
        'submitted_at': req.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        'approved_by': approver.username if approver else '未审批',
        'approved_at': req.approved_at.strftime('%Y-%m-%d %H:%M:%S') if req.approved_at else '未审批'
    }