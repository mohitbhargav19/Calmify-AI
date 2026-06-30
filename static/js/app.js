document.addEventListener("contextmenu", e => e.preventDefault());

document.addEventListener("keydown", function(e){

    if(e.key === "F12"){
        e.preventDefault();
    }

    if(e.ctrlKey && e.shiftKey && e.key === "I"){
        e.preventDefault();
    }

    if(e.ctrlKey && e.shiftKey && e.key === "J"){
        e.preventDefault();
    }

    if(e.ctrlKey && e.key === "U"){
        e.preventDefault();
    }

});



document
.getElementById("assessmentForm")
.addEventListener("submit", async function(e){

    e.preventDefault();

    const payload = {

        age:
        parseFloat(
            document.getElementById("age").value
        ),

        gender:
        parseInt(
            document.getElementById("gender").value
        ),

        academic_pressure:
        parseFloat(
            document.getElementById(
                "academic_pressure"
            ).value
        ),

        exam_pressure:
        parseFloat(
            document.getElementById(
                "exam_pressure"
            ).value
        ),

        study_hours:
        parseFloat(
            document.getElementById(
                "study_hours"
            ).value
        ),

        sleep_hours:
        parseFloat(
            document.getElementById(
                "sleep_hours"
            ).value
        ),

        anxiety_score:
        parseFloat(
            document.getElementById(
                "anxiety_score"
            ).value
        ),

        depression_score:
        parseFloat(
            document.getElementById(
                "depression_score"
            ).value
        ),

        loneliness:
        parseFloat(
            document.getElementById(
                "loneliness"
            ).value
        ),

        screen_time_hours:
        parseFloat(
            document.getElementById(
                "screen_time_hours"
            ).value
        )

    };

    const response =
    await fetch(
        "/analyze/",
        {
            method:"POST",

            headers:{
                "Content-Type":
                "application/json"
            },

            body:
            JSON.stringify(payload)
        }
    );

    const data =
    await response.json();

    document
    .getElementById("resultBox")
    .innerHTML = `

        <h3>
        Wellness Score:
        ${data.dashboard.wellness_score}
        </h3>

        <h3>
        Stress Level:
        ${data.dashboard.stress_level}
        </h3>

        <h3>
        Burnout Score:
        ${data.dashboard.burnout_score}
        </h3>

        <p>
        ${data.dashboard.support_message}
        </p>

        <h4>
        Recommended Music
        </h4>

        <ul>

        ${data.dashboard.recommended_music
        .map(
            item =>
            `<li>${item}</li>`
        )
        .join("")}

        </ul>

        <h4>
        Recommended Activities
        </h4>

        <ul>

        ${data.dashboard.recommended_activities
        .map(
            item =>
            `<li>${item}</li>`
        )
        .join("")}

        </ul>

    `;
});

document.addEventListener("DOMContentLoaded", function () {

    const profileBtn = document.querySelector(".profile-btn");
    const dropdown = document.querySelector(".dropdown-content");

    if(profileBtn && dropdown){

        profileBtn.addEventListener("click", function(e){

            e.stopPropagation();

            dropdown.classList.toggle("show");

        });

        document.addEventListener("click", function(){

            dropdown.classList.remove("show");

        });

    }

});