
import json
import os
from app import app, db, Template

def populate_db():
    with app.app_context():
        db.create_all()

        if Template.query.count() > 0:
            print("Database already populated.")
            return

        print("Populating database with templates...")
        # Use relative path that works in all environments
        catalog_path = os.path.join(os.path.dirname(__file__), "templates_catalog.json")
        with open(catalog_path, "r") as f:
            templates = json.load(f)

        for template_data in templates:
            template = Template(
                id=template_data.get("id"),
                name=template_data.get("name"),
                description=template_data.get("description"),
                industry=template_data.get("industry"),
                category=template_data.get("category"),
                file_type=template_data.get("file_type"),
                filename=template_data.get("filename"),
                downloads=template_data.get("downloads", 0),
                rating=template_data.get("rating", 4.5),
                tags=",".join(template_data.get("tags", [])),
                file_size=template_data.get("file_size"),
                has_formulas=template_data.get("has_formulas", False),
                has_fields=template_data.get("has_fields", False),
                is_premium=template_data.get("is_premium", False),
            )
            db.session.add(template)

        db.session.commit()
        print(f"Database populated with {Template.query.count()} templates.")

if __name__ == "__main__":
    populate_db()

