from getpass import getpass

from app import create_app, db
from app.models import AdminUser


app = create_app()


with app.app_context():

    print()
    print("======================================")
    print(" EFXION ADMIN USER CREATION")
    print("======================================")
    print()

    username = input(
        "Username: "
    ).strip()

    email = input(
        "Email: "
    ).strip()

    full_name = input(
        "Full name: "
    ).strip()

    password = getpass(
        "Password: "
    )

    confirm_password = getpass(
        "Confirm password: "
    )

    if not username:
        print("Username is required.")
        raise SystemExit

    if not email:
        print("Email is required.")
        raise SystemExit

    if not full_name:
        print("Full name is required.")
        raise SystemExit

    if not password:
        print("Password is required.")
        raise SystemExit

    if password != confirm_password:
        print("Passwords do not match.")
        raise SystemExit

    existing_username = (
        AdminUser.query
        .filter_by(
            username=username
        )
        .first()
    )

    if existing_username:
        print(
            "That username already exists."
        )
        raise SystemExit

    existing_email = (
        AdminUser.query
        .filter_by(
            email=email
        )
        .first()
    )

    if existing_email:
        print(
            "That email already exists."
        )
        raise SystemExit

    admin = AdminUser(
        username=username,
        email=email,
        full_name=full_name,
        is_active=True
    )

    admin.set_password(password)

    db.session.add(admin)

    db.session.commit()

    print()
    print("Admin account created successfully.")
    print()