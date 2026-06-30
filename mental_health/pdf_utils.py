# ==========================================================
# pdf_utils.py
# Calmify AI PDF Report Generator
# ==========================================================

from datetime import datetime

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

# ==========================================================
# RISK COLOUR HELPER
# ==========================================================

def get_risk_color(risk_level):
    """
    Returns ReportLab colour based on risk level.
    """

    risk = str(risk_level).strip().lower()

    if risk == "low":
        return HexColor("#2E7D32")      # Green

    elif risk == "moderate":
        return HexColor("#F9A825")      # Orange

    return HexColor("#C62828")          # Red


# ==========================================================
# PART 1
# COVER PAGE
# ==========================================================

# ==========================================================
# PART 1
# COVER PAGE
# ==========================================================

def build_cover_page(
    story,
    dashboard_data,
    user,
    styles,
):
    """
    Builds the Cover Page of the Calmify AI Report.
    """

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["BodyText"]

    # ------------------------------------------------------
    # Title
    # ------------------------------------------------------

    story.append(Spacer(1, 0.5 * inch))

    story.append(
        Paragraph(
            "<font color='#1565C0'><b>Calmify AI</b></font>",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Personalized Mental Wellness Report",
            heading_style,
        )
    )

    story.append(Spacer(1, 0.45 * inch))

    # ------------------------------------------------------
    # User Information
    # ------------------------------------------------------

    username = (
        user.username
        if user and user.is_authenticated
        else "Guest User"
    )

    profile = dashboard_data.get("profile", {})

    age = profile.get("age", "N/A")
    gender = profile.get("gender", "N/A")

    generated_on = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    cover_data = [

        ["Name", username],

        ["Age", age],

        ["Gender", gender],

        ["Generated On", generated_on],

    ]

    cover_table = Table(
        cover_data,
        colWidths=[2.2 * inch, 3.3 * inch],
    )

    cover_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    HexColor("#1565C0"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white,
                ),

                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.whitesmoke,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.grey,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold",
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

            ]

        )

    )

    story.append(cover_table)

    # ------------------------------------------------------
    # Introduction
    # ------------------------------------------------------

    story.append(Spacer(1, 0.6 * inch))

    intro = """

    This report has been automatically generated using
    <b>Calmify AI's Multi-Model Mental Wellness Prediction Pipeline</b>.

    The assessment combines multiple Machine Learning models
    to evaluate burnout risk, stress levels, mental wellness,
    emotional health, and the influence of music on
    psychological well-being.

    The generated report provides a comprehensive overview
    of the user's current mental wellness profile and offers
    AI-driven recommendations to promote healthier lifestyle
    habits and emotional resilience.

    """

    story.append(
        Paragraph(
            intro,
            normal_style,
        )
    )

    story.append(Spacer(1, 1.1 * inch))

    story.append(

        Paragraph(

            "<i>Prepared for educational and wellness awareness purposes only.</i>",

            heading_style,

        )

    )

    story.append(PageBreak())
    
# ==========================================================
# PART 2
# OVERALL WELLNESS SUMMARY
# ==========================================================

