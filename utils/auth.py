# utils/auth.py
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from typing import Iterable

def current_user():
    """
    Very small helper that returns user info stored in session.
    Expected keys (example): {'user_id': 'U001', 'role': 'admin', 'department': 'GEN', 'display_name': '管理者'}
    """
    return session.get("user")

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            flash("ログインが必要です。", "warning")
            return redirect(url_for("login_bp.login"))
        return view(*args, **kwargs)
    return wrapper

def roles_required(roles: Iterable[str]):
    roles = set(roles or [])
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("ログインが必要です。", "warning")
                return redirect(url_for("login_bp.login"))
            if roles and user.get("role") not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorator

def require_feature(app, key: str, default: bool = True):
    """
    Gate feature access based on app.config or DB-backed toggles.
    """
    enabled = app.config.get(key, default)
    if not enabled:
        abort(404)

def switch_account_mode(mode: str):
    """
    Store current account mode, e.g. 'production' or 'staging' in session.
    """
    session["account_mode"] = mode

def get_account_mode():
    return session.get("account_mode", "production")
