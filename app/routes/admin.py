from pathlib import Path
import resend
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
    abort
)

from functools import wraps

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from sqlalchemy import or_

from app import db

from app.models import (
    AdminUser,
    Service,
    ServiceCategory,
    PortfolioCategory,
    PortfolioProject,
    InsightCategory,
    InsightArticle,
    ContactMessage,
    StaffProfile,
    CareerPosition,
    JobApplication,
    FAQ
)
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

def first_admin_required(view):

    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(
                url_for("admin.login")
            )

        if current_user.id != 1:
            flash(
                "You do not have permission to access Admin Users.",
                "danger"
            )
            return redirect(
                url_for("admin.dashboard")
            )

        return view(*args, **kwargs)

    return wrapped_view


# =========================================================
# ADMIN LOGIN
# =========================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(
            url_for("admin.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Please enter your username and password.",
                "danger"
            )

            return render_template(
                "admin/login.html"
            )

        user = (
            AdminUser.query
            .filter_by(username=username)
            .first()
        )

        if user is None:

            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "admin/login.html"
            )

        if not user.is_active:

            flash(
                "This administrator account is currently inactive.",
                "warning"
            )

            return render_template(
                "admin/login.html"
            )

        if not user.check_password(password):

            flash(
                "Invalid username or password.",
                "danger"
            )

            return render_template(
                "admin/login.html"
            )

        login_user(user)

        next_page = request.args.get("next")

        if (
            next_page
            and next_page.startswith("/")
            and not next_page.startswith("//")
        ):
            return redirect(next_page)

        return redirect(
            url_for("admin.dashboard")
        )

    return render_template(
        "admin/login.html"
    )
