from datetime import date

from app import create_app, db
from app.models import StaffProfile

app = create_app()


def seed_staff():

    staff = {
        "full_name": "Emmanuel Ifeanyi Ikukaiwe",
        "slug": "emmanuel-ifeanyi-ikukaiwe",
        "job_title": "Founder & Technology Professional",
        "department": "Technology & Innovation",

        "short_bio": (
            "Technology professional focused on software development, "
            "information technology, artificial intelligence, "
            "cybersecurity and digital solutions."
        ),

        "biography": """
            <p>
                Emmanuel Ifeanyi Ikukaiwe is a technology professional
                and the founder of Efxion Technology Solutions, with an
                interest in building practical digital solutions that
                help businesses and organizations solve real-world
                problems.
            </p>

            <p>
                His work spans software development, information
                technology, artificial intelligence, cybersecurity,
                networking and digital business systems.
            </p>

            <p>
                Through Efxion Technology Solutions, he focuses on
                combining technology, creativity and practical business
                understanding to develop useful digital experiences
                and solutions.
            </p>
        """,

        "experience": """
            <p>
                Experience includes software development, IT support,
                networking, digital systems development and technology
                consulting.
            </p>

            <p>
                His project experience includes business management
                systems, AI-assisted applications, web applications,
                digital platforms and technology-focused solutions.
            </p>
        """,

        "education": """
            <ul>
                <li>
                    B.Sc. Computer Science —
                    University of Benin
                </li>

                <li>
                    M.Sc. Information and Telecommunication Engineering —
                    Centre for Information and Telecommunication
                    Engineering
                </li>
            </ul>
        """,

        "skills": """
            <ul>
                <li>Python & Flask</li>
                <li>JavaScript & Web Development</li>
                <li>Database Development</li>
                <li>Artificial Intelligence</li>
                <li>Cybersecurity</li>
                <li>Networking & IT Support</li>
                <li>System Design</li>
                <li>Digital Business Solutions</li>
            </ul>
        """,

        "expertise": """
            <ul>
                <li>Software Development</li>
                <li>Business Applications</li>
                <li>Artificial Intelligence</li>
                <li>Information Technology</li>
                <li>Cybersecurity</li>
                <li>Networking</li>
                <li>Technology Consulting</li>
            </ul>
        """,

        "date_joined": date(2026, 1, 1),

        "is_featured": True,
        "is_active": True,
        "display_order": 1
    }

    existing = StaffProfile.query.filter_by(
        slug=staff["slug"]
    ).first()

    if existing:
        print("Staff profile already exists.")
        return

    profile = StaffProfile(
        full_name=staff["full_name"],
        slug=staff["slug"],
        job_title=staff["job_title"],
        department=staff["department"],
        short_bio=staff["short_bio"],
        biography=staff["biography"],
        experience=staff["experience"],
        education=staff["education"],
        skills=staff["skills"],
        expertise=staff["expertise"],
        date_joined=staff["date_joined"],
        is_featured=staff["is_featured"],
        is_active=staff["is_active"],
        display_order=staff["display_order"]
    )

    db.session.add(profile)
    db.session.commit()

    print("Staff profile successfully created.")


if __name__ == "__main__":

    with app.app_context():
        seed_staff()