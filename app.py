from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps
from datetime import datetime, timedelta, date
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from db import (
    get_db, users_col, members_col, trainers_col, plans_col,
    memberships_col, payments_col, attendance_col, workout_plans_col,
    member_workouts_col, to_object_id, serialize_doc, serialize_list
)
from api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register REST API blueprint
app.register_blueprint(api_bp)

# ======================================================
# JINJA TEMPLATE FILTERS & CONTEXT PROCESSORS
# ======================================================

@app.template_filter('format_date')
def filter_format_date(val, fmt="%d %b %Y"):
    if not val:
        return "-"
    if isinstance(val, str):
        try:
            val = datetime.fromisoformat(val)
        except ValueError:
            return val
    if isinstance(val, (datetime, date)):
        return val.strftime(fmt)
    return str(val)

@app.template_filter('currency')
def filter_currency(val):
    try:
        val = float(val)
        return f"₹ {val:,.2f}"
    except (ValueError, TypeError):
        return "₹ 0.00"

@app.context_processor
def inject_now():
    return {
        'now': datetime.now(),
        'today_str': datetime.now().strftime("%Y-%m-%d")
    }

# ======================================================
# AUTHENTICATION & ROLE DECORATORS
# ======================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for('login', next=request.path))
            user_role = session.get('role')
            if user_role not in roles:
                return render_template('403.html', required_roles=roles, user_role=user_role), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ======================================================
# PUBLIC & AUTHENTICATION ROUTES
# ======================================================

