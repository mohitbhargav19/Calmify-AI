from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)


def generate_report(
    response,
    user,
    latest_mood,
    wellness_score,
    weekly_average,
    suggestions
):

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "Calmify AI Wellness Report",
        styles['Title']
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            f"User: {user.username}",
            styles['Normal']
        )
    )

    elements.append(
        Paragraph(
            f"Wellness Score: {wellness_score}%",
            styles['Normal']
        )
    )

    elements.append(
        Paragraph(
            f"Weekly Average Mood: {weekly_average}",
            styles['Normal']
        )
    )

    if latest_mood:

        elements.append(
            Paragraph(
                f"Current Emotion: {latest_mood.emotion}",
                styles['Normal']
            )
        )

        elements.append(
            Paragraph(
                f"Sleep Hours: {latest_mood.sleep_hours}",
                styles['Normal']
            )
        )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "AI Suggestions",
            styles['Heading2']
        )
    )

    for item in suggestions:

        elements.append(
            Paragraph(
                f"• {item}",
                styles['Normal']
            )
        )

    doc.build(elements)