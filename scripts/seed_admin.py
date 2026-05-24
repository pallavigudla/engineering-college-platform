"""
scripts/seed_admin.py
Creates the initial admin user and seeds core lookup data
(states, branches, facilities).

Usage:
  python scripts/seed_admin.py
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User, State, Branch, Facility


INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Chandigarh", "Puducherry", "Ladakh", "Jammu and Kashmir",
]

ENGINEERING_BRANCHES = [
    ("Computer Science Engineering", "CSE"),
    ("Electronics and Communication Engineering", "ECE"),
    ("Electrical and Electronics Engineering", "EEE"),
    ("Mechanical Engineering", "MECH"),
    ("Civil Engineering", "CIVIL"),
    ("Information Technology", "IT"),
    ("Chemical Engineering", "CHEM"),
    ("Biotechnology", "BT"),
    ("Aerospace Engineering", "AERO"),
    ("Artificial Intelligence and Machine Learning", "AIML"),
    ("Data Science", "DS"),
    ("Cybersecurity", "CYBER"),
    ("Internet of Things", "IOT"),
    ("Automobile Engineering", "AUTO"),
    ("Mining Engineering", "MINING"),
    ("Metallurgical Engineering", "METAL"),
    ("Production Engineering", "PROD"),
    ("Industrial Engineering", "IE"),
    ("Environmental Engineering", "ENV"),
    ("Marine Engineering", "MARINE"),
    ("Petroleum Engineering", "PETRO"),
    ("Agricultural Engineering", "AGR"),
    ("Instrumentation Engineering", "INST"),
    ("Robotics and Automation", "ROBOT"),
    ("Textile Engineering", "TEXT"),
]

FACILITIES = [
    ("Library", "bi-book"),
    ("Hostel (Boys)", "bi-building"),
    ("Hostel (Girls)", "bi-building-fill"),
    ("Sports Complex", "bi-trophy"),
    ("Computer Lab", "bi-pc-display"),
    ("Research Center", "bi-flask"),
    ("Cafeteria / Canteen", "bi-cup-hot"),
    ("Medical Center", "bi-hospital"),
    ("Wi-Fi Campus", "bi-wifi"),
    ("Auditorium", "bi-mic"),
    ("Gymnasium", "bi-activity"),
    ("Transport / Bus", "bi-bus-front"),
    ("Placement Cell", "bi-briefcase"),
    ("Innovation Lab / Incubation", "bi-lightbulb"),
    ("ATM", "bi-cash"),
    ("Indoor Games", "bi-controller"),
    ("Swimming Pool", "bi-water"),
    ("International Students Cell", "bi-globe"),
]


def seed():
    app = create_app("development")
    with app.app_context():
        print("🌱 Seeding database...")

        # ── Admin User ────────────────────────────────────────
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@collegeplatform.com")
        admin_pass  = os.environ.get("ADMIN_PASSWORD", "AdminPass@123")

        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                full_name="Platform Admin",
                email=admin_email,
                role="admin",
                is_active=True,
            )
            admin.set_password(admin_pass)
            db.session.add(admin)
            print(f"  ✅ Admin user created: {admin_email}")
        else:
            print(f"  ℹ️  Admin already exists: {admin_email}")

        # ── States ────────────────────────────────────────────
        for state_name in INDIAN_STATES:
            if not State.query.filter_by(name=state_name).first():
                db.session.add(State(name=state_name))
        print(f"  ✅ {len(INDIAN_STATES)} states seeded")

        # ── Branches ─────────────────────────────────────────
        for branch_name, branch_code in ENGINEERING_BRANCHES:
            if not Branch.query.filter_by(name=branch_name).first():
                db.session.add(Branch(name=branch_name, code=branch_code))
        print(f"  ✅ {len(ENGINEERING_BRANCHES)} branches seeded")

        # ── Facilities ───────────────────────────────────────
        for fac_name, fac_icon in FACILITIES:
            if not Facility.query.filter_by(name=fac_name).first():
                db.session.add(Facility(name=fac_name, icon=fac_icon))
        print(f"  ✅ {len(FACILITIES)} facilities seeded")

        db.session.commit()
        print("\n✅ Database seeding complete!")
        print(f"   Admin login: {admin_email} / {admin_pass}")


if __name__ == "__main__":
    seed()
