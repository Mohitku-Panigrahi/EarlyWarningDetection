import sys
import argparse
from backend.app.database.session import SessionLocal, engine, Base
import backend.app.models
from backend.app.services.student_import_service import StudentImportService

def main():
    parser = argparse.ArgumentParser(description="Seed LPU-RISK-01 demonstration dataset.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-import and update existing records.",
    )
    args = parser.parse_args()

    print("==================================================================")
    print(" LPU-RISK-01 Academic Early-Warning System — Database Seed Script ")
    print("==================================================================")
    print("Ensuring tables are initialized...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print(f"Executing import pipeline (force_reload={args.force})...")
        report = StudentImportService.import_dataset(db, force_reload=args.force)
        print("\n--- IMPORT EXECUTION REPORT ---")
        for k, v in report.items():
            if k == "validation_errors" and not v:
                print(f"  {k}: None (all validation checks passed)")
            else:
                print(f"  {k}: {v}")
        print("--------------------------------\n")
        print("Demo Accounts Created / Ready:")
        print("  - Admin:  username: admin    password: admin123")
        print("  - Mentor: username: m08      password: mentor123 (Dr. Manoj Saini)")
        print("  - Student:username: 12511001 password: demo123   (Aarav Sharma)")
        print("==================================================================")
    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