def build_overall_summary(
    story,
    dashboard_data,
    title_style,
    heading_style,
    normal_style,
):

    story.append(
        Paragraph(
            "Overall Wellness Summary",
            title_style,
        )
    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    # ------------------------------------------------------
    # Dashboard Data
    # ------------------------------------------------------

    combined_summary = dashboard_data.get(
        "combined_summary",
        {}
    )

    overall_risk = combined_summary.get(
        "overall_risk_level",
        "Unknown"
    )

    wellness_score = dashboard_data.get(
        "wellness_score",
        "N/A"
    )

    predictions = dashboard_data.get(
        "predictions",
        {}
    )

    # ------------------------------------------------------
    # Average AI Confidence
    # ------------------------------------------------------

    confidence_values = []

    for model in predictions.values():

        confidence = model.get("confidence")

        if confidence is not None:

            confidence_values.append(
                float(confidence)
            )

    if confidence_values:

        average_confidence = round(
            sum(confidence_values)
            / len(confidence_values),
            2
        )

    else:

        average_confidence = "N/A"

    # ------------------------------------------------------
    # Summary Table
    # ------------------------------------------------------

    summary_table = Table(

        [

            ["Overall Risk Level", overall_risk],

            ["Wellness Score", str(wellness_score)],

            [
                "Average AI Confidence",
                f"{average_confidence}%"
            ],

        ],

        colWidths=[2.8 * inch, 3.0 * inch]

    )

    summary_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (0,-1),
                    HexColor("#1565C0")
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (0,-1),
                    colors.white
                ),

                (
                    "BACKGROUND",
                    (1,0),
                    (1,-1),
                    colors.whitesmoke
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,-1),
                    "Helvetica-Bold"
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    10
                ),

            ]

        )

    )

    story.append(summary_table)

    story.append(
        Spacer(1, 0.35 * inch)
    )

    # ------------------------------------------------------
    # Executive Assessment Box
    # ------------------------------------------------------

    risk_colour = get_risk_color(
        overall_risk
    )

    executive_text = f"""

    <b>Executive Assessment</b><br/><br/>

    Calmify AI analysed the outputs generated by all
    integrated machine learning models.

    <br/><br/>

    The overall wellness score is
    <b>{wellness_score}</b>.

    <br/><br/>

    The estimated mental wellness risk level is

    <font color="{risk_colour.hexval()}">

    <b>{overall_risk}</b>

    </font>.

    <br/><br/>

    The average confidence across all AI models is

    <b>{average_confidence}%</b>.

    <br/><br/>

    This value represents the combined analysis of
    burnout prediction, wellness assessment,
    stress detection, mental health classification,
    student survey analysis and music-based
    emotional wellbeing models.

    """

    executive_box = Table(

        [

            [

                Paragraph(
                    executive_text,
                    normal_style
                )

            ]

        ],

        colWidths=[6.2 * inch]

    )

    executive_box.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,-1),
                    HexColor("#F4F8FF")
                ),

                (
                    "BOX",
                    (0,0),
                    (-1,-1),
                    1,
                    HexColor("#1565C0")
                ),

                (
                    "LEFTPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

                (
                    "RIGHTPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    14
                ),

            ]

        )

    )

    story.append(executive_box)

    story.append(
        PageBreak()
    )
    
# ==========================================================
# PART 3
# PREDICTION SUMMARY
# ==========================================================

def build_prediction_summary(
    story,
    dashboard_data,
    title_style,
    heading_style,
    normal_style,
):

    story.append(
        Paragraph(
            "Prediction Summary",
            title_style,
        )
    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    predictions = dashboard_data.get(
        "predictions",
        {}
    )

    MODEL_NAMES = {

        "burnout":
            "Burnout Prediction",

        "wellness":
            "Wellness Assessment",

        "mental_health_status":
            "Mental Health Status",

        "student_survey":
            "Student Stress Analysis",

        "stress_dataset":
            "Stress Dataset Prediction",

        "mxmh_case1":
            "Music Impact (Case 1)",

        "mxmh_case2":
            "Music Impact (Case 2)",

    }

    DISPLAY_ORDER = [

        "burnout",

        "wellness",

        "mental_health_status",

        "student_survey",

        "stress_dataset",

        "mxmh_case1",

        "mxmh_case2",

    ]

    table_data = [

        [

            "AI Model",

            "Prediction",

            "Confidence (%)",

        ]

    ]

    for key in DISPLAY_ORDER:

        model = predictions.get(
            key,
            {}
        )

        prediction = model.get(
            "prediction_label",
            "N/A"
        )

        confidence = model.get(
            "confidence",
            "N/A"
        )

        table_data.append(

            [

                MODEL_NAMES.get(
                    key,
                    key
                ),

                str(prediction),

                str(confidence),

            ]

        )

    prediction_table = Table(

        table_data,

        colWidths=[
            3.3 * inch,
            1.8 * inch,
            1.1 * inch,
        ],

    )

    prediction_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    HexColor("#1565C0"),
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,0),
                    "Helvetica-Bold",
                ),

                (
                    "BACKGROUND",
                    (0,1),
                    (-1,-1),
                    colors.whitesmoke,
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.grey,
                ),

                (
                    "ALIGN",
                    (1,1),
                    (-1,-1),
                    "CENTER",
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    8,
                ),

            ]

        )

    )

    story.append(
        prediction_table
    )

    story.append(
        Spacer(1, 0.35 * inch)
    )

    interpretation = """

    <b>Interpretation</b><br/><br/>

    The above table summarises the outputs generated by all
    Machine Learning models integrated within the Calmify AI
    assessment pipeline.

    Each model evaluates a different aspect of mental wellness,
    including burnout risk, emotional health, overall wellness,
    student stress, behavioural stress patterns, and the
    influence of music on emotional wellbeing.

    Confidence values indicate the certainty associated with
    each prediction whenever available.

    """

    story.append(

        Paragraph(

            interpretation,

            normal_style,

        )

    )

    story.append(
        PageBreak()
    )
    
# ==========================================================
# AI INTERPRETATION ENGINE
# ==========================================================

