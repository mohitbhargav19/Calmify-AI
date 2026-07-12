import io
import datetime
from typing import Any, Dict
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas renderer to display accurate dynamic total page counts
    and clear branding running footers.
    """
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Draw top subtle rule border
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 738, 558, 738)
        
        # Running Top Header
        self.drawString(54, 746, "Calmify AI — Personalized Wellness Report")
        
        # Running Bottom Footer
        self.line(54, 55, 558, 55)
        self.drawString(54, 42, f"Generated on: {datetime.date.today().strftime('%B %d, %Y')} | Confidential")
        self.drawRightString(558, 42, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_dashboard_pdf(pdf_payload: Dict[str, Any], user: Any) -> HttpResponse:
    """
    Generates an analytical mental health wellness dossier by extracting data 
    directly from the active session pipeline, preventing dashboard mismatches.
    """
    # -------------------------------------------------------------------------
    # Safe Dashboard Variable Extraction Matching views.py perfectly
    # -------------------------------------------------------------------------
    profile = pdf_payload.get("profile", {})
    predictions = pdf_payload.get("predictions", {})
    
    # Fallback mappings for summary data structures
    summary_data = pdf_payload.get("combined_summary", {})
    overall_risk = summary_data.get("overall_risk_level", "Low Risk")
    wellness_score = pdf_payload.get("wellness_score", 34.01)
    
    # Unpack Model Metric Objects Safely
    burnout_lbl = predictions.get("burnout", {}).get("prediction_label", "Moderate Burnout")
    burnout_conf = predictions.get("burnout", {}).get("confidence", 0.0)
    
    wellness_lbl = predictions.get("wellness", {}).get("prediction_label", "Poor Wellness")
    wellness_conf = predictions.get("wellness", {}).get("confidence", 0.0)
    
    mh_lbl = predictions.get("mental_health_status", {}).get("prediction_label", "Stable")
    mh_conf = predictions.get("mental_health_status", {}).get("confidence", 0.0)
    
    stress_lbl = predictions.get("stress_dataset", {}).get("prediction_label", "Low Stress")
    stress_conf = predictions.get("stress_dataset", {}).get("confidence", 100.0)
    
    student_lbl = predictions.get("student_survey", {}).get("prediction_label", "Low Stress")
    student_conf = predictions.get("student_survey", {}).get("confidence", 0.0)

    # -------------------------------------------------------------------------
    # PDF Setup & Layout Styling Configuration
    # -------------------------------------------------------------------------
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette definitions
    primary_color = colors.HexColor("#4A5568")
    secondary_color = colors.HexColor("#2B6CB0")
    text_dark = colors.HexColor("#2D3748")
    bg_light = colors.HexColor("#F7FAFC")

    # Paragraph style overrides
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=primary_color, spaceAfter=8
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=secondary_color, spaceBefore=14, spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CardHeading', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=primary_color, spaceBefore=6, spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextDark', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=text_dark, spaceAfter=6
    )

    explanation_style = ParagraphStyle(
        'ExplanationText', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9, leading=13,
        textColor=colors.HexColor("#4A5568"), spaceAfter=10
    )

    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=12,
        textColor=colors.white
    )

    story = []

    # -------------------------------------------------------------------------
    # 1. Header Banner & Profile Details Section
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("Calmify AI Wellness Dossier", title_style))
    story.append(Paragraph("Multi-Model Deep-Insight Machine Learning Report Profile", body_style))
    story.append(Spacer(1, 12))

    profile_data = [
        [Paragraph(f"<b>Participant Name:</b> {profile.get('name', user.username)}", body_style),
         Paragraph(f"<b>Age / Gender:</b> {profile.get('age', '22')} / {profile.get('gender', 'Male').title()}", body_style)],
        [Paragraph(f"<b>Academic Track:</b> {profile.get('course', 'Academic Program')}", body_style),
         Paragraph(f"<b>Assessment Date:</b> {datetime.date.today().strftime('%d %B %Y')}", body_style)]
    ]
    
    profile_table = Table(profile_data, colWidths=[250, 254])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # 2. Executive Assessment Dashboard Metrics
    # -------------------------------------------------------------------------
    story.append(Paragraph("Executive Summary Overview", h1_style))
    
    summary_matrix = [
        [Paragraph("<b>Metric Dimension</b>", table_header_style), Paragraph("<b>Status Outcome</b>", table_header_style)],
        [Paragraph("<b>Overall Risk Level Classification:</b>", body_style), Paragraph(f"<b>{overall_risk}</b>", body_style)],
        [Paragraph("<b>Consolidated Wellness Index Score:</b>", body_style), Paragraph(f"<b>{wellness_score}</b>", body_style)]
    ]
    
    summary_table = Table(summary_matrix, colWidths=[250, 254])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), secondary_color),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # 3. Comprehensive Metric Cards & Explanations Block
    # -------------------------------------------------------------------------
    story.append(Paragraph("Deconstructed Predictive Analytics Insights", h1_style))
    story.append(Paragraph("Below is a specific breakdowns of every critical metric card processed across the neural framework pipelines:", body_style))
    story.append(Spacer(1, 5))

    # --- CARD 1: BURNOUT ---
    card_burnout = []
    card_burnout.append(Paragraph("🔥 Occupational & Academic Burnout Risk Card", h2_style))
    card_burnout.append(Paragraph(f"<b>Current Standing:</b> {burnout_lbl} (Calculated Model Certainty: {burnout_conf}%)", body_style))
    card_burnout.append(Paragraph("<i>Analysis Explanation:</i> This index monitors systemic physical, emotional, and cognitive exhaustion levels caused by chronic instructional demands. A high or moderate standing signals that structural boundary protection adjustments are necessary to safeguard focus parameters.", explanation_style))
    story.append(KeepTogether(card_burnout))

    # --- CARD 2: WELLNESS ---
    card_wellness = []
    card_wellness.append(Paragraph("🌱 Holistic Wellness & Psychological Vitality Card", h2_style))
    card_wellness.append(Paragraph(f"<b>Current Standing:</b> {wellness_lbl} (Calculated Model Certainty: {wellness_conf}%)", body_style))
    card_wellness.append(Paragraph("<i>Analysis Explanation:</i> Evaluates cross-functional psychological wellness baselines and self-care maintenance routines. Lower ranges indicate opportunities to reintroduce grounding exercises, structured behavioral pacing protocols, and mindful downtime allocation.", explanation_style))
    story.append(KeepTogether(card_wellness))

    # --- CARD 3: STRESS DATASET ---
    card_stress = []
    card_stress.append(Paragraph("📊 Behavioral Stress Response Matrix Card", h2_style))
    card_stress.append(Paragraph(f"<b>Current Standing:</b> {stress_lbl} (Calculated Model Certainty: {stress_conf}%)", body_style))
    card_stress.append(Paragraph("<i>Analysis Explanation:</i> Gauges acute somatic indicators, biological tension traits, and automated nervous system reactions to daily structural strain. Stable readings highlight strong resilience responses under temporary pressure conditions.", explanation_style))
    story.append(KeepTogether(card_stress))

    # --- CARD 4: MENTAL HEALTH CORE ---
    card_mh = []
    card_mh.append(Paragraph("🧠 Cognitive Regulation & General Mental Health Status Card", h2_style))
    card_mh.append(Paragraph(f"<b>Current Standing:</b> {mh_lbl} (Calculated Model Certainty: {mh_conf}%)", body_style))
    card_mh.append(Paragraph("<i>Analysis Explanation:</i> Tracks psychological alignment metrics and affective stability trends over multi-week intervals to detect early warning signs. A baseline reading confirms standard coping capacity.", explanation_style))
    story.append(KeepTogether(card_mh))

    # --- CARD 5: STUDENT CONTEXT ---
    card_student = []
    card_student.append(Paragraph("🎓 Institutional Fatigue & Student Stress Focus Card", h2_style))
    card_student.append(Paragraph(f"<b>Current Standing:</b> {student_lbl} (Calculated Model Certainty: {student_conf}%)", body_style))
    card_student.append(Paragraph("<i>Analysis Explanation:</i> Tracks academic pressures unique to educational workloads, tracking vulnerabilities related to evaluation anxiety, course performance expectations, and exam-related fatigue cycles.", explanation_style))
    story.append(KeepTogether(card_student))

    # --- CARD 6: MUSIC HABITS ---
    card_music = []
    card_music.append(Paragraph("🎵 Acoustic Resonance & Sound Therapy Coping Card", h2_style))
    
    # Safely look for audio genre variables from view payload strings
    music_data = pdf_payload.get("predictions", {}).get("mxmh_case1", {})
    genres = music_data.get("recommended_genres", [])
    genre_str = ", ".join(genres) if genres else "Ambient, Low-Tempo Instrumental, Classical"
    
    card_music.append(Paragraph(f"<b>Acoustic Impact Orientation:</b> Positive Auditory Alignment Support", body_style))
    card_music.append(Paragraph(f"<b>Recommended Dynamic Audio Backing:</b> {genre_str}", body_style))
    card_music.append(Paragraph("<i>Analysis Explanation:</i> Decodes how auditory exposure impacts emotional self-regulation. Utilizing targeted genres during high-intensity cognitive focus acts as an active acoustic sound filter to quiet neural sympathetic arousal loops.", explanation_style))
    story.append(KeepTogether(card_music))

    # -------------------------------------------------------------------------
    # 4. Tailored Wellness Interventions
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 5))
    story.append(Paragraph("Al-Driven Preventive Recommendations", h1_style))
    
    recs = [
        "<b>Structured Physical Decompression:</b> Dedicate 20-30 minutes to structured, low-impact exercise to clear biological cortisol clearings.",
        "<b>Boundary Integration Practices:</b> Implement strict transitions between academic workflows and sleep window hours to counteract burnout trends.",
        "<b>Acoustic Regulated De-escalation:</b> Integrate non-lyrical ambient soundscapes into study hours to reduce cognitive noise fatigue spikes."
    ]
    
    for rec in recs:
        story.append(Paragraph(f"• {rec}", body_style))
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # 5. Professional Disclaimer
    # -------------------------------------------------------------------------
    disclaimer_block = []
    disclaimer_block.append(Paragraph("<b>Standard Administrative Notice & Terms Disclaimer</b>", h2_style))
    disclaimer_block.append(Paragraph(
        "This diagnostic brief is fully automated utilizing experimental multi-model machine learning weighting parameters. "
        "The conclusions presented are generated solely for self-reflection educational tracking and wellness awareness purposes. "
        "This document does NOT constitute clinical psychiatric counsel, psychological treatment, or medical diagnosis. "
        "If stress levels remain elevated or become disruptive to your daily function, please seek professional support.", 
        explanation_style
    ))
    story.append(KeepTogether(disclaimer_block))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Deliver response block back down pipeline stream
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Calmify_AI_Report_{profile.get("name", "User")}.pdf"'
    return response