"""
One-time script to standardize category names in production.
This will run once on startup if RUN_CATEGORY_FIX environment variable is set.
"""
import os
from standardize_all_categories import standardize_categories

def run_if_enabled():
    """Run category standardization if enabled via environment variable."""
    if os.getenv('RUN_CATEGORY_FIX') == 'true':
        print("🔧 Running one-time category standardization...")
        try:
            standardize_categories()
            print("✅ Category standardization completed successfully!")
        except Exception as e:
            print(f"❌ Category standardization failed: {e}")
            # Don't crash the app if this fails
    else:
        print("ℹ️  Category standardization skipped (RUN_CATEGORY_FIX not set)")

if __name__ == "__main__":
    run_if_enabled()

