document.addEventListener("DOMContentLoaded", function () {
    initDashboardChart();
    initSelfCareCards();
});


// =========================================
// CHART
// =========================================
function initDashboardChart() {
    const chartCanvas = document.getElementById("wellnessBarChart");
    if (!chartCanvas || !window.dashboardChartData) return;

    const data = window.dashboardChartData;

    new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: [
                "Burnout",
                "Wellness",
                "Stress Risk",
                "Student Stress"
            ],
            datasets: [{
                label: "Current Scores",
                data: [
                    Number(data.burnoutScore || 0),
                    Number(data.wellnessScore || 0),
                    Number(data.stressRiskScore || 0),
                    Number(data.studentStressLevel || 0)
                ],
                borderRadius: 12
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#ffffff"
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: "#ffffff"
                    },
                    grid: {
                        color: "rgba(255,255,255,0.08)"
                    }
                }
            }
        }
    });
}


// =========================================
// SELF CARE CARDS
// =========================================
function initSelfCareCards() {
    const cards = document.querySelectorAll(".self-care-card");
    cards.forEach((card, index) => {
        const body = card.querySelector(".self-care-body");
        if (!body) return;

        // first card open by default
        if (index === 0) {
            body.style.display = "block";
            card.classList.add("open");
        } else {
            body.style.display = "none";
        }
    });
}

function toggleSelfCareCard(headerEl) {
    const card = headerEl.closest(".self-care-card");
    if (!card) return;

    const body = card.querySelector(".self-care-body");
    if (!body) return;

    const isOpen = body.style.display === "block";

    if (isOpen) {
        body.style.display = "none";
        card.classList.remove("open");
    } else {
        body.style.display = "block";
        card.classList.add("open");
    }
}

function toggleAllSelfCare() {
    const cards = document.querySelectorAll(".self-care-card");
    if (!cards.length) return;

    const anyClosed = Array.from(cards).some(card => {
        const body = card.querySelector(".self-care-body");
        return body && body.style.display !== "block";
    });

    cards.forEach(card => {
        const body = card.querySelector(".self-care-body");
        if (!body) return;

        if (anyClosed) {
            body.style.display = "block";
            card.classList.add("open");
        } else {
            body.style.display = "none";
            card.classList.remove("open");
        }
    });
}