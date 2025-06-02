from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 注册
@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    department = data.get('department')

    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 400

    # hashed_password = generate_password_hash(password)  password=hashed_password
    new_user = User(username=username, password=password, email=email, department=department)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': '注册成功'})

# 登录
@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    # if user and check_password_hash(user.password, password):
    if user and user.password == password:  # 直接比较明文密码
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({'status': 'success', 'message': '登录成功', 'user': {
            'id': user.id, 'username': user.username, 'role': user.role
        }})
    else:
        return jsonify({'status': 'error', 'message': '用户名或密码错误'}), 401

# 退出登录
@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': '已退出登录'})

# 获取当前登录用户信息
@bp.route('/me', methods=['GET'])
def current_user():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    user = User.query.get(session['user_id'])
    return jsonify({
        'status': 'success',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'department': user.department,
            'role': user.role,
            'description': user.description
        }
    })