@app.route('/')
def index():
    plans = list(plans_col().find({"status": "active"}).limit(3))
    trainers = list(trainers_col().find({"status": "active"}).limit(3))
    stats = {
        'members': members_col().count_documents({"status": "active"}),
        'trainers': trainers_col().count_documents({"status": "active"}),
        'plans': plans_col().count_documents({"status": "active"})
    }
    return render_template('index.html', plans=plans, trainers=trainers, stats=stats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'trainer':
            return redirect(url_for('trainer_dashboard'))
        return redirect(url_for('member_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        user = users_col().find_one({"email": email})
        if not user or not check_password_hash(user.get('password_hash', ''), password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html', email=email)

        if user.get('status') == 'inactive':
            flash("Your account has been deactivated. Please contact gym administration.", "danger")
            return render_template('login.html', email=email)

        # Set session variables
        session['user_id'] = str(user['_id'])
        session['role'] = user.get('role')
        session['user_name'] = user.get('name')
        session['user_email'] = user.get('email')

        flash(f"Welcome back, {user.get('name')}!", "success")

        # Redirect based on user role
        role = user.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'trainer':
            return redirect(url_for('trainer_dashboard'))
        else:
            return redirect(url_for('member_dashboard'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        gender = request.form.get('gender', 'Other')
        dob = request.form.get('dob', '')
        emergency_contact = request.form.get('emergency_contact', '')
        health_notes = request.form.get('health_notes', '')

        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template('register.html')

        if users_col().find_one({"email": email}):
            flash(f"An account with email {email} already exists. Please log in.", "warning")
            return render_template('register.html')

        user_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "password_hash": generate_password_hash(password),
            "role": "member",
            "status": "active",
            "created_at": datetime.now()
        }
        user_id = users_col().insert_one(user_doc).inserted_id

        member_doc = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "dob": dob,
            "emergency_contact": emergency_contact,
            "health_notes": health_notes,
            "status": "active",
            "created_at": datetime.now()
        }
        members_col().insert_one(member_doc)

        session['user_id'] = str(user_id)
        session['role'] = 'member'
        session['user_name'] = name
        session['user_email'] = email

        flash("Registration successful! Welcome to the gym family.", "success")
        return redirect(url_for('member_dashboard'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))


# ======================================================
# ADMIN ROUTES
# ======================================================

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    # 1. Total active members
    total_members = members_col().count_documents({"status": "active"})
    total_trainers = trainers_col().count_documents({"status": "active"})

    now = datetime.now()
    # 2. Memberships stats
    active_memberships = memberships_col().count_documents({
        "status": "active",
        "end_date": {"$gte": now}
    })
    expired_memberships = memberships_col().count_documents({
        "$or": [
            {"status": "expired"},
            {"end_date": {"$lt": now}}
        ]
    })

    # 3. Revenue calculation
    payments = list(payments_col().find())
    total_revenue = sum(float(p.get('amount', 0)) for p in payments)

    # 4. Today's attendance
    today_str = now.strftime("%Y-%m-%d")
    today_attendance = attendance_col().count_documents({"date": today_str})

    # 5. Recent members
    recent_members = list(members_col().find().sort("created_at", -1).limit(5))

    # 6. Recent payments
    recent_payments = list(payments_col().find().sort("payment_date", -1).limit(5))

    # 7. Expiring soon memberships (next 7 days)
    seven_days_later = now + timedelta(days=7)
    expiring_soon = list(memberships_col().find({
        "status": "active",
        "end_date": {"$gte": now, "$lte": seven_days_later}
    }).limit(5))

    stats = {
        'total_members': total_members,
        'total_trainers': total_trainers,
        'active_memberships': active_memberships,
        'expired_memberships': expired_memberships,
        'total_revenue': total_revenue,
        'today_attendance': today_attendance
    }

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_members=recent_members,
                           recent_payments=recent_payments,
                           expiring_soon=expiring_soon)


@app.route('/admin/members')
@role_required('admin')
def admin_members():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = {}
    if status_filter:
        query['status'] = status_filter
    if search:
        query['$or'] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]

    members_list = list(members_col().find(query).sort("created_at", -1))
    
    # Attach active membership info for each member
    for m in members_list:
        active_sub = memberships_col().find_one({
            "member_id": m["_id"],
            "status": "active",
            "end_date": {"$gte": datetime.now()}
        })
        m['active_plan'] = active_sub.get('plan_name') if active_sub else "No active plan"
        m['plan_expiry'] = active_sub.get('end_date') if active_sub else None

    plans = list(plans_col().find({"status": "active"}))
    return render_template('admin/members.html', members=members_list, plans=plans, search=search, status_filter=status_filter)


@app.route('/admin/members/add', methods=['POST'])
@role_required('admin')
def admin_add_member():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', 'gym123').strip()
    gender = request.form.get('gender', 'Other')
    dob = request.form.get('dob', '')
    emergency_contact = request.form.get('emergency_contact', '')
    health_notes = request.form.get('health_notes', '')

    if not name or not email:
        flash("Name and email are required.", "danger")
        return redirect(url_for('admin_members'))

    if users_col().find_one({"email": email}):
        flash(f"User with email {email} already exists.", "danger")
        return redirect(url_for('admin_members'))

    user_id = users_col().insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": generate_password_hash(password),
        "role": "member",
        "status": "active",
        "created_at": datetime.now()
    }).inserted_id

    member_id = members_col().insert_one({
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "emergency_contact": emergency_contact,
        "health_notes": health_notes,
        "status": "active",
        "created_at": datetime.now()
    }).inserted_id

    # Optional auto-assign plan if selected
    plan_id = request.form.get('plan_id')
    if plan_id:
        plan = plans_col().find_one({"_id": to_object_id(plan_id)})
        if plan:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=plan['duration_days'])
            m_sub_id = memberships_col().insert_one({
                "member_id": member_id,
                "user_id": user_id,
                "plan_id": plan['_id'],
                "plan_name": plan['plan_name'],
                "start_date": start_date,
                "end_date": end_date,
                "price": plan['price'],
                "status": "active",
                "assigned_by": session.get('user_name', 'Admin'),
                "created_at": datetime.now()
            }).inserted_id

            # Add payment record
            payments_col().insert_one({
                "member_id": member_id,
                "user_id": user_id,
                "membership_id": m_sub_id,
                "plan_name": plan['plan_name'],
                "amount": plan['price'],
                "payment_date": start_date,
                "payment_method": request.form.get('payment_method', 'Cash'),
                "reference_no": f"PAY-{int(datetime.now().timestamp())}",
                "payment_type": "Recorded / Manual",
                "status": "completed",
                "notes": "Added during member registration"
            })

    flash(f"Member '{name}' added successfully.", "success")
    return redirect(url_for('admin_members'))


