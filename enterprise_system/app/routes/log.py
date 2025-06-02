# 工作日志
# app/routes/log.py
from flask import Blueprint, request, jsonify, session
from app.models import db, WorkLog, User
from datetime import datetime, date
from sqlalchemy import func

bp = Blueprint('work_log', __name__, url_prefix='/log')

# 1. 提交工作日志
@bp.route('/submit', methods=['POST'])
def submit_work_log():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    data = request.json
    log_date = data.get('log_date')
    duration_hours = data.get('duration_hours')
    content = data.get('content')
    
    if not all([log_date, duration_hours, content]):
        return jsonify({'status': 'error', 'message': '请填写完整的日志信息'}), 400
    
    # 日期格式转换
    try:
        log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'status': 'error', 'message': '日期格式错误，应为YYYY-MM-DD'}), 400
    
    # 检查时长是否合法
    try:
        duration_hours = float(duration_hours)
        if duration_hours <= 0 or duration_hours > 24:
            raise ValueError
    except ValueError:
        return jsonify({'status': 'error', 'message': '时长必须在1-24小时之间'}), 400
    
    # 检查当天是否已提交日志
    existing_log = WorkLog.query.filter_by(
        user_id=user_id,
        log_date=log_date
    ).first()
    
    if existing_log:
        return jsonify({'status': 'error', 'message': '当天已提交日志，请勿重复提交'}), 400
    
    new_log = WorkLog(
        user_id=user_id,
        log_date=log_date,
        duration_hours=duration_hours,
        content=content
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '工作日志已提交',
        'log_id': new_log.id
    })

# 2. 修改工作日志
@bp.route('/update/<int:log_id>', methods=['POST'])
def update_work_log(log_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    log = WorkLog.query.get(log_id)
    if not log:
        return jsonify({'status': 'error', 'message': '日志不存在'}), 404
    
    # 只能修改自己的日志
    if log.user_id != user_id:
        return jsonify({'status': 'error', 'message': '无权限修改此日志'}), 403
    
    data = request.json
    duration_hours = data.get('duration_hours')
    content = data.get('content')
    
    if duration_hours is not None:
        # 检查时长是否合法
        try:
            duration_hours = float(duration_hours)
            if duration_hours <= 0 or duration_hours > 24:
                raise ValueError
        except ValueError:
            return jsonify({'status': 'error', 'message': '时长必须在1-24小时之间'}), 400
        log.duration_hours = duration_hours
    
    if content is not None:
        log.content = content
    
    log.created_at = datetime.utcnow()  # 更新创建时间
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '工作日志已更新'
    })

# 3. 获取个人工作日志列表
@bp.route('/my_logs', methods=['GET'])
def get_my_work_logs():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取可选参数：年、月筛选
    year = request.args.get('year')
    month = request.args.get('month')
    
    query = WorkLog.query.filter_by(user_id=user_id)
    
    # 处理筛选条件
    if year:
        try:
            year = int(year)
            start_date = date(year, 1, 1)
            end_date = date(year + 1, 1, 1)
            query = query.filter(
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            )
        except ValueError:
            return jsonify({'status': 'error', 'message': '年份参数格式错误'}), 400
    
    if month:
        try:
            month = int(month)
            current_year = datetime.now().year
            # 如果同时指定了年份，使用该年份；否则使用当前年份
            if year:
                target_year = int(year)
            else:
                target_year = current_year
            
            start_date = date(target_year, month, 1)
            if month == 12:
                end_date = date(target_year + 1, 1, 1)
            else:
                end_date = date(target_year, month + 1, 1)
            
            query = query.filter(
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            )
        except ValueError:
            return jsonify({'status': 'error', 'message': '月份参数格式错误'}), 400
    
    # 按日期降序排列
    logs = query.order_by(WorkLog.log_date.desc()).all()
    
    return jsonify({
        'status': 'success',
        'logs': [_format_work_log(log) for log in logs]
    })

