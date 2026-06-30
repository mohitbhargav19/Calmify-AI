"use strict";

/* ==========================================================
   Calmify AI Assessment
   Phase 1
   Initialization
========================================================== */

/* ==========================================================
   DOM References
========================================================== */

const form = document.getElementById("assessmentForm");

const loader = document.getElementById("loader");

const resultCard = document.getElementById("resultCard");

const progressBar = document.getElementById("progressBar");

const step2Container =
    document.getElementById("step2Questions");

const step3Container =
    document.getElementById("step3Questions");

const stepPills =
    document.querySelectorAll(".step-pill");


/* ==========================================================
   API Endpoints
========================================================== */

const QUESTIONS_API =
    "/api/assessment/questions/";

const SUBMIT_API =
    "/api/assessment/submit/";


/* ==========================================================
   Global State
========================================================== */

let currentStep = 1;

let loading = false;

let totalQuestions = 0;

let profileQuestions = [];

let assessmentSections = [];

let responses = {};


/* ==========================================================
   Initialisation
========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    initialiseAssessment

);

async function initialiseAssessment() {

    try {

        showLoader("Loading assessment...");

        initialiseNavigation();

        await loadQuestions();

        restoreDraft();

        updateProgress();

    }

    catch (error) {

    console.error(error);

    alert(error.message);

}

    finally {

        hideLoader();

    }

}


/* ==========================================================
   Loader
========================================================== */

function showLoader(message = "Loading...") {

    if (!loader) return;

    loader.style.display = "flex";

    const text =
        loader.querySelector("span");

    if (text) {

        text.textContent = message;

    }

}

function hideLoader() {

    if (!loader) return;

    loader.style.display = "none";

}


/* ==========================================================
   Fetch Questions
========================================================== */

async function loadQuestions() {

    const response =
        await fetch(QUESTIONS_API);

    if (!response.ok) {

        throw new Error(
            `Question API returned ${response.status}`
        );

    }

    const json =
        await response.json();

    if (!json.success) {

        throw new Error(

            json.message ||

            "Unable to load assessment."

        );

    }

    profileQuestions =
        json.data.profile_questions || [];

    assessmentSections =
        json.data.assessment_sections || [];

    renderAssessment();

}


/* ==========================================================
   Render Assessment
========================================================== */

function renderAssessment() {

    step2Container.innerHTML = "";

    step3Container.innerHTML = "";

    totalQuestions = 0;

    assessmentSections.forEach((section, index) => {

        const container =
            index === 0
                ? step2Container
                : step3Container;

        const title =
            document.createElement("h3");

        title.className =
            "assessment-section-title";

        title.textContent =
            section.section_title;

        container.appendChild(title);

        section.questions.forEach(question => {

            totalQuestions++;

            container.appendChild(

                createQuestion(question)

            );

        });

    });

}

/* ==========================================================
   Create Question
========================================================== */

function createQuestion(question) {

    const wrapper =
        document.createElement("div");

    wrapper.className = "premium-field";

    const label =
        document.createElement("label");

    label.setAttribute("for", question.key);

    label.innerHTML =

        question.label +

        (question.required
            ? " <span class='required'>*</span>"
            : "");

    wrapper.appendChild(label);

    const type =
        (question.type || "text").toLowerCase();

    switch (type) {

        case "text":
        case "number":
        case "email":
        case "date":
        case "time":

            return createInput(wrapper, question);

        case "textarea":

            return createTextarea(wrapper, question);

        case "select":

            return createSelectField(wrapper, question);

        case "radio":

            return createRadioField(wrapper, question);

        case "checkbox":

            return createCheckboxField(wrapper, question);

        case "slider":
        case "scale":
        case "likert":

            return createSliderField(wrapper, question);

        default:

            return createInput(wrapper, question);

    }

}

/* ==========================================================
   Input
========================================================== */