def build_ai_interpretation_data(dashboard_data):
    """
    Creates a professional executive interpretation
    from all model predictions.
    """

    predictions = dashboard_data.get(
        "predictions",
        {}
    )

    summary = dashboard_data.get(
        "combined_summary",
        {}
    )

    overall_risk = str(
        summary.get(
            "overall_risk_level",
            "Unknown"
        )
    )

    wellness_score = dashboard_data.get(
        "wellness_score",
        0
    )

    strengths = []

    attention = []

    # ------------------------------------------
    # Strengths
    # ------------------------------------------

    if wellness_score >= 75:

        strengths.append(
            "Overall wellness score indicates good emotional resilience."
        )

    burnout = predictions.get(
        "burnout",
        {}
    ).get(
        "prediction_label",
        ""
    ).lower()

    if burnout == "low":

        strengths.append(
            "Burnout prediction suggests a relatively healthy work-life balance."
        )

    wellness = predictions.get(
        "wellness",
        {}
    ).get(
        "prediction_label",
        ""
    ).lower()

    if wellness in [
        "healthy",
        "good",
        "normal",
    ]:

        strengths.append(
            "General wellness assessment is positive."
        )

    # ------------------------------------------
    # Attention Areas
    # ------------------------------------------

    if overall_risk.lower() == "moderate":

        attention.append(
            "Moderate psychological stress indicators were detected."
        )

    elif overall_risk.lower() == "high":

        attention.append(
            "Multiple models detected elevated mental health risk."
        )

    student = predictions.get(
        "student_survey",
        {}
    ).get(
        "prediction_label",
        ""
    ).lower()

    if student in [
        "high",
        "severe",
        "stressed",
    ]:

        attention.append(
            "Student stress assessment indicates increased academic pressure."
        )

    stress = predictions.get(
        "stress_dataset",
        {}
    ).get(
        "prediction_label",
        ""
    ).lower()

    if stress in [
        "high",
        "severe",
        "stressed",
    ]:

        attention.append(
            "Behavioural stress indicators require monitoring."
        )

    if not attention:

        attention.append(
            "No significant psychological concerns were identified."
        )

    # ------------------------------------------
    # Cross-model agreement
    # ------------------------------------------

    high_votes = 0

    for value in predictions.values():

        label = str(
            value.get(
                "prediction_label",
                ""
            )
        ).lower()

        if label in [

            "high",

            "severe",

            "stressed",

            "burnout",

        ]:

            high_votes += 1

    if high_votes >= 5:

        agreement = (
            "Most AI models consistently indicate a similar elevated risk profile."
        )

    elif high_votes >= 3:

        agreement = (
            "The majority of AI models show moderate agreement regarding the user's current wellbeing."
        )

    else:

        agreement = (
            "The AI models generally agree that the user's mental wellness profile is relatively stable."
        )

    # ------------------------------------------
    # Final conclusion
    # ------------------------------------------

    if overall_risk.lower() == "low":

        conclusion = (
            "Overall mental wellbeing appears stable. Continue maintaining healthy lifestyle habits."
        )

    elif overall_risk.lower() == "moderate":

        conclusion = (
            "The assessment indicates moderate emotional strain. Preventive wellness practices are recommended."
        )

    else:

        conclusion = (
            "The assessment indicates elevated psychological risk. Professional mental health support is strongly recommended."
        )

    executive = f"""

    Calmify AI analysed the outputs generated by all
    integrated Machine Learning models.

    The combined wellness score is
    <b>{wellness_score}</b>
    with an overall estimated risk level of
    <b>{overall_risk}</b>.

    The observations below summarize the integrated
    AI assessment.

    """

    return {

        "executive": executive,

        "strengths": strengths,

        "attention": attention,

        "agreement": agreement,

        "conclusion": conclusion,

    }


# ==========================================================
# PART 4
# AI INTERPRETATION
# ==========================================================

