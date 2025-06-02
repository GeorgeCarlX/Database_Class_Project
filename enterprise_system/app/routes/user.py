# 用户信息
# app/routes/user.py
from flask import Blueprint, request, jsonify, session
from app.models import db, User, ProjectMember
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

bp = Blueprint('user', __name__, url_prefix='/user')

# 辅助函数：检查用户是否为管理员
def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

# 1. 获取当前用户信息
@bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'department': user.department,
            'role': user.role,
            'description': user.description,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'projects': _get_user_projects(user_id)  # 获取用户参与的项目
        }
    })

# 2. 更新当前用户信息
@bp.route('/update', methods=['POST'])
def update_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    data = request.json
    email = data.get('email')
    department = data.get('department')
    description = data.get('description')
    
    # 检查邮箱是否已被其他用户使用
    if email and email != user.email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'status': 'error', 'message': '邮箱已被使用'}), 400
    
    if email:
        user.email = email
    if department:
        user.department = department
    if description:
        user.description = description
    
    user.updated_at = datetime.utcnow()  # 注意：你的模型中没有 updated_at 字段，需要手动添加
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '用户信息已更新'})

# 3. 修改密码
@bp.route('/change_password', methods=['POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'status': 'error', 'message': '请提供旧密码和新密码'}), 400
    
    # 验证旧密码
    if not check_password_hash(user.password, old_password):
        return jsonify({'status': 'error', 'message': '旧密码错误'}), 400
    
    # 更新密码
    user.password = new_password
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '密码已更新'})

# 4. 管理员获取用户列表
@bp.route('/list', methods=['GET'])
def get_user_list():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员可以获取用户列表
    if not is_admin(user_id):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取所有非管理员用户
    users = User.query.filter(User.role != 'admin').all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'department': user.department,
            'role': user.role,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'project_count': len(user.projects)  # 用户参与的项目数量
        })
    
    return jsonify({'status': 'success', 'users': user_list})

# 5. 管理员获取用户详情
@bp.route('/detail/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员可以查看其他用户详情
    if not is_admin(current_user_id):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    return jsonify({
        'status': 'success',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'department': user.department,
            'role': user.role,
            'description': user.description,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'projects': _get_user_projects(user_id)  # 获取用户参与的项目
        }
    })

# 6. 管理员更新用户信息
@bp.route('/admin/update/<int:user_id>', methods=['POST'])
def admin_update_user(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员可以更新其他用户信息
    if not is_admin(current_user_id):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    department = data.get('department')
    role = data.get('role')
    
    # 检查用户名是否已被其他用户使用
    if username and username != user.username:
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return jsonify({'status': 'error', 'message': '用户名已被使用'}), 400
    
    # 检查邮箱是否已被其他用户使用
    if email and email != user.email:
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'status': 'error', 'message': '邮箱已被使用'}), 400
    
    if username:
        user.username = username
    if email:
        user.email = email
    if department:
        user.department = department
    if role:
        # 确保角色是有效的枚举值
        if role not in ['employee', 'manager', 'admin']:
            return jsonify({'status': 'error', 'message': '无效的角色'}), 400
        user.role = role
    
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '用户信息已更新'})

# 辅助函数：获取用户参与的项目
def _get_user_projects(user_id):
    projects = []
    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    
    for membership in memberships:
        project = membership.project
        projects.append({
            'project_id': project.id,
            'project_name': project.name,
            'project_description': project.description,
            'role': membership.role,
            'project_creator_id': project.created_by,  # 创建者ID                'project_creator': creator_username,  # 创建者用户名
            'project_created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return projects