# 5. 管理员获取所有工作日志
@bp.route('/all', methods=['GET'])
def get_all_work_logs():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员可以查看所有日志
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取参数（可选）：用户ID、年、月筛选
    user_filter = request.args.get('user_id')
    year = request.args.get('year')
    month = request.args.get('month')
    
    query = WorkLog.query
    
    if user_filter:
        query = query.filter(WorkLog.user_id == user_filter)
    
    # 处理筛选条件（与个人日志逻辑相同）
    if year:
        try:
            year = int(year)
            start_date = date(year, 1, 1)
            end_date = date(year + 1, 1, 1)
            query = query.filter(
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            )
        except ValueError:
            return jsonify({'status': 'error', 'message': '年份参数格式错误'}), 400
    
    if month:
        try:
            month = int(month)
            current_year = datetime.now().year
            if year:
                target_year = int(year)
            else:
                target_year = current_year
            
            start_date = date(target_year, month, 1)
            if month == 12:
                end_date = date(target_year + 1, 1, 1)
            else:
                end_date = date(target_year, month + 1, 1)
            
            query = query.filter(
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            )
        except ValueError:
            return jsonify({'status': 'error', 'message': '月份参数格式错误'}), 400
    
    logs = query.order_by(WorkLog.log_date.desc()).all()
    
    return jsonify({
        'status': 'success',
        'logs': [_format_work_log(log) for log in logs]
    })

# 6. 获取团队成员日志统计（管理员/经理）
@bp.route('/team_stats', methods=['GET'])
def get_team_log_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 只有管理员或经理可以查看团队统计
    user = User.query.get(user_id)
    if not user or (user.role != 'admin' and user.role != 'manager'):
        return jsonify({'status': 'error', 'message': '无权限访问'}), 403
    
    # 获取可选参数：年、月筛选
    year = request.args.get('year')
    month = request.args.get('month')
    
    # 构建查询条件
    conditions = []
    
    if year:
        try:
            year = int(year)
            start_date = date(year, 1, 1)
            if month:
                month = int(month)
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1)
                else:
                    end_date = date(year, month + 1, 1)
            else:
                end_date = date(year + 1, 1, 1)
            
            conditions.extend([
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            ])
        except ValueError:
            return jsonify({'status': 'error', 'message': '年月参数格式错误'}), 400
    
    elif month:  # 只指定月份时，默认使用当前年份
        try:
            month = int(month)
            current_year = datetime.now().year
            start_date = date(current_year, month, 1)
            if month == 12:
                end_date = date(current_year + 1, 1, 1)
            else:
                end_date = date(current_year, month + 1, 1)
            
            conditions.extend([
                WorkLog.log_date >= start_date,
                WorkLog.log_date < end_date
            ])
        except ValueError:
            return jsonify({'status': 'error', 'message': '月份参数格式错误'}), 400
    
    # 查询每个用户的日志总时长
    query = db.session.query(
        WorkLog.user_id,
        User.username,
        func.sum(WorkLog.duration_hours).label('total_hours'),
        func.count(WorkLog.id).label('log_count')
    ).join(
        User, WorkLog.user_id == User.id
    )
    
    if conditions:
        query = query.filter(*conditions)
    
    query = query.group_by(WorkLog.user_id, User.username)
    
    stats = query.all()
    
    result = []
    for stat in stats:
        result.append({
            'user_id': stat.user_id,
            'username': stat.username,
            'total_hours': float(stat.total_hours),
            'log_count': stat.log_count,
            'avg_hours_per_day': float(stat.total_hours) / stat.log_count if stat.log_count > 0 else 0
        })
    
    # 生成统计周期描述
    period_desc = "全部时间"
    if year and month:
        period_desc = f"{year}年{month}月"
    elif year:
        period_desc = f"{year}年"
    elif month:
        period_desc = f"{datetime.now().year}年{month}月"
    
    return jsonify({
        'status': 'success',
        'stats': result,
        'period': period_desc
    })

# 辅助函数：格式化工作日志数据
def _format_work_log(log):
    user = User.query.get(log.user_id)
    
    return {
        'id': log.id,
        'user_id': log.user_id,
        'username': user.username if user else '未知',
        'log_date': log.log_date.strftime('%Y-%m-%d'),
        'duration_hours': float(log.duration_hours),
        'content': log.content,
        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }