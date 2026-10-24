from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from werkzeug.utils import secure_filename
from app import db

from app.models import (
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

main_bp = Blueprint(
    "main",
    __name__
)

from sqlalchemy.exc import SQLAlchemyError


@main_bp.route("/")
def home():

    insights = (
        InsightArticle.query
        .filter_by(is_published=True)
        .order_by(
            InsightArticle.is_featured.desc(),
            InsightArticle.published_at.desc(),
            InsightArticle.created_at.desc()
        )
        .limit(3)
        .all()
    )

    return render_template(
        "index.html",
        insights=insights
    )

@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/services")
def services():
    categories = (
        ServiceCategory.query
        .order_by(ServiceCategory.name.asc())
        .all()
    )

    return render_template(
        "services.html",
        categories=categories
    )


@main_bp.route("/portfolio")
def portfolio():

    categories = (
        PortfolioCategory.query
        .order_by(PortfolioCategory.name.asc())
        .all()
    )

    featured_projects = (
        PortfolioProject.query
        .filter_by(
            is_active=True,
            is_featured=True
        )
        .order_by(
            PortfolioProject.year.desc(),
            PortfolioProject.created_at.desc()
        )
        .all()
    )

    return render_template(
        "portfolio.html",
        categories=categories,
        featured_projects=featured_projects
    )


@main_bp.route("/insights")
def insights():

    articles = (
        InsightArticle.query
        .filter_by(is_published=True)
        .order_by(
            InsightArticle.published_at.desc(),
            InsightArticle.created_at.desc()
        )
        .all()
    )

    categories = (
        InsightCategory.query
        .order_by(InsightCategory.name.asc())
        .all()
    )

    return render_template(
        "insights.html",
        articles=articles,
        categories=categories
    )

@main_bp.route("/insights/<slug>")
def insight_detail(slug):

    article = (
        InsightArticle.query
        .filter_by(
            slug=slug,
            is_published=True
        )
        .first_or_404()
    )

    return render_template(
        "insight_detail.html",
        article=article
    )


@main_bp.route("/faq")
def faq():

    faqs = (
        FAQ.query
        .filter(
            FAQ.is_active.is_(True)
        )
        .order_by(
            FAQ.is_featured.desc(),
            FAQ.display_order.asc(),
            FAQ.created_at.desc()
        )
        .all()
    )

    categories = sorted({
        faq.category
        for faq in faqs
        if faq.category
    })

    return render_template(
        "faq.html",
        faqs=faqs,
        categories=categories
    )

@main_bp.route("/contact", methods=["GET", "POST"])
def contact():

    services = (
        Service.query
        .filter_by(is_active=True)
        .order_by(Service.name.asc())
        .all()
    )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        service = request.form.get(
            "service",
            ""
        ).strip()

        project_type = request.form.get(
            "project_type",
            ""
        ).strip()

        budget = request.form.get(
            "budget",
            ""
        ).strip()

        preferred_contact = request.form.get(
            "preferred_contact",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        # -----------------------------------------
        # BASIC VALIDATION
        # -----------------------------------------

        if not name:
            flash(
                "Please enter your name.",
                "danger"
            )

            return render_template(
                "contact.html",
                services=services
            )

        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )

            return render_template(
                "contact.html",
                services=services
            )

        if "@" not in email:
            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return render_template(
                "contact.html",
                services=services
            )

        if not message:
            flash(
                "Please tell us a little about your project or enquiry.",
                "danger"
            )

            return render_template(
                "contact.html",
                services=services
            )

        # -----------------------------------------
        # SAVE ENQUIRY
        # -----------------------------------------

        enquiry = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            company=company,
            service=service,
            project_type=project_type,
            budget=budget,
            preferred_contact=preferred_contact,
            message=message,
            status="new"
        )

        db.session.add(enquiry)
        db.session.commit()

        flash(
            "Thank you. Your enquiry has been received. "
            "Our team will review it and get back to you.",
            "success"
        )

        return redirect(
            url_for("main.contact")
        )

    return render_template(
        "contact.html",
        services=services
    )

@main_bp.route("/team")
def team():

    staff = (
        StaffProfile.query
        .filter_by(is_active=True)
        .order_by(
            StaffProfile.display_order.asc(),
            StaffProfile.full_name.asc()
        )
        .all()
    )

    return render_template(
        "team.html",
        staff=staff
    )


@main_bp.route("/team/<slug>")
def team_profile(slug):

    member = (
        StaffProfile.query
        .filter_by(
            slug=slug,
            is_active=True
        )
        .first_or_404()
    )

    return render_template(
        "team_profile.html",
        member=member
    )

