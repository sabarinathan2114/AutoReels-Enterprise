import sys
import argparse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.entities import User, PlatformAdmin, AuditLog
from app.services.auth_service import AuthService

def create_superadmin(email: str, password: str, full_name: str = "Platform SuperAdmin", role: str = "super_admin"):
    db: Session = SessionLocal()
    try:
        user = AuthService.get_user_by_email(db, email)
        if not user:
            user = AuthService.create_user(db, email=email, plain_password=password, full_name=full_name)
            print(f"[CLI] Created new user: {email} (ID: {user.id})")
        else:
            # Update password if user already exists
            user.hashed_password = AuthService.hash_password(password)
            user.full_name = full_name
            db.commit()
            print(f"[CLI] Existing user found: {email} (ID: {user.id}). Password updated.")

        admin = db.query(PlatformAdmin).filter(PlatformAdmin.user_id == user.id).first()
        if not admin:
            admin = PlatformAdmin(user_id=user.id, role=role)
            db.add(admin)
        else:
            admin.role = role

        audit = AuditLog(
            user_id=str(user.id),
            action="platform_admin.provisioned_via_cli",
            resource="platform_admins",
            details={"email": email, "role": role}
        )
        db.add(audit)
        db.commit()
        db.refresh(admin)

        print(f"[CLI] Successfully provisioned Platform Admin:")
        print(f"      User ID: {user.id}")
        print(f"      Email:   {user.email}")
        print(f"      Role:    {admin.role}")
        print(f"      Created: {admin.created_at}")
        return admin
    except Exception as e:
        db.rollback()
        print(f"[CLI ERROR] Failed to provision platform admin: {e}", file=sys.stderr)
        raise
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="AutoReels Enterprise Super Admin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-admin", help="Create or elevate a platform administrator")
    create_parser.add_argument("--email", required=True, help="Administrator email address")
    create_parser.add_argument("--password", required=True, help="Administrator password")
    create_parser.add_argument("--name", default="Platform Admin", help="Full name")
    create_parser.add_argument("--role", choices=["super_admin", "support"], default="super_admin", help="Admin role")

    args = parser.parse_args()
    if args.command == "create-admin":
        create_superadmin(
            email=args.email,
            password=args.password,
            full_name=args.name,
            role=args.role
        )

if __name__ == "__main__":
    main()