@app.route('/admin/members/<member_id>/edit', methods=['POST'])
@role_required('admin')
def admin_edit_member(member_id):
    obj_id = to_object_id(member_id)
    if not obj_id:
        flash("Invalid member ID.", "danger")
        return redirect(url_for('admin_members'))

    member = members_col().find_one({"_id": obj_id})
    if not member:
        flash("Member not found.", "danger")
        return redirect(url_for('admin_members'))

    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    gender = request.form.get('gender', 'Other')
    dob = request.form.get('dob', '')
    emergency_contact = request.form.get('emergency_contact', '')
    health_notes = request.form.get('health_notes', '')

    members_col().update_one({"_id": obj_id}, {"$set": {
        "name": name,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "emergency_contact": emergency_contact,
        "health_notes": health_notes
    }})

    if member.get('user_id'):
        users_col().update_one({"_id": member['user_id']}, {"$set": {
            "name": name,
            "phone": phone
        }})

    flash(f"Member details for '{name}' updated successfully.", "success")
    return redirect(url_for('admin_members'))


@app.route('/admin/members/<member_id>/toggle-status', methods=['POST'])
@role_required('admin')
def admin_toggle_member_status(member_id):
    obj_id = to_object_id(member_id)
    member = members_col().find_one({"_id": obj_id})
    if member:
        new_status = 'inactive' if member.get('status') == 'active' else 'active'
        members_col().update_one({"_id": obj_id}, {"$set": {"status": new_status}})
        if member.get('user_id'):
            users_col().update_one({"_id": member['user_id']}, {"$set": {"status": new_status}})
        flash(f"Member status changed to {new_status}.", "info")
    return redirect(url_for('admin_members'))


@app.route('/admin/trainers')
@role_required('admin')
def admin_trainers():
    trainers_list = list(trainers_col().find().sort("created_at", -1))
    return render_template('admin/trainers.html', trainers=trainers_list)


@app.route('/admin/trainers/add', methods=['POST'])
@role_required('admin')
def admin_add_trainer():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', 'trainer123').strip()
    specialization = request.form.get('specialization', '').strip()
    experience_years = int(request.form.get('experience_years', 1))
    availability = request.form.get('availability', 'Full-time')
    bio = request.form.get('bio', '')

    if not name or not email:
        flash("Trainer name and email are required.", "danger")
        return redirect(url_for('admin_trainers'))

    if users_col().find_one({"email": email}):
        flash("Email is already registered.", "danger")
        return redirect(url_for('admin_trainers'))

    user_id = users_col().insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": generate_password_hash(password),
        "role": "trainer",
        "status": "active",
        "created_at": datetime.now()
    }).inserted_id

    trainers_col().insert_one({
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "specialization": specialization,
        "experience_years": experience_years,
        "availability": availability,
        "bio": bio,
        "status": "active",
        "created_at": datetime.now()
    })

    flash(f"Trainer '{name}' added successfully.", "success")
    return redirect(url_for('admin_trainers'))


@app.route('/admin/trainers/<trainer_id>/edit', methods=['POST'])
@role_required('admin')
def admin_edit_trainer(trainer_id):
    obj_id = to_object_id(trainer_id)
    trainer = trainers_col().find_one({"_id": obj_id})
    if not trainer:
        flash("Trainer not found.", "danger")
        return redirect(url_for('admin_trainers'))

    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    specialization = request.form.get('specialization', '').strip()
    experience_years = int(request.form.get('experience_years', 1))
    availability = request.form.get('availability', 'Full-time')
    bio = request.form.get('bio', '')

    trainers_col().update_one({"_id": obj_id}, {"$set": {
        "name": name,
        "phone": phone,
        "specialization": specialization,
        "experience_years": experience_years,
        "availability": availability,
        "bio": bio
    }})

    if trainer.get('user_id'):
        users_col().update_one({"_id": trainer['user_id']}, {"$set": {
            "name": name,
            "phone": phone
        }})

    flash(f"Trainer '{name}' profile updated.", "success")
    return redirect(url_for('admin_trainers'))


