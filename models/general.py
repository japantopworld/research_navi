# models/general.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., GEN, BUY, SAL, LOG
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # admin / staff / contractor
    description = db.Column(db.String(255))

class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Organization(db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)  # business ID like KING1219, 0101A
    display_name = db.Column(db.String(120), nullable=False)
    department_code = db.Column(db.String(10), db.ForeignKey("departments.code"))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))
    introducer = db.Column(db.String(50))  # 紹介者NO
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemSetting(db.Model):
    __tablename__ = "system_settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)  # keep JSON/string
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FeatureToggle(db.Model):
    __tablename__ = "feature_toggles"
    id = db.Column(db.Integer, primary_key=True)
    feature_key = db.Column(db.String(120), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LoginHistory(db.Model):
    __tablename__ = "login_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(300))
    logged_in_at = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordChangeLog(db.Model):
    __tablename__ = "password_change_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(200), nullable=False)  # e.g., "USER_CREATE", "ROLE_UPDATE"
    actor_user_id = db.Column(db.String(50))  # who did this
    target = db.Column(db.String(200))  # which object
    meta = db.Column(db.Text)  # JSON text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UpdateHistory(db.Model):
    __tablename__ = "update_history"
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)   # e.g., "v1.2.0"
    title = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    __tablename__ = "notices"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default="info")  # info/warn/emergency
    is_global = db.Column(db.Boolean, default=False)  # 全員への強制表示
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # 'manual' / 'nda' / 'form' etc.
    current_version_id = db.Column(db.Integer)  # pointer to latest version
    pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DocumentVersion(db.Model):
    __tablename__ = "document_versions"
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"))
    version = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)  # markdown or plain text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FormSubmission(db.Model):
    __tablename__ = "form_submissions"
    id = db.Column(db.Integer, primary_key=True)
    form_type = db.Column(db.String(100), nullable=False)  # 'user_add', 'bug_report'など
    payload = db.Column(db.Text, nullable=False)  # JSON text
    created_by = db.Column(db.String(50))  # user_id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
