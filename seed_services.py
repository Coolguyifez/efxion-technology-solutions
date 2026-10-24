from app import create_app, db
from app.models import ServiceCategory, Service


app = create_app()


def seed_services():

    categories = [
        {
            "name": "Web & Software Development",
            "slug": "web-software-development",
            "description": (
                "Modern websites, web applications and custom "
                "software solutions designed around your goals."
            ),
        },
        {
            "name": "IT & Technical Support",
            "slug": "it-technical-support",
            "description": (
                "Practical technical support for computers, "
                "networks, software and business technology."
            ),
        },
        {
            "name": "Digital & Business Solutions",
            "slug": "digital-business-solutions",
            "description": (
                "Technology solutions that help businesses "
                "improve their digital operations and workflows."
            ),
        },
        {
            "name": "Technology Consulting",
            "slug": "technology-consulting",
            "description": (
                "Professional guidance for businesses and "
                "individuals making technology decisions."
            ),
        },
    ]


    for category_data in categories:

        category = ServiceCategory.query.filter_by(
            slug=category_data["slug"]
        ).first()

        if not category:

            category = ServiceCategory(
                name=category_data["name"],
                slug=category_data["slug"],
                description=category_data["description"]
            )

            db.session.add(category)


    db.session.commit()


    service_data = [

        {
            "category": "web-software-development",
            "name": "Business Website",
            "slug": "business-website",
            "short_description": (
                "Professional responsive website for your business."
            ),
            "description": (
                "A modern business website designed to establish "
                "your online presence and help customers understand "
                "your products or services."
            ),
            "price": 150000,
            "icon": "bi-globe2",
            "featured": True,
        },

        {
            "category": "web-software-development",
            "name": "Web Application",
            "slug": "web-application",
            "short_description": (
                "Custom web applications built around your workflow."
            ),
            "description": (
                "Interactive browser-based applications designed "
                "to automate processes and provide useful digital "
                "functionality."
            ),
            "price": 300000,
            "icon": "bi-window-stack",
            "featured": True,
        },

        {
            "category": "web-software-development",
            "name": "Custom Software",
            "slug": "custom-software",
            "short_description": (
                "Software tailored to your specific requirements."
            ),
            "description": (
                "Custom-built software solutions for organizations "
                "with unique operational requirements."
            ),
            "price": 400000,
            "icon": "bi-code-square",
            "featured": False,
        },

        {
            "category": "it-technical-support",
            "name": "Computer & System Support",
            "slug": "computer-system-support",
            "short_description": (
                "Technical assistance for computers and software."
            ),
            "description": (
                "Diagnosis, configuration, troubleshooting and "
                "general technical support for computer systems."
            ),
            "price": 15000,
            "icon": "bi-pc-display",
            "featured": True,
        },

        {
            "category": "it-technical-support",
            "name": "Network Setup & Support",
            "slug": "network-setup-support",
            "short_description": (
                "Network configuration and troubleshooting."
            ),
            "description": (
                "Support for network setup, connectivity issues, "
                "configuration and basic infrastructure requirements."
            ),
            "price": 25000,
            "icon": "bi-diagram-3",
            "featured": False,
        },

        {
            "category": "digital-business-solutions",
            "name": "Business Process Digitization",
            "slug": "business-process-digitization",
            "short_description": (
                "Turn manual workflows into digital processes."
            ),
            "description": (
                "Helping businesses identify repetitive processes "
                "that can be improved through digital tools."
            ),
            "price": 100000,
            "icon": "bi-arrow-repeat",
            "featured": False,
        },

        {
            "category": "digital-business-solutions",
            "name": "Business Management Systems",
            "slug": "business-management-systems",
            "short_description": (
                "Digital systems for managing business operations."
            ),
            "description": (
                "Technology solutions for areas such as sales, "
                "inventory, customers, purchases, payments and "
                "business reporting."
            ),
            "price": 250000,
            "icon": "bi-kanban",
            "featured": True,
        },

        {
            "category": "technology-consulting",
            "name": "Technology Consultation",
            "slug": "technology-consultation",
            "short_description": (
                "Professional guidance for technology decisions."
            ),
            "description": (
                "Consultation covering software, websites, digital "
                "tools, IT infrastructure and technology strategy."
            ),
            "price": 20000,
            "icon": "bi-lightbulb",
            "featured": False,
        },

        {
            "category": "technology-consulting",
            "name": "IT Project Consultation",
            "slug": "it-project-consultation",
            "short_description": (
                "Technology planning and project guidance."
            ),
            "description": (
                "Helping clients understand project requirements, "
                "technology options, implementation approaches and "
                "potential technical challenges."
            ),
            "price": 30000,
            "icon": "bi-clipboard2-check",
            "featured": False,
        },

    ]


    for item in service_data:

        existing = Service.query.filter_by(
            slug=item["slug"]
        ).first()

        if existing:
            continue


        category = ServiceCategory.query.filter_by(
            slug=item["category"]
        ).first()

        if not category:
            print(
                f"Category not found: {item['category']}"
            )
            continue


        service = Service(
            category_id=category.id,
            name=item["name"],
            slug=item["slug"],
            short_description=item["short_description"],
            description=item["description"],
            starting_price=item["price"],
            currency="NGN",
            icon=item["icon"],
            is_featured=item["featured"],
            is_active=True
        )

        db.session.add(service)


    db.session.commit()

    print("Services successfully seeded.")


if __name__ == "__main__":

    with app.app_context():
        seed_services()