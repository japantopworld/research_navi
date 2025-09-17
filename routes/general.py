# routes/general.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from sqlalchemy import or_
from datetime import datetime
import json

from models.general import db, Department, Role, Brand, Organization, User, SystemSetting, FeatureToggle, \
    LoginHistory, PasswordChangeLog, AuditLog, UpdateHistory, Notice, Document, DocumentVersion, FormSubmission

from utils.auth import login_required, roles_required, require_feature, get_account_mode, switch_account_mode

general_bp = Blueprint("general_bp", __name__, url_prefix="/admin")

# -------------------- Helpers --------------------
def set_toggle(feature_key: str, enabled: bool):
    toggle = FeatureToggle.query.filter_by(feature_key=feature_key).first()
    if not toggle:
        toggle = FeatureToggle(feature_key=feature_key, enabled=enabled)
        db.session.add(toggle)
    else:
        toggle.enabled = enabled
    db.session.commit()
    db.session.add(AuditLog(event="FEATURE_TOGGLE", actor_user_id=session.get("user",{}).get("user_id"),
                            target=feature_key, meta=json.dumps({"enabled": enabled})))
    db.session.commit()

def get_toggle(feature_key: str, default=True) -> bool:
    t = FeatureToggle.query.filter_by(feature_key=feature_key).first()
    return t.enabled if t else default

# -------------------- Dashboard --------------------
@general_bp.route("/")
@login_required
@roles_required(["admin"])
def dashboard():
    require_feature(current_app, "FEATURE_ADMIN", True)
    stats = {
        "users": User.query.count(),
        "departments": Department.query.count(),
        "roles": Role.query.count(),
        "brands": Brand.query.count(),
        "orgs": Organization.query.count(),
        "logins_24h": LoginHistory.query.filter(LoginHistory.logged_in_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)).count(),
        "notices": Notice.query.count(),
    }
    account_mode = get_account_mode()
    maintenance = get_toggle("maintenance_mode", False)
    updates = UpdateHistory.query.order_by(UpdateHistory.published_at.desc()).limit(5).all()
    emergencies = Notice.query.filter_by(level="emergency").order_by(Notice.created_at.desc()).limit(3).all()
    return render_template("admin/dashboard.html", stats=stats, account_mode=account_mode,
                           maintenance=maintenance, updates=updates, emergencies=emergencies)