function createInput(wrapper, question) {

    const input =
        document.createElement("input");

    input.type = question.type || "text";

    input.id = question.key;

    input.name = question.key;

    input.className = "assessment-input";

    input.required = !!question.required;

    input.placeholder =
        question.placeholder || "";

    if (question.min !== undefined)
        input.min = question.min;

    if (question.max !== undefined)
        input.max = question.max;

    if (question.step !== undefined)
        input.step = question.step;

    input.addEventListener(

        "input",

        autoSave

    );

    wrapper.appendChild(input);

    return wrapper;

}

/* ==========================================================
   Textarea
========================================================== */

function createTextarea(wrapper, question) {

    const textarea =
        document.createElement("textarea");

    textarea.id = question.key;

    textarea.name = question.key;

    textarea.rows = question.rows || 4;

    textarea.required = !!question.required;

    textarea.placeholder =
        question.placeholder || "";

    textarea.className =
        "assessment-input";

    textarea.addEventListener(

        "input",

        autoSave

    );

    wrapper.appendChild(textarea);

    return wrapper;

}

/* ==========================================================
   Select
========================================================== */

function createSelectField(wrapper, question) {

    const select =
        document.createElement("select");

    select.id = question.key;

    select.name = question.key;

    select.required = !!question.required;

    select.className =
        "assessment-input";

    const first =
        document.createElement("option");

    first.value = "";

    first.textContent = "Select";

    select.appendChild(first);

    (question.options || []).forEach(option => {

        const opt =
            document.createElement("option");

        if (typeof option === "object") {

            opt.value = option.value;

            opt.textContent = option.label;

        }

        else {

            opt.value = option;

            opt.textContent = option;

        }

        select.appendChild(opt);

    });

    select.addEventListener(

        "change",

        autoSave

    );

    wrapper.appendChild(select);

    return wrapper;

}

/* ==========================================================
   Radio
========================================================== */

function createRadioField(wrapper, question) {

    const group =
        document.createElement("div");

    group.className = "option-group";

    (question.options || []).forEach(option => {

        const value =
            typeof option === "object"
                ? option.value
                : option;

        const text =
            typeof option === "object"
                ? option.label
                : option;

        const label =
            document.createElement("label");

        label.className = "option-item";

        label.innerHTML = `

            <input
                type="radio"
                name="${question.key}"
                value="${value}"
            >

            <span>${text}</span>

        `;

        label.querySelector("input")

            .addEventListener(

                "change",

                autoSave

            );

        group.appendChild(label);

    });

    wrapper.appendChild(group);

    return wrapper;

}

/* ==========================================================
   Checkbox
========================================================== */

function createCheckboxField(wrapper, question) {

    const group =
        document.createElement("div");

    group.className = "option-group";

    (question.options || []).forEach(option => {

        const value =
            typeof option === "object"
                ? option.value
                : option;

        const text =
            typeof option === "object"
                ? option.label
                : option;

        const label =
            document.createElement("label");

        label.className = "option-item";

        label.innerHTML = `

            <input
                type="checkbox"
                name="${question.key}"
                value="${value}"
            >

            <span>${text}</span>

        `;

        label.querySelector("input")

            .addEventListener(

                "change",

                autoSave

            );

        group.appendChild(label);

    });

    wrapper.appendChild(group);

    return wrapper;

}

/* ==========================================================
   Slider
========================================================== */

function createSliderField(wrapper, question) {

    const container =
        document.createElement("div");

    container.className =
        "slider-container";

    const slider =
        document.createElement("input");

    slider.type = "range";

    slider.id = question.key;

    slider.name = question.key;

    slider.min = question.min ?? 0;

    slider.max = question.max ?? 10;

    slider.step = question.step ?? 1;

    slider.value = question.default ?? slider.min;

    slider.className =
        "assessment-slider";

    const value =
        document.createElement("span");

    value.className =
        "slider-value";

    value.textContent = slider.value;

    slider.addEventListener(

        "input",

        () => {

            value.textContent = slider.value;

            autoSave();

        }

    );

    container.appendChild(slider);

    container.appendChild(value);

    wrapper.appendChild(container);

    return wrapper;

}

/* ==========================================================
   Navigation
========================================================== */

