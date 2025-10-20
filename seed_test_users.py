#!/usr/bin/env python3
"""
Database Seeding Script - Test Users
Creates test users for all subscription tiers with correct permissions
Run this script to ensure test users exist in all environments
"""
from app import app
from models import db, User
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test users configuration
TEST_USERS = [
    {
        'email': 'free@pmblueprints.com',
        'password': 'TestFree123!',
        'first_name': 'Free',
        'last_name': 'User',
        'subscription_tier': 'free',
        'subscription_status': 'active'
    },
    {
        'email': 'individual@pmblueprints.com',
        'password': 'TestIndividual123!',
        'first_name': 'Individual',
        'last_name': 'User',
        'subscription_tier': 'individual',
        'subscription_status': 'active'
    },
    {
        'email': 'professional@pmblueprints.com',
        'password': 'TestPro123!',
        'first_name': 'Professional',
        'last_name': 'User',
        'subscription_tier': 'professional',
        'subscription_status': 'active'
    },
    {
        'email': 'enterprise@pmblueprints.com',
        'password': 'TestEnterprise123!',
        'first_name': 'Enterprise',
        'last_name': 'User',
        'subscription_tier': 'enterprise',
        'subscription_status': 'active'
    }
]

def seed_test_users():
    """Create or update test users in the database"""
    with app.app_context():
        logger.info("Starting test user seeding...")
        logger.info("=" * 80)
        
        created_count = 0
        updated_count = 0
        
        for user_config in TEST_USERS:
            email = user_config['email']
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Update existing user
                logger.info(f"Updating existing user: {email}")
                user.password_hash = generate_password_hash(user_config['password'])
                user.first_name = user_config['first_name']
                user.last_name = user_config['last_name']
                user.subscription_tier = user_config['subscription_tier']
                user.subscription_status = user_config['subscription_status']
                updated_count += 1
            else:
                # Create new user
                logger.info(f"Creating new user: {email}")
                user = User(
                    email=email,
                    password_hash=generate_password_hash(user_config['password']),
                    first_name=user_config['first_name'],
                    last_name=user_config['last_name'],
                    subscription_tier=user_config['subscription_tier'],
                    subscription_status=user_config['subscription_status']
                )
                db.session.add(user)
                created_count += 1
            
            logger.info(f"  Tier: {user_config['subscription_tier']}")
            logger.info(f"  Status: {user_config['subscription_status']}")
        
        # Commit all changes
        try:
            db.session.commit()
            logger.info("=" * 80)
            logger.info(f"✓ Seeding complete!")
            logger.info(f"  Created: {created_count} users")
            logger.info(f"  Updated: {updated_count} users")
            logger.info(f"  Total: {len(TEST_USERS)} users")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"✗ Seeding failed: {e}")
            return False

if __name__ == '__main__':
    success = seed_test_users()
    exit(0 if success else 1)

