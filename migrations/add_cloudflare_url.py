"""
Migration: Add cloudflare_url column to templates table
"""
from sqlalchemy import text

def upgrade(db):
    """Add cloudflare_url column"""
    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='templates' AND column_name='cloudflare_url'
        """))
        
        if result.fetchone() is None:
            # Column doesn't exist, add it
            db.session.execute(text("""
                ALTER TABLE templates 
                ADD COLUMN cloudflare_url VARCHAR(500)
            """))
            db.session.commit()
            print("✅ Added cloudflare_url column to templates table")
        else:
            print("ℹ️  cloudflare_url column already exists")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {e}")
        raise

def downgrade(db):
    """Remove cloudflare_url column"""
    try:
        db.session.execute(text("""
            ALTER TABLE templates 
            DROP COLUMN IF EXISTS cloudflare_url
        """))
        db.session.commit()
        print("✅ Removed cloudflare_url column from templates table")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Rollback failed: {e}")
        raise
