"""
Script to generate a professional, high-resolution ER Diagram PDF
for the FitPulse Gym Management System project.
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Polygon, Group, Circle
)
from reportlab.pdfgen import canvas

class ERDiagramCanvas(canvas.Canvas):
    """Custom canvas for header/footer and page numbering on landscape pages."""
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
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Top Running Header
        self.drawString(36, 582, "FITPULSE GYM MANAGEMENT SYSTEM — ENTITY RELATIONSHIP (ER) DIAGRAM & SCHEMA SPECIFICATION")
        self.drawRightString(792 - 36, 582, "MongoDB NoSQL Data Model")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(36, 576, 792 - 36, 576)

        # Bottom Running Footer
        self.line(36, 32, 792 - 36, 32)
        self.setFont("Helvetica", 8)
        self.drawString(36, 22, "Candidate: Pranav Bhujbal | Prepared for Capstone Project Defense & Technical Viva")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(792 - 36, 22, page_str)
        self.restoreState()


def draw_entity_card(d, x, y, width, height, title, fields, header_color="#1e293b", badge_text="Collection"):
    """Draws a UML / Database Entity Card with a header bar and typed fields."""
    # Shadow
    d.add(Rect(x + 3, y - 3, width, height, rx=5, ry=5, fillColor=colors.HexColor("#e2e8f0"), strokeColor=None))
    # Box Background
    d.add(Rect(x, y, width, height, rx=5, ry=5, fillColor=colors.white, strokeColor=colors.HexColor("#94a3b8"), strokeWidth=1))
    
    # Header Bar
    header_height = 24
    d.add(Rect(x, y + height - header_height, width, header_height, rx=5, ry=5, fillColor=colors.HexColor(header_color), strokeColor=None))
    # Cover bottom corners of header so inside is flush
    d.add(Rect(x, y + height - header_height, width, 5, fillColor=colors.HexColor(header_color), strokeColor=None))
    
    # Header Title
    d.add(String(x + 10, y + height - 16, title, fontName="Helvetica-Bold", fontSize=10, fillColor=colors.white))
    
    # Header Badge (e.g. PK / Collection)
    badge_w = 48
    d.add(Rect(x + width - badge_w - 6, y + height - 18, badge_w, 12, rx=3, ry=3, fillColor=colors.HexColor("#334155"), strokeColor=None))
    d.add(String(x + width - badge_w + 3, y + height - 15, badge_text, fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.white))

    # Fields separator line
    curr_y = y + height - header_height - 13
    for f in fields:
        is_pk = "(PK)" in f
        is_fk = "(FK)" in f
        
        # Icon / bullet / prefix
        if is_pk:
            d.add(Circle(x + 10, curr_y + 3, 2.5, fillColor=colors.HexColor("#d97706"), strokeColor=None))
            field_font = "Helvetica-Bold"
            text_color = colors.HexColor("#0f172a")
        elif is_fk:
            d.add(Circle(x + 10, curr_y + 3, 2.5, fillColor=colors.HexColor("#2563eb"), strokeColor=None))
            field_font = "Helvetica"
            text_color = colors.HexColor("#1e40af")
        else:
            d.add(Circle(x + 10, curr_y + 3, 1.5, fillColor=colors.HexColor("#94a3b8"), strokeColor=None))
            field_font = "Helvetica"
            text_color = colors.HexColor("#334155")

        d.add(String(x + 18, curr_y, f, fontName=field_font, fontSize=7.5, fillColor=text_color))
        curr_y -= 11.5


def build_er_diagram_drawing():
    """Generates the visual vector ER Diagram using ReportLab Graphics."""
    d = Drawing(720, 480)

    # 1. Background grid panel
    d.add(Rect(0, 0, 720, 480, rx=8, ry=8, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=1))

    # -------------------------------------------------------------
    # ENTITY DEFINITIONS & COORDINATES
    # Canvas Size: 720 wide x 480 high
    # -------------------------------------------------------------

    # USERS (Top Middle)
    draw_entity_card(
        d, x=270, y=340, width=175, height=125,
        title="users",
        header_color="#0f172a",
        badge_text="Auth Core",
        fields=[
            "_id: ObjectId (PK)",
            "name: String",
            "email: String (UNIQUE)",
            "phone: String",
            "password_hash: String",
            "role: Enum(admin/trainer/member)",
            "status: String (active/inactive)",
            "created_at: DateTime"
        ]
    )

    # MEMBERS (Mid Left)
    draw_entity_card(
        d, x=20, y=260, width=180, height=135,
        title="members",
        header_color="#1d4ed8",
        badge_text="Actor",
        fields=[
            "_id: ObjectId (PK)",
            "user_id: ObjectId (FK)",
            "name: String",
            "email: String",
            "phone: String",
            "gender: String",
            "dob: String (YYYY-MM-DD)",
            "emergency_contact: String",
            "health_notes: String",
            "status: String (active/inactive)"
        ]
    )

    # TRAINERS (Mid Right)
    draw_entity_card(
        d, x=515, y=270, width=185, height=125,
        title="trainers",
        header_color="#0891b2",
        badge_text="Staff Actor",
        fields=[
            "_id: ObjectId (PK)",
            "user_id: ObjectId (FK)",
            "name: String",
            "email: String",
            "phone: String",
            "specialization: String",
            "experience_years: Integer",
            "availability: String",
            "bio: String"
        ]
    )

    # MEMBERSHIP_PLANS (Bottom Left)
    draw_entity_card(
        d, x=20, y=55, width=175, height=110,
        title="membership_plans",
        header_color="#047857",
        badge_text="Catalog",
        fields=[
            "_id: ObjectId (PK)",
            "plan_name: String",
            "duration_days: Integer",
            "price: Float / Decimal",
            "description: String",
            "status: String (active/inactive)",
            "created_at: DateTime"
        ]
    )

    # MEMBER_MEMBERSHIPS (Center / Lower Center)
    draw_entity_card(
        d, x=260, y=175, width=195, height=130,
        title="member_memberships",
        header_color="#b45309",
        badge_text="Subscription",
        fields=[
            "_id: ObjectId (PK)",
            "member_id: ObjectId (FK)",
            "plan_id: ObjectId (FK)",
            "user_id: ObjectId (FK)",
            "plan_name: String",
            "start_date: DateTime",
            "end_date: DateTime",
            "price: Float",
            "status: String (active/expired)"
        ]
    )

    # PAYMENTS (Bottom Center)
    draw_entity_card(
        d, x=260, y=15, width=195, height=125,
        title="payments",
        header_color="#059669",
        badge_text="Transactions",
        fields=[
            "_id: ObjectId (PK)",
            "member_id: ObjectId (FK)",
            "membership_id: ObjectId (FK)",
            "amount: Float",
            "payment_date: DateTime",
            "payment_method: String",
            "reference_no: String (PAY-XXXX)",
            "status: String (completed)"
        ]
    )

    # ATTENDANCE (Far Left Lower)
    draw_entity_card(
        d, x=20, y=175, width=180, height=75,
        title="attendance",
        header_color="#6d28d9",
        badge_text="Event Log",
        fields=[
            "_id: ObjectId (PK)",
            "member_id: ObjectId (FK)",
            "date: String (YYYY-MM-DD)",
            "check_in_time: String",
            "check_out_time: String",
            "status: String (Present)"
        ]
    )

    # WORKOUT_PLANS (Bottom Right)
    draw_entity_card(
        d, x=515, y=145, width=185, height=110,
        title="workout_plans",
        header_color="#be185d",
        badge_text="Blueprint",
        fields=[
            "_id: ObjectId (PK)",
            "name: String",
            "difficulty: Enum(Beg/Int/Adv)",
            "description: String",
            "created_by: String",
            "exercises: Array of Objects [ ]",
            "  ↳ {name, sets, reps, notes}"
        ]
    )

    # MEMBER_WORKOUTS (Bottom Far Right)
    draw_entity_card(
        d, x=515, y=15, width=185, height=115,
        title="member_workouts",
        header_color="#9333ea",
        badge_text="Assignment",
        fields=[
            "_id: ObjectId (PK)",
            "member_id: ObjectId (FK)",
            "trainer_id: ObjectId (FK)",
            "workout_plan_id: ObjectId (FK)",
            "workout_name: String",
            "exercises: Array [ {..} ]",
            "assigned_date: DateTime",
            "notes: String"
        ]
    )

    # -------------------------------------------------------------
    # RELATIONSHIP CONNECTORS & CARDINALITY LABELS
    # -------------------------------------------------------------

    def add_line(x1, y1, x2, y2, color="#475569", width=1.2, dashed=False):
        l = Line(x1, y1, x2, y2, strokeColor=colors.HexColor(color), strokeWidth=width)
        if dashed:
            l.strokeDashArray = [4, 3]
        d.add(l)

    def add_label(x, y, text, font_size=7.5, color="#1e293b", bg="#ffffff"):
        txt_w = len(text) * 4.5 + 4
        d.add(Rect(x - 2, y - 2, txt_w, 10, rx=2, ry=2, fillColor=colors.HexColor(bg), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=0.5))
        d.add(String(x, y, text, fontName="Helvetica-Bold", fontSize=font_size, fillColor=colors.HexColor(color)))

    # 1. users (1) <---> (1) members
    add_line(270, 395, 200, 335, color="#2563eb")
    add_label(250, 395, "1", color="#2563eb")
    add_label(205, 335, "1", color="#2563eb")
    add_label(220, 370, "1 : 1", color="#1e40af", bg="#eff6ff")

    # 2. users (1) <---> (1) trainers
    add_line(445, 395, 515, 335, color="#0891b2")
    add_label(450, 395, "1", color="#0891b2")
    add_label(500, 335, "1", color="#0891b2")
    add_label(470, 370, "1 : 1", color="#0891b2", bg="#ecfeff")

    # 3. members (1) <---> (0..N) member_memberships
    add_line(200, 290, 260, 255, color="#b45309")
    add_label(205, 285, "1", color="#b45309")
    add_label(245, 255, "N", color="#b45309")

    # 4. membership_plans (1) <---> (0..N) member_memberships
    add_line(195, 120, 260, 205, color="#b45309")
    add_label(200, 125, "1", color="#b45309")
    add_label(245, 200, "N", color="#b45309")
    add_label(210, 160, "1 : N", color="#b45309", bg="#fef3c7")

    # 5. member_memberships (1) <---> (1..N) payments
    add_line(355, 175, 355, 140, color="#059669")
    add_label(360, 165, "1", color="#059669")
    add_label(360, 142, "N", color="#059669")

    # 6. members (1) <---> (0..N) attendance
    add_line(110, 260, 110, 250, color="#6d28d9")
    add_label(115, 252, "1:N", color="#6d28d9", bg="#f5f3ff")

    # 7. trainers (1) <---> (0..N) member_workouts
    add_line(610, 270, 610, 130, color="#0891b2", dashed=True)
    add_label(615, 260, "1", color="#0891b2")
    add_label(615, 132, "N", color="#0891b2")

    # 8. workout_plans (1) <---> (0..N) member_workouts
    add_line(605, 145, 605, 130, color="#9333ea")
    add_label(612, 136, "1:N", color="#9333ea", bg="#faf5ff")

    # 9. members (1) <---> (0..1) member_workouts
    # Connect from member bottom to member_workouts
    add_line(110, 175, 110, 5, color="#9333ea", dashed=True)
    add_line(110, 5, 515, 5, color="#9333ea", dashed=True)
    add_line(515, 5, 515, 30, color="#9333ea", dashed=True)
    add_label(290, 8, "members (1) ---> (0..1) member_workouts", color="#9333ea", bg="#faf5ff")

    # Legend / Key
    d.add(Rect(530, 415, 170, 55, rx=4, ry=4, fillColor=colors.white, strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=0.75))
    d.add(String(538, 455, "DIAGRAM KEY & SYMBOLS:", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#0f172a")))
    d.add(Circle(545, 442, 3, fillColor=colors.HexColor("#d97706"), strokeColor=None))
    d.add(String(553, 440, "Primary Key (PK) / _id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#334155")))
    d.add(Circle(545, 428, 3, fillColor=colors.HexColor("#2563eb"), strokeColor=None))
    d.add(String(553, 426, "Foreign Key (FK) Reference", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#334155")))
    d.add(Line(625, 442, 650, 442, strokeColor=colors.HexColor("#475569"), strokeWidth=1.2))
    d.add(String(655, 440, "1:1 / 1:N Direct", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#334155")))
    d.add(Line(625, 428, 650, 428, strokeColor=colors.HexColor("#9333ea"), strokeWidth=1.2, strokeDashArray=[3,2]))
    d.add(String(655, 426, "Cross-ref (FK)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#334155")))

    return d


def build_er_pdf(filename="Gym_Management_System_ER_Diagram.pdf"):
    """Compiles the complete multi-page ER Diagram document in landscape orientation."""
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ER_Title',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'ER_Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'ER_H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ER_Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    table_cell = ParagraphStyle(
        'ER_TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'ER_TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # =========================================================
    # PAGE 1: VISUAL ER DIAGRAM
    # =========================================================
    story.append(Paragraph("FitPulse: Entity Relationship (ER) Diagram", title_style))
    story.append(Paragraph("Complete MongoDB Schema Architecture, Primary Keys, Foreign Keys, and Referential Multiplicity", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb'), spaceAfter=8))

    # Add Visual Diagram Drawing
    story.append(build_er_diagram_drawing())

    # =========================================================
    # PAGE 2: DATA DICTIONARY & COLLECTION SCHEMAS
    # =========================================================
    story.append(PageBreak())
    story.append(Paragraph("Complete Database Schema & Data Dictionary", title_style))
    story.append(Paragraph("Detailed technical specification for all 9 MongoDB collections in the `gym_management` database", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb'), spaceAfter=10))

    schema_rows = [
        [
            Paragraph("<b>Collection Name</b>", table_header),
            Paragraph("<b>Field Name</b>", table_header),
            Paragraph("<b>Data Type</b>", table_header),
            Paragraph("<b>Key / Constraint</b>", table_header),
            Paragraph("<b>Description & Business Rules</b>", table_header)
        ],
        [
            Paragraph("<b>users</b><br/><i>(Auth Core)</i>", table_cell),
            Paragraph("_id<br/>name<br/>email<br/>phone<br/>password_hash<br/>role<br/>status", table_cell),
            Paragraph("ObjectId<br/>String<br/>String<br/>String<br/>String<br/>String<br/>String", table_cell),
            Paragraph("PK (Indexed)<br/>Required<br/>Unique Index<br/>Optional<br/>Salted Hash<br/>admin/trainer/member<br/>active/inactive", table_cell),
            Paragraph("Primary authentication collection. Stores encrypted PBKDF2 passwords (never plaintext). Role determines access to admin, trainer, or member routes.", table_cell)
        ],
        [
            Paragraph("<b>members</b><br/><i>(Athlete Profile)</i>", table_cell),
            Paragraph("_id<br/>user_id<br/>gender<br/>dob<br/>emergency_contact<br/>health_notes", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>String<br/>String<br/>String<br/>String", table_cell),
            Paragraph("PK<br/>FK -> users._id (Unique)<br/>Male/Female/Other<br/>YYYY-MM-DD<br/>Optional<br/>Text", table_cell),
            Paragraph("Member profile information. 1:1 relationship with users collection. Health notes provide trainers with medical limitations and fitness goals.", table_cell)
        ],
        [
            Paragraph("<b>trainers</b><br/><i>(Staff Profile)</i>", table_cell),
            Paragraph("_id<br/>user_id<br/>specialization<br/>experience_years<br/>availability<br/>bio", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>String<br/>Integer<br/>String<br/>String", table_cell),
            Paragraph("PK<br/>FK -> users._id (Unique)<br/>Required<br/>min=0<br/>Shift times<br/>Text", table_cell),
            Paragraph("Gym coach profile. 1:1 relationship with users collection. Defines coaching specialties (e.g. HIIT, CrossFit) and gym floor duty shifts.", table_cell)
        ],
        [
            Paragraph("<b>membership_plans</b><br/><i>(Packages)</i>", table_cell),
            Paragraph("_id<br/>plan_name<br/>duration_days<br/>price<br/>description", table_cell),
            Paragraph("ObjectId<br/>String<br/>Integer<br/>Float<br/>String", table_cell),
            Paragraph("PK<br/>Indexed<br/>min=1<br/>min=0.0<br/>Text", table_cell),
            Paragraph("Membership catalog. Defines gym packages (e.g., Monthly Starter 30 days, Annual Elite 365 days) and pricing in Indian Rupees (₹).", table_cell)
        ],
        [
            Paragraph("<b>member_memberships</b><br/><i>(Subscriptions)</i>", table_cell),
            Paragraph("_id<br/>member_id<br/>plan_id<br/>start_date<br/>end_date<br/>status", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>ObjectId<br/>DateTime<br/>DateTime<br/>String", table_cell),
            Paragraph("PK<br/>FK -> members._id<br/>FK -> plans._id<br/>Computed<br/>Computed<br/>active/expired", table_cell),
            Paragraph("Subscription contract. Automatically computes end_date = start_date + duration_days. Controls access countdown in the member dashboard.", table_cell)
        ],
        [
            Paragraph("<b>payments</b><br/><i>(Transactions)</i>", table_cell),
            Paragraph("_id<br/>member_id<br/>membership_id<br/>amount<br/>payment_date<br/>payment_method<br/>reference_no", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>ObjectId<br/>Float<br/>DateTime<br/>String<br/>String", table_cell),
            Paragraph("PK<br/>FK -> members._id<br/>FK -> memberships._id<br/>min=0.0<br/>Now<br/>Cash/Card/UPI<br/>Unique Token", table_cell),
            Paragraph("Audit trail of recorded payments. Generates unique receipt references (PAY-XXXX) for accounting ledger and revenue charts.", table_cell)
        ],
        [
            Paragraph("<b>attendance</b><br/><i>(Check-ins)</i>", table_cell),
            Paragraph("_id<br/>member_id<br/>date<br/>check_in_time<br/>check_out_time<br/>status", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>String<br/>String<br/>String<br/>String", table_cell),
            Paragraph("PK<br/>FK -> members._id<br/>YYYY-MM-DD<br/>HH:MM:SS<br/>HH:MM:SS<br/>Present", table_cell),
            Paragraph("Daily check-in registry. Tracks facility attendance per date for capacity management and member habit analytics.", table_cell)
        ],
        [
            Paragraph("<b>workout_plans</b><br/><i>(Templates)</i>", table_cell),
            Paragraph("_id<br/>name<br/>difficulty<br/>exercises", table_cell),
            Paragraph("ObjectId<br/>String<br/>Enum<br/>Array of Sub-docs", table_cell),
            Paragraph("PK<br/>Indexed<br/>Beg/Int/Adv<br/>Embedded Objects", table_cell),
            Paragraph("Custom fitness blueprints. Contains an embedded array of exercise objects: [{name: 'Bench Press', sets: '3', reps: '10-12', instructions: '...'}].", table_cell)
        ],
        [
            Paragraph("<b>member_workouts</b><br/><i>(Assignments)</i>", table_cell),
            Paragraph("_id<br/>member_id<br/>workout_plan_id<br/>trainer_id<br/>assigned_date", table_cell),
            Paragraph("ObjectId<br/>ObjectId<br/>ObjectId<br/>ObjectId<br/>DateTime", table_cell),
            Paragraph("PK<br/>FK -> members._id<br/>FK -> workouts._id<br/>FK -> trainers._id<br/>Now", table_cell),
            Paragraph("Direct assignment linking a member to their active workout routine, supervised by an assigned coach.", table_cell)
        ]
    ]

    t_schema = Table(schema_rows, colWidths=[100, 110, 80, 120, 310])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_schema)

    # =========================================================
    # PAGE 3: RELATIONSHIPS & VIVA DEFENSE
    # =========================================================
    story.append(PageBreak())
    story.append(Paragraph("Entity Relationships & Architectural Rationale", title_style))
    story.append(Paragraph("Cardinality analysis, referential integrity rules, and viva defense rationale for choosing MongoDB", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb'), spaceAfter=10))

    rel_rows = [
        [
            Paragraph("<b>Source Entity</b>", table_header),
            Paragraph("<b>Cardinality</b>", table_header),
            Paragraph("<b>Target Entity</b>", table_header),
            Paragraph("<b>Foreign Key Used</b>", table_header),
            Paragraph("<b>Real-World Business Relationship Description</b>", table_header)
        ],
        [
            Paragraph("<b>users</b>", table_cell),
            Paragraph("<b>1 : 1</b>", table_cell),
            Paragraph("<b>members</b>", table_cell),
            Paragraph("<code>members.user_id</code>", table_cell),
            Paragraph("Each login account with the 'member' role is paired with exactly one member profile record containing emergency contact and fitness notes.", table_cell)
        ],
        [
            Paragraph("<b>users</b>", table_cell),
            Paragraph("<b>1 : 1</b>", table_cell),
            Paragraph("<b>trainers</b>", table_cell),
            Paragraph("<code>trainers.user_id</code>", table_cell),
            Paragraph("Each login account with the 'trainer' role is paired with exactly one coach profile containing certifications, experience, and shift hours.", table_cell)
        ],
        [
            Paragraph("<b>members</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>member_memberships</b>", table_cell),
            Paragraph("<code>memberships.member_id</code>", table_cell),
            Paragraph("A member can subscribe to multiple membership plans over their lifetime (initial joining, renewals, upgrades to Annual Elite).", table_cell)
        ],
        [
            Paragraph("<b>membership_plans</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>member_memberships</b>", table_cell),
            Paragraph("<code>memberships.plan_id</code>", table_cell),
            Paragraph("A single catalog package (e.g. Quarterly Pro) can be purchased by hundreds of different gym members.", table_cell)
        ],
        [
            Paragraph("<b>member_memberships</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>payments</b>", table_cell),
            Paragraph("<code>payments.membership_id</code>", table_cell),
            Paragraph("Each subscription generates completed payment transaction records for auditing revenue and generating invoices.", table_cell)
        ],
        [
            Paragraph("<b>members</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>attendance</b>", table_cell),
            Paragraph("<code>attendance.member_id</code>", table_cell),
            Paragraph("A single member creates many attendance check-in entries (one per day they visit the gym).", table_cell)
        ],
        [
            Paragraph("<b>workout_plans</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>member_workouts</b>", table_cell),
            Paragraph("<code>member_workouts.workout_plan_id</code>", table_cell),
            Paragraph("A standardized routine template (e.g. 'Beginner Full Body Foundation') can be assigned to multiple trainees at once.", table_cell)
        ],
        [
            Paragraph("<b>trainers</b>", table_cell),
            Paragraph("<b>1 : N</b>", table_cell),
            Paragraph("<b>member_workouts</b>", table_cell),
            Paragraph("<code>member_workouts.trainer_id</code>", table_cell),
            Paragraph("A fitness coach can supervise and assign customized routines to dozens of different athletes.", table_cell)
        ],
        [
            Paragraph("<b>members</b>", table_cell),
            Paragraph("<b>1 : 0..1</b>", table_cell),
            Paragraph("<b>member_workouts</b>", table_cell),
            Paragraph("<code>member_workouts.member_id</code>", table_cell),
            Paragraph("At any single point in time, an athlete has one active prescribed workout program to prevent conflicting routines.", table_cell)
        ]
    ]

    t_rel = Table(rel_rows, colWidths=[90, 70, 110, 130, 320])
    t_rel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_rel)
    story.append(Spacer(1, 12))

    # Viva Defense Callout
    viva_text = (
        "<b>Key Technical Defense for Viva Examiner: Why MongoDB's Hybrid Model Outperforms Traditional Relational SQL in this Project:</b><br/>"
        "1. <b>Embedded Documents vs Junction Tables:</b> In traditional SQL, storing a workout plan requires 3 tables (<code>workout_plans</code>, <code>exercises</code>, and <code>plan_exercises</code>) joined with 2 Foreign Keys. In MongoDB, exercises are embedded directly as a sub-document array: <code>exercises: [{name, sets, reps, notes}]</code>. This eliminates expensive JOIN operations, loads instantly in a single query, and maps directly to Python dictionaries and JSON.<br/>"
        "2. <b>Referential Integrity via ObjectIds:</b> Where independent lifecycle tracking is needed (e.g. member profiles, payments ledger, and attendance logs), we use normalized <code>ObjectId</code> cross-references. This gives the speed and flexibility of NoSQL while maintaining strict relational boundaries."
    )
    t_viva = Table([[Paragraph(viva_text, body_style)]], colWidths=[720])
    t_viva.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_viva)

    doc.build(story, canvasmaker=ERDiagramCanvas)
    print(f"[+] Successfully generated ER Diagram PDF: {filename}")
    return os.path.abspath(filename)

if __name__ == "__main__":
    build_er_pdf()
