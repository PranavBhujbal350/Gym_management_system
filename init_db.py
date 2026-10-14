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

DEMO_PASSWORD = "12345678"

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

    # 4. Seed Membership Plans (exact prices as requested)
    print("\n[*] Setting up Membership Plans...")
    # Clear and re-seed plans to ensure correct prices
    existing_plans = plans_col().count_documents({})
    if existing_plans == 0:
        sample_plans = [
            {
                "plan_name": "Monthly Plan",
                "duration_days": 30,
                "price": 2000.00,
                "description": "Full gym equipment access, locker facility, and 1 fitness assessment per month.",
                "status": "active",
                "created_at": datetime.now()
            },
            {
                "plan_name": "Quarterly Plan",
                "duration_days": 90,
                "price": 4000.00,
                "description": "3-month gym access, cardio zone, sauna access, and personalized trainer consult.",
                "status": "active",
                "created_at": datetime.now()
            },
            {
                "plan_name": "Half-Yearly Plan",
                "duration_days": 180,
                "price": 6000.00,
                "description": "6-month all-access pass with group classes, nutrition guide, and body metrics tracking.",
                "status": "active",
                "created_at": datetime.now()
            },
            {
                "plan_name": "Annual Elite Plan",
                "duration_days": 365,
                "price": 12000.00,
                "description": "Full year VIP access: 24/7 gym, personal trainer sessions, diet chart, and guest passes.",
                "status": "active",
                "created_at": datetime.now()
            }
        ]
        plans_col().insert_many(sample_plans)
        print(f"[+] Created {len(sample_plans)} membership plans.")
        print("    Monthly: ₹2000 | Quarterly: ₹4000 | Half-Yearly: ₹6000 | Annual: ₹12000")
    else:
        print("[*] Membership plans already configured.")

    # 5. Seed Demo Trainer (trainer@gym.com / 12345678)
    print("\n[*] Checking Demo Trainer account...")
    trainer_user = users_col().find_one({"email": "trainer@gym.com"})
    if not trainer_user:
        t_user_doc = {
            "name": "Alex Rivera",
            "email": "trainer@gym.com",
            "phone": "9876543211",
            "password_hash": generate_password_hash(DEMO_PASSWORD),
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
        print(f"[+] Trainer created: trainer@gym.com / password: {DEMO_PASSWORD}")
    else:
        # Update password to 12345678
        users_col().update_one(
            {"email": "trainer@gym.com"},
            {"$set": {"password_hash": generate_password_hash(DEMO_PASSWORD)}}
        )
        t_user_id = trainer_user["_id"]
        print(f"[*] Trainer account updated: trainer@gym.com / password: {DEMO_PASSWORD}")

    # Get the trainer document
    trainer_doc = trainers_col().find_one({"user_id": t_user_id})

    # 6. Seed Demo Member (member@gym.com / 12345678)
    print("\n[*] Checking Demo Member account...")
    member_user = users_col().find_one({"email": "member@gym.com"})
    if not member_user:
        m_user_doc = {
            "name": "John Doe",
            "email": "member@gym.com",
            "phone": "9876543212",
            "password_hash": generate_password_hash(DEMO_PASSWORD),
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
            "health_notes": "No restrictions. Aiming for muscle gain and endurance.",
            "status": "active",
            "created_at": datetime.now()
        }
        m_id = members_col().insert_one(member_profile).inserted_id
        print(f"[+] Member created: member@gym.com / password: {DEMO_PASSWORD}")
    else:
        # Update password to 12345678
        users_col().update_one(
            {"email": "member@gym.com"},
            {"$set": {"password_hash": generate_password_hash(DEMO_PASSWORD)}}
        )
        m_user_id = member_user["_id"]
        m_id = members_col().find_one({"user_id": m_user_id})["_id"]
        print(f"[*] Member account updated: member@gym.com / password: {DEMO_PASSWORD}")

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
            },
            {
                "name": "Fat Burn HIIT Cardio",
                "difficulty": "Advanced",
                "description": "High-intensity interval training for maximum calorie burn and cardio endurance.",
                "created_by": "Alex Rivera",
                "exercises": [
                    {"name": "Burpees", "sets": "5", "reps": "15", "instructions": "Full explosive jump at top."},
                    {"name": "Jump Rope", "sets": "4", "reps": "60 secs", "instructions": "Maintain rhythm, stay on toes."},
                    {"name": "Mountain Climbers", "sets": "4", "reps": "20 each", "instructions": "Keep hips level, fast tempo."},
                    {"name": "Box Jumps", "sets": "4", "reps": "10", "instructions": "Land softly with bent knees."}
                ],
                "created_at": datetime.now()
            }
        ]
        workout_plans_col().insert_many(sample_workouts)
        print(f"[+] Created {len(sample_workouts)} workout plans.")
    else:
        print("[*] Workout plans already configured.")

    # 8. Assign membership + payment + attendance to demo member (if not already done)
    print("\n[*] Checking member membership & payment records...")
    existing_membership = memberships_col().find_one({"member_id": m_id})
    if not existing_membership:
        plan = plans_col().find_one({"plan_name": "Quarterly Plan"})
        if plan:
            start_date = datetime.now() - timedelta(days=15)  # started 15 days ago
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
                "assigned_by": "Gym Admin",
                "created_at": start_date
            }
            membership_id = memberships_col().insert_one(membership_doc).inserted_id

            # Add payment record with receipt
            import random
            ref_no = f"PAY-{random.randint(10000, 99999)}"
            payments_col().insert_one({
                "member_id": m_id,
                "user_id": m_user_id,
                "membership_id": membership_id,
                "plan_name": plan["plan_name"],
                "amount": plan["price"],
                "payment_date": start_date,
                "payment_method": "Cash",
                "reference_no": ref_no,
                "payment_type": "New Membership",
                "status": "completed",
                "notes": "Initial quarterly membership payment",
                "member_name": "John Doe",
                "member_email": "member@gym.com",
                "member_phone": "9876543212"
            })
            print(f"[+] Membership assigned: Quarterly Plan | Ref: {ref_no}")
    else:
        print("[*] Member membership already exists.")

    # 9. Add sample attendance records for demo member
    print("\n[*] Checking attendance records...")
    existing_attendance = attendance_col().count_documents({"member_id": m_id})
    if existing_attendance == 0:
        now = datetime.now()
        attendance_records = []
        for i in range(7):
            if i % 3 != 1:  # skip some days to be realistic
                att_date = now - timedelta(days=i)
                attendance_records.append({
                    "member_id": m_id,
                    "user_id": m_user_id,
                    "member_name": "John Doe",
                    "date": att_date.strftime("%Y-%m-%d"),
                    "check_in_time": "07:30:00",
                    "check_out_time": "09:00:00",
                    "status": "Present",
                    "created_at": att_date
                })
        attendance_col().insert_many(attendance_records)
        print(f"[+] Added {len(attendance_records)} attendance records for demo member.")
    else:
        print(f"[*] Attendance records already exist ({existing_attendance} records).")

    # 10. Assign workout to demo member from trainer
    print("\n[*] Checking workout assignment for demo member...")
    existing_workout_assign = member_workouts_col().find_one({"member_id": m_id})
    if not existing_workout_assign:
        workout = workout_plans_col().find_one({"name": "Beginner Full Body Foundation"})
        if workout and trainer_doc:
            member_workouts_col().insert_one({
                "member_id": m_id,
                "member_name": "John Doe",
                "user_id": m_user_id,
                "workout_plan_id": workout["_id"],
                "workout_name": workout.get("name"),
                "difficulty": workout.get("difficulty"),
                "exercises": workout.get("exercises", []),
                "trainer_name": trainer_doc.get("name", "Alex Rivera"),
                "trainer_id": trainer_doc.get("_id"),
                "assigned_date": datetime.now(),
                "notes": "Focus on form. Warm up for 10 mins before starting. Rest 60s between sets."
            })
            print(f"[+] Workout 'Beginner Full Body Foundation' assigned to John Doe by Alex Rivera.")
    else:
        print("[*] Workout already assigned to demo member.")

    print("\n==================================================")
    print(" Database setup & seeding complete!")
    print("")
    print(" DEMO CREDENTIALS (all passwords: 12345678)")
    print(" -----------------------------------------------")
    print(f"   Admin:   admin@gym.com   / admin123")
    print(f"   Trainer: trainer@gym.com / {DEMO_PASSWORD}")
    print(f"   Member:  member@gym.com  / {DEMO_PASSWORD}")
    print("")
    print(" MEMBERSHIP PRICES:")
    print("   Monthly:     Rs.2,000  (30 days)")
    print("   Quarterly:   Rs.4,000  (90 days)")
    print("   Half-Yearly: Rs.6,000  (180 days)")
    print("   Annual:      Rs.12,000 (365 days)")
    print("==================================================")
    return True

if __name__ == "__main__":
    init_database()