function initialiseNavigation() {

    document
        .querySelectorAll(".next-step-btn")
        .forEach(button => {

            button.addEventListener("click", () => {

                if (!validateStep(currentStep))
                    return;

                showStep(

                    Number(button.dataset.next)

                );

            });

        });

    document
        .querySelectorAll(".prev-step-btn")
        .forEach(button => {

            button.addEventListener("click", () => {

                showStep(

                    Number(button.dataset.prev)

                );

            });

        });

    showStep(1);

}

/* ==========================================================
   Step Switching
========================================================== */

function showStep(step) {

    document

        .querySelectorAll(".assessment-step")

        .forEach(section =>

            section.classList.remove("active-step")

        );

    document

        .getElementById(`step-${step}`)

        ?.classList.add("active-step");

    currentStep = step;

    stepPills.forEach((pill, index) => {

        pill.classList.toggle(

            "active",

            index < step

        );

    });

    updateProgress();

}

/* ==========================================================
   Validation
========================================================== */

function validateStep(step) {

    const container =

        document.getElementById(

            `step-${step}`

        );

    if (!container)
        return true;

    const requiredFields =

        container.querySelectorAll(

            "[required]"

        );

    for (const field of requiredFields) {

        if (

            field.type === "radio"

        ) {

            const checked =

                container.querySelector(

                    `input[name="${field.name}"]:checked`

                );

            if (!checked) {

                alert("Please answer all required questions.");

                return false;

            }

            continue;

        }

        if (

            field.type === "checkbox"

        ) {

            const checked =

                container.querySelectorAll(

                    `input[name="${field.name}"]:checked`

                );

            if (!checked.length) {

                alert("Please answer all required questions.");

                return false;

            }

            continue;

        }

        if (

            field.value === ""

        ) {

            field.focus();

            alert("Please complete all required fields.");

            return false;

        }

    }

    return true;

}

/* ==========================================================
   Autosave
========================================================== */

function autoSave() {

    saveDraft();

    updateProgress();

}

/* ==========================================================
   Progress
========================================================== */

function updateProgress() {

    let total = 0;

    let completed = 0;

    document

        .querySelectorAll(

            "#step-1 input,#step-1 select"

        )

        .forEach(field => {

            total++;

            if (field.value !== "")

                completed++;

        });

    assessmentSections.forEach(section => {

        section.questions.forEach(question => {

            total++;

            const type =

                (question.type || "")

                .toLowerCase();

            if (

                type === "slider" ||

                type === "scale" ||

                type === "likert"

            ) {

                const slider =

                    document.getElementById(

                        question.key

                    );

                if (slider)

                    completed++;

                return;

            }

            if (type === "radio") {

                const checked =

                    document.querySelector(

                        `input[name="${question.key}"]:checked`

                    );

                if (checked)

                    completed++;

                return;

            }

            if (type === "checkbox") {

                const checked =

                    document.querySelectorAll(

                        `input[name="${question.key}"]:checked`

                    );

                if (checked.length)

                    completed++;

                return;

            }

            const field =

                document.getElementById(

                    question.key

                );

            if (

                field &&

                field.value !== ""

            )

                completed++;

        });

    });

    const percentage =

        total === 0

            ? 0

            : Math.round(

                (completed / total) * 100

            );

    progressBar.style.width =

        percentage + "%";

}

/* ==========================================================
   Save Draft
========================================================== */

function saveDraft() {

    localStorage.setItem(

        "assessmentDraft",

        JSON.stringify(

            buildPayload()

        )

    );

}

/* ==========================================================
   Restore Draft
========================================================== */

