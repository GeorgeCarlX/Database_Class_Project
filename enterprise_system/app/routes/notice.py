# 公告通知管理，可以添加按照部门通知的功能，但是不想加
# app/routes/notice.py
from flask import Blueprint, request, jsonify, session
from app.models import db, Notice, User
from datetime import datetime

bp = Blueprint('notice', __name__, url_prefix='/notice')

# 辅助函数：检查用户是否为管理员
def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

# 1. 发布公告（仅管理员）
@bp.route('/publish', methods=['POST'])
def publish_notice():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    if not is_admin(user_id):
        return jsonify({'status': 'error', 'message': '只有管理员可发布公告'}), 403
    
    data = request.json
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'status': 'error', 'message': '标题和内容不能为空'}), 400
    
    new_notice = Notice(
        title=title,
        content=content,
        created_by=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_notice)
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'message': '公告发布成功', 
        'notice_id': new_notice.id
    })

# 2. 删除公告（仅管理员）
@bp.route('/delete/<int:notice_id>', methods=['POST'])
def delete_notice(notice_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    if not is_admin(user_id):
        return jsonify({'status': 'error', 'message': '只有管理员可删除公告'}), 403
    
    notice = Notice.query.get(notice_id)
    if not notice:
        return jsonify({'status': 'error', 'message': '公告不存在'}), 404
    
    db.session.delete(notice)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': '公告已删除'})

# 3. 获取公告列表（支持分页）
@bp.route('/list', methods=['GET'])
def get_notice_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    notices = Notice.query.order_by(Notice.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    notice_list = []
    for notice in notices.items:
        creator = User.query.get(notice.created_by)
        notice_list.append({
            'id': notice.id,
            'title': notice.title,
            'content': notice.content[:100] + '...',  # 内容摘要
            'created_by': creator.username if creator else '未知',
            'created_at': notice.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'status': 'success',
        'total': notices.total,
        'pages': notices.pages,
        'current_page': page,
        'notices': notice_list
    })

# 4. 获取公告详情
@bp.route('/detail/<int:notice_id>', methods=['GET'])
def get_notice_detail(notice_id):
    notice = Notice.query.get(notice_id)
    if not notice:
        return jsonify({'status': 'error', 'message': '公告不存在'}), 404
    
    creator = User.query.get(notice.created_by)
    return jsonify({
        'status': 'success',
        'notice': {
            'id': notice.id,
            'title': notice.title,
            'content': notice.content,
            'created_by': creator.username if creator else '未知',
            'created_at': notice.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })