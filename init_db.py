"""
MongoDB Database Initialization and Seed Script for Gym Management System.
Run this script using: python init_db.py
"""

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from db import (
    get_db, test_connection, users_col, members_col, trainers_col,
    plans_col, memberships_col, payments_col, attendance_col,
    workout_plans_col, member_workouts_col
)

def init_database():
    print("==================================================")
    print(" Gym Management System - Database Initialization ")
    print("==================================================")

    # 1. Test Connection
    success, msg = test_connection()
    if not success:
        print(f"[!] MongoDB Connection Failed: {msg}")
        print("[!] Ensure MongoDB service is running (or check MONGO_URI in .env).")
        return False
    print(f"[+] MongoDB Connected successfully.")

    db = get_db()

    # 2. Setup Indexes
    print("\n[*] Creating collection indexes...")
    users_col().create_index("email", unique=True)
    members_col().create_index("user_id", unique=True)
    trainers_col().create_index("user_id", unique=True)
    plans_col().create_index("plan_name")
    memberships_col().create_index([("member_id", 1), ("status", 1)])
    payments_col().create_index("member_id")
    attendance_col().create_index([("member_id", 1), ("date", -1)])
    workout_plans_col().create_index("name")
    member_workouts_col().create_index("member_id")
    print("[+] Indexes created successfully.")

    # 3. Seed Default Admin
    print("\n[*] Checking Admin account...")
    admin = users_col().find_one({"email": "admin@gym.com"})
    if not admin:
        admin_doc = {
            "name": "Gym Administrator",
            "email": "admin@gym.com",
            "phone": "9876543210",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin",
            "status": "active",
            "created_at": datetime.now()
        }
        admin_id = users_col().insert_one(admin_doc).inserted_id
        print(f"[+] Admin created: admin@gym.com / password: admin123")
    else:
        admin_id = admin["_id"]
        print(f"[*] Admin account already exists: admin@gym.com")

    # 4. Seed Membership Plans
    print("\n[*] Checking Membership Plans...")
    if plans_col().count_documents({}) == 0:
        sample_plans = [
            {
                "plan_name": "Monthly Starter",
                "duration_days": 30,
                "price": 1499.00,
                "description": "Full gym equipment access, locker facility, and 1 fitness assessment.",
                "status": "active",
                "created_at": datetime.now()
            },
            {
                "plan_name": "Quarterly Pro",
                "duration_days": 90,
                "price": 3899.00,
                "description": "Gym access, cardio zone, sauna access, and personalized trainer consult.",
                "status": "active",
                "created_at": datetime.now()
            },
            {
                "plan_name": "Annual Elite",
                "duration_days": 365,
                "price": 11999.00,
                "description": "All access VIP: 24/7 gym, personal trainer sessions, diet chart, and guest passes.",
                "status": "active",
                "created_at": datetime.now()
            }
        ]
        plans_col().insert_many(sample_plans)
        print(f"[+] Created {len(sample_plans)} default membership plans.")
    else:
        print("[*] Membership plans already configured.")

    # 5. Seed Sample Trainer
    print("\n[*] Checking Trainer account...")
    trainer_user = users_col().find_one({"email": "trainer@gym.com"})
    if not trainer_user:
        t_user_doc = {
            "name": "Alex Rivera",
            "email": "trainer@gym.com",
            "phone": "9876543211",
            "password_hash": generate_password_hash("trainer123"),
            "role": "trainer",
            "status": "active",
            "created_at": datetime.now()
        }
        t_user_id = users_col().insert_one(t_user_doc).inserted_id

        trainers_col().insert_one({
            "user_id": t_user_id,
            "name": "Alex Rivera",
            "email": "trainer@gym.com",
            "phone": "9876543211",
            "specialization": "Strength & Conditioning, HIIT, Core",
            "experience_years": 5,
            "availability": "Mon-Sat (6 AM - 2 PM)",
            "bio": "Certified fitness instructor with a passion for functional strength and posture transformation.",
            "status": "active",
            "created_at": datetime.now()
        })
        print("[+] Trainer created: trainer@gym.com / password: trainer123")
    else:
        t_user_id = trainer_user["_id"]
        print("[*] Trainer account already exists: trainer@gym.com")

    # 6. Seed Sample Member
    print("\n[*] Checking Member account...")
    member_user = users_col().find_one({"email": "member@gym.com"})
    if not member_user:
        m_user_doc = {
            "name": "John Doe",
            "email": "member@gym.com",
            "phone": "9876543212",
            "password_hash": generate_password_hash("member123"),
            "role": "member",
            "status": "active",
            "created_at": datetime.now()
        }
        m_user_id = users_col().insert_one(m_user_doc).inserted_id

        member_profile = {
            "user_id": m_user_id,
            "name": "John Doe",
            "email": "member@gym.com",
            "phone": "9876543212",
            "gender": "Male",
            "dob": "1998-05-14",
            "emergency_contact": "9876500000",
            "health_notes": "None, aiming for muscle gain and endurance.",
            "status": "active",
            "created_at": datetime.now()
        }
        m_id = members_col().insert_one(member_profile).inserted_id
        print("[+] Member created: member@gym.com / password: member123")

        # Assign a default membership plan to this member
        plan = plans_col().find_one({"plan_name": "Quarterly Pro"})
        if plan:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=plan["duration_days"])
            membership_doc = {
                "member_id": m_id,
                "user_id": m_user_id,
                "plan_id": plan["_id"],
                "plan_name": plan["plan_name"],
                "start_date": start_date,
                "end_date": end_date,
                "price": plan["price"],
                "status": "active",
                "assigned_by": "System Admin",
                "created_at": datetime.now()
            }
            membership_id = memberships_col().insert_one(membership_doc).inserted_id

            # Add payment record
            payments_col().insert_one({
                "member_id": m_id,
                "user_id": m_user_id,
                "membership_id": membership_id,
                "plan_name": plan["plan_name"],
                "amount": plan["price"],
                "payment_date": start_date,
                "payment_method": "Card / Online",
                "reference_no": "PAY-SIM-1001",
                "payment_type": "Recorded / Simulated",
                "status": "completed",
                "notes": "Initial quarterly membership fee"
            })

            # Add sample attendance log
            attendance_col().insert_one({
                "member_id": m_id,
                "user_id": m_user_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "check_in_time": datetime.now().strftime("%H:%M:%S"),
                "check_out_time": (datetime.now() + timedelta(hours=1, minutes=15)).strftime("%H:%M:%S"),
                "status": "Present"
            })
    else:
        print("[*] Member account already exists: member@gym.com")

    # 7. Seed Workout Plans
    print("\n[*] Checking Workout Plans...")
    if workout_plans_col().count_documents({}) == 0:
        sample_workouts = [
            {
                "name": "Beginner Full Body Foundation",
                "difficulty": "Beginner",
                "description": "3-day split designed to build basic motor skills, joint stability, and foundational strength.",
                "created_by": "Alex Rivera",
                "exercises": [
                    {"name": "Bodyweight Squats", "sets": "3", "reps": "12-15", "instructions": "Keep chest upright and feet shoulder width apart."},
                    {"name": "Push-ups / Incline Push-ups", "sets": "3", "reps": "10-12", "instructions": "Maintain straight core plank."},
                    {"name": "Dumbbell Lat Rows", "sets": "3", "reps": "12", "instructions": "Squeeze shoulder blades at top."},
                    {"name": "Plank Hold", "sets": "3", "reps": "45 secs", "instructions": "Breathe steadily without sagging hips."}
                ],
                "created_at": datetime.now()
            },
            {
                "name": "Hypertrophy Upper Body Power",
                "difficulty": "Intermediate",
                "description": "Targeted upper body muscle growth routine focusing on compound presses and pulls.",
                "created_by": "Alex Rivera",
                "exercises": [
                    {"name": "Barbell Bench Press", "sets": "4", "reps": "8-10", "instructions": "Controlled 2-sec eccentric phase."},
                    {"name": "Overhead Barbell Press", "sets": "3", "reps": "8", "instructions": "Brace core and press straight up."},
                    {"name": "Seated Cable Row", "sets": "4", "reps": "10-12", "instructions": "Full stretch forward, tight contraction."},
                    {"name": "Barbell Bicep Curls", "sets": "3", "reps": "12", "instructions": "Strict form without elbow swing."}
                ],
                "created_at": datetime.now()
            }
        ]
        workout_plans_col().insert_many(sample_workouts)
        print(f"[+] Created {len(sample_workouts)} workout plans.")
    else:
        print("[*] Workout plans already configured.")

    print("\n==================================================")
    print(" Database setup & seeding complete!")
    print(" You can log in using:")
    print("   Admin:   admin@gym.com   / admin123")
    print("   Trainer: trainer@gym.com / trainer123")
    print("   Member:  member@gym.com  / member123")
    print("==================================================")
    return True

if __name__ == "__main__":
    init_database()
