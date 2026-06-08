def detect_emotion(text):

    text = text.lower()

    stressed_words = [

        "stress",
        "pressure",
        "tired",
        "exhausted",
        "overwhelmed",
        "burnout",
    ]

    sad_words = [

        "sad",
        "depressed",
        "cry",
        "lonely",
        "upset",
        "hurt",
    ]

    anxious_words = [

        "anxious",
        "panic",
        "fear",
        "nervous",
        "worried",
        "overthinking",
    ]

    happy_words = [

        "happy",
        "excited",
        "great",
        "good",
        "motivated",
        "amazing",
    ]


    # CHECK STRESSED
    for word in stressed_words:

        if word in text:

            return "stressed"

    # CHECK SAD
    for word in sad_words:

        if word in text:

            return "sad"

    # CHECK ANXIOUS
    for word in anxious_words:

        if word in text:

            return "anxious"

    # CHECK HAPPY
    for word in happy_words:

        if word in text:

            return "happy"

    return "neutral"



# =========================================
# WELLNESS SCORE AI
# =========================================

def calculate_wellness(

    mood_score,

    sleep_hours,

    emotion
):

    score = 50


    # Mood Score Effect
    score += mood_score * 5


    # Sleep Effect
    if sleep_hours >= 7:

        score += 15

    elif sleep_hours >= 5:

        score += 5

    else:

        score -= 15


    # Emotion Effect
    if emotion == "happy":

        score += 15

    elif emotion == "neutral":

        score += 5

    elif emotion == "sad":

        score -= 10

    elif emotion == "anxious":

        score -= 15

    elif emotion == "stressed":

        score -= 20


    # LIMIT RANGE
    if score > 100:

        score = 100

    if score < 0:

        score = 0


    return score