import sys
from app import create_app

app = create_app()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--seed':
        import seed
        seed.run_seed()
    else:
        print("\n========================================================")
        print(">> SMART INTERVIEW PREPARATION PLATFORM")
        print("   URL: http://127.0.0.1:5000")
        print("   Admin Account:   admin@smartprep.com   / Admin@123")
        print("   Student Account: student@smartprep.com / Student@123")
        print("========================================================\n")
        app.run(host='127.0.0.1', port=5000, debug=True)
