from flask import Blueprint, render_template, request, make_response, send_from_directory
from flask_login import login_required
from models import Cabinet, Reagent, DepletionAlert
import csv
import io
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    cabinets = Cabinet.query.order_by(Cabinet.name).all()
    cabinet_id = request.args.get('cabinet_id', type=int)

    current_cabinet = None
    reagents = []
    alerts = []

    if cabinets:
        if cabinet_id:
            current_cabinet = Cabinet.query.get(cabinet_id)
        if not current_cabinet:
            current_cabinet = cabinets[0]

        reagents = Reagent.query.filter_by(
            cabinet_id=current_cabinet.id
        ).order_by(Reagent.name).all()

        alerts = DepletionAlert.query.filter_by(
            cabinet_id=current_cabinet.id
        ).order_by(DepletionAlert.created_at.desc()).all()

    return render_template('index.html',
                           cabinets=cabinets,
                           current_cabinet=current_cabinet,
                           reagents=reagents,
                           alerts=alerts)


@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        results = Reagent.query.filter(
            (Reagent.name.ilike(f'%{query}%')) |
            (Reagent.cas_number.ilike(f'%{query}%')) |
            (Reagent.product_number.ilike(f'%{query}%'))
        ).order_by(Reagent.name).all()

    cabinets = Cabinet.query.order_by(Cabinet.name).all()
    return render_template('search.html',
                           results=results,
                           query=query,
                           cabinets=cabinets)

@main_bp.route('/export/cabinet/<int:cabinet_id>')
@login_required
def export_cabinet(cabinet_id):
    cabinet = Cabinet.query.get_or_404(cabinet_id)
    reagents = Reagent.query.filter_by(cabinet_id=cabinet_id).order_by(Reagent.name).all()

    si = io.StringIO()
    # 写入 UTF-8 BOM，确保 Excel 直接打开不乱码
    si.write('\ufeff')
    writer = csv.writer(si)
    writer.writerow(['试剂名称', 'CAS号', '货号', '规格', '当前数量', '最近入库时间', '最近领用时间', '所属试剂柜'])
    for r in reagents:
        writer.writerow([
            r.name,
            r.cas_number or '',
            r.product_number or '',
            r.specification or '',
            r.quantity,
            r.last_stock_in.strftime('%Y-%m-%d %H:%M') if r.last_stock_in else '',
            r.last_withdrawal.strftime('%Y-%m-%d %H:%M') if r.last_withdrawal else '',
            cabinet.name,
        ])

    output = make_response(si.getvalue())
    filename = f"{cabinet.name}_试剂清单.csv"
    # 对中文文件名进行 RFC 5987 编码，避免 HTTP 头 latin-1 编码报错
    from urllib.parse import quote
    encoded_filename = quote(filename, encoding='utf-8')
    output.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    output.headers['Content-Disposition'] = (
        f"attachment; filename*=UTF-8''{encoded_filename}"
    )
    return output
    
@main_bp.route('/user-doc')
@login_required
def user_doc():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    docs_dir = os.path.join(base_dir, 'static', 'docs')
    return send_from_directory(docs_dir, 'USER_DOC.pdf')
