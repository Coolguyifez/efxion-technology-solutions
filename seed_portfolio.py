from app import create_app, db
from app.models import PortfolioCategory, PortfolioProject


app = create_app()


def seed_portfolio():

    categories = [

        {
            "name": "Web Development",
            "slug": "web-development",
            "description": (
                "Responsive websites and browser-based "
                "digital experiences."
            ),
        },

        {
            "name": "Web Applications",
            "slug": "web-applications",
            "description": (
                "Interactive applications designed around "
                "specific business and user requirements."
            ),
        },

        {
            "name": "Business Systems",
            "slug": "business-systems",
            "description": (
                "Digital platforms designed to improve "
                "business operations."
            ),
        },

        {
            "name": "AI & Emerging Technology",
            "slug": "ai-emerging-technology",
            "description": (
                "Projects exploring artificial intelligence "
                "and emerging technologies."
            ),
        },

    ]


    for item in categories:

        existing = PortfolioCategory.query.filter_by(
            slug=item["slug"]
        ).first()

        if not existing:

            category = PortfolioCategory(
                name=item["name"],
                slug=item["slug"],
                description=item["description"]
            )

            db.session.add(category)


    db.session.commit()


    projects = [

        {
            "category": "business-systems",
            "title": "BizTrace IMS",
            "slug": "biztrace-ims",
            "short_description": (
                "Business management and subscription platform "
                "for sales, purchases, inventory and operations."
            ),
            "description": (
                "A web-based business management platform designed "
                "to help businesses manage sales, purchases, inventory, "
                "expenses, customers, suppliers, payments and reports "
                "from one place."
            ),
            "technologies": (
                "Python, Flask, PostgreSQL, Bootstrap, JavaScript, PWA"
            ),
            "year": 2026,
            "featured": True,
        },

        {
            "category": "ai-emerging-technology",
            "title": "CoreEfx AI Digital Health Advisory",
            "slug": "coreefx-ai-digital-health",
            "short_description": (
                "AI-assisted digital health advisory and hospital "
                "referral platform."
            ),
            "description": (
                "A digital health prototype designed for preliminary "
                "self-assessment and location-based hospital referral."
            ),
            "technologies": (
                "Python, Flask, Machine Learning, NLP, PostgreSQL, PWA"
            ),
            "year": 2026,
            "featured": True,
        },

        {
            "category": "web-applications",
            "title": "Speedy Auto Broker Hub",
            "slug": "speedy-auto-broker-hub",
            "short_description": (
                "Digital platform concept for automobile brokerage "
                "and customer vehicle discovery."
            ),
            "description": (
                "A technology platform designed to connect customers "
                "with vehicle opportunities while supporting the "
                "automobile brokerage workflow."
            ),
            "technologies": (
                "React, Python, FastAPI, PostgreSQL, AI"
            ),
            "year": 2026,
            "featured": True,
        },

        {
            "category": "web-development",
            "title": "Efxion Technology Solutions",
            "slug": "efxion-technology-solutions",
            "short_description": (
                "Corporate technology website and digital presence "
                "for Efxion Technology Solutions."
            ),
            "description": (
                "A responsive corporate website designed to present "
                "Efxion's services, portfolio, professional profile "
                "and technology capabilities."
            ),
            "technologies": (
                "Python, Flask, Bootstrap, CSS, JavaScript"
            ),
            "year": 2026,
            "featured": True,
        },

    ]


    for item in projects:

        existing = PortfolioProject.query.filter_by(
            slug=item["slug"]
        ).first()

        if existing:
            continue


        category = PortfolioCategory.query.filter_by(
            slug=item["category"]
        ).first()

        if not category:
            continue


        project = PortfolioProject(
            category_id=category.id,
            title=item["title"],
            slug=item["slug"],
            short_description=item["short_description"],
            description=item["description"],
            technologies=item["technologies"],
            year=item["year"],
            is_featured=item["featured"],
            is_active=True
        )

        db.session.add(project)


    db.session.commit()

    print("Portfolio successfully seeded.")


if __name__ == "__main__":

    with app.app_context():
        seed_portfolio()