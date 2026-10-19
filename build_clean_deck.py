import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    template_path = "template.pptx"
    output_path = "AegisOps_Official_Pitch.pptx"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError("template.pptx not found!")
        
    prs = pptx.Presentation(template_path)
    
    # Modern, high-contrast readable palette
    NAVY = RGBColor(11, 37, 69)          # #0B2545 - Primary Headers
    BLUE = RGBColor(2, 132, 199)         # #0284C7 - Accents & Links
    SLATE = RGBColor(30, 41, 59)         # #1E293B - Body text (High contrast)
    DARK_SLATE = RGBColor(15, 23, 42)    # #0F172A - Deep contrast
    WHITE = RGBColor(255, 255, 255)
    BORDER_GRAY = RGBColor(203, 213, 225) # Soft card border
    CARD_BG = RGBColor(255, 255, 255)
    GREEN = RGBColor(22, 101, 52)        # Verified/Success
    TABLE_HDR_BG = RGBColor(11, 37, 69)
    TABLE_ALT_BG = RGBColor(241, 245, 249)
    
    FONT_FAMILY = "Times New Roman"
    
    def add_card(slide, left=Inches(0.9), top=Inches(1.25), width=Inches(11.53), height=Inches(5.9)):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_GRAY
        card.line.width = Pt(1.5)
        return card

    def set_top_title(slide, title_text):
        for shape in list(slide.shapes):
            if shape.name.startswith("Google Shape;89") or \
               shape.name.startswith("Google Shape;99") or \
               shape.name.startswith("Google Shape;108") or \
               shape.name.startswith("Google Shape;118") or \
               shape.name.startswith("Google Shape;127") or \
               shape.name.startswith("Google Shape;137") or \
               shape.name.startswith("Google Shape;146"):
                tf = shape.text_frame
                tf.clear()
                shape.left = Inches(2.7)
                shape.top = Inches(0.25)
                shape.width = Inches(7.9)
                shape.height = Inches(0.85)
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                r = p.add_run()
                r.text = title_text
                r.font.name = FONT_FAMILY
                r.font.size = Pt(22)
                r.font.bold = True
                r.font.color.rgb = NAVY
                return shape
        tb = slide.shapes.add_textbox(Inches(2.7), Inches(0.25), Inches(7.9), Inches(0.85))
        p = tb.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title_text
        r.font.name = FONT_FAMILY
        r.font.size = Pt(22)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return tb

    def clean_slide_body(slide):
        for shape in list(slide.shapes):
            if shape.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE:
                continue
            if shape.top < Inches(1.1):
                continue
            sp = shape._element
            sp.getparent().remove(sp)

    # =========================================================================
    # SLIDE 1: Title & Team Details
    # =========================================================================
    slide1 = prs.slides[0]
    set_top_title(slide1, "IDEA SUBMISSION PPT")
    clean_slide_body(slide1)
    
    card1 = add_card(slide1)
    
    # Header inside card
    tb_title = slide1.shapes.add_textbox(Inches(1.2), Inches(1.4), Inches(10.9), Inches(1.5))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    
    p = tf_title.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(4)
    r = p.add_run()
    r.text = "AEGISOPS"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(32)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    p = tf_title.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(4)
    r = p.add_run()
    r.text = "Offline-First Disaster Coordination & DTN Mesh Platform"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = BLUE
    
    p = tf_title.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(8)
    r = p.add_run()
    r.text = "Track 1: Emergency Response Coordination After Disasters"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = SLATE

    p = tf_title.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "—" * 65
    r.font.name = FONT_FAMILY
    r.font.size = Pt(9)
    r.font.color.rgb = BORDER_GRAY

    # Left Box: Team Details (Spacious)
    tb_team = slide1.shapes.add_textbox(Inches(1.3), Inches(3.2), Inches(5.2), Inches(3.6))
    tf_team = tb_team.text_frame
    tf_team.word_wrap = True
    
    p = tf_team.paragraphs[0]
    p.space_after = Pt(14)
    r = p.add_run()
    r.text = "Team & Institution Information:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    team_items = [
        ("Institution: ", "Mangalore Institute of Technology & Engineering (MITE)", True),
        ("Team Leader: ", "Thwish rai", True),
        ("Team Members: ", "ujwal naik  •  shraddha  •  ninad d k", False),
        ("Track: ", "Problem Statement 1 (Disaster Response)", False),
        ("Public GitHub: ", "https://github.com/ujwal-naik/aegisops", True),
    ]
    for lbl, val, is_bld in team_items:
        p = tf_team.add_paragraph()
        p.space_after = Pt(12)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13)
        r2.font.bold = is_bld
        r2.font.color.rgb = BLUE if "http" in val else SLATE

    # Right Box: Prototype Highlights (Spacious)
    tb_hl = slide1.shapes.add_textbox(Inches(6.9), Inches(3.2), Inches(5.1), Inches(3.6))
    tf_hl = tb_hl.text_frame
    tf_hl.word_wrap = True
    
    p = tf_hl.paragraphs[0]
    p.space_after = Pt(14)
    r = p.add_run()
    r.text = "Shortlisting Submission Highlights:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    hl_items = [
        ("Working Prototype: ", "100% Implemented & Tested", GREEN),
        ("Zero Dependency: ", "Runs 100% Offline (No Cloud/API Keys)", SLATE),
        ("Clinical Triage: ", "START Protocol (Red / Yellow / Green / Black)", SLATE),
        ("Spatial Intelligence: ", "Deduplication via Haversine & Jaccard (<500m)", SLATE),
        ("Test Verification: ", "10/10 Passing Automated Pytest Suite", GREEN),
    ]
    for lbl, val, clr in hl_items:
        p = tf_hl.add_paragraph()
        p.space_after = Pt(12)
        r1 = p.add_run()
        r1.text = f"✔ {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13)
        r2.font.bold = (clr == GREEN)
        r2.font.color.rgb = clr

    # =========================================================================
    # SLIDE 2: Problem Statement & Problem Gap (Spacious & Clean)
    # =========================================================================
    slide2 = prs.slides[1]
    set_top_title(slide2, "PROBLEM STATEMENT & PROBLEM GAP")
    clean_slide_body(slide2)
    
    card2 = add_card(slide2)
    
    # Section 1: Problem Statement
    tb2_prob = slide2.shapes.add_textbox(Inches(1.3), Inches(1.45), Inches(10.7), Inches(2.5))
    tf2_prob = tb2_prob.text_frame
    tf2_prob.word_wrap = True
    
    p = tf2_prob.paragraphs[0]
    p.space_after = Pt(10)
    r = p.add_run()
    r.text = "1. Problem Statement: Emergency Response Coordination After Disasters"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    prob_bullets = [
        ("Information Chaos: ", "In sudden floods or earthquakes, control rooms are overwhelmed by thousands of messy, duplicate, and vague SOS reports across calls, SMS, and messengers."),
        ("Rescue Starvation: ", "Rescue boats and ambulances are strictly scarce. Aid disproportionately flows to the loudest or best-connected urban areas, leaving cut-off pockets unassisted."),
        ("Telecom Fragility: ", "Cellular towers and power grids collapse in the impact zone, creating total communication blackouts when help is needed most.")
    ]
    for lbl, val in prob_bullets:
        p = tf2_prob.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = SLATE

    # Section 2: Problem Gap
    tb2_gap = slide2.shapes.add_textbox(Inches(1.3), Inches(4.15), Inches(10.7), Inches(2.6))
    tf2_gap = tb2_gap.text_frame
    tf2_gap.word_wrap = True
    
    p = tf2_gap.paragraphs[0]
    p.space_after = Pt(10)
    r = p.add_run()
    r.text = "2. Problem Gap: Why Existing Systems Fail"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    gap_bullets = [
        ("Cloud Dependency: ", "Existing tools (Ushahidi, Google Crisis Map, Twitter scrapers) require active internet; they fail completely in zero-connectivity blackout zones."),
        ("Zero Clinical Triage: ", "Current tools treat SOS alerts as unranked raw text streams without clinical urgency scoring (START medical triage protocol)."),
        ("No Capability Matching: ", "Coordinators manually guess assignments without checking whether a vehicle matches terrain needs (e.g., sending vans to submerged roads).")
    ]
    for lbl, val in gap_bullets:
        p = tf2_gap.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = SLATE

    # =========================================================================
    # SLIDE 3: Proposed Solution & Innovation (Spacious & Clean)
    # =========================================================================
    slide3 = prs.slides[2]
    set_top_title(slide3, "PROPOSED SOLUTION & INNOVATION")
    clean_slide_body(slide3)
    
    card3 = add_card(slide3)
    
    # Top Callout Box
    tb3_top = slide3.shapes.add_textbox(Inches(1.3), Inches(1.4), Inches(10.7), Inches(0.8))
    tf3_top = tb3_top.text_frame
    tf3_top.word_wrap = True
    
    p = tf3_top.paragraphs[0]
    r1 = p.add_run()
    r1.text = "Proposed Solution in One Sentence:\n"
    r1.font.name = FONT_FAMILY
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r2 = p.add_run()
    r2.text = "\"AegisOps is an offline-first disaster coordination platform that structures chaotic multi-channel reports, triages casualties via clinical START logic, merges spatial duplicates, and computes equitable ICS-204 capability dispatches over DTN mesh.\""
    r2.font.name = FONT_FAMILY
    r2.font.size = Pt(13)
    r2.font.italic = True
    r2.font.bold = True
    r2.font.color.rgb = BLUE

    # Left Column: How It Works
    tb3_left = slide3.shapes.add_textbox(Inches(1.3), Inches(2.4), Inches(5.2), Inches(4.5))
    tf3_left = tb3_left.text_frame
    tf3_left.word_wrap = True
    
    p = tf3_left.paragraphs[0]
    p.space_after = Pt(12)
    r = p.add_run()
    r.text = "How The Solution Works:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    sol_items = [
        ("1. Offline PWA Ingestion: ", "Volunteers log structured SOS alerts locally via Service Workers & IndexedDB without internet."),
        ("2. START Clinical Triage: ", "NLP engine categorizes casualties into Immediate (Red), Delayed (Yellow), and Minor (Green)."),
        ("3. Spatial Deduplication: ", "Haversine clustering (<500m) merges duplicate reports into single high-confidence incidents."),
        ("4. Capability Dispatch: ", "Matches responder gear (Boats, Medics, USAR) to incident terrain and urgency.")
    ]
    for lbl, val in sol_items:
        p = tf3_left.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = lbl
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(12.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12.5)
        r2.font.color.rgb = SLATE

    # Right Column: Key Innovations
    tb3_right = slide3.shapes.add_textbox(Inches(6.8), Inches(2.4), Inches(5.2), Inches(4.5))
    tf3_right = tb3_right.text_frame
    tf3_right.word_wrap = True
    
    p = tf3_right.paragraphs[0]
    p.space_after = Pt(12)
    r = p.add_run()
    r.text = "Key Innovations & Value:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    innov_items = [
        ("• DTN Store-and-Forward Mesh: ", "Peer-to-peer bundle sync over Bluetooth/Wi-Fi Direct; guarantees zero packet loss in blackouts."),
        ("• Transparent Urgency Formula: ", "Auditable scoring: Urgency = (0.45 * Triage) + (0.30 * Vulnerability) + (0.25 * Hazard)."),
        ("• Anti-Starvation Fairness: ", "Actively prioritizes remote pockets that have gone the longest without rescue verification."),
        ("• Sub-250ms Recommendations: ", "Delivers human-in-the-loop dispatch recommendations in under 250 milliseconds.")
    ]
    for lbl, val in innov_items:
        p = tf3_right.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = lbl
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(12.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12.5)
        r2.font.color.rgb = SLATE

    # =========================================================================
    # SLIDE 4: System Architecture & Technology Stack (Spacious)
    # =========================================================================
    slide4 = prs.slides[3]
    set_top_title(slide4, "SYSTEM ARCHITECTURE & TECHNOLOGY STACK")
    clean_slide_body(slide4)
    
    card4 = add_card(slide4)
    
    # Diagram image in upper half
    diag_path = "docs/screenshots/architecture_diagram.png"
    if os.path.exists(diag_path):
        slide4.shapes.add_picture(diag_path, Inches(1.3), Inches(1.45), width=Inches(10.7), height=Inches(2.55))
        
    # Lower half: Technology Stack in clean, spacious bullet format
    tb4 = slide4.shapes.add_textbox(Inches(1.3), Inches(4.2), Inches(10.7), Inches(2.7))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    
    p = tf4.paragraphs[0]
    p.space_after = Pt(12)
    r = p.add_run()
    r.text = "Technology Stack & Technical Specifications:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    tech_bullets = [
        ("Offline Frontend: ", "Progressive Web App (PWA) • HTML5/CSS3 Tactical Dark Mode • Leaflet.js Tactical GIS • IndexedDB Vault"),
        ("Backend & Mesh: ", "Python 3.14 • FastAPI Asynchronous Framework • Uvicorn ASGI Server • RESTful DTN Sync Protocol"),
        ("Algorithmic Standards: ", "Simple Triage & Rapid Treatment (START) Medical Standard • ICS-204 Incident Command System"),
        ("Zero Dependency: ", "100% Free & Open-Source • Zero Paid API Keys • OpenStreetMap with Custom CSS Shader • 10/10 Passing Tests")
    ]
    for lbl, val in tech_bullets:
        p = tf4.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = SLATE

    # =========================================================================
    # SLIDE 5: Existing vs Proposed Solution & Impact (Spacious & Clean)
    # =========================================================================
    slide5 = prs.slides[4]
    set_top_title(slide5, "EXISTING VS PROPOSED SOLUTION & MEASURABLE IMPACT")
    clean_slide_body(slide5)
    
    card5 = add_card(slide5)
    
    # Table inside card
    rows, cols = 5, 2
    table_shape = slide5.shapes.add_table(rows, cols, Inches(1.3), Inches(1.45), Inches(10.7), Inches(2.4))
    table = table_shape.table
    table.columns[0].width = Inches(4.7)
    table.columns[1].width = Inches(6.0)
    
    table_data = [
        ("Existing Disaster Approaches", "Proposed Solution: AegisOps"),
        ("Cloud-dependent forms; fails completely when towers collapse.", "100% Offline-First PWA + DTN mesh; zero packet loss."),
        ("Manual sorting; loudest callers win (Rescue Starvation).", "Clinical START triage NLP + Anti-Starvation equitable weighting."),
        ("Control rooms flooded with 40-60% duplicate SOS reports.", "Haversine clustering (<500m) merges duplicates automatically."),
        ("Ad-hoc dispatches with no capability or terrain checks.", "Automated ICS-204 task matching (Boats, Medics, USAR).")
    ]
    
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            is_hdr = (r_idx == 0)
            font_sz = 12 if is_hdr else 11.5
            clr = WHITE if is_hdr else SLATE
            r = p.add_run()
            r.text = val
            r.font.name = FONT_FAMILY
            r.font.size = Pt(font_sz)
            r.font.bold = is_hdr
            r.font.color.rgb = clr
            
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_HDR_BG if is_hdr else (TABLE_ALT_BG if r_idx % 2 == 1 else WHITE)

    # Impact section below table
    tb5 = slide5.shapes.add_textbox(Inches(1.3), Inches(4.2), Inches(10.7), Inches(2.7))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    
    p = tf5.paragraphs[0]
    p.space_after = Pt(12)
    r = p.add_run()
    r.text = "Key Measurable Impacts & Public Benefit:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    impact_items = [
        ("98% Latency Reduction: ", "Emergency triage processing cut from ~15 minutes down to <250 milliseconds per incident."),
        (">45% Resource Optimization: ", "Spatial deduplication eliminates redundant dispatches and prevents wrong-vehicle errors."),
        ("Rescue Equity & Zero Cost: ", "Guarantees fair aid distribution to isolated zones; runs 100% free with zero paid API subscriptions.")
    ]
    for lbl, val in impact_items:
        p = tf5.add_paragraph()
        p.space_after = Pt(10)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = SLATE

    # =========================================================================
    # SLIDE 6: Prototype Demonstration & Implementation Plan (Spacious)
    # =========================================================================
    slide6 = prs.slides[5]
    set_top_title(slide6, "PROTOTYPE DEMONSTRATION & IMPLEMENTATION PLAN")
    clean_slide_body(slide6)
    
    card6 = add_card(slide6)
    
    # Left column: Implementation Plan & Prototype Status
    tb6 = slide6.shapes.add_textbox(Inches(1.3), Inches(1.45), Inches(5.0), Inches(5.4))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    
    p = tf6.paragraphs[0]
    p.space_after = Pt(10)
    r = p.add_run()
    r.text = "Implementation Plan (4 Phases):"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    phases = [
        ("Phase 1 (Completed): ", "Core START Triage NLP, Spatial Deduplication & ICS-204 Optimizer", GREEN),
        ("Phase 2 (Completed): ", "Tactical Dark Leaflet GIS Dashboard & Offline PWA Sync", GREEN),
        ("Phase 3 (Next - Round 2): ", "ESP32 LoRa & Bluetooth Low Energy (BLE) Hardware Mesh", BLUE),
        ("Phase 4 (Scale): ", "Multi-Agency SDMA / NDRF CAP Protocol Integration", BLUE)
    ]
    for lbl, val, clr in phases:
        p = tf6.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = f"✔ {lbl}" if clr == GREEN else f"→ {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(12.5)
        r1.font.bold = True
        r1.font.color.rgb = clr
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12)
        r2.font.color.rgb = SLATE

    p = tf6.add_paragraph()
    p.space_before = Pt(8)
    p.space_after = Pt(10)
    r = p.add_run()
    r.text = "Prototype Status & Public Links:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    links = [
        ("Status: ", "100% Implemented & Verified", GREEN),
        ("GitHub: ", "https://github.com/ujwal-naik/aegisops", BLUE),
        ("Video Pitch: ", "https://drive.google.com/file/d/your-presentation-video-link", BLUE)
    ]
    for lbl, val, clr in links:
        p = tf6.add_paragraph()
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = f"• {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(12.5)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12)
        r2.font.bold = (clr == GREEN)
        r2.font.color.rgb = clr

    # Right column: Dashboard Screenshot with Title
    tb6_img_title = slide6.shapes.add_textbox(Inches(6.6), Inches(1.45), Inches(5.6), Inches(0.4))
    p = tb6_img_title.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Live Tactical GIS Command Dashboard:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    dash_path = "docs/screenshots/dashboard.png"
    if os.path.exists(dash_path):
        slide6.shapes.add_picture(dash_path, Inches(6.6), Inches(1.9), width=Inches(5.5), height=Inches(4.9))

    # =========================================================================
    # SLIDE 7: Evaluation Alignment & Conclusion (Spacious & Clean)
    # =========================================================================
    slide7 = prs.slides[6]
    set_top_title(slide7, "HACKATHON EVALUATION ALIGNMENT & CONCLUSION")
    clean_slide_body(slide7)
    
    card7 = add_card(slide7)
    
    # 4 Judging Rubric Points
    tb7 = slide7.shapes.add_textbox(Inches(1.3), Inches(1.4), Inches(10.9), Inches(4.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    
    p = tf7.paragraphs[0]
    p.space_after = Pt(12)
    r = p.add_run()
    r.text = "Alignment with Problem Statement 1 Evaluation Criteria:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(16.5)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    rubric_points = [
        ("1. Feasibility & Approach: ", "Engineered for real-world chaotic disaster data (messy text, vague coordinates, high duplicate volume). Tested and verified locally with zero cloud latency."),
        ("2. Transparent Logic: ", "Full explainability: every incident displays its exact triage formula breakdown (Triage 0.45 + Vulnerability 0.30 + Hazard 0.25) with plain-English reasoning."),
        ("3. Equitable Focus: ", "Anti-starvation algorithm ensures remote, low-connectivity pockets receive equal rescue priority against loud, well-connected urban centers."),
        ("4. Human-in-the-Loop: ", "System acts as an AI copilot: coordinators retain 1-click authority to approve, reassign, or override all ICS-204 capability dispatches.")
    ]
    for lbl, desc in rubric_points:
        p = tf7.add_paragraph()
        p.space_after = Pt(12)
        r1 = p.add_run()
        r1.text = f"✔ {lbl}"
        r1.font.name = FONT_FAMILY
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_FAMILY
        r2.font.size = Pt(12.5)
        r2.font.color.rgb = SLATE

    # Bottom Box: Team Summary
    tb7_team = slide7.shapes.add_textbox(Inches(1.3), Inches(5.5), Inches(10.9), Inches(1.4))
    tf7_team = tb7_team.text_frame
    tf7_team.word_wrap = True
    
    p = tf7_team.paragraphs[0]
    p.space_after = Pt(6)
    r = p.add_run()
    r.text = "Project & Team Summary:"
    r.font.name = FONT_FAMILY
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = NAVY
    
    p = tf7_team.add_paragraph()
    p.space_after = Pt(6)
    r1 = p.add_run()
    r1.text = "• Institution: "
    r1.font.name = FONT_FAMILY
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r2 = p.add_run()
    r2.text = "Mangalore Institute of Technology & Engineering (MITE)"
    r2.font.name = FONT_FAMILY
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = BLUE
    r3 = p.add_run()
    r3.text = "   |   Leader: "
    r3.font.name = FONT_FAMILY
    r3.font.size = Pt(12)
    r3.font.bold = True
    r3.font.color.rgb = NAVY
    r4 = p.add_run()
    r4.text = "Thwish rai"
    r4.font.name = FONT_FAMILY
    r4.font.size = Pt(12)
    r4.font.bold = True
    r4.font.color.rgb = NAVY
    r5 = p.add_run()
    r5.text = "   |   Members: ujwal naik, shraddha, ninad d k"
    r5.font.name = FONT_FAMILY
    r5.font.size = Pt(12)
    r5.font.color.rgb = SLATE
    
    p = tf7_team.add_paragraph()
    r1 = p.add_run()
    r1.text = "• Public Repository: "
    r1.font.name = FONT_FAMILY
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r2 = p.add_run()
    r2.text = "https://github.com/ujwal-naik/aegisops"
    r2.font.name = FONT_FAMILY
    r2.font.size = Pt(12)
    r2.font.bold = True
    r2.font.color.rgb = BLUE

    prs.save(output_path)
    print(f"Spacious clean deck successfully generated at {output_path}")

if __name__ == '__main__':
    create_deck()
