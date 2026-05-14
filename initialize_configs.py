#!/usr/bin/env python3
"""
Script to initialize default frontend configurations and categories.
Usage: python initialize_configs.py
"""

from app.crud import create_frontend_config, create_category
from app.db.session import SessionLocal
from app.schemas import FrontendConfigCreate, CategoryCreate


def initialize_configs():
    """Initialize default frontend configurations."""
    db = SessionLocal()
    
    try:
        print("\n=== Initializing Frontend Configurations ===\n")
        
        # Navbar config
        navbar_config = FrontendConfigCreate(
            config_key="navbar",
            config_value={
                "items": [
                    {"label": "Home", "href": "/"},
                    {"label": "Collections", "href": "/collections"},
                    {"label": "About", "href": "/about"},
                    {"label": "Sustainability", "href": "/sustainability"},
                    {"label": "Contact", "href": "/contact"},
                ]
            },
            description="Main navigation bar items"
        )
        create_frontend_config(db, navbar_config)
        print("✅ Navbar config initialized")
        
        # Hero config
        hero_config = FrontendConfigCreate(
            config_key="hero",
            config_value={
                "title": "Premium Wooden Furniture",
                "subtitle": "Handcrafted from Pakistan for Your Home",
                "image_url": "https://images.unsplash.com/photo-1772797583328-f83bc3f94f80?w=1200&q=80",
                "cta_text": "Explore Collections",
                "cta_link": "/collections"
            },
            description="Hero section configuration"
        )
        create_frontend_config(db, hero_config)
        print("✅ Hero section config initialized")
        
        # Footer config
        footer_config = FrontendConfigCreate(
            config_key="footer",
            config_value={
                "company_name": "Chiniot Furniture",
                "description": "Quality wooden furniture crafted for Pakistani homes. Specializing in beds, sofas, tables, chairs, and wardrobes made from premium sheesham and kikar wood.",
                "phone": "+92-XXX-XXXXXXX",
                "email": "info@chinotfurniture.com",
                "address": "Chiniot, Punjab, Pakistan"
            },
            description="Footer content"
        )
        create_frontend_config(db, footer_config)
        print("✅ Footer config initialized")
        
        # Social links
        social_config = FrontendConfigCreate(
            config_key="social_links",
            config_value={
                "facebook": "",
                "instagram": "",
                "whatsapp": "",
                "youtube": ""
            },
            description="Social media links"
        )
        create_frontend_config(db, social_config)
        print("✅ Social links config initialized")
        
        print("\n✅ All configurations initialized successfully!\n")
        
    except Exception as e:
        print(f"❌ Error initializing configs: {e}\n")
    finally:
        db.close()


def initialize_categories():
    """Initialize default product categories."""
    db = SessionLocal()
    
    try:
        print("=== Initializing Product Categories ===\n")
        
        categories = [
            CategoryCreate(
                name="chairs",
                display_name="Chairs",
                description="Wooden chairs including dining chairs, armchairs, and more",
                icon="🪑",
                sort_order=0
            ),
            CategoryCreate(
                name="sofas",
                display_name="Sofas",
                description="Comfortable wooden sofas and seating arrangements",
                icon="🛋️",
                sort_order=1
            ),
            CategoryCreate(
                name="beds",
                display_name="Beds",
                description="Wooden beds of various sizes and styles",
                icon="🛏️",
                sort_order=2
            ),
            CategoryCreate(
                name="tables",
                display_name="Tables",
                description="Dining tables, center tables, and side tables",
                icon="📦",
                sort_order=3
            ),
            CategoryCreate(
                name="wardrobes",
                display_name="Wardrobes",
                description="Wooden wardrobes and storage furniture",
                icon="🚪",
                sort_order=4
            ),
        ]
        
        for cat in categories:
            create_category(db, cat)
            print(f"✅ Category '{cat.display_name}' created")
        
        print("\n✅ All categories initialized successfully!\n")
        
    except Exception as e:
        print(f"❌ Error initializing categories: {e}\n")
    finally:
        db.close()


if __name__ == "__main__":
    initialize_configs()
    initialize_categories()
    print("=== Initialization Complete ===\n")