function restoreDraft() {

    const raw =

        localStorage.getItem(

            "assessmentDraft"

        );

    if (!raw)
        return;

    const draft =

        JSON.parse(raw);

    Object.entries(

        draft.profile || {}

    ).forEach(([key, value]) => {

        const field =

            document.getElementById(key);

        if (field)

            field.value = value;

    });

    Object.entries(

        draft.answers || {}

    ).forEach(([key, value]) => {

        if (

            Array.isArray(value)

        ) {

            value.forEach(v => {

                document.querySelector(

                    `input[name="${key}"][value="${v}"]`

                )?.click();

            });

            return;

        }

        const radio =

            document.querySelector(

                `input[name="${key}"][value="${value}"]`

            );

        if (radio) {

            radio.checked = true;

            return;

        }

        const field =

            document.getElementById(key);

        if (field) {

            field.value = value;

            if (

                field.type === "range"

            ) {

                const valueLabel =

                    field.parentElement.querySelector(

                        ".slider-value"

                    );

                if (valueLabel)

                    valueLabel.textContent = value;

            }

        }

    });

    updateProgress();

}

/* ==========================================================
   Reset
========================================================== */

function resetAssessment() {

    form.reset();

    localStorage.removeItem(

        "assessmentDraft"

    );

    currentStep = 1;

    showStep(1);

    updateProgress();

    resultCard.style.display = "none";

}

/* ==========================================================
   PHASE 4
   Payload Builder + Submit
========================================================== */

function buildPayload() {

    const profile = {

        name:
            document.getElementById("name")?.value.trim() || "",

        age:
            Number(document.getElementById("age")?.value || 0),

        gender:
            document.getElementById("gender")?.value || "",

        college_year:
            document.getElementById("college_year")?.value || "",

        course:
            document.getElementById("course")?.value.trim() || ""

    };

    const answers = {};

    assessmentSections.forEach(section => {

        section.questions.forEach(question => {

            const key = question.key;

            const type = (question.type || "text").toLowerCase();

            // ===========================
            // Slider
            // ===========================

            if (
                type === "slider" ||
                type === "scale" ||
                type === "likert"
            ) {

                const slider =
                    document.getElementById(key);

                answers[key] = slider
                    ? Number(slider.value)
                    : null;

                return;
            }

            // ===========================
            // Radio
            // ===========================

            if (type === "radio") {

                const checked =
                    document.querySelector(
                        `input[name="${key}"]:checked`
                    );

                answers[key] =
                    checked
                        ? Number(checked.value)
                        : null;

                return;
            }

            // ===========================
            // Checkbox
            // ===========================

            if (type === "checkbox") {

                answers[key] = Array.from(

                    document.querySelectorAll(
                        `input[name="${key}"]:checked`
                    )

                ).map(item => item.value);

                return;
            }

            // ===========================
            // Select
            // ===========================

            if (type === "select") {

                const select =
                    document.getElementById(key);

                answers[key] =
                    select
                        ? select.value
                        : "";

                return;
            }

            // ===========================
            // Text / Number / Textarea
            // ===========================

            const field =
                document.getElementById(key);

            if (!field) {

                answers[key] = "";

                return;
            }

            if (type === "number") {

                answers[key] =
                    field.value === ""
                        ? null
                        : Number(field.value);

            }

            else {

                answers[key] = field.value.trim();

            }

        });

    });

    return {

        profile,

        answers

    };

}

form.addEventListener(
    "submit",
    submitAssessment
);

async function submitAssessment(e) {

    e.preventDefault();

    if (loading) return;

    if (!validateStep(currentStep))
        return;

    loading = true;

    showLoader("Analyzing your responses...");

    try {

        const payload = buildPayload();

        console.log(payload);

        const response = await fetch(
            SUBMIT_API,
            {
                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "X-CSRFToken": getCSRFToken()

                },

                body: JSON.stringify(payload)

            }
        );

        const result = await response.json();

        console.log(result);

        if (!response.ok || !result.success) {

            throw new Error(
                result.message || "Assessment failed."
            );

        }

        localStorage.removeItem("assessmentDraft");

        if (result.redirect_url) {
            window.location.href = result.redirect_url;
            } else {
                window.location.href = "/dashboard/";
                }
                

    }

    catch (error) {

        console.error(error);

        alert(error.message);

    }

    finally {

        loading = false;

        hideLoader();

    }

}

function getCSRFToken() {

    const csrf =
        document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

    return csrf
        ? csrf.value
        : "";

}