@app.route('/admin/trainers/<trainer_id>/toggle-status', methods=['POST'])
@role_required('admin')
def admin_toggle_trainer_status(trainer_id):
    obj_id = to_object_id(trainer_id)
    trainer = trainers_col().find_one({"_id": obj_id})
    if trainer:
        new_status = 'inactive' if trainer.get('status') == 'active' else 'active'
        trainers_col().update_one({"_id": obj_id}, {"$set": {"status": new_status}})
        if trainer.get('user_id'):
            users_col().update_one({"_id": trainer['user_id']}, {"$set": {"status": new_status}})
        flash(f"Trainer status set to {new_status}.", "info")
    return redirect(url_for('admin_trainers'))


@app.route('/admin/plans')
@role_required('admin')
def admin_plans():
    plans_list = list(plans_col().find().sort("duration_days", 1))
    return render_template('admin/plans.html', plans=plans_list)


@app.route('/admin/plans/add', methods=['POST'])
@role_required('admin')
def admin_add_plan():
    plan_name = request.form.get('plan_name', '').strip()
    duration_days = int(request.form.get('duration_days', 30))
    price = float(request.form.get('price', 0))
    description = request.form.get('description', '').strip()

    if not plan_name or price <= 0:
        flash("Valid plan name and price are required.", "danger")
        return redirect(url_for('admin_plans'))

    plans_col().insert_one({
        "plan_name": plan_name,
        "duration_days": duration_days,
        "price": price,
        "description": description,
        "status": "active",
        "created_at": datetime.now()
    })

    flash(f"Plan '{plan_name}' created successfully.", "success")
    return redirect(url_for('admin_plans'))


@app.route('/admin/plans/<plan_id>/edit', methods=['POST'])
@role_required('admin')
def admin_edit_plan(plan_id):
    obj_id = to_object_id(plan_id)
    plans_col().update_one({"_id": obj_id}, {"$set": {
        "plan_name": request.form.get('plan_name', '').strip(),
        "duration_days": int(request.form.get('duration_days', 30)),
        "price": float(request.form.get('price', 0)),
        "description": request.form.get('description', '').strip()
    }})
    flash("Membership plan updated.", "success")
    return redirect(url_for('admin_plans'))


@app.route('/admin/plans/<plan_id>/toggle-status', methods=['POST'])
@role_required('admin')
def admin_toggle_plan_status(plan_id):
    obj_id = to_object_id(plan_id)
    plan = plans_col().find_one({"_id": obj_id})
    if plan:
        new_status = 'inactive' if plan.get('status') == 'active' else 'active'
        plans_col().update_one({"_id": obj_id}, {"$set": {"status": new_status}})
        flash(f"Plan status updated to {new_status}.", "info")
    return redirect(url_for('admin_plans'))


@app.route('/admin/memberships/assign', methods=['GET', 'POST'])
@role_required('admin')
def admin_assign_membership():
    if request.method == 'POST':
        member_id_str = request.form.get('member_id')
        plan_id_str = request.form.get('plan_id')
        payment_method = request.form.get('payment_method', 'Cash')

        member = members_col().find_one({"_id": to_object_id(member_id_str)})
        plan = plans_col().find_one({"_id": to_object_id(plan_id_str)})

        if not member or not plan:
            flash("Please select both a valid member and plan.", "danger")
            return redirect(url_for('admin_assign_membership'))

        # Deactivate any previous active memberships for this member
        memberships_col().update_many(
            {"member_id": member["_id"], "status": "active"},
            {"$set": {"status": "renewed_or_replaced"}}
        )

        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])

        sub_id = memberships_col().insert_one({
            "member_id": member["_id"],
            "user_id": member.get("user_id"),
            "member_name": member.get("name"),
            "plan_id": plan["_id"],
            "plan_name": plan["plan_name"],
            "start_date": start_date,
            "end_date": end_date,
            "price": plan["price"],
            "status": "active",
            "assigned_by": session.get('user_name', 'Admin'),
            "created_at": datetime.now()
        }).inserted_id

        # Record payment transaction
        payments_col().insert_one({
            "member_id": member["_id"],
            "user_id": member.get("user_id"),
            "member_name": member.get("name"),
            "membership_id": sub_id,
            "plan_name": plan["plan_name"],
            "amount": plan["price"],
            "payment_date": start_date,
            "payment_method": payment_method,
            "reference_no": f"PAY-{int(datetime.now().timestamp())}",
            "payment_type": "Recorded / Simulated",
            "status": "completed",
            "notes": f"Plan assignment: {plan['plan_name']}"
        })

        flash(f"Assigned '{plan['plan_name']}' to {member['name']} successfully.", "success")
        return redirect(url_for('admin_members'))

    members_list = list(members_col().find({"status": "active"}).sort("name", 1))
    plans_list = list(plans_col().find({"status": "active"}).sort("duration_days", 1))
    selected_member_id = request.args.get('member_id', '')

    return render_template('admin/assign_plan.html',
                           members=members_list,
                           plans=plans_list,
                           selected_member_id=selected_member_id)


@app.route('/admin/payments', methods=['GET', 'POST'])
@role_required('admin')
def admin_payments():
    if request.method == 'POST':
        member_id_str = request.form.get('member_id')
        amount = float(request.form.get('amount', 0))
        method = request.form.get('payment_method', 'Cash')
        notes = request.form.get('notes', 'Manual recorded payment')

        member = members_col().find_one({"_id": to_object_id(member_id_str)})
        if not member or amount <= 0:
            flash("Please provide a valid member and amount.", "danger")
            return redirect(url_for('admin_payments'))

        payments_col().insert_one({
            "member_id": member["_id"],
            "user_id": member.get("user_id"),
            "member_name": member.get("name"),
            "plan_name": "Direct Payment / Dues",
            "amount": amount,
            "payment_date": datetime.now(),
            "payment_method": method,
            "reference_no": f"PAY-MAN-{int(datetime.now().timestamp())}",
            "payment_type": "Recorded / Manual",
            "status": "completed",
            "notes": notes
        })

        flash(f"Payment of ₹{amount:,.2f} recorded for {member['name']}.", "success")
        return redirect(url_for('admin_payments'))

    payments_list = list(payments_col().find().sort("payment_date", -1))
    members_list = list(members_col().find({"status": "active"}).sort("name", 1))
    total_amount = sum(float(p.get('amount', 0)) for p in payments_list)

    return render_template('admin/payments.html',
                           payments=payments_list,
                           members=members_list,
                           total_amount=total_amount)


@app.route('/admin/attendance', methods=['GET', 'POST'])
@role_required('admin')
def admin_attendance():
    if request.method == 'POST':
        member_id_str = request.form.get('member_id')
        att_date = request.form.get('date', datetime.now().strftime("%Y-%m-%d"))
        check_in = request.form.get('check_in_time', datetime.now().strftime("%H:%M:%S"))
        check_out = request.form.get('check_out_time', '')

        member = members_col().find_one({"_id": to_object_id(member_id_str)})
        if not member:
            flash("Select a valid member for attendance.", "danger")
            return redirect(url_for('admin_attendance'))

        attendance_col().insert_one({
            "member_id": member["_id"],
            "user_id": member.get("user_id"),
            "member_name": member.get("name"),
            "date": att_date,
            "check_in_time": check_in,
            "check_out_time": check_out,
            "status": "Present",
            "created_at": datetime.now()
        })

        flash(f"Attendance recorded for {member['name']}.", "success")
        return redirect(url_for('admin_attendance', date=att_date))

    filter_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    records = list(attendance_col().find({"date": filter_date}).sort("check_in_time", -1))
    members_list = list(members_col().find({"status": "active"}).sort("name", 1))

    return render_template('admin/attendance.html',
                           records=records,
                           members=members_list,
                           filter_date=filter_date)


@app.route('/admin/workouts', methods=['GET'])
@role_required('admin')
def admin_workouts():
    workouts = list(workout_plans_col().find().sort("created_at", -1))
    members = list(members_col().find({"status": "active"}).sort("name", 1))
    trainers = list(trainers_col().find({"status": "active"}).sort("name", 1))
    assigned = list(member_workouts_col().find().sort("assigned_date", -1))

    return render_template('admin/workouts.html',
                           workouts=workouts,
                           members=members,
                           trainers=trainers,
                           assigned=assigned)


@app.route('/admin/workouts/add', methods=['POST'])
@role_required('admin')
def admin_add_workout():
    name = request.form.get('name', '').strip()
    difficulty = request.form.get('difficulty', 'Beginner')
    description = request.form.get('description', '').strip()

    # Collect exercises from dynamic form fields
    ex_names = request.form.getlist('exercise_name[]')
    ex_sets = request.form.getlist('exercise_sets[]')
    ex_reps = request.form.getlist('exercise_reps[]')
    ex_notes = request.form.getlist('exercise_notes[]')

    exercises = []
    for i in range(len(ex_names)):
        if ex_names[i].strip():
            exercises.append({
                "name": ex_names[i].strip(),
                "sets": ex_sets[i].strip() if i < len(ex_sets) else "3",
                "reps": ex_reps[i].strip() if i < len(ex_reps) else "10",
                "instructions": ex_notes[i].strip() if i < len(ex_notes) else ""
            })

    if not name or not exercises:
        flash("Workout plan requires a name and at least one exercise.", "danger")
        return redirect(url_for('admin_workouts'))

    workout_plans_col().insert_one({
        "name": name,
        "difficulty": difficulty,
        "description": description,
        "created_by": session.get('user_name', 'Admin'),
        "exercises": exercises,
        "created_at": datetime.now()
    })

    flash(f"Workout plan '{name}' created with {len(exercises)} exercises.", "success")
    return redirect(url_for('admin_workouts'))


@app.route('/admin/workouts/assign', methods=['POST'])
@role_required('admin')
def admin_assign_workout():
    member_id_str = request.form.get('member_id')
    workout_id_str = request.form.get('workout_id')
    trainer_id_str = request.form.get('trainer_id')
    notes = request.form.get('notes', '')

    member = members_col().find_one({"_id": to_object_id(member_id_str)})
    workout = workout_plans_col().find_one({"_id": to_object_id(workout_id_str)})
    trainer = trainers_col().find_one({"_id": to_object_id(trainer_id_str)}) if trainer_id_str else None

    if not member or not workout:
        flash("Select a valid member and workout plan.", "danger")
        return redirect(url_for('admin_workouts'))

    # Replace any existing active assignment for this member
    member_workouts_col().delete_many({"member_id": member["_id"]})

    member_workouts_col().insert_one({
        "member_id": member["_id"],
        "member_name": member.get("name"),
        "user_id": member.get("user_id"),
        "workout_plan_id": workout["_id"],
        "workout_name": workout.get("name"),
        "difficulty": workout.get("difficulty"),
        "exercises": workout.get("exercises", []),
        "trainer_name": trainer.get("name") if trainer else "Gym Staff",
        "trainer_id": trainer["_id"] if trainer else None,
        "assigned_date": datetime.now(),
        "notes": notes
    })

    flash(f"Assigned '{workout['name']}' to {member['name']}.", "success")
    return redirect(url_for('admin_workouts'))


@app.route('/admin/reports')
@role_required('admin')
def admin_reports():
    # 1. Total revenue & breakdown
    payments = list(payments_col().find())
    total_revenue = sum(float(p.get('amount', 0)) for p in payments)

    # 2. Membership status counts
    now = datetime.now()
    active_subs = memberships_col().count_documents({"status": "active", "end_date": {"$gte": now}})
    expired_subs = memberships_col().count_documents({"$or": [{"status": "expired"}, {"end_date": {"$lt": now}}]})
    total_members = members_col().count_documents({})

    # 3. Attendance stats - last 7 days count
    dates_labels = []
    attendance_counts = []
    for i in range(6, -1, -1):
        d_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        cnt = attendance_col().count_documents({"date": d_str})
        dates_labels.append(d_str)
        attendance_counts.append(cnt)

    # 4. Plan popularity breakdown
    plans = list(plans_col().find())
    plan_stats = []
    for p in plans:
        sold_count = memberships_col().count_documents({"plan_name": p["plan_name"]})
        plan_revenue = sum(float(pay.get('amount', 0)) for pay in payments_col().find({"plan_name": p["plan_name"]}))
        plan_stats.append({
            "name": p["plan_name"],
            "sold_count": sold_count,
            "revenue": plan_revenue
        })

    report_data = {
        "total_revenue": total_revenue,
        "active_subs": active_subs,
        "expired_subs": expired_subs,
        "total_members": total_members,
        "dates_labels": dates_labels,
        "attendance_counts": attendance_counts,
        "plan_stats": plan_stats
    }

    return render_template('admin/reports.html', report=report_data)


