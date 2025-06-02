# 内部邮件管理
from flask import Blueprint, request, jsonify, session
from app.models import db, Mail, User, datetime

bp = Blueprint('mail', __name__, url_prefix='/mail')

# 发送邮件
@bp.route('/send', methods=['POST'])
def send_mail():
    data = request.json
    sender_id = session.get('user_id')
    receiver_id = data.get('receiver_id')
    subject = data.get('subject')
    content = data.get('content')
    is_reply = data.get('is_reply', False)

    if not sender_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    if not receiver_id or not subject or not content:
        return jsonify({'status': 'error', 'message': '收件人、主题和内容不能为空'}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'status': 'error', 'message': '收件人不存在'}), 404

    new_mail = Mail(
        sender_id=sender_id,
        receiver_id=receiver_id,
        subject=subject,
        content=content,
        is_reply=is_reply
    )
    db.session.add(new_mail)
    db.session.commit()

    return jsonify({'status': 'success', 'message': '邮件发送成功'})

# 获取收件箱邮件列表
@bp.route('/inbox', methods=['GET'])
def get_inbox():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    mails = Mail.query.filter_by(receiver_id=user_id).order_by(Mail.sent_at.desc()).all()
    mail_list = []
    for mail in mails:
        sender = User.query.get(mail.sender_id)
        mail_list.append({
            'id': mail.id,
            'sender': sender.username,
            'subject': mail.subject,
            'content': mail.content,
            'is_read': mail.is_read,
            'is_reply': mail.is_reply,
            'sent_at': mail.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'status': 'success', 'mails': mail_list})

# 获取发件箱邮件列表
@bp.route('/sent', methods=['GET'])
def get_sent():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    mails = Mail.query.filter_by(sender_id=user_id).order_by(Mail.sent_at.desc()).all()
    mail_list = []
    for mail in mails:
        receiver = User.query.get(mail.receiver_id)
        mail_list.append({
            'id': mail.id,
            'receiver': receiver.username,
            'subject': mail.subject,
            'content': mail.content,
            'is_read': mail.is_read,
            'is_reply': mail.is_reply,
            'sent_at': mail.sent_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'status': 'success', 'mails': mail_list})

# 标记邮件为已读
@bp.route('/read/<int:mail_id>', methods=['POST'])
def mark_mail_read(mail_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    mail = Mail.query.get(mail_id)
    if not mail:
        return jsonify({'status': 'error', 'message': '邮件不存在'}), 404

    if mail.receiver_id != user_id:
        return jsonify({'status': 'error', 'message': '无权限标记该邮件为已读'}), 403

    mail.is_read = True
    db.session.commit()

    return jsonify({'status': 'success', 'message': '邮件已标记为已读'})

# 回复邮件（将原始邮件的 is_reply 设为 True）
@bp.route('/reply/<int:original_mail_id>', methods=['POST'])
def reply_mail(original_mail_id):
    data = request.json
    sender_id = session.get('user_id')
    content = data.get('content')

    if not sender_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401

    if not content:
        return jsonify({'status': 'error', 'message': '回复内容不能为空'}), 400

    # 查询原始邮件
    original_mail = Mail.query.get(original_mail_id)
    if not original_mail:
        return jsonify({'status': 'error', 'message': '原始邮件不存在'}), 404

    # 检查当前用户是否是原始邮件的接收者
    if original_mail.receiver_id != sender_id:
        return jsonify({'status': 'error', 'message': '只能回复自己收到的邮件'}), 403

    # 创建新邮件（普通邮件，is_reply 保持默认 False）
    reply_subject = f"Re: {original_mail.subject}"
    new_mail = Mail(
        sender_id=sender_id,
        receiver_id=original_mail.sender_id,
        subject=reply_subject,
        content=content,
        is_read=False,  # 新邮件默认未读
        sent_at=datetime.utcnow()
    )
    
    # 将原始邮件标记为"已回复"
    original_mail.is_reply = True
    
    db.session.add(new_mail)
    db.session.commit()

    return jsonify({'status': 'success', 'message': '回复邮件发送成功'})