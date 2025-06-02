from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.models import db  # 从 models 中导入 db，确保是同一个

# db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # 配置数据库(用户名:密码@ip:端口/数据库名)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/class_project'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    db.init_app(app)

    # 注册蓝图
    from app.routes import auth, mail, notice, project, reimbursement, leave, attendance, log, user
    app.register_blueprint(auth.bp)
    app.register_blueprint(mail.bp)
    app.register_blueprint(notice.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(reimbursement.bp)
    app.register_blueprint(leave.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(log.bp)
    app.register_blueprint(user.bp)

    return app