# ======================================================
# MEMBER ROUTES
# ======================================================

@app.route('/member/dashboard')
@role_required('member')
def member_dashboard():
    user_id = to_object_id(session['user_id'])
    member = members_col().find_one({"user_id": user_id})
    if not member:
        flash("Member profile not found.", "danger")
        return redirect(url_for('logout'))

    # Active membership
    now = datetime.now()
    active_sub = memberships_col().find_one({
        "member_id": member["_id"],
        "status": "active",
        "end_date": {"$gte": now}
    })

    days_remaining = None
    if active_sub:
        delta = active_sub['end_date'] - now
        days_remaining = max(0, delta.days)

    # Assigned workout
    assigned_workout = member_workouts_col().find_one({"member_id": member["_id"]})

    # Attendance summary
    recent_attendance = list(attendance_col().find({"member_id": member["_id"]}).sort("date", -1).limit(5))
    total_checkins = attendance_col().count_documents({"member_id": member["_id"]})

    # Recent payments
    recent_payments = list(payments_col().find({"member_id": member["_id"]}).sort("payment_date", -1).limit(3))

    return render_template('member/dashboard.html',
                           member=member,
                           active_sub=active_sub,
                           days_remaining=days_remaining,
                           assigned_workout=assigned_workout,
                           recent_attendance=recent_attendance,
                           total_checkins=total_checkins,
                           recent_payments=recent_payments)


@app.route('/member/profile', methods=['GET', 'POST'])
@role_required('member')
def member_profile():
    user_id = to_object_id(session['user_id'])
    member = members_col().find_one({"user_id": user_id})

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        health_notes = request.form.get('health_notes', '').strip()
        gender = request.form.get('gender', member.get('gender', 'Other'))

        members_col().update_one({"user_id": user_id}, {"$set": {
            "phone": phone,
            "emergency_contact": emergency_contact,
            "health_notes": health_notes,
            "gender": gender
        }})

        users_col().update_one({"_id": user_id}, {"$set": {"phone": phone}})
        flash("Profile updated successfully.", "success")
        return redirect(url_for('member_profile'))

    return render_template('member/profile.html', member=member)


@app.route('/member/attendance')
@role_required('member')
def member_attendance():
    user_id = to_object_id(session['user_id'])
    member = members_col().find_one({"user_id": user_id})
    records = list(attendance_col().find({"member_id": member["_id"]}).sort("date", -1))
    return render_template('member/attendance.html', records=records, member=member)


@app.route('/member/payments')
@role_required('member')
def member_payments():
    user_id = to_object_id(session['user_id'])
    member = members_col().find_one({"user_id": user_id})
    payments = list(payments_col().find({"member_id": member["_id"]}).sort("payment_date", -1))
    return render_template('member/payments.html', payments=payments, member=member)


@app.route('/member/workouts')
@role_required('member')
def member_workouts():
    user_id = to_object_id(session['user_id'])
    member = members_col().find_one({"user_id": user_id})
    assigned = member_workouts_col().find_one({"member_id": member["_id"]})
    return render_template('member/workouts.html', assigned=assigned, member=member)


# ======================================================
# TRAINER ROUTES
# ======================================================

@app.route('/trainer/dashboard')
@role_required('trainer')
def trainer_dashboard():
    user_id = to_object_id(session['user_id'])
    trainer = trainers_col().find_one({"user_id": user_id})

    # Find members who have workouts assigned by this trainer or all active members
    assigned_members = list(member_workouts_col().find({"trainer_id": trainer["_id"] if trainer else None}))
    total_trainees = len(assigned_members)
    available_workouts = workout_plans_col().count_documents({})

    return render_template('trainer/dashboard.html',
                           trainer=trainer,
                           total_trainees=total_trainees,
                           available_workouts=available_workouts,
                           assigned_members=assigned_members)


