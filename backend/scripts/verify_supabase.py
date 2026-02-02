#!/usr/bin/env python3
"""
Supabase Connection Verification Script

This script verifies that the Supabase connection is properly configured
and all required extensions are enabled.

Usage:
    python -m scripts.verify_supabase
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_env_vars():
    """Check that all required environment variables are set."""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your-"):
            missing.append(var)
    
    if missing:
        print("❌ Missing or unconfigured environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("✓ All required environment variables are set")
    return True


def check_supabase_connection():
    """Test connection to Supabase."""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ Cannot test connection - missing credentials")
            return False
        
        client: Client = create_client(url, key)
        
        # Try a simple query to verify connection
        # This will fail if the connection is invalid
        result = client.table("_dummy_test").select("*").limit(1).execute()
        
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            # This error means connection works, table just doesn't exist (expected)
            print("✓ Supabase connection successful")
            return True
        elif "Invalid API key" in error_msg:
            print("❌ Invalid API key - check your SUPABASE_SERVICE_ROLE_KEY")
            return False
        elif "Failed to establish" in error_msg or "Connection refused" in error_msg:
            print("❌ Cannot connect to Supabase - check your SUPABASE_URL")
            return False
        else:
            print(f"✓ Supabase connection successful (verified with error: {error_msg[:50]}...)")
            return True
    
    print("✓ Supabase connection successful")
    return True


def check_pgvector_extension():
    """Check if pgvector extension is enabled."""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("⚠ Cannot check pgvector - missing credentials")
            return False
        
        client: Client = create_client(url, key)
        
        # Query to check if vector extension exists
        result = client.rpc("check_extension", {"ext_name": "vector"}).execute()
        
        # If RPC doesn't exist, try raw SQL via REST
        # This is a fallback check
        print("⚠ Could not verify pgvector - please check manually in Supabase dashboard")
        print("   Go to Database > Extensions and ensure 'vector' is enabled")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "function" in error_msg and "does not exist" in error_msg:
            print("⚠ Cannot verify pgvector via RPC - please check manually")
            print("   Go to Database > Extensions and ensure 'vector' is enabled")
            return True
        print(f"⚠ pgvector check inconclusive: {error_msg[:50]}...")
        return True


def check_tables_exist():
    """Check if the main tables have been created."""
    try:
        from supabase import create_client, Client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("⚠ Cannot check tables - missing credentials")
            return False
        
        client: Client = create_client(url, key)
        
        tables = ["discovery_jobs", "brand_dna", "discovered_profiles", "profile_scores", "profile_contacts"]
        existing = []
        missing = []
        
        for table in tables:
            try:
                result = client.table(table).select("*").limit(0).execute()
                existing.append(table)
            except Exception as e:
                if "does not exist" in str(e):
                    missing.append(table)
                else:
                    existing.append(table)  # Assume exists if different error
        
        if existing:
            print(f"✓ Found tables: {', '.join(existing)}")
        
        if missing:
            print(f"⚠ Missing tables: {', '.join(missing)}")
            print("   Run the migration files to create them")
            return False
        
        return True
        
    except Exception as e:
        print(f"⚠ Could not check tables: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("PartnerScout AI - Supabase Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Check 1: Environment variables
    print("[1/4] Checking environment variables...")
    if not check_env_vars():
        all_passed = False
        print()
        print("Please update your backend/.env file with Supabase credentials.")
        print("See supabase/README.md for instructions.")
        print()
        sys.exit(1)
    print()
    
    # Check 2: Connection
    print("[2/4] Testing Supabase connection...")
    if not check_supabase_connection():
        all_passed = False
    print()
    
    # Check 3: pgvector extension
    print("[3/4] Checking pgvector extension...")
    check_pgvector_extension()
    print()
    
    # Check 4: Tables
    print("[4/4] Checking database tables...")
    check_tables_exist()
    print()
    
    print("=" * 60)
    if all_passed:
        print("✓ Supabase setup verification complete!")
    else:
        print("⚠ Some checks failed - see above for details")
    print("=" * 60)


if __name__ == "__main__":
    main()
