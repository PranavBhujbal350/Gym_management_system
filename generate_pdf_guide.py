"""
Script to generate a comprehensive, beginner-friendly Viva and Interview Guide PDF
for the Gym Management System project.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds Page X of Y and running footer to every page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header line (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "FitPulse Gym Management System — Complete Viva & Interview Guide")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 747, letter[0] - 54, 747)
        
        # Footer line
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        
        # Footer text
        self.drawString(54, 32, "Confidential — Prepared for College Project Defense & Technical Interview")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        self.restoreState()


def build_pdf(filename="Gym_Management_System_Viva_Interview_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        spaceAfter=3
    )

    q_style = ParagraphStyle(
        'Question_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        'Answer_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=12,
        spaceAfter=6
    )

    code_pill = ParagraphStyle(
        'CodePill',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        spaceAfter=4
    )

    story = []

    # ==============================================================
    # COVER / HEADER
    # ==============================================================
    story.append(Paragraph("FitPulse: Gym Management System", title_style))
    story.append(Paragraph("Complete Technical Project Defense & Viva Interview Master Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))

    # Meta banner
    summary_data = [
        [
            Paragraph("<b>Candidate:</b> Pranav Bhujbal<br/><b>Technology Stack:</b> Python Flask, MongoDB, Jinja2, Bootstrap 5", body_style),
            Paragraph("<b>Project Role:</b> Full Stack Developer<br/><b>Version Control:</b> Git & GitHub", body_style)
        ]
    ]
    t_summary = Table(summary_data, colWidths=[250, 254])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # ==============================================================
    # SECTION 1: 30-SECOND ELEVATOR PITCH
    # ==============================================================
    story.append(Paragraph("1. How to Introduce the Project (30-Second Elevator Pitch)", h1_style))
    story.append(Paragraph(
        "When the interviewer asks: <i>'Can you introduce your project?'</i>, do NOT panic. Say this confidently:",
        body_style
    ))
    
    pitch_text = (
        "<i>\"FitPulse is a full-stack Gym Management Web Application built with Python Flask, MongoDB, and Bootstrap 5. "
        "It solves the real-world operational challenges of a fitness facility by replacing manual paperwork and spreadsheets with an automated, role-based platform. "
        "It features three distinct portals: an <b>Admin Portal</b> for business metrics, plan renewals, manual/simulated payments, and attendance; a <b>Trainer Portal</b> for crafting workout routines and coaching athletes; and a <b>Member Portal</b> where gym-goers track their subscription validity, assigned workout routines, and check-in history. "
        "It also exposes a testable JSON REST API verified via Postman.\"</i>"
    )
    t_pitch = Table([[Paragraph(pitch_text, body_style)]], colWidths=[504])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_pitch)
    story.append(Spacer(1, 15))

    # ==============================================================
    # SECTION 2: SYSTEM ARCHITECTURE EXPLAINED FOR BEGINNERS
    # ==============================================================
    story.append(Paragraph("2. System Architecture Explained from Scratch", h1_style))
    story.append(Paragraph(
        "A web application is divided into three tiers: <b>Frontend</b> (Client), <b>Backend</b> (Server), and <b>Database</b> (Data Storage). Here is how they interact:",
        body_style
    ))

    arch_rows = [
        [Paragraph("<b>Tier</b>", body_style), Paragraph("<b>Technology Used</b>", body_style), Paragraph("<b>What it Does (Beginner Friendly)</b>", body_style)],
        [
            Paragraph("<b>Frontend (Presentation Layer)</b>", body_style),
            Paragraph("HTML5, CSS3, JavaScript, Bootstrap 5, Jinja2", body_style),
            Paragraph("What the user sees in their browser: buttons, input forms, tables, and responsive mobile sidebar. Jinja2 injects dynamic data into HTML before rendering.", body_style)
        ],
        [
            Paragraph("<b>Backend (Application Layer)</b>", body_style),
            Paragraph("Python 3, Flask Framework", body_style),
            Paragraph("The brains of the project. It listens for incoming HTTP requests (like login or add member), validates input, checks security permissions, and decides what to do.", body_style)
        ],
        [
            Paragraph("<b>Database (Data Layer)</b>", body_style),
            Paragraph("MongoDB (NoSQL Document Store)", body_style),
            Paragraph("The permanent filing cabinet. Stores user logins, workout lists, attendance dates, and payments as JSON-like BSON documents in collections.", body_style)
        ],
        [
            Paragraph("<b>Database Connector</b>", body_style),
            Paragraph("PyMongo Driver", body_style),
            Paragraph("The Python bridge that sends MongoDB queries from Flask to the database server.", body_style)
        ],
        [
            Paragraph("<b>API Testing Tool</b>", body_style),
            Paragraph("Postman", body_style),
            Paragraph("Allows sending raw HTTP requests (GET, POST, PUT) to test endpoints without using the browser UI.", body_style)
        ]
    ]
    t_arch = Table(arch_rows, colWidths=[110, 130, 264])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 15))

    # ==============================================================
    # SECTION 3: WHAT IS GIT AND GITHUB?
    # ==============================================================
    story.append(Paragraph("3. Everything About Git & GitHub (Explained for Viva)", h1_style))
    story.append(Paragraph(
        "Interviewers love asking about Git and GitHub. Here is the exact difference and breakdown:",
        body_style
    ))
    story.append(Paragraph("<b>• Git vs GitHub:</b>", body_style))
    story.append(Paragraph("<b>Git</b> is a local command-line software running on your laptop. It acts like a time-machine that tracks every change made to your source code files over time.", bullet_style))
    story.append(Paragraph("<b>GitHub</b> is a cloud website (hosted by Microsoft) where developers upload and store copies of their Git repositories to back up code and collaborate with others.", bullet_style))

    story.append(Paragraph("<b>• Key Git Commands Explained:</b>", body_style))
    story.append(Paragraph("<b>1. git init:</b> Turns the current folder into a new Git repository by creating a hidden <code>.git/</code> tracking folder.", bullet_style))
    story.append(Paragraph("<b>2. git add .:</b> Stages all modified and new files, telling Git: <i>'Prepare these files to be recorded'</i>.", bullet_style))
    story.append(Paragraph("<b>3. git commit -m \"message\":</b> Takes a permanent snapshot of the staged files with an explanatory note.", bullet_style))
    story.append(Paragraph("<b>4. git branch -M main:</b> Renames the default branch to 'main'.", bullet_style))
    story.append(Paragraph("<b>5. git remote add origin &lt;URL&gt;:</b> Connects your local folder to your remote repository on GitHub.", bullet_style))
    story.append(Paragraph("<b>6. git push -u origin main:</b> Uploads your committed files from your laptop up to GitHub.", bullet_style))

    story.append(Paragraph("<b>• What is .gitignore and why is it critical?</b>", body_style))
    story.append(Paragraph(
        "A <code>.gitignore</code> file tells Git which files it must NEVER upload to GitHub. "
        "In our project, we ignore <code>.env</code> (because it contains database passwords and secret session keys), <code>__pycache__/</code> (temporary compiled Python files), and <code>venv/</code> (huge virtual environment libraries). Committing passwords to a public GitHub repository is a major security vulnerability!",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==============================================================
    # SECTION 4: FILE-BY-FILE CODE EXPLANATION
    # ==============================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Complete File-by-File Breakdown: What Code is in Which File?", h1_style))
    story.append(Paragraph(
        "If the interviewer opens your VS Code and points to any file, here is exactly what each file contains and why it exists:",
        body_style
    ))

    files_data = [
        [Paragraph("<b>File Path</b>", body_style), Paragraph("<b>Primary Purpose & What Code is Inside</b>", body_style)],
        [
            Paragraph("<b>app.py</b><br/><i>(Main Application)</i>", body_style),
            Paragraph("The core controller of the entire web application.<br/>"
                      "• Initializes the Flask application with <code>app = Flask(__name__)</code>.<br/>"
                      "• Defines custom Jinja filters: <code>currency</code> (adds ₹ symbol) and <code>format_date</code>.<br/>"
                      "• Implements authentication decorators: <code>@login_required</code> and <code>@role_required('admin')</code>.<br/>"
                      "• Contains all route handlers: <code>/login</code>, <code>/register</code>, <code>/logout</code>, <code>/admin/dashboard</code>, <code>/admin/members</code>, <code>/admin/payments</code>, <code>/member/dashboard</code>, <code>/trainer/workouts</code>, etc.<br/>"
                      "• Handles form submissions, password verification, database queries, and template rendering.", body_style)
        ],
        [
            Paragraph("<b>config.py</b><br/><i>(Configuration)</i>", body_style),
            Paragraph("Manages app settings and environment variables.<br/>"
                      "• Calls <code>load_dotenv()</code> to securely read the <code>.env</code> file.<br/>"
                      "• Defines the <code>Config</code> class holding <code>SECRET_KEY</code>, <code>MONGO_URI</code>, <code>PORT</code>, and <code>FLASK_DEBUG</code>.<br/>"
                      "• Prevents hardcoding database URLs or passwords inside Python code.", body_style)
        ],
        [
            Paragraph("<b>db.py</b><br/><i>(Database Layer)</i>", body_style),
            Paragraph("The centralized MongoDB connection and helper module.<br/>"
                      "• Uses a <b>Singleton pattern</b> (<code>get_client()</code> and <code>get_db()</code>) so the app reuses a single connection pool instead of opening a new socket on every request.<br/>"
                      "• Provides collection shortcuts: <code>users_col()</code>, <code>members_col()</code>, <code>plans_col()</code>, <code>payments_col()</code>, <code>attendance_col()</code>, etc.<br/>"
                      "• Provides BSON conversion helpers: <code>to_object_id()</code> to convert strings into MongoDB <code>ObjectId</code> and <code>serialize_doc()</code> to convert ObjectIds and datetimes into strings so JSON and Jinja can handle them.", body_style)
        ],
        [
            Paragraph("<b>init_db.py</b><br/><i>(Database Seeder)</i>", body_style),
            Paragraph("Database initialization and indexing script. Run once with <code>python init_db.py</code>.<br/>"
                      "• Tests connection to MongoDB.<br/>"
                      "• Creates unique indexes: <code>users.email</code> (prevents duplicate emails), <code>members.user_id</code>.<br/>"
                      "• Automatically seeds initial demo accounts: Admin (<code>admin@gym.com</code>), Coach (<code>trainer@gym.com</code>), Member (<code>member@gym.com</code>) with hashed passwords.<br/>"
                      "• Seeds 3 membership plans, 2 workout plans, sample attendance, and payment records.", body_style)
        ],
        [
            Paragraph("<b>requirements.txt</b><br/><i>(Dependencies)</i>", body_style),
            Paragraph("List of all third-party Python packages required to run the project: <code>Flask</code>, <code>pymongo</code>, <code>python-dotenv</code>, <code>Werkzeug</code>, <code>dnspython</code>, and <code>reportlab</code>.", body_style)
        ],
        [
            Paragraph("<b>.env / .env.example</b><br/><i>(Env Variables)</i>", body_style),
            Paragraph("<code>.env</code> stores local connection settings (<code>MONGO_URI</code>, <code>SECRET_KEY</code>).<br/>"
                      "<code>.env.example</code> is a blank template safe to commit to GitHub so other developers know which keys to fill in.", body_style)
        ],
        [
            Paragraph("<b>api/__init__.py &<br/>api/routes.py</b><br/><i>(REST API)</i>", body_style),
            Paragraph("Dedicated JSON REST API blueprint registered under prefix <code>/api</code>.<br/>"
                      "• Contains endpoints: <code>POST /api/auth/login</code>, <code>POST /api/auth/register</code>, <code>GET /api/members</code>, <code>POST /api/members</code>, <code>PUT /api/members/&lt;id&gt;</code>, <code>GET /api/attendance</code>.<br/>"
                      "• Returns structured JSON responses with HTTP status codes (200, 201, 400, 404, 409). Tested via Postman.", body_style)
        ],
        [
            Paragraph("<b>static/css/style.css &<br/>static/js/main.js</b><br/><i>(Assets)</i>", body_style),
            Paragraph("<code>style.css</code> defines the modern dark-navy sidebar, responsive cards, status badge pills (green for active, red for expired), and custom typography.<br/>"
                      "<code>main.js</code> handles mobile sidebar toggling, 1-click viva demo credentials autofill, and dynamic exercise row addition in the workout builder.", body_style)
        ],
        [
            Paragraph("<b>templates/base.html</b><br/><i>(Master Layout)</i>", body_style),
            Paragraph("The parent template extended by all other pages (Jinja2 inheritance).<br/>"
                      "• Imports Bootstrap 5 and FontAwesome 6 icons.<br/>"
                      "• Contains the responsive navigation sidebar that adapts according to <code>session['role']</code> (shows Admin links to admin, Coach links to coach, Member links to member).<br/>"
                      "• Contains topbar with profile dropdown and flash alert messaging block.", body_style)
        ]
    ]

    t_files = Table(files_data, colWidths=[130, 374])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_files)
    story.append(Spacer(1, 15))

    # ==============================================================
    # SECTION 5: TEMPLATES FOLDER EXPLAINED
    # ==============================================================
    story.append(Paragraph("Template Subfolders Breakdown:", h2_style))
    story.append(Paragraph("• <b>Public Pages:</b> <code>index.html</code> (landing page with pricing cards), <code>login.html</code> (login with 1-click test pills), <code>register.html</code> (member signup), <code>403.html</code> (Forbidden), <code>404.html</code> (Not Found).", bullet_style))
    story.append(Paragraph("• <b>templates/admin/ (9 views):</b> <code>dashboard.html</code> (KPI cards & revenue), <code>members.html</code> (member list, add/edit modals), <code>trainers.html</code> (coach roster), <code>plans.html</code> (pricing cards), <code>assign_plan.html</code> (assign plan with auto-calculated duration), <code>payments.html</code> (payment ledger), <code>attendance.html</code> (check-in registry), <code>workouts.html</code> (routine builder), <code>reports.html</code> (revenue & attendance charts).", bullet_style))
    story.append(Paragraph("• <b>templates/member/ (5 views):</b> <code>dashboard.html</code> (active plan & countdown badge), <code>profile.html</code> (personal contact & health notes), <code>attendance.html</code> (check-in history), <code>payments.html</code> (receipts), <code>workouts.html</code> (exercise checklist with sets/reps).", bullet_style))
    story.append(Paragraph("• <b>templates/trainer/ (3 views):</b> <code>dashboard.html</code> (coach metrics & daily schedule), <code>trainees.html</code> (assigned athletes list), <code>workouts.html</code> (custom routine creator).", bullet_style))

    # ==============================================================
    # SECTION 6: CORE CONCEPTS & HOW IT WORKS UNDER THE HOOD
    # ==============================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Core Technical Concepts (How it Works Under the Hood)", h1_style))
    story.append(Paragraph(
        "These are fundamental web concepts the examiner will probe you on:",
        body_style
    ))

    # Concept 1
    story.append(Paragraph("A. How Session Authentication Works:", h2_style))
    story.append(Paragraph(
        "HTTP is a <i>stateless</i> protocol — by default, the server forgets who you are after every click. "
        "When a user enters valid credentials in <code>login()</code>, Flask creates a cryptographically signed cookie stored in the user's browser. On the backend, we store: "
        "<code>session['user_id'] = str(user['_id'])</code> and <code>session['role'] = 'admin'</code>. "
        "On every subsequent click, Flask reads this cookie and immediately knows who the user is without re-asking for their password.",
        body_style
    ))

    # Concept 2
    story.append(Paragraph("B. How Password Hashing Works (Werkzeug Security):", h2_style))
    story.append(Paragraph(
        "We NEVER store plaintext passwords (e.g., 'admin123'). Instead, we use <code>generate_password_hash('admin123')</code>. "
        "This runs a one-way cryptographic hashing algorithm (PBKDF2 with SHA-256 and random salt). The result looks like <code>scrypt:32768:8:1$...</code>. "
        "When logging in, we use <code>check_password_hash(saved_hash, input_password)</code>. Even if someone hacks the database, they cannot reverse the hashes to discover user passwords.",
        body_style
    ))

    # Concept 3
    story.append(Paragraph("C. How Role-Based Access Control (Decorators) Works:", h2_style))
    story.append(Paragraph(
        "To prevent regular gym members from opening admin pages, we built a Python decorator <code>@role_required('admin')</code>. "
        "Before any route function executes, this decorator checks <code>session.get('role')</code>. If a member attempts to manually type <code>http://127.0.0.1:5000/admin/dashboard</code>, "
        "the decorator intercepts the request, blocks execution, and serves the <b>403 Access Denied</b> page with an HTTP 403 status code.",
        body_style
    ))

    # Concept 4
    story.append(Paragraph("D. Why MongoDB (NoSQL) Instead of MySQL (SQL)?", h2_style))
    story.append(Paragraph(
        "In a Gym system, workout routines contain a dynamic list of exercises (Bench Press, 3 sets, 10 reps). "
        "In a relational database (MySQL), this requires 3 separate tables linked by Foreign Keys with complex SQL JOIN queries. "
        "In MongoDB, documents can store arrays of sub-documents naturally (<code>exercises: [{name, sets, reps}]</code>). "
        "It provides schema flexibility, high performance, and natural mapping to Python dictionaries and JSON.",
        body_style
    ))

    # Concept 5
    story.append(Paragraph("E. How the Database Connection (PyMongo) Works:", h2_style))
    story.append(Paragraph(
        "In <code>db.py</code>, we initialize <code>MongoClient(Config.MONGO_URI)</code>. "
        "We implement a helper <code>get_db()</code> that returns the <code>gym_management</code> database. "
        "Whenever a route needs data, it calls functions like <code>members_col().find({'status': 'active'})</code> or <code>users_col().insert_one(user_doc)</code>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # ==============================================================
    # SECTION 7: TOP 20 VIVA QUESTIONS AND ANSWERS
    # ==============================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Top 20 Technical Viva Questions & Direct Answers", h1_style))
    story.append(Paragraph("Memorize or review these direct answers before stepping into the viva room:", body_style))

    qas = [
        ("Q1: What is Flask and why did you choose it over Django?",
         "Flask is a lightweight, modular Python WSGI web micro-framework. Unlike Django which is heavy and opinionated, Flask gives full control over architecture, is simple to understand, and connects smoothly with NoSQL databases like MongoDB."),
        
        ("Q2: What is Jinja2?",
         "Jinja2 is Flask's built-in templating engine. It lets us write HTML with dynamic programming logic using placeholders like {{ user.name }}, conditionals {% if session.role == 'admin' %}, and loops {% for m in members %}."),
        
        ("Q3: What is PyMongo?",
         "PyMongo is the official Python distribution containing tools for interacting with MongoDB databases from Python applications."),
        
        ("Q4: What is an ObjectId in MongoDB?",
         "An ObjectId is a 12-byte unique BSON identifier automatically assigned to the '_id' field of every document in MongoDB. It includes a 4-byte timestamp, 5-byte random value, and 3-byte incrementing counter."),
        
        ("Q5: What are the main user roles in your project?",
         "Three roles: Admin (complete oversight of members, coaches, revenue, attendance, plans), Trainer (manages assigned trainees and builds workout routines), and Member (views active plan, expiry countdown, workouts, and attendance)."),
        
        ("Q6: How does the system calculate membership expiry?",
         "When an admin assigns a plan (e.g. 90-day Quarterly Pro), the backend computes: end_date = start_date + timedelta(days=plan['duration_days']). The member dashboard displays days_remaining = (end_date - today).days."),
        
        ("Q7: How are payments handled in the project?",
         "Payments are implemented as a simulated/manual recording ledger. It records transaction references (PAY-XXXX), payment methods (Cash, Card, UPI), amounts, and timestamps into the payments collection without depending on external bank gateways."),
        
        ("Q8: How do you prevent duplicate email registrations?",
         "We set a unique index on 'email' in the users collection: users_col().create_index('email', unique=True). In addition, app.py queries users_col().find_one({'email': email}) before inserting."),
        
        ("Q9: What happens if an unauthorized user tries to access an Admin page?",
         "Our custom @role_required('admin') decorator inspects session['role']. If the role is not 'admin', it aborts the request and serves 403.html with an HTTP 403 Forbidden status code."),
        
        ("Q10: Where is the database connection string stored?",
         "In the .env file as MONGO_URI=mongodb://localhost:27017/gym_management. config.py reads it using python-dotenv. It is never hardcoded in source code."),
        
        ("Q11: Why is .env included in .gitignore?",
         "Because .env contains sensitive configuration such as SECRET_KEY and database credentials. Uploading it to GitHub exposes credentials publicly."),
        
        ("Q12: What is the purpose of init_db.py?",
         "It initializes database indexes, verifies server connectivity, and seeds default accounts (admin@gym.com, trainer@gym.com, member@gym.com) so the system is ready for demonstration."),
        
        ("Q13: What is the difference between GET and POST HTTP methods?",
         "GET requests retrieve data from the server and pass parameters in the URL query string. POST requests send data in the request body to create or update resources securely."),
        
        ("Q14: What is a REST API?",
         "A REST (Representational State Transfer) API is a standardized architectural style that uses HTTP methods (GET, POST, PUT, DELETE) to send and receive structured JSON data between clients and servers."),
        
        ("Q15: How did you test your REST API endpoints?",
         "Using Postman. We created a collection with requests for /api/auth/login, /api/members, /api/memberships, and /api/attendance to verify status codes (200, 201, 400, 404)."),
        
        ("Q16: Can this project be hosted directly on GitHub Pages? Why?",
         "No. GitHub Pages only hosts static HTML, CSS, and client-side JavaScript. It cannot execute a Python backend (app.py) or run a MongoDB server. To host online, we use services like Render.com or PythonAnywhere."),
        
        ("Q17: What does the attendance module do?",
         "It allows administrators to log daily member check-ins and check-outs with date filters. Members can view their complete personal attendance history on their dashboard."),
        
        ("Q18: What is Bootstrap 5 and how is it used?",
         "Bootstrap 5 is a modern responsive CSS framework. We used its grid system (row, col-md-*), modals, cards, badges, and utility classes to ensure the UI looks polished on mobile, tablet, and desktop."),
        
        ("Q19: How are workout plans structured in MongoDB?",
         "Each workout document contains: name, difficulty, created_by, and an embedded array 'exercises' containing objects with name, target sets, repetitions, and form notes."),
        
        ("Q20: What would be your future enhancements for this project?",
         "1. Real-time QR code attendance scanning at gym entrance.\n2. Integration with payment gateways like Stripe or Razorpay.\n3. Automated SMS / WhatsApp renewal reminders before subscription expiry.\n4. BMI and body fat measurement progress charts.")
    ]

    for q, a in qas:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a.replace('\n', '<br/>'), a_style))

    # ==============================================================
    # SECTION 8: STEP-BY-STEP LIVE DEMO WALKTHROUGH
    # ==============================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Step-by-Step Live Demonstration Checklist for the Examiner", h1_style))
    story.append(Paragraph(
        "Follow this exact script when demonstrating the live application to the examiner:",
        body_style
    ))

    demo_steps = [
        ("Step 1: Start the Server", "Open terminal, type 'python app.py', and open http://127.0.0.1:5000 in your browser."),
        ("Step 2: Show the Landing Page", "Show the responsive hero banner, membership package pricing (Starter, Pro, Elite), and coaches roster."),
        ("Step 3: Demonstrate Admin Portal", "Go to /login, click the 'Admin' button (autofills admin@gym.com / admin123). Show the KPI statistics cards (active members, active plans, revenue, check-ins)."),
        ("Step 4: Demonstrate Member Management", "Navigate to 'Members'. Show search filtering. Click 'Add New Member' or 'Assign Plan' to show automated expiry calculation."),
        ("Step 5: Demonstrate Payments Ledger", "Navigate to 'Payments Ledger'. Point out the simulated payment history and gross revenue sum."),
        ("Step 6: Demonstrate Workout Builder", "Navigate to 'Workout Plans'. Show how routines have embedded exercises with sets and repetitions."),
        ("Step 7: Log Out & Sign In as Member", "Log out, click 'Member' (member@gym.com / member123). Point out the active plan countdown badge ('X Days Remaining'), assigned workout routine, and attendance history."),
        ("Step 8: Demonstrate Security (403)", "While logged in as a Member, manually type 'http://127.0.0.1:5000/admin/dashboard' into the browser address bar. Show the examiner the 403 Access Denied page to prove server-side role security!")
    ]

    for title, desc in demo_steps:
        story.append(Paragraph(f"<b>{title}:</b>", body_style))
        story.append(Paragraph(desc, bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully generated: {filename}")
    return os.path.abspath(filename)

if __name__ == "__main__":
    build_pdf()