# -------------------- Settings --------------------
@general_bp.route("/settings", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def settings():
    require_feature(current_app, "FEATURE_ADMIN", True)
    if request.method == "POST":
        # module toggle example
        toggles = request.form.getlist("modules")
        all_keys = ["SEARCH", "PROFIT", "HISTORY", "RANKING", "ALERTS", "ACCOUNTING", "LOGISTICS"]
        for k in all_keys:
            set_toggle(f"module_{k.lower()}", k in toggles)
        # notifications
        set_toggle("notify_email", request.form.get("notify_email") == "on")
        set_toggle("notify_webpush", request.form.get("notify_webpush") == "on")
        flash("設定を保存しました。", "success")
        return redirect(url_for("general_bp.settings"))
    module_toggles = {k.feature_key: k.enabled for k in FeatureToggle.query.filter(FeatureToggle.feature_key.like("module_%")).all()}
    notify_email = get_toggle("notify_email", True)
    notify_webpush = get_toggle("notify_webpush", False)
    return render_template("admin/settings.html", module_toggles=module_toggles,
                           notify_email=notify_email, notify_webpush=notify_webpush)

@general_bp.route("/maintenance/toggle", methods=["POST"])
@login_required
@roles_required(["admin"])
def toggle_maintenance():
    on = request.form.get("on") == "1"
    set_toggle("maintenance_mode", on)
    flash("メンテナンスモードを切り替えました。", "info")
    return redirect(url_for("general_bp.dashboard"))

@general_bp.route("/account-mode", methods=["POST"])
@login_required
@roles_required(["admin"])
def switch_mode():
    mode = request.form.get("mode", "production")
    switch_account_mode(mode if mode in ("production","staging","testing") else "production")
    flash("アカウントモードを切り替えました。", "info")
    return redirect(url_for("general_bp.dashboard"))

# -------------------- Logs --------------------
@general_bp.route("/logs")
@login_required
@roles_required(["admin"])
def logs():
    q = request.args.get("q","").strip()
    base = AuditLog.query
    if q:
        base = base.filter(or_(AuditLog.event.ilike(f"%{q}%"), AuditLog.target.ilike(f"%{q}%"), AuditLog.meta.ilike(f"%{q}%")))
    logs = base.order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template("admin/logs.html", logs=logs, q=q)

# -------------------- Users & Departments --------------------
@general_bp.route("/users")
@login_required
@roles_required(["admin"])
def users():
    q = request.args.get("q","").strip()
    base = User.query
    if q:
        base = base.filter(or_(User.user_id.ilike(f"%{q}%"), User.display_name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%")))
    items = base.order_by(User.created_at.desc()).limit(200).all()
    depts = Department.query.order_by(Department.code).all()
    roles = Role.query.order_by(Role.name).all()
    return render_template("admin/users.html", items=items, depts=depts, roles=roles, q=q)

@general_bp.route("/users/create", methods=["POST"])
@login_required
@roles_required(["admin"])
def users_create():
    data = request.form
    u = User(
        user_id=data.get("user_id").strip(),
        display_name=data.get("display_name").strip(),
        department_code=data.get("department_code") or None,
        email=data.get("email") or None,
        phone=data.get("phone") or None,
        role_id=int(data.get("role_id")) if data.get("role_id") else None,
    )
    db.session.add(u)
    db.session.commit()
    db.session.add(AuditLog(event="USER_CREATE", actor_user_id=session.get("user",{}).get("user_id"),
                            target=u.user_id, meta="{}"))
    db.session.commit()
    flash("ユーザーを作成しました。", "success")
    return redirect(url_for("general_bp.users"))

@general_bp.route("/users/<int:user_pk>/update", methods=["POST"])
@login_required
@roles_required(["admin"])
def users_update(user_pk):
    u = User.query.get_or_404(user_pk)
    data = request.form
    u.display_name = data.get("display_name") or u.display_name
    u.department_code = data.get("department_code") or u.department_code
    u.email = data.get("email") or u.email
    u.phone = data.get("phone") or u.phone
    if data.get("role_id"):
        u.role_id = int(data.get("role_id"))
    u.is_active = (data.get("is_active") == "on")
    db.session.commit()
    db.session.add(AuditLog(event="USER_UPDATE", actor_user_id=session.get("user",{}).get("user_id"),
                            target=u.user_id, meta="{}"))
    db.session.commit()
    flash("ユーザー情報を更新しました。", "success")
    return redirect(url_for("general_bp.users"))

@general_bp.route("/departments")
@login_required
@roles_required(["admin"])
def departments():
    items = Department.query.order_by(Department.code).all()
    return render_template("admin/departments.html", items=items)

@general_bp.route("/departments/create", methods=["POST"])
@login_required
@roles_required(["admin"])
def departments_create():
    code = request.form.get("code").strip().upper()
    name = request.form.get("name").strip()
    d = Department(code=code, name=name, is_active=True)
    db.session.add(d)
    db.session.commit()
    db.session.add(AuditLog(event="DEPT_CREATE", actor_user_id=session.get("user",{}).get("user_id"),
                            target=code, meta="{}"))
    db.session.commit()
    flash("部署を作成しました。", "success")
    return redirect(url_for("general_bp.departments"))

# -------------------- Docs & Forms --------------------
@general_bp.route("/documents")
@login_required
@roles_required(["admin"])
def documents():
    docs = Document.query.order_by(Document.created_at.desc()).limit(200).all()
    return render_template("admin/documents.html", docs=docs)

@general_bp.route("/documents/create", methods=["POST"])
@login_required
@roles_required(["admin"])
def documents_create():
    title = request.form.get("title").strip()
    category = request.form.get("category").strip()
    content = request.form.get("content").strip()
    version = request.form.get("version", "v1.0.0").strip()
    doc = Document(title=title, category=category)
    db.session.add(doc); db.session.commit()
    dv = DocumentVersion(document_id=doc.id, version=version, content=content)
    db.session.add(dv); db.session.commit()
    doc.current_version_id = dv.id
    db.session.commit()
    db.session.add(AuditLog(event="DOC_CREATE", actor_user_id=session.get("user",{}).get("user_id"),
                            target=title, meta=json.dumps({"category": category, "version": version})))
    db.session.commit()
    flash("ドキュメントを作成しました。", "success")
    return redirect(url_for("general_bp.documents"))

@general_bp.route("/forms")
@login_required
@roles_required(["admin"])
def forms():
    items = FormSubmission.query.order_by(FormSubmission.created_at.desc()).limit(200).all()
    return render_template("admin/forms.html", items=items)

@general_bp.route("/forms/submit", methods=["POST"])
@login_required
def forms_submit():
    # Generic form handler for 'user_add' / 'bug_report' etc.
    form_type = request.form.get("form_type", "unknown")
    payload = {k:v for k,v in request.form.items() if k not in ("form_type",)}
    sub = FormSubmission(form_type=form_type, payload=json.dumps(payload, ensure_ascii=False),
                         created_by=session.get("user",{}).get("user_id"))
    db.session.add(sub); db.session.commit()
    db.session.add(AuditLog(event="FORM_SUBMIT", actor_user_id=session.get("user",{}).get("user_id"),
                            target=form_type, meta=json.dumps(payload, ensure_ascii=False)))
    db.session.commit()
    flash("送信しました。", "success")
    return redirect(url_for("general_bp.forms"))

# -------------------- Notices & Updates --------------------
@general_bp.route("/notices", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def notices():
    if request.method == "POST":
        n = Notice(
            title=request.form.get("title").strip(),
            body=request.form.get("body").strip(),
            level=request.form.get("level","info"),
            is_global=(request.form.get("is_global")=="on")
        )
        db.session.add(n); db.session.commit()
        db.session.add(AuditLog(event="NOTICE_CREATE", actor_user_id=session.get("user",{}).get("user_id"),
                                target=n.title, meta=json.dumps({"level": n.level, "is_global": n.is_global})))
        db.session.commit()
        flash("お知らせを作成しました。", "success")
        return redirect(url_for("general_bp.notices"))
    items = Notice.query.order_by(Notice.created_at.desc()).limit(200).all()
    return render_template("admin/notices.html", items=items)

@general_bp.route("/updates", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def updates():
    if request.method == "POST":
        up = UpdateHistory(
            version=request.form.get("version").strip(),
            title=request.form.get("title").strip(),
            details=request.form.get("details").strip()
        )
        db.session.add(up); db.session.commit()
        db.session.add(AuditLog(event="UPDATE_ADD", actor_user_id=session.get("user",{}).get("user_id"),
                                target=up.version, meta=json.dumps({"title": up.title})))
        db.session.commit()
        flash("更新履歴を登録しました。", "success")
        return redirect(url_for("general_bp.updates"))
    items = UpdateHistory.query.order_by(UpdateHistory.published_at.desc()).limit(200).all()
    return render_template("admin/updates.html", items=items)
