from flask import Flask
from config import Config
from extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录后再访问此页面'
    login_manager.login_message_category = 'warning'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Jinja2 自定义过滤器
    @app.template_filter('fmt_qty')
    def fmt_qty(value):
        if value is None:
            return '-'
        if value == int(value):
            return str(int(value))
        return f'{value:.4f}'.rstrip('0').rstrip('.')

    @app.template_filter('fmt_dt')
    def fmt_dt(value):
        if value is None:
            return '-'
        return value.strftime('%Y-%m-%d %H:%M')

    # 注册蓝图
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.reagent import reagent_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(reagent_bp, url_prefix='/reagent')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        _init_db()

    return app


def _init_db():
    from models import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            name='管理员',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        #print('[INFO] 默认管理员账户已创建  用户名: admin  密码: admin123')