@admin_bp.route(
    "/setup",
    methods=["GET", "POST"]
)
def setup_admin():

    # --------------------------------------------------
    # SETUP IS ONLY AVAILABLE IF NO ADMIN EXISTS
    # --------------------------------------------------

    existing_admin = AdminUser.query.first()

    if existing_admin:
        flash(
            "Initial administrator setup has already been completed.",
            "warning"
        )
        return redirect(
            url_for("admin.login")
        )

    # --------------------------------------------------
    # CHECK SETUP KEY
    # --------------------------------------------------

    setup_key = current_app.config.get(
        "ADMIN_SETUP_KEY"
    )

    if not setup_key:
        current_app.logger.error(
            "ADMIN_SETUP_KEY is not configured."
        )

        return (
            "Admin setup is not configured on this server.",
            503
        )

    # --------------------------------------------------
    # FORM SUBMISSION
    # --------------------------------------------------

    if request.method == "POST":

        submitted_key = (
            request.form
            .get("setup_key", "")
            .strip()
        )

        full_name = (
            request.form
            .get("full_name", "")
            .strip()
        )

        username = (
            request.form
            .get("username", "")
            .strip()
        )

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # --------------------------------------------------
        # VALIDATE SETUP KEY
        # --------------------------------------------------

        if submitted_key != setup_key:
            flash(
                "Invalid administrator setup key.",
                "danger"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # VALIDATE FULL NAME
        # --------------------------------------------------

        if not full_name:
            flash(
                "Please enter the administrator's full name.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # VALIDATE USERNAME
        # --------------------------------------------------

        if not username:
            flash(
                "Please enter an administrator username.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        existing_username = (
            AdminUser.query
            .filter_by(username=username)
            .first()
        )

        if existing_username:
            flash(
                "That username is already in use.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # VALIDATE EMAIL
        # --------------------------------------------------

        if not email:
            flash(
                "Please enter the administrator's email address.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        existing_email = (
            AdminUser.query
            .filter_by(email=email)
            .first()
        )

        if existing_email:
            flash(
                "That email address is already in use.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # VALIDATE PASSWORD
        # --------------------------------------------------

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        if password != confirm_password:
            flash(
                "The passwords do not match.",
                "warning"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # CREATE ADMIN
        # --------------------------------------------------

        admin_user = AdminUser(
            full_name=full_name,
            username=username,
            email=email,
            password_hash=generate_password_hash(
                password
            )
        )

        db.session.add(admin_user)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Initial administrator creation failed."
            )

            flash(
                "Unable to create the administrator account. "
                "Please try again.",
                "danger"
            )

            return render_template(
                "admin/setup.html"
            )

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        flash(
            "Administrator account created successfully. "
            "You can now log in.",
            "success"
        )

        return redirect(
            url_for("admin.login")
        )

    return render_template(
        "admin/setup.html"
    )


@admin_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        if not email:

            flash(
                "Please enter your admin email address.",
                "warning"
            )

            return render_template(
                "admin/forgot_password.html"
            )


        admin_user = (
            AdminUser.query
            .filter(
                db.func.lower(
                    AdminUser.email
                ) == email
            )
            .first()
        )


        # Always show the same message whether
        # the email exists or not.
        if admin_user:

            raw_token = secrets.token_urlsafe(48)

            token_hash = hashlib.sha256(
                raw_token.encode("utf-8")
            ).hexdigest()

            admin_user.reset_token_hash = token_hash

            admin_user.reset_token_expires_at = (
                datetime.now(timezone.utc)
                + timedelta(
                    minutes=current_app.config[
                        "ADMIN_RESET_TOKEN_EXPIRY_MINUTES"
                    ]
                )
            )


            try:

                db.session.commit()

            except Exception:

                db.session.rollback()

                flash(
                    "Unable to process your request right now. Please try again.",
                    "danger"
                )

                return render_template(
                    "admin/forgot_password.html"
                )


            reset_url = url_for(
                "admin.reset_password",
                token=raw_token,
                _external=True
            )


            api_key = current_app.config.get(
                "RESEND_API_KEY"
            )

            if not api_key:

                current_app.logger.error(
                    "RESEND_API_KEY is not configured."
                )

                flash(
                    "Unable to send the password reset email right now.",
                    "danger"
                )

                return render_template(
                    "admin/forgot_password.html"
                )


            resend.api_key = api_key


            try:

                resend.Emails.send(
                    {
                        "from": current_app.config[
                            "RESEND_FROM_EMAIL"
                        ],
                        "to": [admin_user.email],
                        "subject": (
                            "Reset Your Efxion Admin Password"
                        ),
                        "html": f"""
                        <div style="
                            font-family: Arial, sans-serif;
                            background:#f6f8f7;
                            padding:40px 20px;
                        ">

                            <div style="
                                max-width:600px;
                                margin:0 auto;
                                background:#ffffff;
                                border-radius:16px;
                                padding:40px;
                            ">

                                <h2 style="
                                    color:#071a2b;
                                    margin-top:0;
                                ">
                                    Password Reset Request
                                </h2>

                                <p style="
                                    color:#667085;
                                    line-height:1.7;
                                ">
                                    We received a request to reset
                                    the password for your Efxion
                                    Technology Solutions admin account.
                                </p>

                                <p style="
                                    color:#667085;
                                    line-height:1.7;
                                ">
                                    Click the button below to create
                                    a new password.
                                </p>

                                <p style="
                                    margin:30px 0;
                                ">
                                    <a
                                        href="{reset_url}"
                                        style="
                                            display:inline-block;
                                            background:#708238;
                                            color:#ffffff;
                                            text-decoration:none;
                                            padding:14px 22px;
                                            border-radius:10px;
                                            font-weight:bold;
                                        "
                                    >
                                        Reset Password
                                    </a>
                                </p>

                                <p style="
                                    color:#667085;
                                    line-height:1.7;
                                ">
                                    This password reset link will
                                    expire in
                                    {
                                        current_app.config[
                                            "ADMIN_RESET_TOKEN_EXPIRY_MINUTES"
                                        ]
                                    }
                                    minutes.
                                </p>

                                <p style="
                                    color:#667085;
                                    line-height:1.7;
                                ">
                                    If you did not request this
                                    password reset, you can safely
                                    ignore this email.
                                </p>

                                <hr style="
                                    border:0;
                                    border-top:1px solid #e5e9e7;
                                    margin:30px 0;
                                ">

                                <p style="
                                    color:#98a2b3;
                                    font-size:13px;
                                ">
                                    Efxion Technology Solutions
                                </p>

                            </div>

                        </div>
                        """
                    }
                )

            except Exception as error:

                current_app.logger.exception(
                    "Resend password reset email failed: %s",
                    error
                )

                flash(
                    "Unable to send the password reset email right now.",
                    "danger"
                )

                return render_template(
                    "admin/forgot_password.html"
                )


        flash(
            "If an administrator account exists for that email, "
            "a password reset link has been sent.",
            "success"
        )

        return redirect(
            url_for("admin.login")
        )


    return render_template(
        "admin/forgot_password.html"
    )

@admin_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


    admin_user = (
        AdminUser.query
        .filter_by(
            reset_token_hash=token_hash
        )
        .first()
    )


    if not admin_user:

        flash(
            "This password reset link is invalid or has already been used.",
            "danger"
        )

        return redirect(
            url_for("admin.forgot_password")
        )


    expires_at = (
        admin_user.reset_token_expires_at
    )


    if not expires_at:

        flash(
            "This password reset link is invalid.",
            "danger"
        )

        return redirect(
            url_for("admin.forgot_password")
        )


    # Handle timezone differences safely.
    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )


    if datetime.now(timezone.utc) > expires_at:

        admin_user.reset_token_hash = None

        admin_user.reset_token_expires_at = None

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()


        flash(
            "This password reset link has expired. Please request a new one.",
            "warning"
        )

        return redirect(
            url_for("admin.forgot_password")
        )


    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        if not password:

            flash(
                "Please enter a new password.",
                "warning"
            )

            return render_template(
                "admin/reset_password.html",
                token=token
            )


        if len(password) < 8:

            flash(
                "Your password must contain at least 8 characters.",
                "warning"
            )

            return render_template(
                "admin/reset_password.html",
                token=token
            )


        if password != confirm_password:

            flash(
                "The passwords do not match.",
                "warning"
            )

            return render_template(
                "admin/reset_password.html",
                token=token
            )


        admin_user.password_hash = (
            generate_password_hash(
                password
            )
        )


        # Make the reset link single-use.
        admin_user.reset_token_hash = None

        admin_user.reset_token_expires_at = None


        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update your password. Please try again.",
                "danger"
            )

            return render_template(
                "admin/reset_password.html",
                token=token
            )


        flash(
            "Your password has been reset successfully. "
            "You can now log in.",
            "success"
        )

        return redirect(
            url_for("admin.login")
        )


    return render_template(
        "admin/reset_password.html",
        token=token
    )

# ============================================================
# ADMIN USERS
# ============================================================

@admin_bp.route("/users")
@login_required
@first_admin_required
def users():

    admin_users = (
        AdminUser.query
        .order_by(
            AdminUser.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin/users.html",
        admin_users=admin_users
    )


@admin_bp.route(
    "/users/new",
    methods=["GET", "POST"]
)
@login_required
def new_user():

    if request.method == "POST":

        full_name = (
            request.form
            .get("full_name", "")
            .strip()
        )

        username = (
            request.form
            .get("username", "")
            .strip()
            
        )

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not full_name:
            flash(
                "Please enter the administrator's full name.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        if not username:
            flash(
                "Please enter a username.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        if not email:
            flash(
                "Please enter an email address.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        existing_username = (
            AdminUser.query
            .filter_by(username=username)
            .first()
        )

        if existing_username:
            flash(
                "That username is already in use.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        existing_email = (
            AdminUser.query
            .filter_by(email=email)
            .first()
        )

        if existing_email:
            flash(
                "That email address is already in use.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        if password != confirm_password:
            flash(
                "The passwords do not match.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        # --------------------------------------------------
        # CREATE ADMIN
        # --------------------------------------------------

        admin_user = AdminUser(
            full_name=full_name,
            username=username,
            email=email,
            password_hash=generate_password_hash(
                password
            )
        )

        db.session.add(admin_user)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Administrator creation failed."
            )

            flash(
                "Unable to create the administrator. "
                "Please try again.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                admin_user=None
            )

        flash(
            "Administrator account created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin/user_form.html",
        admin_user=None
    )


@admin_bp.route(
    "/users/<int:user_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_user(user_id):

    admin_user = db.session.get(
        AdminUser,
        user_id
    )

    if not admin_user:
        flash(
            "Administrator account not found.",
            "danger"
        )
        return redirect(
            url_for("admin.users")
        )

    if request.method == "POST":

        full_name = (
            request.form
            .get("full_name", "")
            .strip()
        )

        username = (
            request.form
            .get("username", "")
            .strip()
            
        )

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        if not full_name:
            flash(
                "Please enter the administrator's full name.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        if not username:
            flash(
                "Please enter a username.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        if not email:
            flash(
                "Please enter an email address.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        existing_username = (
            AdminUser.query
            .filter(
                AdminUser.username == username,
                AdminUser.id != admin_user.id
            )
            .first()
        )

        if existing_username:
            flash(
                "That username is already in use.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        existing_email = (
            AdminUser.query
            .filter(
                AdminUser.email == email,
                AdminUser.id != admin_user.id
            )
            .first()
        )

        if existing_email:
            flash(
                "That email address is already in use.",
                "warning"
            )
            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        admin_user.full_name = full_name
        admin_user.username = username
        admin_user.email = email

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

            current_app.logger.exception(
                "Administrator update failed."
            )

            flash(
                "Unable to update the administrator.",
                "danger"
            )

            return render_template(
                "admin/user_form.html",
                admin_user=admin_user
            )

        flash(
            "Administrator account updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.users")
        )

    return render_template(
        "admin/user_form.html",
        admin_user=admin_user
    )

# ============================================================
# TOGGLE ADMIN USER STATUS
# ============================================================

@admin_bp.route(
    "/users/<int:user_id>/toggle-active",
    methods=["POST"]
)
@login_required
def toggle_user_active(user_id):

    admin_user = db.session.get(
        AdminUser,
        user_id
    )

    if not admin_user:
        flash(
            "Administrator account not found.",
            "danger"
        )
        return redirect(
            url_for("admin.users")
        )

    # --------------------------------------------------
    # PREVENT SELF-DEACTIVATION
    # --------------------------------------------------

    if admin_user.id == current_user.id:
        flash(
            "You cannot deactivate your own administrator account.",
            "warning"
        )
        return redirect(
            url_for("admin.users")
        )

    admin_user.is_active = not admin_user.is_active

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "Administrator status update failed."
        )

        flash(
            "Unable to update administrator status.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    if admin_user.is_active:
        flash(
            f"{admin_user.full_name} has been activated.",
            "success"
        )
    else:
        flash(
            f"{admin_user.full_name} has been deactivated.",
            "warning"
        )

    return redirect(
        url_for("admin.users")
    )


# ============================================================
# DELETE ADMIN USER
# ============================================================

@admin_bp.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@login_required
def delete_user(user_id):

    admin_user = db.session.get(
        AdminUser,
        user_id
    )

    if not admin_user:
        flash(
            "Administrator account not found.",
            "danger"
        )
        return redirect(
            url_for("admin.users")
        )

    # --------------------------------------------------
    # PREVENT SELF-DELETION
    # --------------------------------------------------

    if admin_user.id == current_user.id:
        flash(
            "You cannot delete your own administrator account.",
            "warning"
        )
        return redirect(
            url_for("admin.users")
        )

    try:

        db.session.delete(admin_user)
        db.session.commit()

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Administrator deletion failed."
        )

        flash(
            "Unable to delete the administrator.",
            "danger"
        )

        return redirect(
            url_for("admin.users")
        )

    flash(
        "Administrator account deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.users")
    )


# =========================================================
# LOGOUT
# =========================================================

@admin_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("admin.login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@admin_bp.route("/")
@login_required
def dashboard():

    open_positions = (
        CareerPosition.query
        .filter_by(
            is_published=True,
            is_closed=False
        )
        .count()
    )

    total_applications = (
        JobApplication.query.count()
    )

    new_applications = (
        JobApplication.query
        .filter_by(status="new")
        .count()
    )

    total_enquiries = (
        ContactMessage.query.count()
    )

    published_insights = (
        InsightArticle.query
        .filter_by(is_published=True)
        .count()
    )

    return render_template(
        "admin/dashboard.html",
        open_positions=open_positions,
        total_applications=total_applications,
        new_applications=new_applications,
        total_enquiries=total_enquiries,
        published_insights=published_insights
    )


# =========================================================
# JOB APPLICATIONS
# =========================================================

@admin_bp.route("/applications")
@login_required
def applications():

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip().lower()

    position_id = request.args.get(
        "position",
        type=int
    )

    allowed_statuses = {
        "new",
        "reviewing",
        "shortlisted",
        "rejected",
        "hired"
    }

    query = JobApplication.query

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                JobApplication.full_name.ilike(
                    search_term
                ),
                JobApplication.email.ilike(
                    search_term
                ),
                JobApplication.phone.ilike(
                    search_term
                )
            )
        )

    if status in allowed_statuses:

        query = query.filter(
            JobApplication.status == status
        )

    if position_id:

        query = query.filter(
            JobApplication.career_position_id
            == position_id
        )

    applications = (
        query
        .order_by(
            JobApplication.created_at.desc()
        )
        .all()
    )

    positions = (
        CareerPosition.query
        .order_by(
            CareerPosition.title.asc()
        )
        .all()
    )

    counts = {
        "all": JobApplication.query.count(),

        "new": (
            JobApplication.query
            .filter_by(status="new")
            .count()
        ),

        "reviewing": (
            JobApplication.query
            .filter_by(status="reviewing")
            .count()
        ),

        "shortlisted": (
            JobApplication.query
            .filter_by(status="shortlisted")
            .count()
        ),

        "hired": (
            JobApplication.query
            .filter_by(status="hired")
            .count()
        ),

        "rejected": (
            JobApplication.query
            .filter_by(status="rejected")
            .count()
        )
    }

    return render_template(
        "admin/applications.html",
        applications=applications,
        positions=positions,
        counts=counts,
        search=search,
        selected_status=status,
        selected_position=position_id
    )


# =========================================================
# APPLICATION DETAIL
# =========================================================

@admin_bp.route(
    "/applications/<int:application_id>"
)
@login_required
def application_detail(application_id):

    application = (
        JobApplication.query
        .filter_by(id=application_id)
        .first_or_404()
    )

    return render_template(
        "admin/application_detail.html",
        application=application
    )


# =========================================================
# UPDATE APPLICATION
# =========================================================

@admin_bp.route(
    "/applications/<int:application_id>/update",
    methods=["POST"]
)
@login_required
def update_application(application_id):

    application = (
        JobApplication.query
        .filter_by(id=application_id)
        .first_or_404()
    )

    status = request.form.get(
        "status",
        ""
    ).strip().lower()

    notes = request.form.get(
        "notes",
        ""
    ).strip()

    allowed_statuses = {
        "new",
        "reviewing",
        "shortlisted",
        "rejected",
        "hired"
    }

    if status not in allowed_statuses:

        flash(
            "Invalid application status.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.application_detail",
                application_id=application.id
            )
        )

    application.status = status
    application.notes = notes

    db.session.commit()

    flash(
        "Application updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin.application_detail",
            application_id=application.id
        )
    )


# =========================================================
# PROTECTED RESUME
# =========================================================

@admin_bp.route(
    "/applications/<int:application_id>/resume"
)
@login_required
def application_resume(application_id):

    application = (
        JobApplication.query
        .filter_by(id=application_id)
        .first_or_404()
    )

    if not application.resume_path:
        abort(404)

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).resolve()

    resume_name = Path(
        application.resume_path
    ).name

    resume_file = (
        upload_folder / resume_name
    ).resolve()

    # Prevent path traversal
    if resume_file.parent != upload_folder:
        abort(404)

    if not resume_file.is_file():
        abort(404)

    download_name = (
        application.resume_filename
        or resume_name
    )

    return send_from_directory(
        directory=str(upload_folder),
        path=resume_name,
        as_attachment=True,
        download_name=download_name
    )

# =========================================================
# CAREERS MANAGEMENT
# =========================================================

@admin_bp.route("/careers")
@login_required
def careers():

    positions = (
        CareerPosition.query
        .order_by(
            CareerPosition.is_published.desc(),
            CareerPosition.is_closed.asc(),
            CareerPosition.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin/careers.html",
        positions=positions
    )


# =========================================================
# CREATE CAREER
# =========================================================

@admin_bp.route(
    "/careers/new",
    methods=["GET", "POST"]
)
@login_required
def career_create():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        department = request.form.get(
            "department",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        employment_type = request.form.get(
            "employment_type",
            ""
        ).strip()

        work_mode = request.form.get(
            "work_mode",
            ""
        ).strip()

        salary = request.form.get(
            "salary",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        responsibilities = request.form.get(
            "responsibilities",
            ""
        ).strip()

        requirements = request.form.get(
            "requirements",
            ""
        ).strip()

        qualifications = request.form.get(
            "qualifications",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        experience_required = request.form.get(
            "experience_required",
            ""
        ).strip()

        application_email = request.form.get(
            "application_email",
            ""
        ).strip()

        deadline_string = request.form.get(
            "application_deadline",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_published = (
            request.form.get("is_published")
            == "on"
        )

        is_closed = (
            request.form.get("is_closed")
            == "on"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Job title is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=None,
                form_data=request.form
            )

        if not slug:

            flash(
                "URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=None,
                form_data=request.form
            )

        if not description:

            flash(
                "Job description is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=None,
                form_data=request.form
            )

        existing_slug = (
            CareerPosition.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:

            flash(
                "That URL slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=None,
                form_data=request.form
            )

        # -------------------------------------------------
        # DEADLINE
        # -------------------------------------------------

        application_deadline = None

        if deadline_string:

            try:

                from datetime import date

                application_deadline = (
                    date.fromisoformat(
                        deadline_string
                    )
                )

            except ValueError:

                flash(
                    "Invalid application deadline.",
                    "danger"
                )

                return render_template(
                    "admin/career_form.html",
                    position=None,
                    form_data=request.form
                )

        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------

        position = CareerPosition(

            title=title,

            slug=slug,

            department=department,

            location=location,

            employment_type=employment_type,

            work_mode=work_mode,

            salary=salary,

            short_description=short_description,

            description=description,

            responsibilities=responsibilities,

            requirements=requirements,

            qualifications=qualifications,

            skills=skills,

            experience_required=experience_required,

            application_email=(
                application_email
                or None
            ),

            application_deadline=(
                application_deadline
            ),

            is_featured=is_featured,

            is_published=is_published,

            is_closed=is_closed
        )

        db.session.add(position)

        db.session.commit()

        flash(
            "Career position created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.career_edit",
                position_id=position.id
            )
        )

    return render_template(
        "admin/career_form.html",
        position=None,
        form_data=None
    )


# =========================================================
# EDIT CAREER
# =========================================================

@admin_bp.route(
    "/careers/<int:position_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def career_edit(position_id):

    position = (
        CareerPosition.query
        .filter_by(id=position_id)
        .first_or_404()
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        department = request.form.get(
            "department",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        employment_type = request.form.get(
            "employment_type",
            ""
        ).strip()

        work_mode = request.form.get(
            "work_mode",
            ""
        ).strip()

        salary = request.form.get(
            "salary",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        responsibilities = request.form.get(
            "responsibilities",
            ""
        ).strip()

        requirements = request.form.get(
            "requirements",
            ""
        ).strip()

        qualifications = request.form.get(
            "qualifications",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        experience_required = request.form.get(
            "experience_required",
            ""
        ).strip()

        application_email = request.form.get(
            "application_email",
            ""
        ).strip()

        deadline_string = request.form.get(
            "application_deadline",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_published = (
            request.form.get("is_published")
            == "on"
        )

        is_closed = (
            request.form.get("is_closed")
            == "on"
        )

        if not title:

            flash(
                "Job title is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=position,
                form_data=request.form
            )

        if not slug:

            flash(
                "URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=position,
                form_data=request.form
            )

        if not description:

            flash(
                "Job description is required.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=position,
                form_data=request.form
            )

        existing_slug = (
            CareerPosition.query
            .filter(
                CareerPosition.slug == slug,
                CareerPosition.id != position.id
            )
            .first()
        )

        if existing_slug:

            flash(
                "That URL slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/career_form.html",
                position=position,
                form_data=request.form
            )

        # -------------------------------------------------
        # DEADLINE
        # -------------------------------------------------

        application_deadline = None

        if deadline_string:

            try:

                from datetime import date

                application_deadline = (
                    date.fromisoformat(
                        deadline_string
                    )
                )

            except ValueError:

                flash(
                    "Invalid application deadline.",
                    "danger"
                )

                return render_template(
                    "admin/career_form.html",
                    position=position,
                    form_data=request.form
                )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        position.title = title

        position.slug = slug

        position.department = department

        position.location = location

        position.employment_type = employment_type

        position.work_mode = work_mode

        position.salary = salary

        position.short_description = (
            short_description
        )

        position.description = description

        position.responsibilities = (
            responsibilities
        )

        position.requirements = (
            requirements
        )

        position.qualifications = (
            qualifications
        )

        position.skills = skills

        position.experience_required = (
            experience_required
        )

        position.application_email = (
            application_email
            or None
        )

        position.application_deadline = (
            application_deadline
        )

        position.is_featured = (
            is_featured
        )

        position.is_published = (
            is_published
        )

        position.is_closed = (
            is_closed
        )

        db.session.commit()

        flash(
            "Career position updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.careers"
            )
        )

    return render_template(
        "admin/career_form.html",
        position=position,
        form_data=None
    )


# =========================================================
# CLOSE / REOPEN CAREER
# =========================================================

@admin_bp.route(
    "/careers/<int:position_id>/toggle-status",
    methods=["POST"]
)
@login_required
def career_toggle_status(position_id):

    position = (
        CareerPosition.query
        .filter_by(id=position_id)
        .first_or_404()
    )

    position.is_closed = (
        not position.is_closed
    )

    db.session.commit()

    if position.is_closed:

        flash(
            f"{position.title} has been closed.",
            "success"
        )

    else:

        flash(
            f"{position.title} has been reopened.",
            "success"
        )

    return redirect(
        url_for("admin.careers")
    )


# =========================================================
# PUBLISH / UNPUBLISH CAREER
# =========================================================

@admin_bp.route(
    "/careers/<int:position_id>/toggle-publish",
    methods=["POST"]
)
@login_required
def career_toggle_publish(position_id):

    position = (
        CareerPosition.query
        .filter_by(id=position_id)
        .first_or_404()
    )

    position.is_published = (
        not position.is_published
    )

    db.session.commit()

    if position.is_published:

        flash(
            f"{position.title} is now published.",
            "success"
        )

    else:

        flash(
            f"{position.title} has been unpublished.",
            "success"
        )

    return redirect(
        url_for("admin.careers")
    )


# =========================================================
# DELETE CAREER
# =========================================================

@admin_bp.route(
    "/careers/<int:position_id>/delete",
    methods=["POST"]
)
@login_required
def career_delete(position_id):

    position = (
        CareerPosition.query
        .filter_by(id=position_id)
        .first_or_404()
    )

    application_count = (
        JobApplication.query
        .filter_by(
            career_position_id=position.id
        )
        .count()
    )

    if application_count > 0:

        flash(
            "This vacancy cannot be deleted because "
            f"it has {application_count} application(s). "
            "Close or unpublish it instead.",
            "warning"
        )

        return redirect(
            url_for("admin.careers")
        )

    title = position.title

    db.session.delete(position)

    db.session.commit()

    flash(
        f"{title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.careers")
    )

# =========================================================
# SERVICES MANAGEMENT
# =========================================================

@admin_bp.route("/services")
@login_required
def services():

    categories = (
        ServiceCategory.query
        .order_by(
            ServiceCategory.name.asc()
        )
        .all()
    )

    service_list = (
        Service.query
        .order_by(
            Service.is_active.desc(),
            Service.is_featured.desc(),
            Service.name.asc()
        )
        .all()
    )

    return render_template(
        "admin/services.html",
        categories=categories,
        services=service_list
    )


# =========================================================
# CREATE SERVICE
# =========================================================

@admin_bp.route(
    "/services/new",
    methods=["GET", "POST"]
)
@login_required
def service_create():

    categories = (
        ServiceCategory.query
        .order_by(
            ServiceCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        starting_price_string = request.form.get(
            "starting_price",
            ""
        ).strip()

        currency = request.form.get(
            "currency",
            "NGN"
        ).strip().upper()

        icon = request.form.get(
            "icon",
            "bi-code-slash"
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:

            flash(
                "Service name is required.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=None,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Service URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=None,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select a service category.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=None,
                categories=categories,
                form_data=request.form
            )

        category = db.session.get(
            ServiceCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected service category does not exist.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=None,
                categories=categories,
                form_data=request.form
            )

        existing_slug = (
            Service.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:

            flash(
                "That service slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # STARTING PRICE
        # -------------------------------------------------

        starting_price = None

        if starting_price_string:

            try:

                starting_price = float(
                    starting_price_string
                )

                if starting_price < 0:
                    raise ValueError

            except ValueError:

                flash(
                    "Please enter a valid starting price.",
                    "danger"
                )

                return render_template(
                    "admin/service_form.html",
                    service=None,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # CREATE
        # -------------------------------------------------

        service = Service(

            category_id=category_id,

            name=name,

            slug=slug,

            short_description=(
                short_description
                or None
            ),

            description=(
                description
                or None
            ),

            starting_price=(
                starting_price
            ),

            currency=(
                currency
                or "NGN"
            ),

            icon=(
                icon
                or "bi-code-slash"
            ),

            is_featured=is_featured,

            is_active=is_active
        )

        db.session.add(service)

        db.session.commit()

        flash(
            "Service created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.service_edit",
                service_id=service.id
            )
        )

    return render_template(
        "admin/service_form.html",
        service=None,
        categories=categories,
        form_data=None
    )


# =========================================================
# EDIT SERVICE
# =========================================================

@admin_bp.route(
    "/services/<int:service_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def service_edit(service_id):

    service = (
        Service.query
        .filter_by(id=service_id)
        .first_or_404()
    )

    categories = (
        ServiceCategory.query
        .order_by(
            ServiceCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        starting_price_string = request.form.get(
            "starting_price",
            ""
        ).strip()

        currency = request.form.get(
            "currency",
            "NGN"
        ).strip().upper()

        icon = request.form.get(
            "icon",
            "bi-code-slash"
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not name:

            flash(
                "Service name is required.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=service,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Service URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=service,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select a service category.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=service,
                categories=categories,
                form_data=request.form
            )

        category = db.session.get(
            ServiceCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected service category does not exist.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=service,
                categories=categories,
                form_data=request.form
            )

        existing_slug = (
            Service.query
            .filter(
                Service.slug == slug,
                Service.id != service.id
            )
            .first()
        )

        if existing_slug:

            flash(
                "That service slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/service_form.html",
                service=service,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # STARTING PRICE
        # -------------------------------------------------

        starting_price = None

        if starting_price_string:

            try:

                starting_price = float(
                    starting_price_string
                )

                if starting_price < 0:
                    raise ValueError

            except ValueError:

                flash(
                    "Please enter a valid starting price.",
                    "danger"
                )

                return render_template(
                    "admin/service_form.html",
                    service=service,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        service.category_id = category_id

        service.name = name

        service.slug = slug

        service.short_description = (
            short_description
            or None
        )

        service.description = (
            description
            or None
        )

        service.starting_price = (
            starting_price
        )

        service.currency = (
            currency
            or "NGN"
        )

        service.icon = (
            icon
            or "bi-code-slash"
        )

        service.is_featured = (
            is_featured
        )

        service.is_active = (
            is_active
        )

        db.session.commit()

        flash(
            "Service updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.services"
            )
        )

    return render_template(
        "admin/service_form.html",
        service=service,
        categories=categories,
        form_data=None
    )


# =========================================================
# ACTIVATE / DEACTIVATE SERVICE
# =========================================================

@admin_bp.route(
    "/services/<int:service_id>/toggle-active",
    methods=["POST"]
)
@login_required
def service_toggle_active(service_id):

    service = (
        Service.query
        .filter_by(id=service_id)
        .first_or_404()
    )

    service.is_active = (
        not service.is_active
    )

    db.session.commit()

    if service.is_active:

        flash(
            f"{service.name} is now active.",
            "success"
        )

    else:

        flash(
            f"{service.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for("admin.services")
    )


# =========================================================
# FEATURE / UNFEATURE SERVICE
# =========================================================

@admin_bp.route(
    "/services/<int:service_id>/toggle-featured",
    methods=["POST"]
)
@login_required
def service_toggle_featured(service_id):

    service = (
        Service.query
        .filter_by(id=service_id)
        .first_or_404()
    )

    service.is_featured = (
        not service.is_featured
    )

    db.session.commit()

    if service.is_featured:

        flash(
            f"{service.name} is now featured.",
            "success"
        )

    else:

        flash(
            f"{service.name} is no longer featured.",
            "success"
        )

    return redirect(
        url_for("admin.services")
    )


# =========================================================
# DELETE SERVICE
# =========================================================

@admin_bp.route(
    "/services/<int:service_id>/delete",
    methods=["POST"]
)
@login_required
def service_delete(service_id):

    service = (
        Service.query
        .filter_by(id=service_id)
        .first_or_404()
    )

    service_name = service.name

    db.session.delete(service)

    db.session.commit()

    flash(
        f"{service_name} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.services")
    )

# =========================================================
# PORTFOLIO MANAGEMENT
# =========================================================

@admin_bp.route("/portfolio")
@login_required
def portfolio():

    categories = (
        PortfolioCategory.query
        .order_by(
            PortfolioCategory.name.asc()
        )
        .all()
    )

    projects = (
        PortfolioProject.query
        .order_by(
            PortfolioProject.is_active.desc(),
            PortfolioProject.is_featured.desc(),
            PortfolioProject.year.desc(),
            PortfolioProject.title.asc()
        )
        .all()
    )

    return render_template(
        "admin/portfolio.html",
        categories=categories,
        projects=projects
    )


# =========================================================
# CREATE PORTFOLIO PROJECT
# =========================================================

@admin_bp.route(
    "/portfolio/new",
    methods=["GET", "POST"]
)
@login_required
def portfolio_create():

    categories = (
        PortfolioCategory.query
        .order_by(
            PortfolioCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        client_name = request.form.get(
            "client_name",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        technologies = request.form.get(
            "technologies",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        project_url = request.form.get(
            "project_url",
            ""
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        year_string = request.form.get(
            "year",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # -------------------------------------------------
        # REQUIRED VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Project title is required.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=None,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Project URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=None,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select a portfolio category.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        category = db.session.get(
            PortfolioCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected portfolio category does not exist.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # SLUG VALIDATION
        # -------------------------------------------------

        existing_slug = (
            PortfolioProject.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:

            flash(
                "That project slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # YEAR VALIDATION
        # -------------------------------------------------

        year = None

        if year_string:

            try:

                year = int(year_string)

                if year < 1900 or year > 2100:
                    raise ValueError

            except ValueError:

                flash(
                    "Please enter a valid project year.",
                    "danger"
                )

                return render_template(
                    "admin/portfolio_form.html",
                    project=None,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # CREATE PROJECT
        # -------------------------------------------------

        project = PortfolioProject(

            category_id=category_id,

            title=title,

            slug=slug,

            client_name=(
                client_name
                or None
            ),

            short_description=(
                short_description
                or None
            ),

            description=(
                description
                or None
            ),

            technologies=(
                technologies
                or None
            ),

            image=(
                image
                or None
            ),

            project_url=(
                project_url
                or None
            ),

            github_url=(
                github_url
                or None
            ),

            year=year,

            is_featured=is_featured,

            is_active=is_active
        )

        db.session.add(project)
        db.session.commit()

        flash(
            "Portfolio project created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.portfolio_edit",
                project_id=project.id
            )
        )

    return render_template(
        "admin/portfolio_form.html",
        project=None,
        categories=categories,
        form_data=None
    )


# =========================================================
# EDIT PORTFOLIO PROJECT
# =========================================================

@admin_bp.route(
    "/portfolio/<int:project_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def portfolio_edit(project_id):

    project = (
        PortfolioProject.query
        .filter_by(id=project_id)
        .first_or_404()
    )

    categories = (
        PortfolioCategory.query
        .order_by(
            PortfolioCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        client_name = request.form.get(
            "client_name",
            ""
        ).strip()

        short_description = request.form.get(
            "short_description",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        technologies = request.form.get(
            "technologies",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        project_url = request.form.get(
            "project_url",
            ""
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        year_string = request.form.get(
            "year",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        if not title:

            flash(
                "Project title is required.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=project,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Project URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=project,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select a portfolio category.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=project,
                categories=categories,
                form_data=request.form
            )

        category = db.session.get(
            PortfolioCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected portfolio category does not exist.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=project,
                categories=categories,
                form_data=request.form
            )

        existing_slug = (
            PortfolioProject.query
            .filter(
                PortfolioProject.slug == slug,
                PortfolioProject.id != project.id
            )
            .first()
        )

        if existing_slug:

            flash(
                "That project slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/portfolio_form.html",
                project=project,
                categories=categories,
                form_data=request.form
            )

        year = None

        if year_string:

            try:

                year = int(year_string)

                if year < 1900 or year > 2100:
                    raise ValueError

            except ValueError:

                flash(
                    "Please enter a valid project year.",
                    "danger"
                )

                return render_template(
                    "admin/portfolio_form.html",
                    project=project,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # UPDATE PROJECT
        # -------------------------------------------------

        project.category_id = category_id

        project.title = title

        project.slug = slug

        project.client_name = (
            client_name
            or None
        )

        project.short_description = (
            short_description
            or None
        )

        project.description = (
            description
            or None
        )

        project.technologies = (
            technologies
            or None
        )

        project.image = (
            image
            or None
        )

        project.project_url = (
            project_url
            or None
        )

        project.github_url = (
            github_url
            or None
        )

        project.year = year

        project.is_featured = is_featured

        project.is_active = is_active

        db.session.commit()

        flash(
            "Portfolio project updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.portfolio")
        )

    return render_template(
        "admin/portfolio_form.html",
        project=project,
        categories=categories,
        form_data=None
    )


# =========================================================
# ACTIVATE / DEACTIVATE PORTFOLIO PROJECT
# =========================================================

@admin_bp.route(
    "/portfolio/<int:project_id>/toggle-active",
    methods=["POST"]
)
@login_required
def portfolio_toggle_active(project_id):

    project = (
        PortfolioProject.query
        .filter_by(id=project_id)
        .first_or_404()
    )

    project.is_active = not project.is_active

    db.session.commit()

    if project.is_active:

        flash(
            f"{project.title} is now active.",
            "success"
        )

    else:

        flash(
            f"{project.title} has been deactivated.",
            "success"
        )

    return redirect(
        url_for("admin.portfolio")
    )


# =========================================================
# FEATURE / UNFEATURE PORTFOLIO PROJECT
# =========================================================

@admin_bp.route(
    "/portfolio/<int:project_id>/toggle-featured",
    methods=["POST"]
)
@login_required
def portfolio_toggle_featured(project_id):

    project = (
        PortfolioProject.query
        .filter_by(id=project_id)
        .first_or_404()
    )

    project.is_featured = not project.is_featured

    db.session.commit()

    if project.is_featured:

        flash(
            f"{project.title} is now featured.",
            "success"
        )

    else:

        flash(
            f"{project.title} is no longer featured.",
            "success"
        )

    return redirect(
        url_for("admin.portfolio")
    )


# =========================================================
# DELETE PORTFOLIO PROJECT
# =========================================================

@admin_bp.route(
    "/portfolio/<int:project_id>/delete",
    methods=["POST"]
)
@login_required
def portfolio_delete(project_id):

    project = (
        PortfolioProject.query
        .filter_by(id=project_id)
        .first_or_404()
    )

    project_title = project.title

    db.session.delete(project)

    db.session.commit()

    flash(
        f"{project_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.portfolio")
    )

# =========================================================
# INSIGHTS MANAGEMENT
# =========================================================

@admin_bp.route("/insights")
@login_required
def insights():

    categories = (
        InsightCategory.query
        .order_by(
            InsightCategory.name.asc()
        )
        .all()
    )

    articles = (
        InsightArticle.query
        .order_by(
            InsightArticle.is_featured.desc(),
            InsightArticle.published_at.desc(),
            InsightArticle.created_at.desc()
        )
        .all()
    )

    return render_template(
        "admin/insights.html",
        categories=categories,
        articles=articles
    )


# =========================================================
# CREATE INSIGHT ARTICLE
# =========================================================

@admin_bp.route(
    "/insights/new",
    methods=["GET", "POST"]
)
@login_required
def insight_create():

    categories = (
        InsightCategory.query
        .order_by(
            InsightCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        excerpt = request.form.get(
            "excerpt",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        featured_image = request.form.get(
            "featured_image",
            ""
        ).strip()

        reading_time_string = request.form.get(
            "reading_time",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_published = (
            request.form.get("is_published")
            == "on"
        )

        # -------------------------------------------------
        # REQUIRED VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Article title is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Article URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select an insight category.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        if not content:

            flash(
                "Article content is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        category = db.session.get(
            InsightCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected insight category does not exist.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # SLUG VALIDATION
        # -------------------------------------------------

        existing_slug = (
            InsightArticle.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:

            flash(
                "That article slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=None,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # READING TIME VALIDATION
        # -------------------------------------------------

        reading_time = 5

        if reading_time_string:

            try:

                reading_time = int(
                    reading_time_string
                )

                if reading_time < 1:
                    raise ValueError

            except ValueError:

                flash(
                    "Reading time must be at least 1 minute.",
                    "danger"
                )

                return render_template(
                    "admin/insight_form.html",
                    article=None,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # PUBLICATION DATE
        # -------------------------------------------------

        published_at = None

        if is_published:

            published_at = datetime.now(
                timezone.utc
            )

        # -------------------------------------------------
        # CREATE ARTICLE
        # -------------------------------------------------

        article = InsightArticle(

            category_id=category_id,

            title=title,

            slug=slug,

            excerpt=(
                excerpt
                or None
            ),

            content=content,

            author=(
                author
                or "Efxion Technology Solutions"
            ),

            featured_image=(
                featured_image
                or None
            ),

            reading_time=reading_time,

            published_at=published_at,

            is_featured=is_featured,

            is_published=is_published
        )

        db.session.add(article)

        db.session.commit()

        flash(
            "Insight article created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.insight_edit",
                article_id=article.id
            )
        )

    return render_template(
        "admin/insight_form.html",
        article=None,
        categories=categories,
        form_data=None
    )


# =========================================================
# EDIT INSIGHT ARTICLE
# =========================================================

@admin_bp.route(
    "/insights/<int:article_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def insight_edit(article_id):

    article = (
        InsightArticle.query
        .filter_by(id=article_id)
        .first_or_404()
    )

    categories = (
        InsightCategory.query
        .order_by(
            InsightCategory.name.asc()
        )
        .all()
    )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip().lower()

        category_id = request.form.get(
            "category_id",
            type=int
        )

        excerpt = request.form.get(
            "excerpt",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        featured_image = request.form.get(
            "featured_image",
            ""
        ).strip()

        reading_time_string = request.form.get(
            "reading_time",
            ""
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_published = (
            request.form.get("is_published")
            == "on"
        )

        # -------------------------------------------------
        # REQUIRED VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Article title is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        if not slug:

            flash(
                "Article URL slug is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        if not category_id:

            flash(
                "Please select an insight category.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        if not content:

            flash(
                "Article content is required.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------

        category = db.session.get(
            InsightCategory,
            category_id
        )

        if category is None:

            flash(
                "Selected insight category does not exist.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # SLUG VALIDATION
        # -------------------------------------------------

        existing_slug = (
            InsightArticle.query
            .filter(
                InsightArticle.slug == slug,
                InsightArticle.id != article.id
            )
            .first()
        )

        if existing_slug:

            flash(
                "That article slug is already being used.",
                "danger"
            )

            return render_template(
                "admin/insight_form.html",
                article=article,
                categories=categories,
                form_data=request.form
            )

        # -------------------------------------------------
        # READING TIME VALIDATION
        # -------------------------------------------------

        reading_time = 5

        if reading_time_string:

            try:

                reading_time = int(
                    reading_time_string
                )

                if reading_time < 1:
                    raise ValueError

            except ValueError:

                flash(
                    "Reading time must be at least 1 minute.",
                    "danger"
                )

                return render_template(
                    "admin/insight_form.html",
                    article=article,
                    categories=categories,
                    form_data=request.form
                )

        # -------------------------------------------------
        # PUBLICATION DATE
        # -------------------------------------------------

        if (
            is_published
            and article.published_at is None
        ):

            article.published_at = (
                datetime.now(
                    timezone.utc
                )
            )

        elif not is_published:

            article.published_at = None

        # -------------------------------------------------
        # UPDATE ARTICLE
        # -------------------------------------------------

        article.category_id = category_id

        article.title = title

        article.slug = slug

        article.excerpt = (
            excerpt
            or None
        )

        article.content = content

        article.author = (
            author
            or "Efxion Technology Solutions"
        )

        article.featured_image = (
            featured_image
            or None
        )

        article.reading_time = reading_time

        article.is_featured = is_featured

        article.is_published = is_published

        db.session.commit()

        flash(
            "Insight article updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin.insights")
        )

    return render_template(
        "admin/insight_form.html",
        article=article,
        categories=categories,
        form_data=None
    )


# =========================================================
# PUBLISH / UNPUBLISH ARTICLE
# =========================================================

@admin_bp.route(
    "/insights/<int:article_id>/toggle-published",
    methods=["POST"]
)
@login_required
def insight_toggle_published(article_id):

    article = (
        InsightArticle.query
        .filter_by(id=article_id)
        .first_or_404()
    )

    if article.is_published:

        article.is_published = False
        article.published_at = None

        message = (
            f"{article.title} has been unpublished."
        )

    else:

        article.is_published = True

        article.published_at = (
            datetime.now(
                timezone.utc
            )
        )

        message = (
            f"{article.title} has been published."
        )

    db.session.commit()

    flash(
        message,
        "success"
    )

    return redirect(
        url_for("admin.insights")
    )


# =========================================================
# FEATURE / UNFEATURE ARTICLE
# =========================================================

@admin_bp.route(
    "/insights/<int:article_id>/toggle-featured",
    methods=["POST"]
)
@login_required
def insight_toggle_featured(article_id):

    article = (
        InsightArticle.query
        .filter_by(id=article_id)
        .first_or_404()
    )

    article.is_featured = (
        not article.is_featured
    )

    db.session.commit()

    if article.is_featured:

        flash(
            f"{article.title} is now featured.",
            "success"
        )

    else:

        flash(
            f"{article.title} is no longer featured.",
            "success"
        )

    return redirect(
        url_for("admin.insights")
    )


# =========================================================
# DELETE INSIGHT ARTICLE
# =========================================================

@admin_bp.route(
    "/insights/<int:article_id>/delete",
    methods=["POST"]
)
@login_required
def insight_delete(article_id):

    article = (
        InsightArticle.query
        .filter_by(id=article_id)
        .first_or_404()
    )

    article_title = article.title

    db.session.delete(article)

    db.session.commit()

    flash(
        f"{article_title} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin.insights")
    )

# =========================================================
# CONTACT MESSAGES / ENQUIRIES MANAGEMENT
# =========================================================

@admin_bp.route("/messages")
@login_required
def messages():

    messages = (
        ContactMessage.query
        .order_by(
            ContactMessage.status.asc(),
            ContactMessage.created_at.desc()
        )
        .all()
    )

    total_messages = len(messages)

    new_messages = sum(
        1
        for message in messages
        if message.status == "new"
    )

    read_messages = sum(
        1
        for message in messages
        if message.status == "read"
    )

    replied_messages = sum(
        1
        for message in messages
        if message.status == "replied"
    )

    closed_messages = sum(
        1
        for message in messages
        if message.status == "closed"
    )

    return render_template(
        "admin/messages.html",
        messages=messages,
        total_messages=total_messages,
        new_messages=new_messages,
        read_messages=read_messages,
        replied_messages=replied_messages,
        closed_messages=closed_messages
    )


@admin_bp.route(
    "/messages/<int:message_id>"
)
@login_required
def message_detail(message_id):

    contact_message = db.session.get(
        ContactMessage,
        message_id
    )

    if not contact_message:
        flash(
            "Contact message not found.",
            "danger"
        )

        return redirect(
            url_for("admin.messages")
        )

    # Automatically mark a new message as read
    if contact_message.status == "new":

        contact_message.status = "read"

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

    return render_template(
        "admin/message_detail.html",
        contact_message=contact_message
    )


@admin_bp.route(
    "/messages/<int:message_id>/status/<status>",
    methods=["POST"]
)
@login_required
def update_message_status(
    message_id,
    status
):

    allowed_statuses = {
        "new",
        "read",
        "replied",
        "closed"
    }

    if status not in allowed_statuses:

        flash(
            "Invalid message status.",
            "danger"
        )

        return redirect(
            url_for("admin.messages")
        )

    contact_message = db.session.get(
        ContactMessage,
        message_id
    )

    if not contact_message:

        flash(
            "Contact message not found.",
            "danger"
        )

        return redirect(
            url_for("admin.messages")
        )

    contact_message.status = status

    try:

        db.session.commit()

        status_labels = {
            "new": "New",
            "read": "Read",
            "replied": "Replied",
            "closed": "Closed"
        }

        flash(
            f"Message marked as "
            f"{status_labels[status]}.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update message status.",
            "danger"
        )

    return redirect(
        request.referrer
        or url_for("admin.messages")
    )


@admin_bp.route(
    "/messages/<int:message_id>/delete",
    methods=["POST"]
)
@login_required
def delete_message(message_id):

    contact_message = db.session.get(
        ContactMessage,
        message_id
    )

    if not contact_message:

        flash(
            "Contact message not found.",
            "danger"
        )

        return redirect(
            url_for("admin.messages")
        )

    try:

        db.session.delete(
            contact_message
        )

        db.session.commit()

        flash(
            "Contact message deleted successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete contact message.",
            "danger"
        )

    return redirect(
        url_for("admin.messages")
    )

# =========================================================
# TEAM / STAFF MANAGEMENT
# =========================================================

@admin_bp.route("/team")
@login_required
def team():

    staff_profiles = (
        StaffProfile.query
        .order_by(
            StaffProfile.is_active.desc(),
            StaffProfile.is_featured.desc(),
            StaffProfile.display_order.asc(),
            StaffProfile.full_name.asc()
        )
        .all()
    )

    total_staff = len(staff_profiles)

    active_staff = sum(
        1
        for staff in staff_profiles
        if staff.is_active
    )

    featured_staff = sum(
        1
        for staff in staff_profiles
        if staff.is_featured
    )

    inactive_staff = sum(
        1
        for staff in staff_profiles
        if not staff.is_active
    )

    return render_template(
        "admin/team.html",
        staff_profiles=staff_profiles,
        total_staff=total_staff,
        active_staff=active_staff,
        featured_staff=featured_staff,
        inactive_staff=inactive_staff
    )


@admin_bp.route(
    "/team/new",
    methods=["GET", "POST"]
)
@login_required
def new_staff():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip()

        job_title = request.form.get(
            "job_title",
            ""
        ).strip()

        department = request.form.get(
            "department",
            ""
        ).strip()

        profile_image = request.form.get(
            "profile_image",
            ""
        ).strip()

        short_bio = request.form.get(
            "short_bio",
            ""
        ).strip()

        biography = request.form.get(
            "biography",
            ""
        ).strip()

        experience = request.form.get(
            "experience",
            ""
        ).strip()

        education = request.form.get(
            "education",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        expertise = request.form.get(
            "expertise",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        linkedin_url = request.form.get(
            "linkedin_url",
            ""
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        portfolio_url = request.form.get(
            "portfolio_url",
            ""
        ).strip()

        date_joined_value = request.form.get(
            "date_joined",
            ""
        ).strip()

        display_order_value = request.form.get(
            "display_order",
            "0"
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # ---------------------------------------------
        # Validation
        # ---------------------------------------------

        if not full_name:
            flash(
                "Full name is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

        if not slug:
            flash(
                "Slug is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

        if not job_title:
            flash(
                "Job title is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

        existing_slug = (
            StaffProfile.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:
            flash(
                "That slug is already in use.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

        # ---------------------------------------------
        # Date
        # ---------------------------------------------

        date_joined = None

        if date_joined_value:

            try:

                date_joined = datetime.strptime(
                    date_joined_value,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                flash(
                    "Please enter a valid joining date.",
                    "danger"
                )

                return render_template(
                    "admin/team_form.html",
                    staff=None
                )

        # ---------------------------------------------
        # Display order
        # ---------------------------------------------

        try:

            display_order = int(
                display_order_value
                or 0
            )

        except ValueError:

            flash(
                "Display order must be a number.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

        staff = StaffProfile(
            full_name=full_name,
            slug=slug,
            job_title=job_title,
            department=department,
            profile_image=profile_image,
            short_bio=short_bio,
            biography=biography,
            experience=experience,
            education=education,
            skills=skills,
            expertise=expertise,
            email=email,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
            date_joined=date_joined,
            is_featured=is_featured,
            is_active=is_active,
            display_order=display_order
        )

        try:

            db.session.add(staff)
            db.session.commit()

            flash(
                "Team member created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.team")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to create team member.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=None
            )

    return render_template(
        "admin/team_form.html",
        staff=None
    )


@admin_bp.route(
    "/team/<int:staff_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_staff(staff_id):

    staff = db.session.get(
        StaffProfile,
        staff_id
    )

    if not staff:

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("admin.team")
        )

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        slug = request.form.get(
            "slug",
            ""
        ).strip()

        job_title = request.form.get(
            "job_title",
            ""
        ).strip()

        if not full_name:

            flash(
                "Full name is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=staff
            )

        if not slug:

            flash(
                "Slug is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=staff
            )

        if not job_title:

            flash(
                "Job title is required.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=staff
            )

        existing_slug = (
            StaffProfile.query
            .filter(
                StaffProfile.slug == slug,
                StaffProfile.id != staff.id
            )
            .first()
        )

        if existing_slug:

            flash(
                "That slug is already in use.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=staff
            )

        date_joined_value = request.form.get(
            "date_joined",
            ""
        ).strip()

        date_joined = None

        if date_joined_value:

            try:

                date_joined = datetime.strptime(
                    date_joined_value,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                flash(
                    "Please enter a valid joining date.",
                    "danger"
                )

                return render_template(
                    "admin/team_form.html",
                    staff=staff
                )

        try:

            display_order = int(
                request.form.get(
                    "display_order",
                    "0"
                ).strip()
                or 0
            )

        except ValueError:

            flash(
                "Display order must be a number.",
                "danger"
            )

            return render_template(
                "admin/team_form.html",
                staff=staff
            )

        staff.full_name = full_name
        staff.slug = slug
        staff.job_title = job_title

        staff.department = request.form.get(
            "department",
            ""
        ).strip()

        staff.profile_image = request.form.get(
            "profile_image",
            ""
        ).strip()

        staff.short_bio = request.form.get(
            "short_bio",
            ""
        ).strip()

        staff.biography = request.form.get(
            "biography",
            ""
        ).strip()

        staff.experience = request.form.get(
            "experience",
            ""
        ).strip()

        staff.education = request.form.get(
            "education",
            ""
        ).strip()

        staff.skills = request.form.get(
            "skills",
            ""
        ).strip()

        staff.expertise = request.form.get(
            "expertise",
            ""
        ).strip()

        staff.email = request.form.get(
            "email",
            ""
        ).strip()

        staff.linkedin_url = request.form.get(
            "linkedin_url",
            ""
        ).strip()

        staff.github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        staff.portfolio_url = request.form.get(
            "portfolio_url",
            ""
        ).strip()

        staff.date_joined = date_joined

        staff.is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        staff.is_active = (
            request.form.get("is_active")
            == "on"
        )

        staff.display_order = display_order

        try:

            db.session.commit()

            flash(
                "Team member updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin.team")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update team member.",
                "danger"
            )

    return render_template(
        "admin/team_form.html",
        staff=staff
    )


@admin_bp.route(
    "/team/<int:staff_id>/toggle-active",
    methods=["POST"]
)
@login_required
def toggle_staff_active(staff_id):

    staff = db.session.get(
        StaffProfile,
        staff_id
    )

    if not staff:

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("admin.team")
        )

    staff.is_active = not staff.is_active

    try:

        db.session.commit()

        flash(
            "Team member visibility updated.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update team member visibility.",
            "danger"
        )

    return redirect(
        request.referrer
        or url_for("admin.team")
    )


@admin_bp.route(
    "/team/<int:staff_id>/toggle-featured",
    methods=["POST"]
)
@login_required
def toggle_staff_featured(staff_id):

    staff = db.session.get(
        StaffProfile,
        staff_id
    )

    if not staff:

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("admin.team")
        )

    staff.is_featured = not staff.is_featured

    try:

        db.session.commit()

        flash(
            "Team member featured status updated.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update featured status.",
            "danger"
        )

    return redirect(
        request.referrer
        or url_for("admin.team")
    )


@admin_bp.route(
    "/team/<int:staff_id>/delete",
    methods=["POST"]
)
@login_required
def delete_staff(staff_id):

    staff = db.session.get(
        StaffProfile,
        staff_id
    )

    if not staff:

        flash(
            "Team member not found.",
            "danger"
        )

        return redirect(
            url_for("admin.team")
        )

    try:

        db.session.delete(staff)
        db.session.commit()

        flash(
            "Team member deleted successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete team member.",
            "danger"
        )

    return redirect(
        url_for("admin.team")
    )
# =========================================================
# FAQ MANAGEMENT
# =========================================================

@admin_bp.route("/faq")
@login_required
def faq():

    faqs = (
        FAQ.query
        .order_by(
            FAQ.is_active.desc(),
            FAQ.is_featured.desc(),
            FAQ.display_order.asc(),
            FAQ.created_at.desc()
        )
        .all()
    )

    total_faqs = len(faqs)

    active_faqs = sum(
        1
        for item in faqs
        if item.is_active
    )

    featured_faqs = sum(
        1
        for item in faqs
        if item.is_featured
    )

    inactive_faqs = sum(
        1
        for item in faqs
        if not item.is_active
    )

    return render_template(
        "admin/faq.html",
        faqs=faqs,
        total_faqs=total_faqs,
        active_faqs=active_faqs,
        featured_faqs=featured_faqs,
        inactive_faqs=inactive_faqs
    )


@admin_bp.route(
    "/faq/new",
    methods=["GET", "POST"]
)
@login_required
def new_faq():

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        answer = request.form.get(
            "answer",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        display_order_value = request.form.get(
            "display_order",
            "0"
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # ---------------------------------------------
        # Validation
        # ---------------------------------------------

        if not question:

            flash(
                "FAQ question is required.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=None
            )

        if not answer:

            flash(
                "FAQ answer is required.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=None
            )

        try:

            display_order = int(
                display_order_value or 0
            )

        except ValueError:

            flash(
                "Display order must be a number.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=None
            )

        if display_order < 0:

            flash(
                "Display order cannot be negative.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=None
            )

        faq_item = FAQ(
            question=question,
            answer=answer,
            category=category,
            display_order=display_order,
            is_featured=is_featured,
            is_active=is_active
        )

        try:

            db.session.add(faq_item)
            db.session.commit()

            flash(
                "FAQ created successfully.",
                "success"
            )

            return redirect(
                url_for("admin.faq")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to create FAQ.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=None
            )

    return render_template(
        "admin/faq_form.html",
        faq_item=None
    )


@admin_bp.route(
    "/faq/<int:faq_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_faq(faq_id):

    faq_item = db.session.get(
        FAQ,
        faq_id
    )

    if not faq_item:

        flash(
            "FAQ not found.",
            "danger"
        )

        return redirect(
            url_for("admin.faq")
        )

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        answer = request.form.get(
            "answer",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        display_order_value = request.form.get(
            "display_order",
            "0"
        ).strip()

        is_featured = (
            request.form.get("is_featured")
            == "on"
        )

        is_active = (
            request.form.get("is_active")
            == "on"
        )

        # ---------------------------------------------
        # Validation
        # ---------------------------------------------

        if not question:

            flash(
                "FAQ question is required.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=faq_item
            )

        if not answer:

            flash(
                "FAQ answer is required.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=faq_item
            )

        try:

            display_order = int(
                display_order_value or 0
            )

        except ValueError:

            flash(
                "Display order must be a number.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=faq_item
            )

        if display_order < 0:

            flash(
                "Display order cannot be negative.",
                "danger"
            )

            return render_template(
                "admin/faq_form.html",
                faq_item=faq_item
            )

        # ---------------------------------------------
        # Update
        # ---------------------------------------------

        faq_item.question = question
        faq_item.answer = answer
        faq_item.category = category
        faq_item.display_order = display_order
        faq_item.is_featured = is_featured
        faq_item.is_active = is_active

        try:

            db.session.commit()

            flash(
                "FAQ updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin.faq")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to update FAQ.",
                "danger"
            )

    return render_template(
        "admin/faq_form.html",
        faq_item=faq_item
    )


@admin_bp.route(
    "/faq/<int:faq_id>/toggle-active",
    methods=["POST"]
)
@login_required
def toggle_faq_active(faq_id):

    faq_item = db.session.get(
        FAQ,
        faq_id
    )

    if not faq_item:

        flash(
            "FAQ not found.",
            "danger"
        )

        return redirect(
            url_for("admin.faq")
        )

    faq_item.is_active = (
        not faq_item.is_active
    )

    try:

        db.session.commit()

        flash(
            "FAQ visibility updated.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update FAQ visibility.",
            "danger"
        )

    return redirect(
        request.referrer
        or url_for("admin.faq")
    )


@admin_bp.route(
    "/faq/<int:faq_id>/toggle-featured",
    methods=["POST"]
)
@login_required
def toggle_faq_featured(faq_id):

    faq_item = db.session.get(
        FAQ,
        faq_id
    )

    if not faq_item:

        flash(
            "FAQ not found.",
            "danger"
        )

        return redirect(
            url_for("admin.faq")
        )

    faq_item.is_featured = (
        not faq_item.is_featured
    )

    try:

        db.session.commit()

        flash(
            "FAQ featured status updated.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update FAQ featured status.",
            "danger"
        )

    return redirect(
        request.referrer
        or url_for("admin.faq")
    )


@admin_bp.route(
    "/faq/<int:faq_id>/delete",
    methods=["POST"]
)
@login_required
def delete_faq(faq_id):

    faq_item = db.session.get(
        FAQ,
        faq_id
    )

    if not faq_item:

        flash(
            "FAQ not found.",
            "danger"
        )

        return redirect(
            url_for("admin.faq")
        )

    try:

        db.session.delete(faq_item)
        db.session.commit()

        flash(
            "FAQ deleted successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete FAQ.",
            "danger"
        )

    return redirect(
        url_for("admin.faq")
    )
