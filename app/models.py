from datetime import datetime, timezone
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_login import UserMixin
from app import db

class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.String(180),
        nullable=False,
        unique=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    full_name = db.Column(
        db.String(180),
        nullable=False
    )

    reset_token_hash = db.Column(
        db.String(128),
        nullable=True
    )

    reset_token_expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def __repr__(self):
        return f"<AdminUser {self.username}>"

class ServiceCategory(db.Model):
    __tablename__ = "service_categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    description = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    services = db.relationship(
        "Service",
        backref="category",
        lazy=True
    )


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("service_categories.id"),
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    slug = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    short_description = db.Column(
        db.String(300)
    )

    description = db.Column(db.Text)

    starting_price = db.Column(
        db.Numeric(14, 2),
        nullable=True
    )

    currency = db.Column(
        db.String(10),
        default="NGN"
    )

    icon = db.Column(
        db.String(100),
        default="bi-code-slash"
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

class PortfolioCategory(db.Model):
    __tablename__ = "portfolio_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    description = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    projects = db.relationship(
        "PortfolioProject",
        backref="category",
        lazy=True
    )


class PortfolioProject(db.Model):
    __tablename__ = "portfolio_projects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("portfolio_categories.id"),
        nullable=False
    )

    title = db.Column(
        db.String(180),
        nullable=False
    )

    slug = db.Column(
        db.String(180),
        nullable=False,
        unique=True
    )

    client_name = db.Column(
        db.String(180),
        nullable=True
    )

    short_description = db.Column(
        db.String(350)
    )

    description = db.Column(
        db.Text
    )

    technologies = db.Column(
        db.String(500)
    )

    image = db.Column(
        db.String(255)
    )

    project_url = db.Column(
        db.String(500)
    )

    github_url = db.Column(
        db.String(500)
    )

    year = db.Column(
        db.Integer
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

class InsightCategory(db.Model):
    __tablename__ = "insight_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    slug = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    articles = db.relationship(
        "InsightArticle",
        backref="category",
        lazy=True
    )


class InsightArticle(db.Model):
    __tablename__ = "insight_articles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("insight_categories.id"),
        nullable=False
    )

    title = db.Column(
        db.String(250),
        nullable=False
    )

    slug = db.Column(
        db.String(250),
        nullable=False,
        unique=True
    )

    excerpt = db.Column(
        db.String(500)
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.String(150),
        default="Efxion Technology Solutions"
    )

    featured_image = db.Column(
        db.String(255)
    )

    reading_time = db.Column(
        db.Integer,
        default=5
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_published = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(180),
        nullable=False
    )

    phone = db.Column(
        db.String(50),
        nullable=True
    )

    company = db.Column(
        db.String(180),
        nullable=True
    )

    service = db.Column(
        db.String(180),
        nullable=True
    )

    project_type = db.Column(
        db.String(150),
        nullable=True
    )

    budget = db.Column(
        db.String(100),
        nullable=True
    )

    preferred_contact = db.Column(
        db.String(50),
        nullable=True
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="new"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"<ContactMessage "
            f"{self.id} - {self.name}>"
        )

class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(180),
        nullable=False
    )

    slug = db.Column(
        db.String(180),
        nullable=False,
        unique=True
    )

    job_title = db.Column(
        db.String(180),
        nullable=False
    )

    department = db.Column(
        db.String(150),
        nullable=True
    )

    profile_image = db.Column(
        db.String(255),
        nullable=True
    )

    short_bio = db.Column(
        db.String(500),
        nullable=True
    )

    biography = db.Column(
        db.Text,
        nullable=True
    )

    experience = db.Column(
        db.Text,
        nullable=True
    )

    education = db.Column(
        db.Text,
        nullable=True
    )

    skills = db.Column(
        db.Text,
        nullable=True
    )

    expertise = db.Column(
        db.Text,
        nullable=True
    )

    email = db.Column(
        db.String(180),
        nullable=True
    )

    linkedin_url = db.Column(
        db.String(500),
        nullable=True
    )

    github_url = db.Column(
        db.String(500),
        nullable=True
    )

    portfolio_url = db.Column(
        db.String(500),
        nullable=True
    )

    date_joined = db.Column(
        db.Date,
        nullable=True
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    display_order = db.Column(
        db.Integer,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"<StaffProfile "
            f"{self.id} - {self.full_name}>"
        )

class CareerPosition(db.Model):
    __tablename__ = "career_positions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(180),
        nullable=False
    )

    slug = db.Column(
        db.String(180),
        nullable=False,
        unique=True
    )

    department = db.Column(
        db.String(150),
        nullable=True
    )

    location = db.Column(
        db.String(180),
        nullable=True
    )

    employment_type = db.Column(
        db.String(100),
        nullable=True
    )

    work_mode = db.Column(
        db.String(100),
        nullable=True
    )

    salary = db.Column(
        db.String(150),
        nullable=True
    )

    short_description = db.Column(
        db.String(500),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    responsibilities = db.Column(
        db.Text,
        nullable=True
    )

    requirements = db.Column(
        db.Text,
        nullable=True
    )

    qualifications = db.Column(
        db.Text,
        nullable=True
    )

    skills = db.Column(
        db.Text,
        nullable=True
    )

    experience_required = db.Column(
        db.String(150),
        nullable=True
    )

    application_email = db.Column(
        db.String(180),
        nullable=True
    )

    application_deadline = db.Column(
        db.Date,
        nullable=True
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_published = db.Column(
        db.Boolean,
        default=True
    )

    is_closed = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"<CareerPosition "
            f"{self.id} - {self.title}>"
        )

class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)

    career_position_id = db.Column(
        db.Integer,
        db.ForeignKey("career_positions.id"),
        nullable=False
    )

    # Applicant information
    full_name = db.Column(
        db.String(180),
        nullable=False
    )

    email = db.Column(
        db.String(180),
        nullable=False
    )

    phone = db.Column(
        db.String(50),
        nullable=True
    )

    location = db.Column(
        db.String(180),
        nullable=True
    )

    # Professional information
    current_job_title = db.Column(
        db.String(180),
        nullable=True
    )

    years_of_experience = db.Column(
        db.String(100),
        nullable=True
    )

    linkedin_url = db.Column(
        db.String(500),
        nullable=True
    )

    portfolio_url = db.Column(
        db.String(500),
        nullable=True
    )

    github_url = db.Column(
        db.String(500),
        nullable=True
    )

    # Application
    cover_letter = db.Column(
        db.Text,
        nullable=True
    )

    resume_filename = db.Column(
        db.String(255),
        nullable=True
    )

    resume_path = db.Column(
        db.String(500),
        nullable=True
    )

    # Application status
    status = db.Column(
        db.String(30),
        nullable=False,
        default="new"
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    position = db.relationship(
        "CareerPosition",
        backref=db.backref(
            "applications",
            lazy=True
        )
    )

    def __repr__(self):
        return (
            f"<JobApplication "
            f"{self.id} - {self.full_name}>"
        )

# =========================================================
# FAQ
# =========================================================

class FAQ(db.Model):
    __tablename__ = "faqs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question = db.Column(
        db.String(500),
        nullable=False
    )

    answer = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(150),
        nullable=True
    )

    display_order = db.Column(
        db.Integer,
        default=0
    )

    is_featured = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return (
            f"<FAQ "
            f"{self.id} - {self.question[:50]}>"
        )

