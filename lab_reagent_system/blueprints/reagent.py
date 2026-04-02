from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Reagent, Cabinet, StockRecord, DepletionAlert
from datetime import datetime

reagent_bp = Blueprint('reagent', __name__)


def _save_record(reagent_id, name, cas, product_number, spec, cabinet_name, qty, op_type):
    """保存入库/领用记录"""
    record = StockRecord(
        reagent_id=reagent_id,
        reagent_name=name,
        cas_number=cas,
        product_number=product_number,
        specification=spec,
        cabinet_name=cabinet_name,
        user_id=current_user.id,
        user_name=current_user.name,
        quantity=qty,
        operation_type=op_type
    )
    db.session.add(record)


@reagent_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    cas = request.form.get('cas_number', '').strip() or None
    spec = request.form.get('specification', '').strip()
    cabinet_id = request.form.get('cabinet_id', type=int)
    product_number = request.form.get('product_number', '').strip() or None

    try:
        quantity = float(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = 0

    back_url = url_for('main.index', cabinet_id=cabinet_id)

    if not name:
        flash('试剂名称不能为空', 'danger')
        return redirect(back_url)
    if not spec:
        flash('规格不能为空', 'danger')
        return redirect(back_url)
    if quantity <= 0:
        flash('数量必须大于0', 'danger')
        return redirect(back_url)
    if not cabinet_id:
        flash('请选择试剂柜', 'danger')
        return redirect(url_for('main.index'))

    cabinet = Cabinet.query.get_or_404(cabinet_id)

    # 查找完全匹配的试剂（名称+规格相同，CAS号一致）
    q = Reagent.query.filter_by(cabinet_id=cabinet_id, name=name, specification=spec)
    if cas:
        q = q.filter_by(cas_number=cas)
    else:
        q = q.filter((Reagent.cas_number == None) | (Reagent.cas_number == ''))
    if product_number:
        q = q.filter_by(product_number=product_number)
    else:
        q = q.filter((Reagent.product_number == None) | (Reagent.product_number == ''))
    existing = q.first()

    if existing:
        existing.quantity += quantity
        existing.last_stock_in = datetime.now()
        _save_record(existing.id, existing.name, existing.cas_number, existing.product_number,
                     existing.specification, cabinet.name, quantity, 'in')
        db.session.commit()
        flash(f'试剂"{name}"已存在，已自动执行入库操作（入库数量：{quantity}）', 'success')
    else:
        reagent = Reagent(
            name=name,
            cas_number=cas,
            product_number=product_number,
            specification=spec,
            quantity=quantity,
            cabinet_id=cabinet_id,
            last_stock_in=datetime.now()
        )
        db.session.add(reagent)
        db.session.flush()
        _save_record(reagent.id, name, cas, product_number, spec, cabinet.name, quantity, 'in')
        db.session.commit()
        flash(f'试剂"{name}"添加成功', 'success')

    return redirect(back_url)

@reagent_bp.route('/edit/<int:reagent_id>', methods=['POST'])
@login_required
def edit(reagent_id):
    if not current_user.is_admin:
        flash('只有管理员可以修改试剂信息', 'danger')
        return redirect(url_for('main.index'))

    reagent = Reagent.query.get_or_404(reagent_id)

    name = request.form.get('name', '').strip()
    cas = request.form.get('cas_number', '').strip() or None
    product_number = request.form.get('product_number', '').strip() or None
    spec = request.form.get('specification', '').strip()

    try:
        quantity = float(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = -1

    from_search = request.form.get('from_search', '').strip()
    back_url = (
        url_for('main.search', q=from_search)
        if from_search else
        url_for('main.index', cabinet_id=reagent.cabinet_id)
    )

    if not name:
        flash('试剂名称不能为空', 'danger')
        return redirect(back_url)

    if not spec:
        flash('规格不能为空', 'danger')
        return redirect(back_url)

    if quantity < 0:
        flash('数量不能小于0', 'danger')
        return redirect(back_url)

    # 避免编辑后与同柜中其他试剂重复
    q = Reagent.query.filter(
        Reagent.id != reagent.id,
        Reagent.cabinet_id == reagent.cabinet_id,
        Reagent.name == name,
        Reagent.specification == spec
    )

    if cas:
        q = q.filter(Reagent.cas_number == cas)
    else:
        q = q.filter((Reagent.cas_number == None) | (Reagent.cas_number == ''))

    if product_number:
        q = q.filter(Reagent.product_number == product_number)
    else:
        q = q.filter((Reagent.product_number == None) | (Reagent.product_number == ''))

    duplicate = q.first()
    if duplicate:
        flash('修改失败：当前试剂柜中已存在相同名称/规格/CAS/货号的试剂条目', 'danger')
        return redirect(back_url)

    reagent.name = name
    reagent.cas_number = cas
    reagent.product_number = product_number
    reagent.specification = spec
    reagent.quantity = quantity

    db.session.commit()
    flash(f'试剂“{reagent.name}”信息修改成功', 'success')
    return redirect(back_url)


@reagent_bp.route('/stock_in/<int:reagent_id>', methods=['POST'])
@login_required
def stock_in(reagent_id):
    reagent = Reagent.query.get_or_404(reagent_id)
    try:
        quantity = float(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = 0

    from_search = request.form.get('from_search', '')
    back_url = (url_for('main.search', q=from_search) if from_search
                else url_for('main.index', cabinet_id=reagent.cabinet_id))

    if quantity <= 0:
        flash('请输入有效的入库数量（必须大于0）', 'danger')
        return redirect(back_url)

    reagent.quantity += quantity
    reagent.last_stock_in = datetime.now()
    _save_record(reagent.id, reagent.name, reagent.cas_number, reagent.product_number,
                 reagent.specification, reagent.cabinet.name, quantity, 'in')
    db.session.commit()
    flash(f'"{reagent.name}" 入库成功，入库数量：{quantity}，当前库存：{reagent.quantity}', 'success')
    return redirect(back_url)


@reagent_bp.route('/withdrawal/<int:reagent_id>', methods=['POST'])
@login_required
def withdrawal(reagent_id):
    reagent = Reagent.query.get_or_404(reagent_id)
    try:
        quantity = float(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = 0

    from_search = request.form.get('from_search', '')
    cabinet_id = reagent.cabinet_id
    back_url = (url_for('main.search', q=from_search) if from_search
                else url_for('main.index', cabinet_id=cabinet_id))

    if quantity <= 0:
        flash('请输入有效的领用数量（必须大于0）', 'danger')
        return redirect(back_url)

    new_qty = reagent.quantity - quantity
    if new_qty < -1e-9:
        flash(f'库存不足！当前库存为 {reagent.quantity}，无法领用 {quantity}', 'danger')
        return redirect(back_url)

    cabinet_name = reagent.cabinet.name
    r_name = reagent.name
    r_cas = reagent.cas_number
    r_spec = reagent.specification
    r_product_number = reagent.product_number

    reagent.last_withdrawal = datetime.now()
    _save_record(reagent.id, r_name, r_cas, r_product_number, r_spec, cabinet_name, quantity, 'out')

    if new_qty <= 1e-9:
        # 试剂耗尽：创建提醒，删除条目
        alert = DepletionAlert(
            reagent_name=r_name,
            cas_number=r_cas,
            product_number=r_product_number,
            specification=r_spec,
            cabinet_id=cabinet_id
        )
        db.session.add(alert)
        db.session.delete(reagent)
        db.session.commit()
        flash(f'"{r_name}" 领用成功，试剂已耗尽，已在主页生成补货提醒', 'warning')
    else:
        reagent.quantity = new_qty
        db.session.commit()
        flash(f'"{r_name}" 领用成功，领用数量：{quantity}，剩余库存：{new_qty}', 'success')

    return redirect(back_url)


@reagent_bp.route('/restock_alert/<int:alert_id>', methods=['POST'])
@login_required
def restock_alert(alert_id):
    alert = DepletionAlert.query.get_or_404(alert_id)
    try:
        quantity = float(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = 0

    back_url = url_for('main.index', cabinet_id=alert.cabinet_id)

    if quantity <= 0:
        flash('请输入有效的入库数量（必须大于0）', 'danger')
        return redirect(back_url)

    cabinet = Cabinet.query.get_or_404(alert.cabinet_id)

    # 查找是否已有同名试剂（极少数情况）
    existing = Reagent.query.filter_by(
        cabinet_id=alert.cabinet_id,
        name=alert.reagent_name,
        cas_number=alert.cas_number,
        product_number=alert.product_number,
        specification=alert.specification
    ).first()

    if existing:
        existing.quantity += quantity
        existing.last_stock_in = datetime.now()
        _save_record(existing.id, existing.name, existing.cas_number, existing.product_number,
                     existing.specification, cabinet.name, quantity, 'in')
    else:
        reagent = Reagent(
            name=alert.reagent_name,
            cas_number=alert.cas_number,
            product_number=alert.product_number,
            specification=alert.specification,
            quantity=quantity,
            cabinet_id=alert.cabinet_id,
            last_stock_in=datetime.now()
        )
        db.session.add(reagent)
        db.session.flush()
        _save_record(reagent.id, alert.reagent_name, alert.cas_number, alert.product_number,
                     alert.specification, cabinet.name, quantity, 'in')

    db.session.delete(alert)
    db.session.commit()
    flash(f'"{alert.reagent_name}" 已重新入库，数量：{quantity}', 'success')
    return redirect(back_url)