def build_ai_interpretation(
    story,
    dashboard_data,
    title_style,
    heading_style,
    normal_style,
):

    story.append(
        Paragraph(
            "AI Interpretation",
            title_style,
        )
    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    analysis = build_ai_interpretation_data(
        dashboard_data
    )

    story.append(
        Paragraph(
            "<b>Executive Risk Analysis</b>",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            analysis["executive"],
            normal_style,
        )
    )

    story.append(
        Spacer(1, 0.20 * inch)
    )

    story.append(
        Paragraph(
            "<b>Strengths Identified</b>",
            heading_style,
        )
    )

    for item in analysis["strengths"]:

        story.append(
            Paragraph(
                f"• {item}",
                normal_style,
            )
        )

    story.append(
        Spacer(1, 0.20 * inch)
    )

    story.append(
        Paragraph(
            "<b>Areas Requiring Attention</b>",
            heading_style,
        )
    )

    for item in analysis["attention"]:

        story.append(
            Paragraph(
                f"• {item}",
                normal_style,
            )
        )

    story.append(
        Spacer(1, 0.20 * inch)
    )

    story.append(
        Paragraph(
            "<b>Cross-Model Agreement</b>",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            analysis["agreement"],
            normal_style,
        )
    )

    story.append(
        Spacer(1, 0.20 * inch)
    )

    story.append(
        Paragraph(
            "<b>Overall AI Conclusion</b>",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            analysis["conclusion"],
            normal_style,
        )
    )

    story.append(
        PageBreak()
    )
    
# ==========================================================
# RECOMMENDATION ENGINE
# ==========================================================

def build_recommendation_data(dashboard_data):
    """
    Generates personalised wellness recommendations
    based on overall AI predictions.
    """

    recommendations = []

    summary = dashboard_data.get(
        "combined_summary",
        {}
    )

    predictions = dashboard_data.get(
        "predictions",
        {}
    )

    overall_risk = str(
        summary.get(
            "overall_risk_level",
            ""
        )
    ).lower()

    wellness_score = dashboard_data.get(
        "wellness_score",
        0
    )

    # --------------------------------------------------

    if overall_risk in ["moderate", "high"]:

        recommendations.append({

            "title": "Sleep Hygiene",

            "description":
            "Maintain a regular sleep schedule of 7–8 hours every night. Consistent sleep significantly improves emotional regulation and cognitive performance."

        })

    # --------------------------------------------------

    if wellness_score < 80:

        recommendations.append({

            "title": "Physical Activity",

            "description":
            "Engage in at least 30 minutes of moderate exercise five days a week to reduce stress hormones and improve mood."

        })

    # --------------------------------------------------

    mental_status = predictions.get(
        "mental_health_status",
        {}
    ).get(
        "prediction_label",
        ""
    ).lower()

    if mental_status not in [

        "healthy",

        "normal",

        "stable",

    ]:

        recommendations.append({

            "title": "Mindfulness Practice",

            "description":
            "Practice breathing exercises or guided meditation for 10–15 minutes daily to improve emotional stability."

        })

    # --------------------------------------------------

    recommendations.append({

        "title": "Music Therapy",

        "description":
        "Listen to calming instrumental, ambient or low-tempo music during stressful periods to promote relaxation."

    })

    # --------------------------------------------------

    if overall_risk == "high":

        recommendations.append({

            "title": "Social Support",

            "description":
            "Stay connected with trusted family members, close friends or mentors. Social interaction is an important protective factor."

        })

        recommendations.append({

            "title": "Professional Consultation",

            "description":
            "If symptoms persist or interfere with daily functioning, consult a qualified mental health professional."

        })

    return recommendations


# ==========================================================
# PART 6
# PERSONALISED RECOMMENDATIONS
# ==========================================================

def build_recommendations(
    story,
    dashboard_data,
    title_style,
    heading_style,
    normal_style,
):

    story.append(

        Paragraph(

            "Personalized Recommendations",

            title_style,

        )

    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    recommendations = build_recommendation_data(
        dashboard_data
    )

    for item in recommendations:

        story.append(

            Paragraph(

                f"<b>✓ {item['title']}</b>",

                heading_style,

            )

        )

        story.append(

            Paragraph(

                item["description"],

                normal_style,

            )

        )

        story.append(
            Spacer(1, 0.20 * inch)
        )

    story.append(
        Spacer(1, 0.25 * inch)
    )

    story.append(

        Paragraph(

            """
            <b>Important Note</b><br/><br/>

            These recommendations have been generated
            automatically using Calmify AI's integrated
            machine learning assessment pipeline.
            They are intended to promote healthy lifestyle
            practices and wellness awareness and should not
            replace professional medical advice.

            """,

            normal_style,

        )

    )

    story.append(
        PageBreak()
    )
    
# ==========================================================
# PART 7
# DISCLAIMER & REPORT INFORMATION
# ==========================================================

def build_disclaimer(
    story,
    title_style,
    heading_style,
    normal_style,
):

    story.append(

        Paragraph(

            "Disclaimer & Report Information",

            title_style,

        )

    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    # ======================================================
    # Disclaimer
    # ======================================================

    story.append(

        Paragraph(

            "<b>Professional Disclaimer</b>",

            heading_style,

        )

    )

    story.append(

        Paragraph(

            """
            This report has been automatically generated by
            Calmify AI using multiple Machine Learning models.

            The predictions presented in this report are
            intended solely for educational purposes,
            wellness awareness and early self-reflection.

            They should <b>NOT</b> be interpreted as a
            medical diagnosis, psychiatric evaluation,
            or professional clinical opinion.

            If emotional distress, anxiety, depression,
            burnout or psychological symptoms continue or
            worsen, consultation with a qualified mental
            health professional is strongly recommended.

            """,

            normal_style,

        )

    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    # ======================================================
    # Confidentiality
    # ======================================================

    story.append(

        Paragraph(

            "<b>Confidentiality Notice</b>",

            heading_style,

        )

    )

    story.append(

        Paragraph(

            """
            Calmify AI is designed to maintain user privacy.

            Personal information used for generating this
            report is processed only for assessment purposes.

            Users should avoid sharing this report publicly
            if it contains sensitive personal information.

            """,

            normal_style,

        )

    )

    story.append(
        Spacer(1, 0.30 * inch)
    )

    # ======================================================
    # Report Metadata
    # ======================================================

    story.append(

        Paragraph(

            "<b>Report Metadata</b>",

            heading_style,

        )

    )

    report_data = [

        ["Application", "Calmify AI"],

        ["Report Type", "Mental Wellness Assessment"],

        ["Prediction Engine", "Multi-Model Machine Learning Pipeline"],

        ["Generated On", datetime.now().strftime("%d %B %Y")],

        ["Version", "1.0"],

    ]

    metadata_table = Table(

        report_data,

        colWidths=[2.3 * inch, 3.8 * inch],

    )

    metadata_table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (0,-1),
                    HexColor("#1565C0"),
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (0,-1),
                    colors.white,
                ),

                (
                    "BACKGROUND",
                    (1,0),
                    (1,-1),
                    colors.whitesmoke,
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.grey,
                ),

                (
                    "BOTTOMPADDING",
                    (0,0),
                    (-1,-1),
                    9,
                ),

                (
                    "TOPPADDING",
                    (0,0),
                    (-1,-1),
                    9,
                ),

                (
                    "FONTNAME",
                    (0,0),
                    (-1,-1),
                    "Helvetica-Bold",
                ),

            ]

        )

    )

    story.append(metadata_table)

    story.append(
        Spacer(1, 0.60 * inch)
    )

    # ======================================================
    # Footer
    # ======================================================

    story.append(

        Paragraph(

            "<b>Generated by Calmify AI</b>",

            heading_style,

        )

    )

    story.append(

        Paragraph(

            """
            © Calmify AI

            AI-powered Mental Wellness Assessment Platform

            Built for educational research, wellness
            awareness and early risk identification.

            """,

            normal_style,

        )

    )
    
