from src.database.supabase_client import SupabaseClient
import os

def verify_env_setup():
    
    print(f"\n🔧 Environment Setup:")
    print("=" * 50)
    
    database_url = os.getenv('DATABASE_URL')
    reporter_name = os.getenv('REPORTER_NAME')
    
    print(f"DATABASE_URL: {'✅ Set' if database_url else '❌ Missing'}")
    print(f"REPORTER_NAME: {'✅ Set' if reporter_name else '❌ Missing'}")
    
    # Check for missing required environment variables
    missing_vars = []
    if not database_url:
        missing_vars.append('DATABASE_URL')
    if not reporter_name:
        missing_vars.append('REPORTER_NAME')
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        print(f"\n❌ {error_msg}")
        if 'REPORTER_NAME' in missing_vars:
            print(f"\n💡 To set reporter name, add to your .env file:")
            print(f"   REPORTER_NAME=Your_Name_Here")
        raise EnvironmentError(error_msg)
    
    # Test database connection
    try:
        SupabaseClient()
        print("✅ Database connection successful")
    except Exception as e:
        error_msg = f"Database connection failed: {e}"
        print(f"\n❌ {error_msg}")
        raise ConnectionError(error_msg)
