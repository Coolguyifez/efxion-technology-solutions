from datetime import date

from app import create_app, db
from app.models import CareerPosition


app = create_app()


with app.app_context():

    # Prevent duplicate vacancy
    existing = CareerPosition.query.filter_by(
        slug="frontend-developer"
    ).first()

    if existing:
        print("Frontend Developer vacancy already exists.")
    else:

        position = CareerPosition(
            title="Frontend Developer",

            slug="frontend-developer",

            department="Technology",

            location="Nigeria",

            employment_type="Full-time",

            work_mode="Hybrid",

            salary="Competitive",

            short_description=(
                "We are looking for a creative and motivated "
                "Frontend Developer to build modern, responsive "
                "and user-friendly web applications."
            ),

            description=(
                "The Frontend Developer will work with the "
                "Efxion Technology Solutions team to design and "
                "develop modern web interfaces and applications. "
                "The successful candidate will translate ideas "
                "and business requirements into responsive, "
                "accessible and high-quality digital experiences."
            ),

            responsibilities="""
<ul>
    <li>Build responsive and user-friendly web interfaces.</li>
    <li>Develop reusable frontend components.</li>
    <li>Work with HTML, CSS and JavaScript.</li>
    <li>Work with modern frontend frameworks when required.</li>
    <li>Integrate frontend applications with backend APIs.</li>
    <li>Test and debug applications across different devices.</li>
    <li>Improve website performance, accessibility and usability.</li>
    <li>Collaborate with designers, developers and other team members.</li>
    <li>Maintain and improve existing web applications.</li>
</ul>
""",

            requirements="""
<ul>
    <li>Good understanding of HTML, CSS and JavaScript.</li>
    <li>Experience building responsive websites or web applications.</li>
    <li>Understanding of modern frontend development practices.</li>
    <li>Ability to work with APIs and backend services.</li>
    <li>Good debugging and problem-solving skills.</li>
    <li>Ability to write clean and maintainable code.</li>
    <li>Good communication and teamwork skills.</li>
</ul>
""",

            qualifications="""
<ul>
    <li>Degree, diploma or relevant training in Computer Science,
        Software Engineering, Information Technology or a related field.</li>
    <li>Relevant practical experience or a strong project portfolio
        may be considered.</li>
</ul>
""",

            skills="""
<ul>
    <li>HTML5</li>
    <li>CSS3</li>
    <li>JavaScript</li>
    <li>Responsive Web Design</li>
    <li>Git and GitHub</li>
    <li>REST APIs</li>
    <li>Frontend debugging</li>
    <li>UI/UX awareness</li>
</ul>
""",

            experience_required="1–3 years or demonstrable project experience",

            application_email=None,

            application_deadline=date(2026, 12, 31),

            is_featured=True,

            is_published=True,

            is_closed=False
        )

        db.session.add(position)
        db.session.commit()

        print("Frontend Developer vacancy created successfully.")