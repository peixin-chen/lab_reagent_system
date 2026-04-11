from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Cabinet, Reagent, StockRecord, DepletionAlert

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限才能访问此页面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# ────────────────── 控制面板 ──────────────────
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'cabinets': Cabinet.query.count(),
        'reagents': Reagent.query.count(),
        'alerts': DepletionAlert.query.count(),
    }
    recent_records = (StockRecord.query
                      .order_by(StockRecord.timestamp.desc())
                      .limit(15).all())
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_records=recent_records)


# ────────────────── 用户管理 ──────────────────
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('不能删除当前登录的账户', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    username = user.username
    name = user.name
    # 保留记录，仅清除外键
    StockRecord.query.filter_by(user_id=user.id).update({'user_id': None})
    db.session.delete(user)
    db.session.commit()
    flash(f'用户"{name}"（{username}）已删除', 'success')
    return redirect(url_for('admin.users'))


# ────────────────── 试剂柜管理 ──────────────────
@admin_bp.route('/cabinets')
@login_required
@admin_required
def cabinets():
    all_cabinets = Cabinet.query.order_by(Cabinet.name).all()
    return render_template('admin/cabinets.html', cabinets=all_cabinets)


@admin_bp.route('/cabinets/add', methods=['POST'])
@login_required
@admin_required
def add_cabinet():
    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('试剂柜名称不能为空', 'danger')
        return redirect(url_for('admin.cabinets'))

    if Cabinet.query.filter_by(name=name).first():
        flash(f'试剂柜名称"{name}"已存在', 'danger')
        return redirect(url_for('admin.cabinets'))

    cabinet = Cabinet(name=name, location=location, description=description)
    db.session.add(cabinet)
    db.session.commit()
    flash(f'试剂柜"{name}"添加成功', 'success')
    return redirect(url_for('admin.cabinets'))


@admin_bp.route('/cabinets/edit/<int:cabinet_id>', methods=['POST'])
@login_required
@admin_required
def edit_cabinet(cabinet_id):
    cabinet = Cabinet.query.get_or_404(cabinet_id)
    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('试剂柜名称不能为空', 'danger')
        return redirect(url_for('admin.cabinets'))

    conflict = Cabinet.query.filter(
        Cabinet.name == name, Cabinet.id != cabinet_id
    ).first()
    if conflict:
        flash(f'试剂柜名称"{name}"已存在', 'danger')
        return redirect(url_for('admin.cabinets'))

    cabinet.name = name
    cabinet.location = location
    cabinet.description = description
    db.session.commit()
    flash(f'试剂柜信息已更新', 'success')
    return redirect(url_for('admin.cabinets'))


@admin_bp.route('/cabinets/delete/<int:cabinet_id>', methods=['POST'])
@login_required
@admin_required
def delete_cabinet(cabinet_id):
    cabinet = Cabinet.query.get_or_404(cabinet_id)
    name = cabinet.name
    # ORM cascade 会自动删除试剂和耗尽提醒
    db.session.delete(cabinet)
    db.session.commit()
    flash(f'试剂柜"{name}"及其所有试剂已删除', 'success')
    return redirect(url_for('admin.cabinets'))


# ────────────────── 操作记录 ──────────────────
@admin_bp.route('/records')
@login_required
@admin_required
def records():
    page = request.args.get('page', 1, type=int)
    op_filter = request.args.get('op', '')
    q = StockRecord.query
    if op_filter in ('in', 'out'):
        q = q.filter_by(operation_type=op_filter)
    pagination = q.order_by(StockRecord.timestamp.desc()).paginate(
        page=page, per_page=200, error_out=False)
    return render_template('admin/records.html',
                           pagination=pagination,
                           op_filter=op_filter)


# ────────────────── 删除耗尽提醒 ──────────────────
@admin_bp.route('/alerts/delete/<int:alert_id>', methods=['POST'])
@login_required
@admin_required
def delete_alert(alert_id):
    alert = DepletionAlert.query.get_or_404(alert_id)
    cabinet_id = alert.cabinet_id
    name = alert.reagent_name
    db.session.delete(alert)
    db.session.commit()
    flash(f'"{name}"的耗尽提醒已删除', 'success')
    return redirect(url_for('main.index', cabinet_id=cabinet_id))
