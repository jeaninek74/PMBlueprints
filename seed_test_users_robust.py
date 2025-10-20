#!/usr/bin/env python3
"""
Robust Database Seeding Script for Test Users
==============================================

This script ensures all test users exist with correct subscription tiers
in the production database. It handles all edge cases and never crashes.

Features:
- Idempotent: Safe to run multiple times
- Error handling: Graceful failure with detailed logging
- Validation: Verifies all users after creation
- Rollback: Can undo changes if needed

Usage:
    python3 seed_test_users_robust.py [--verify-only] [--rollback]

Options:
    --verify-only    Only check if users exist, don't create/update
    --rollback       Delete all test users (use with caution!)
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import User
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test user configuration
TEST_USERS = [
    {
        'email': 'free@pmblueprints.com',
        'password': 'TestFree123!',
        'first_name': 'Free',
        'last_name': 'User',
        'subscription_tier': 'free'
    },
    {
        'email': 'individual@pmblueprints.com',
        'password': 'TestIndividual123!',
        'first_name': 'Individual',
        'last_name': 'User',
        'subscription_tier': 'individual'
    },
    {
        'email': 'professional@pmblueprints.com',
        'password': 'TestPro123!',
        'first_name': 'Professional',
        'last_name': 'User',
        'subscription_tier': 'professional'
    },
    {
        'email': 'enterprise@pmblueprints.com',
        'password': 'TestEnterprise123!',
        'first_name': 'Enterprise',
        'last_name': 'User',
        'subscription_tier': 'enterprise'
    }
]


def verify_database_connection():
    """Verify database connection is working."""
    try:
        with app.app_context():
            # Try a simple query
            User.query.first()
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def get_user_by_email(email):
    """Safely get user by email."""
    try:
        return User.query.filter_by(email=email).first()
    except Exception as e:
        logger.error(f"❌ Error querying user {email}: {e}")
        return None


def create_or_update_user(user_config):
    """Create or update a single test user."""
    email = user_config['email']
    
    try:
        # Check if user exists
        user = get_user_by_email(email)
        
        if user:
            # Update existing user
            logger.info(f"📝 Updating existing user: {email}")
            
            # Update fields
            user.first_name = user_config['first_name']
            user.last_name = user_config['last_name']
            user.subscription_tier = user_config['subscription_tier']
            
            # Only update password if it's different (check hash)
            # Note: We can't verify the old password, so we always update it
            user.password_hash = generate_password_hash(user_config['password'])
            
            db.session.commit()
            logger.info(f"✅ Updated user: {email} (tier: {user.subscription_tier})")
            return True
            
        else:
            # Create new user
            logger.info(f"➕ Creating new user: {email}")
            
            new_user = User(
                email=email,
                first_name=user_config['first_name'],
                last_name=user_config['last_name'],
                password_hash=generate_password_hash(user_config['password']),
                subscription_tier=user_config['subscription_tier']
            )
            
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"✅ Created user: {email} (tier: {new_user.subscription_tier})")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating/updating user {email}: {e}")
        try:
            db.session.rollback()
            logger.info("🔄 Database rolled back")
        except Exception as rollback_error:
            logger.error(f"❌ Rollback failed: {rollback_error}")
        return False


def verify_user(user_config):
    """Verify a user exists with correct configuration."""
    email = user_config['email']
    expected_tier = user_config['subscription_tier']
    
    try:
        user = get_user_by_email(email)
        
        if not user:
            logger.error(f"❌ User not found: {email}")
            return False
            
        if user.subscription_tier != expected_tier:
            logger.error(f"❌ User {email} has wrong tier: {user.subscription_tier} (expected: {expected_tier})")
            return False
            
        logger.info(f"✅ Verified user: {email} (tier: {user.subscription_tier})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying user {email}: {e}")
        return False


def delete_test_user(email):
    """Delete a test user (for rollback)."""
    try:
        user = get_user_by_email(email)
        
        if user:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"🗑️  Deleted user: {email}")
            return True
        else:
            logger.warning(f"⚠️  User not found for deletion: {email}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error deleting user {email}: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def seed_all_users():
    """Create or update all test users."""
    logger.info("=" * 60)
    logger.info("STARTING DATABASE SEEDING")
    logger.info("=" * 60)
    
    success_count = 0
    failure_count = 0
    
    with app.app_context():
        for user_config in TEST_USERS:
            if create_or_update_user(user_config):
                success_count += 1
            else:
                failure_count += 1
    
    logger.info("=" * 60)
    logger.info(f"SEEDING COMPLETE: {success_count} success, {failure_count} failures")
    logger.info("=" * 60)
    
    return failure_count == 0


def verify_all_users():
    """Verify all test users exist with correct configuration."""
    logger.info("=" * 60)
    logger.info("VERIFYING TEST USERS")
    logger.info("=" * 60)
    
    success_count = 0
    failure_count = 0
    
    with app.app_context():
        for user_config in TEST_USERS:
            if verify_user(user_config):
                success_count += 1
            else:
                failure_count += 1
    
    logger.info("=" * 60)
    logger.info(f"VERIFICATION COMPLETE: {success_count} success, {failure_count} failures")
    logger.info("=" * 60)
    
    return failure_count == 0


def rollback_all_users():
    """Delete all test users."""
    logger.warning("=" * 60)
    logger.warning("ROLLING BACK TEST USERS (DELETING)")
    logger.warning("=" * 60)
    
    success_count = 0
    failure_count = 0
    
    with app.app_context():
        for user_config in TEST_USERS:
            if delete_test_user(user_config['email']):
                success_count += 1
            else:
                failure_count += 1
    
    logger.info("=" * 60)
    logger.info(f"ROLLBACK COMPLETE: {success_count} deleted, {failure_count} failures")
    logger.info("=" * 60)
    
    return failure_count == 0


def main():
    """Main entry point."""
    # Parse command line arguments
    verify_only = '--verify-only' in sys.argv
    rollback = '--rollback' in sys.argv
    
    # Verify database connection first
    if not verify_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    try:
        if rollback:
            # Rollback mode: delete all test users
            logger.warning("⚠️  ROLLBACK MODE: This will delete all test users!")
            logger.warning("Press Ctrl+C within 3 seconds to cancel...")
            import time
            time.sleep(3)
            
            success = rollback_all_users()
            sys.exit(0 if success else 1)
            
        elif verify_only:
            # Verify-only mode: just check users exist
            success = verify_all_users()
            sys.exit(0 if success else 1)
            
        else:
            # Normal mode: create/update users
            seed_success = seed_all_users()
            
            if seed_success:
                logger.info("✅ All users seeded successfully")
                
                # Verify after seeding
                logger.info("\nVerifying seeded users...")
                verify_success = verify_all_users()
                
                if verify_success:
                    logger.info("✅ All users verified successfully")
                    sys.exit(0)
                else:
                    logger.error("❌ Verification failed after seeding")
                    sys.exit(1)
            else:
                logger.error("❌ Seeding failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

