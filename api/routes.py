from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from bson import ObjectId
from . import api_bp
from db import (
    users_col, members_col, plans_col, memberships_col,
    attendance_col, to_object_id, serialize_doc, serialize_list
)

def get_current_api_user():
    """Helper to check current user from session or header."""
    user_id = session.get('user_id')
    if user_id:
        return users_col().find_one({"_id": to_object_id(user_id)})
    return None

# ==========================================
# 1. AUTHENTICATION ENDPOINTS
# ==========================================

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    """
    POST /api/auth/register
    Body: { "name": "...", "email": "...", "phone": "...", "password": "...", "gender": "...", "dob": "..." }
    """
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    gender = data.get('gender', 'Other')
    dob = data.get('dob', '')

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "error": "Name, email, and password are required fields."
        }), 400

    if users_col().find_one({"email": email}):
        return jsonify({
            "success": False,
            "error": f"An account with email '{email}' already exists."
        }), 409

    # Create user
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

    # Create member record
    member_doc = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "emergency_contact": data.get("emergency_contact", ""),
        "health_notes": data.get("health_notes", ""),
        "status": "active",
        "created_at": datetime.now()
    }
    member_id = members_col().insert_one(member_doc).inserted_id

    # Set session
    session['user_id'] = str(user_id)
    session['role'] = 'member'
    session['user_name'] = name

    return jsonify({
        "success": True,
        "message": "Member registered successfully.",
        "data": {
            "user_id": str(user_id),
            "member_id": str(member_id),
            "name": name,
            "email": email,
            "role": "member"
        }
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """
    POST /api/auth/login
    Body: { "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email and password are required."
        }), 400

    user = users_col().find_one({"email": email})
    if not user or not check_password_hash(user.get('password_hash', ''), password):
        return jsonify({
            "success": False,
            "error": "Invalid email or password."
        }), 401

    if user.get('status') == 'inactive':
        return jsonify({
            "success": False,
            "error": "Account is deactivated. Contact gym administration."
        }), 403

    # Store in session
    session['user_id'] = str(user['_id'])
    session['role'] = user.get('role')
    session['user_name'] = user.get('name')

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "data": {
            "user_id": str(user['_id']),
            "name": user.get('name'),
            "email": user.get('email'),
            "role": user.get('role')
        }
    }), 200


@api_bp.route('/auth/logout', methods=['POST'])
def api_logout():
    """POST /api/auth/logout"""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


# ==========================================
# 2. MEMBERS ENDPOINTS
# ==========================================

@api_bp.route('/members', methods=['GET'])
def api_get_members():
    """
    GET /api/members
    Query Params: ?search=...&status=...
    """
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    query = {}
    if status:
        query['status'] = status
    if search:
        query['$or'] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]

    members_cursor = members_col().find(query).sort("created_at", -1)
    members_list = serialize_list(list(members_cursor))

    return jsonify({
        "success": True,
        "count": len(members_list),
        "data": members_list
    }), 200


@api_bp.route('/members/<member_id>', methods=['GET'])
def api_get_member_by_id(member_id):
    """GET /api/members/<id>"""
    obj_id = to_object_id(member_id)
    if not obj_id:
        return jsonify({"success": False, "error": "Invalid member ID format."}), 400

    member = members_col().find_one({"_id": obj_id})
    if not member:
        return jsonify({"success": False, "error": "Member not found."}), 404

    # Attach current active membership if any
    membership = memberships_col().find_one({
        "member_id": obj_id,
        "status": "active"
    })

    serialized = serialize_doc(member)
    serialized['active_membership'] = serialize_doc(membership) if membership else None

    return jsonify({
        "success": True,
        "data": serialized
    }), 200


@api_bp.route('/members', methods=['POST'])
def api_create_member():
    """
    POST /api/members (Admin action)
    Body: { "name": "...", "email": "...", "phone": "...", "password": "...", "gender": "...", "dob": "..." }
    """
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', 'gym123').strip()

    if not name or not email:
        return jsonify({"success": False, "error": "Name and email are required."}), 400

    if users_col().find_one({"email": email}):
        return jsonify({"success": False, "error": "Email is already registered."}), 409

    # Create User
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

    # Create Member
    member_doc = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "gender": data.get("gender", "Other"),
        "dob": data.get("dob", ""),
        "emergency_contact": data.get("emergency_contact", ""),
        "health_notes": data.get("health_notes", ""),
        "status": "active",
        "created_at": datetime.now()
    }
    member_id = members_col().insert_one(member_doc).inserted_id

    return jsonify({
        "success": True,
        "message": "Member created successfully.",
        "data": {
            "member_id": str(member_id),
            "user_id": str(user_id),
            "name": name,
            "email": email
        }
    }), 201


@api_bp.route('/members/<member_id>', methods=['PUT'])
def api_update_member(member_id):
    """PUT /api/members/<id>"""
    obj_id = to_object_id(member_id)
    if not obj_id:
        return jsonify({"success": False, "error": "Invalid member ID format."}), 400

    member = members_col().find_one({"_id": obj_id})
    if not member:
        return jsonify({"success": False, "error": "Member not found."}), 404

    data = request.get_json(silent=True) or {}
    update_fields = {}
    for key in ['name', 'phone', 'gender', 'dob', 'emergency_contact', 'health_notes', 'status']:
        if key in data:
            update_fields[key] = data[key]

    if update_fields:
        members_col().update_one({"_id": obj_id}, {"$set": update_fields})
        # If name or phone updated, sync with users collection
        user_sync = {}
        if 'name' in update_fields:
            user_sync['name'] = update_fields['name']
        if 'phone' in update_fields:
            user_sync['phone'] = update_fields['phone']
        if 'status' in update_fields:
            user_sync['status'] = update_fields['status']
        if user_sync and member.get('user_id'):
            users_col().update_one({"_id": member['user_id']}, {"$set": user_sync})

    updated_member = members_col().find_one({"_id": obj_id})
    return jsonify({
        "success": True,
        "message": "Member updated successfully.",
        "data": serialize_doc(updated_member)
    }), 200


# ==========================================
# 3. MEMBERSHIPS ENDPOINTS
# ==========================================

@api_bp.route('/memberships', methods=['GET'])
def api_get_memberships():
    """GET /api/memberships - returns active and historic memberships"""
    status = request.args.get('status', '').strip()
    query = {}
    if status:
        query['status'] = status

    records = list(memberships_col().find(query).sort("created_at", -1))
    return jsonify({
        "success": True,
        "count": len(records),
        "data": serialize_list(records)
    }), 200


# ==========================================
# 4. ATTENDANCE ENDPOINTS
# ==========================================

@api_bp.route('/attendance', methods=['GET'])
def api_get_attendance():
    """GET /api/attendance - list attendance logs"""
    date_filter = request.args.get('date', '').strip()
    member_id = request.args.get('member_id', '').strip()

    query = {}
    if date_filter:
        query['date'] = date_filter
    if member_id:
        obj_m_id = to_object_id(member_id)
        if obj_m_id:
            query['member_id'] = obj_m_id

    records = list(attendance_col().find(query).sort([("date", -1), ("check_in_time", -1)]))
    return jsonify({
        "success": True,
        "count": len(records),
        "data": serialize_list(records)
    }), 200


@api_bp.route('/attendance', methods=['POST'])
def api_log_attendance():
    """
    POST /api/attendance
    Body: { "member_id": "...", "date": "YYYY-MM-DD", "check_in_time": "HH:MM", "check_out_time": "HH:MM" }
    """
    data = request.get_json(silent=True) or {}
    member_id_str = data.get('member_id', '').strip()
    m_obj_id = to_object_id(member_id_str)

    if not m_obj_id:
        return jsonify({"success": False, "error": "Valid member_id is required."}), 400

    member = members_col().find_one({"_id": m_obj_id})
    if not member:
        return jsonify({"success": False, "error": "Member not found."}), 404

    att_date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
    check_in = data.get('check_in_time', datetime.now().strftime("%H:%M:%S"))
    check_out = data.get('check_out_time', '')

    attendance_doc = {
        "member_id": m_obj_id,
        "member_name": member.get("name", "Unknown"),
        "user_id": member.get("user_id"),
        "date": att_date,
        "check_in_time": check_in,
        "check_out_time": check_out,
        "status": "Present",
        "created_at": datetime.now()
    }
    att_id = attendance_col().insert_one(attendance_doc).inserted_id

    return jsonify({
        "success": True,
        "message": f"Attendance logged for {member.get('name')}.",
        "data": serialize_doc(attendance_doc)
    }), 201
