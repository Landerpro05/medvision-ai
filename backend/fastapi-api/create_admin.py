import sys
import argparse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.user.models import User, Role
from app.security import hash_password

def create_admin(username: str, email: str, password: str):
    db: Session = SessionLocal()
    try:
        # Check if role ADMIN exists, create if not
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            admin_role = Role(name="ADMIN")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        # Check if user exists
        user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if user:
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            sys.exit(1)

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )
        # Assign admin role
        user.roles.append(admin_role)
        
        db.add(user)
        db.commit()
        print(f"Success: Admin user '{username}' created successfully.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an initial ADMIN user.")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    
    args = parser.parse_args()
    create_admin(args.username, args.email, args.password)
