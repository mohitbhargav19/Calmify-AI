document.getElementById("moodForm").addEventListener("submit", async function(e) {

    e.preventDefault();

    const data = {
        mood_score: document.getElementById("mood_score").value,
        emotion: document.getElementById("emotion").value,
        journal_text: document.getElementById("journal_text").value,
        sleep_hours: document.getElementById("sleep_hours").value,
    };

    const response = await fetch("http://127.0.0.1:8000/api/moods/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    console.log(result);

    alert("Mood Submitted Successfully!");
});