@app.route('/trainer/trainees')
@role_required('trainer')
def trainer_trainees():
    user_id = to_object_id(session['user_id'])
    trainer = trainers_col().find_one({"user_id": user_id})

    all_members = list(members_col().find({"status": "active"}).sort("name", 1))
    workouts = list(workout_plans_col().find().sort("name", 1))

    # Attach current workout plan for each member
    for m in all_members:
        mw = member_workouts_col().find_one({"member_id": m["_id"]})
        m['current_workout'] = mw.get('workout_name') if mw else "None"
        m['assigned_trainer'] = mw.get('trainer_name') if mw else "Unassigned"

    return render_template('trainer/trainees.html',
                           trainer=trainer,
                           members=all_members,
                           workouts=workouts)


@app.route('/trainer/workouts', methods=['GET', 'POST'])
@role_required('trainer')
def trainer_workouts():
    user_id = to_object_id(session['user_id'])
    trainer = trainers_col().find_one({"user_id": user_id})

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        difficulty = request.form.get('difficulty', 'Beginner')
        description = request.form.get('description', '').strip()

        ex_names = request.form.getlist('exercise_name[]')
        ex_sets = request.form.getlist('exercise_sets[]')
        ex_reps = request.form.getlist('exercise_reps[]')
        ex_notes = request.form.getlist('exercise_notes[]')

        exercises = []
        for i in range(len(ex_names)):
            if ex_names[i].strip():
                exercises.append({
                    "name": ex_names[i].strip(),
                    "sets": ex_sets[i].strip() if i < len(ex_sets) else "3",
                    "reps": ex_reps[i].strip() if i < len(ex_reps) else "10",
                    "instructions": ex_notes[i].strip() if i < len(ex_notes) else ""
                })

        if not name or not exercises:
            flash("Plan name and at least one exercise are required.", "danger")
            return redirect(url_for('trainer_workouts'))

        workout_plans_col().insert_one({
            "name": name,
            "difficulty": difficulty,
            "description": description,
            "created_by": trainer.get('name') if trainer else "Trainer",
            "exercises": exercises,
            "created_at": datetime.now()
        })

        flash(f"Workout routine '{name}' saved successfully.", "success")
        return redirect(url_for('trainer_workouts'))

    workouts = list(workout_plans_col().find().sort("created_at", -1))
    members = list(members_col().find({"status": "active"}).sort("name", 1))

    return render_template('trainer/workouts.html',
                           workouts=workouts,
                           members=members,
                           trainer=trainer)


@app.route('/trainer/workouts/assign', methods=['POST'])
@role_required('trainer')
def trainer_assign_workout():
    user_id = to_object_id(session['user_id'])
    trainer = trainers_col().find_one({"user_id": user_id})

    member_id_str = request.form.get('member_id')
    workout_id_str = request.form.get('workout_id')
    notes = request.form.get('notes', '')

    member = members_col().find_one({"_id": to_object_id(member_id_str)})
    workout = workout_plans_col().find_one({"_id": to_object_id(workout_id_str)})

    if not member or not workout:
        flash("Please choose a valid member and workout routine.", "danger")
        return redirect(url_for('trainer_trainees'))

    member_workouts_col().delete_many({"member_id": member["_id"]})

    member_workouts_col().insert_one({
        "member_id": member["_id"],
        "member_name": member.get("name"),
        "user_id": member.get("user_id"),
        "workout_plan_id": workout["_id"],
        "workout_name": workout.get("name"),
        "difficulty": workout.get("difficulty"),
        "exercises": workout.get("exercises", []),
        "trainer_name": trainer.get("name") if trainer else "Trainer",
        "trainer_id": trainer["_id"] if trainer else None,
        "assigned_date": datetime.now(),
        "notes": notes
    })

    flash(f"Workout routine assigned to {member['name']}.", "success")
    return redirect(url_for('trainer_trainees'))


# ======================================================
# ERROR PAGES
# ======================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html', message="Internal Server Error"), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
