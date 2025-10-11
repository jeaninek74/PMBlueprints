"""
Supabase database module for PMBlueprints
Replaces SQLite with Supabase PostgreSQL
"""

import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://mmrazymwgqfxkhczqpus.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tcmF6eW13Z3FmeGtoY3pxcHVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAxNjk5NDIsImV4cCI6MjA3NTc0NTk0Mn0.65JsP7dhRAz4IKGUMuz6VhA3jM-Zb8EZlOVUfJE2i6k')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_templates():
    """Get all templates from Supabase"""
    try:
        response = supabase.table('templates').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return []

def get_template_by_id(template_id):
    """Get a specific template by ID"""
    try:
        response = supabase.table('templates').select('*').eq('id', template_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching template: {e}")
        return None

def get_template_by_filename(filename):
    """Get a specific template by filename"""
    try:
        response = supabase.table('templates').select('*').eq('filename', filename).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching template: {e}")
        return None

def get_templates_by_industry(industry):
    """Get templates filtered by industry"""
    try:
        response = supabase.table('templates').select('*').eq('industry', industry).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching templates by industry: {e}")
        return []

def get_templates_by_category(category):
    """Get templates filtered by category"""
    try:
        response = supabase.table('templates').select('*').eq('category', category).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching templates by category: {e}")
        return []

def increment_downloads(template_id):
    """Increment download count for a template"""
    try:
        # Get current downloads
        template = get_template_by_id(template_id)
        if template:
            new_count = template.get('downloads', 0) + 1
            supabase.table('templates').update({'downloads': new_count}).eq('id', template_id).execute()
            return True
        return False
    except Exception as e:
        print(f"Error incrementing downloads: {e}")
        return False

def search_templates(query):
    """Search templates by name or description"""
    try:
        # Supabase text search
        response = supabase.table('templates').select('*').or_(
            f"name.ilike.%{query}%,description.ilike.%{query}%"
        ).execute()
        return response.data
    except Exception as e:
        print(f"Error searching templates: {e}")
        return []

def get_industries():
    """Get list of all industries"""
    try:
        response = supabase.table('templates').select('industry').execute()
        industries = list(set([t['industry'] for t in response.data]))
        return sorted(industries)
    except Exception as e:
        print(f"Error fetching industries: {e}")
        return []

def get_categories():
    """Get list of all categories"""
    try:
        response = supabase.table('templates').select('category').execute()
        categories = list(set([t['category'] for t in response.data]))
        return sorted(categories)
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

# Initialize function (no longer needed with Supabase, but kept for compatibility)
def init_db():
    """Initialize database - no-op for Supabase"""
    return True