@main_bp.route("/careers")
def careers():

    positions = (
        CareerPosition.query
        .filter_by(
            is_published=True,
            is_closed=False
        )
        .order_by(
            CareerPosition.is_featured.desc(),
            CareerPosition.created_at.desc()
        )
        .all()
    )

    return render_template(
        "careers.html",
        positions=positions
    )


@main_bp.route("/careers/<slug>")
def career_detail(slug):

    position = (
        CareerPosition.query
        .filter_by(
            slug=slug,
            is_published=True
        )
        .first_or_404()
    )

    return render_template(
        "career_detail.html",
        position=position
    )

@main_bp.route(
    "/careers/<slug>/apply",
    methods=["GET", "POST"]
)
def career_apply(slug):

    position = (
        CareerPosition.query
        .filter_by(
            slug=slug,
            is_published=True
        )
        .first_or_404()
    )

    if position.is_closed:
        flash(
            "Applications for this position are currently closed.",
            "warning"
        )

        return redirect(
            url_for(
                "main.career_detail",
                slug=position.slug
            )
        )

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        current_job_title = request.form.get(
            "current_job_title",
            ""
        ).strip()

        years_of_experience = request.form.get(
            "years_of_experience",
            ""
        ).strip()

        linkedin_url = request.form.get(
            "linkedin_url",
            ""
        ).strip()

        portfolio_url = request.form.get(
            "portfolio_url",
            ""
        ).strip()

        github_url = request.form.get(
            "github_url",
            ""
        ).strip()

        cover_letter = request.form.get(
            "cover_letter",
            ""
        ).strip()

        resume = request.files.get("resume")

        # -------------------------------
        # BASIC VALIDATION
        # -------------------------------

        if not full_name:
            flash(
                "Please enter your full name.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        if not email:
            flash(
                "Please enter your email address.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        if "@" not in email:
            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        if not cover_letter:
            flash(
                "Please provide a cover letter.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        if not resume:
            flash(
                "Please upload your CV or resume.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        # -------------------------------
        # RESUME VALIDATION
        # -------------------------------

        original_filename = secure_filename(
            resume.filename or ""
        )

        if not original_filename:
            flash(
                "The uploaded CV filename is invalid.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        extension = (
            original_filename
            .rsplit(".", 1)[-1]
            .lower()
            if "." in original_filename
            else ""
        )

        allowed_extensions = (
            current_app.config[
                "ALLOWED_RESUME_EXTENSIONS"
            ]
        )

        if extension not in allowed_extensions:
            flash(
                "Invalid CV format. "
                "Please upload a PDF, DOC, or DOCX file.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        # -------------------------------
        # DUPLICATE APPLICATION CHECK
        # -------------------------------

        existing_application = (
            JobApplication.query
            .filter_by(
                career_position_id=position.id,
                email=email
            )
            .filter(
                JobApplication.status != "rejected"
            )
            .first()
        )

        if existing_application:
            flash(
                "You have already submitted an application "
                "for this position.",
                "warning"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        # -------------------------------
        # SAVE RESUME
        # -------------------------------

        import uuid

        unique_filename = (
            f"{uuid.uuid4().hex}_"
            f"{original_filename}"
        )

        upload_folder = current_app.config[
            "UPLOAD_FOLDER"
        ]

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        resume.save(
            upload_folder / unique_filename
        )

        # -------------------------------
        # SAVE APPLICATION
        # -------------------------------

        application = JobApplication(
            career_position_id=position.id,

            full_name=full_name,
            email=email,
            phone=phone,
            location=location,

            current_job_title=current_job_title,
            years_of_experience=years_of_experience,

            linkedin_url=linkedin_url,
            portfolio_url=portfolio_url,
            github_url=github_url,

            cover_letter=cover_letter,

            resume_filename=original_filename,
            resume_path=unique_filename,

            status="new"
        )

        try:

            db.session.add(application)

            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()

            # Remove the uploaded CV because
            # the database application was not saved.
            resume_file = (
                    upload_folder
                    / unique_filename
            )

            if resume_file.exists():
                resume_file.unlink()

            current_app.logger.exception(
                "Failed to save job application."
            )

            flash(
                "We could not submit your application "
                "at this time. Please try again.",
                "danger"
            )

            return render_template(
                "career_apply.html",
                position=position
            )

        flash(
            "Your application has been submitted successfully. "
            "Thank you for your interest in "
            "Efxion Technology Solutions.",
            "success"
        )

        return redirect(
            url_for(
                "main.career_detail",
                slug=position.slug
            )
        )

    return render_template(
        "career_apply.html",
        position=position
    )

# =========================================================
# PRIVACY POLICY
# =========================================================

@main_bp.route("/privacy")
def privacy():

    return render_template(
        "privacy.html"
    )


# =========================================================
# TERMS OF SERVICE
# =========================================================

@main_bp.route("/terms")
def terms():

    return render_template(
        "terms.html"
    )

