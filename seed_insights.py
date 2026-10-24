from datetime import datetime, timezone

from app import create_app, db
from app.models import InsightCategory, InsightArticle


app = create_app()


def seed_insights():

    categories = [

        {
            "name": "Technology",
            "slug": "technology",
            "description": (
                "Technology trends, tools and ideas."
            ),
        },

        {
            "name": "Business & Digital",
            "slug": "business-digital",
            "description": (
                "Digital business strategies and transformation."
            ),
        },

        {
            "name": "Software Development",
            "slug": "software-development",
            "description": (
                "Software engineering and development insights."
            ),
        },

        {
            "name": "AI & Innovation",
            "slug": "ai-innovation",
            "description": (
                "Artificial intelligence and emerging technology."
            ),
        },

    ]


    for item in categories:

        existing = InsightCategory.query.filter_by(
            slug=item["slug"]
        ).first()

        if not existing:

            db.session.add(
                InsightCategory(
                    name=item["name"],
                    slug=item["slug"],
                    description=item["description"]
                )
            )


    db.session.commit()


    articles = [

        {
            "category": "technology",
            "title": "Why Businesses Need a Strong Digital Foundation",
            "slug": "why-businesses-need-strong-digital-foundation",
            "excerpt": (
                "A strong digital foundation can help businesses "
                "operate more efficiently and create better "
                "customer experiences."
            ),
            "content": """
                <p>
                    Technology has become an important part of how
                    modern businesses operate. From communication
                    and customer management to payments and reporting,
                    digital tools increasingly influence everyday
                    business operations.
                </p>

                <h2>
                    Technology should support the business
                </h2>

                <p>
                    A digital system should not exist simply because
                    technology is available. It should address a
                    genuine business need and make an existing
                    process better.
                </p>

                <p>
                    Businesses can benefit from understanding their
                    processes first and then selecting technology
                    that fits those processes.
                </p>

                <h2>
                    Start with the problem
                </h2>

                <p>
                    Before investing in software or digital tools,
                    identify the problem you are trying to solve.
                    This makes it easier to determine what technology
                    is actually necessary.
                </p>
            """,
            "author": "Efxion Technology Solutions",
            "reading_time": 4,
            "featured": True,
        },

        {
            "category": "business-digital",
            "title": "How Digital Systems Can Improve Business Operations",
            "slug": "how-digital-systems-improve-business-operations",
            "excerpt": (
                "Digital systems can reduce repetitive work, "
                "organize information and give businesses better "
                "visibility into their operations."
            ),
            "content": """
                <p>
                    Many businesses still rely on spreadsheets,
                    paper records and disconnected tools to manage
                    important operations.
                </p>

                <p>
                    Digital business systems can bring these
                    processes together and make information easier
                    to access.
                </p>

                <h2>
                    Better organization
                </h2>

                <p>
                    Centralizing information can make it easier to
                    understand customers, inventory, transactions,
                    expenses and other business activities.
                </p>

                <h2>
                    Better decisions
                </h2>

                <p>
                    When useful business information is available
                    in one place, business owners and managers can
                    make decisions with greater visibility.
                </p>
            """,
            "author": "Efxion Technology Solutions",
            "reading_time": 4,
            "featured": False,
        },

        {
            "category": "ai-innovation",
            "title": "Understanding the Practical Side of Artificial Intelligence",
            "slug": "understanding-practical-side-of-artificial-intelligence",
            "excerpt": (
                "Artificial intelligence becomes more useful when "
                "it is applied to specific problems rather than "
                "treated simply as a trend."
            ),
            "content": """
                <p>
                    Artificial intelligence is becoming increasingly
                    accessible to businesses, developers and
                    individuals.
                </p>

                <p>
                    However, adopting AI successfully requires more
                    than simply adding an AI feature to a product.
                </p>

                <h2>
                    Identify useful applications
                </h2>

                <p>
                    AI can be useful for areas such as information
                    processing, prediction, automation, natural
                    language interaction and decision support.
                </p>

                <p>
                    The most valuable applications are usually those
                    that solve a clearly defined problem.
                </p>
            """,
            "author": "Efxion Technology Solutions",
            "reading_time": 5,
            "featured": True,
        },

    ]


    for item in articles:

        existing = InsightArticle.query.filter_by(
            slug=item["slug"]
        ).first()

        if existing:
            continue


        category = InsightCategory.query.filter_by(
            slug=item["category"]
        ).first()

        if not category:
            continue


        article = InsightArticle(
            category_id=category.id,
            title=item["title"],
            slug=item["slug"],
            excerpt=item["excerpt"],
            content=item["content"],
            author=item["author"],
            reading_time=item["reading_time"],
            published_at=datetime.now(timezone.utc),
            is_featured=item["featured"],
            is_published=True
        )

        db.session.add(article)


    db.session.commit()

    print("Insights successfully seeded.")


if __name__ == "__main__":

    with app.app_context():
        seed_insights()