# ==========================================================
# PAGE NUMBER FOOTER
# ==========================================================

from reportlab.lib.units import mm


def add_page_number(canvas, doc):
    """
    Draws page number on every page.
    """

    page_num = canvas.getPageNumber()

    footer = f"Page {page_num}"

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        9,
    )

    canvas.setFillColor(
        colors.grey,
    )

    canvas.drawRightString(
    doc.width + doc.leftMargin,
    15,
    footer,
)

    canvas.restoreState()
    
# ==========================================================
# MAIN PDF GENERATOR
# ==========================================================

def generate_dashboard_pdf(
    dashboard_data,
    user=None,
):
    """
    Generates the complete Calmify AI
    Mental Wellness Report.
    """

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="Calmify_AI_Report.pdf"'

    # ------------------------------------------------------

    doc = SimpleDocTemplate(

        response,

        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50,

    )

    # ------------------------------------------------------
    # Styles
    # ------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    heading_style.alignment = TA_CENTER

    normal_style = styles["BodyText"]

    # ------------------------------------------------------

    story = []

    # ======================================================
    # BUILD REPORT
    # ======================================================

    build_cover_page(

    story,
    dashboard_data,
    user,
    styles,

)

    build_overall_summary(

        story,
        dashboard_data,
        title_style,
        heading_style,
        normal_style,

    )

    build_prediction_summary(

        story,
        dashboard_data,
        title_style,
        heading_style,
        normal_style,

    )

    build_ai_interpretation(

        story,
        dashboard_data,
        title_style,
        heading_style,
        normal_style,

    )

    build_recommendations(

        story,
        dashboard_data,
        title_style,
        heading_style,
        normal_style,

    )

    build_disclaimer(

        story,
        title_style,
        heading_style,
        normal_style,

    )

    # ======================================================
    # BUILD PDF
    # ======================================================

    doc.build(

        story,

        onFirstPage=add_page_number,

        onLaterPages=add_page_number,

    )

    return response