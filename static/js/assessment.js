/* ==========================================================================
   Calmify AI
   assessment.js

   Module 1
   --------------------------------------------------------------------------
   Configuration / Constants / Global State
   ========================================================================= */

"use strict";

const APP = Object.freeze({
    NAME: "Calmify AI",
    VERSION: "2.0.0",
    DEBUG: true,
    AUTO_SAVE_INTERVAL: 30000,
    MAX_TEXTAREA_LENGTH: 5000,
    PROGRESS_STEPS: 3
});

const API = Object.freeze({
    QUESTIONS: "/api/assessment/questions/",
    SUBMIT: "/api/assessment/submit/"
});

const STEP = Object.freeze({
    PROFILE: 1,
    LIFESTYLE: 2,
    MENTAL_HEALTH: 3,
    TOTAL: 3
});

const SECTION_MAP = Object.freeze({
    PROFILE: [],
    LIFESTYLE: [
        "daily_wellness",
        "stress_burnout"
    ],
    MENTAL_HEALTH: [
        "mental_health_core",
        "student_context",
        "music_habits",
        "music_frequency_matrix",
        "music_effects_section",
        "detailed_stress_symptoms"
    ]
});

const VALIDATION = Object.freeze({
    REQUIRED_CLASS: "field-required",
    INVALID_CLASS: "field-invalid",
    ERROR_CLASS: "validation-error"
});

const STORAGE = Object.freeze({
    DRAFT: "calmify_assessment_draft",
    PROFILE: "calmify_profile"
});

const MESSAGE = Object.freeze({
    LOADING: "Loading assessment...",
    LOAD_ERROR: "Unable to load assessment.",
    SAVED: "Draft saved.",
    SUBMITTING: "Submitting assessment...",
    SUCCESS: "Assessment completed successfully.",
    VALIDATION: "Please complete all required questions."
});

const STATE = {
    initialized: false,
    loading: false,
    submitting: false,
    savingDraft: false,
    currentStep: STEP.PROFILE,
    currentSectionIndex: 0,
    profileQuestions: [],
    assessmentSections: [],
    lifestyleSections: [],
    mentalHealthSections: [],
    profileAnswers: {},
    assessmentAnswers: {},
    validationErrors: {},
    questionIndex: {},
    sectionsById: {},
    totalQuestions: 0,
    answeredQuestions: 0,
    dashboard: null,
    draftLoaded: false,
    lastAutoSave: null
};

const Logger = {
    log(...args) {
        if (!APP.DEBUG) return;
        console.log("[Calmify]", ...args);
    },
    warn(...args) {
        if (!APP.DEBUG) return;
        console.warn("[Calmify]", ...args);
    },
    error(...args) {
        console.error("[Calmify]", ...args);
    }
};

/* ==========================================================================
   Module 2
   --------------------------------------------------------------------------
   DOM Cache / Initialization Loader
   ========================================================================== */

const DOM = {
    form: null,
    container: null,
    assessmentContainer: null,
    profileContainer: null,
    questionContainer: null,
    sectionContainer: null,
    navigationContainer: null,
    pageTitle: null,
    pageSubtitle: null,
    stepButtons: [],
    progressBar: null,
    previousButton: null,
    nextButton: null,
    submitButton: null,
    resultContainer: null,
    resultCard: null,
    loadingOverlay: null,
    stepPills: []
};

function byId(id) {
    return document.getElementById(id);
}

function byClass(className) {
    return Array.from(document.getElementsByClassName(className));
}

function cacheDOM() {
    Logger.log("Caching DOM...");
    DOM.form = byId("assessmentForm");
    DOM.container = byId("assessment");
    DOM.assessmentContainer = byId("assessmentContainer");
    DOM.profileContainer = byId("profileContainer");
    DOM.questionContainer = byId("questionContainer");
    DOM.sectionContainer = byId("sectionContainer");
    DOM.navigationContainer = byId("navigationContainer");
    DOM.pageTitle = byId("assessmentTitle");
    DOM.pageSubtitle = byId("assessmentSubtitle");
    DOM.progressBar = byId("progressFill");
    DOM.previousButton = byId("previousButton");
    DOM.nextButton = byId("nextButton");
    DOM.submitButton = byId("submitButton");
    DOM.resultContainer = byId("resultContainer");
    DOM.resultCard = byId("resultCard");
    DOM.loadingOverlay = byId("loadingOverlay");
    DOM.stepButtons = byClass("assessment-step");
    DOM.stepPills = byClass("step-pill");
    Logger.log("DOM Cached.");
}

function verifyDOM() {
    const required = ["form", "progressBar"];
    required.forEach(name => {
        if (!DOM[name]) {
            Logger.warn(`DOM element validation warning: ${name} not found.`);
        }
    });
}

function showLoader(message = MESSAGE.LOADING) {
    if (DOM.loadingOverlay) {
        DOM.loadingOverlay.style.display = "flex";
    }
}

function hideLoader() {
    if (DOM.loadingOverlay) {
        DOM.loadingOverlay.style.display = "none";
    }
}

/* ==========================================================================
   Module 3
   --------------------------------------------------------------------------
   Question API & Parse Lookups
   ========================================================================== */

async function loadQuestions() {
    Logger.log("Loading assessment questions...");
    STATE.loading = true;
    showLoader(MESSAGE.LOADING);
    try {
        const response = await fetch(API.QUESTIONS, {
            method: "GET",
            credentials: "same-origin",
            headers: { "Accept": "application/json" }
        });
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }
        const json = await response.json();
        if (!json.success) {
            throw new Error(json.message || MESSAGE.LOAD_ERROR);
        }
        parseBackendData(json.data);
        renderAssessment();
        Logger.log("Questions loaded successfully.");
    } finally {
        STATE.loading = false;
        hideLoader();
    }
}

function parseBackendData(data) {
    resetQuestionState();
    STATE.profileQuestions = Array.isArray(data.profile_questions) ? data.profile_questions : [];
    STATE.assessmentSections = Array.isArray(data.assessment_sections) ? data.assessment_sections : [];
    buildSectionLookup();
    buildQuestionLookup();
    splitSections();
    calculateQuestionCount();
}

function resetQuestionState() {
    STATE.profileQuestions = [];
    STATE.assessmentSections = [];
    STATE.sectionsById = {};
    STATE.questionIndex = {};
    STATE.lifestyleSections = [];
    STATE.mentalHealthSections = [];
    STATE.totalQuestions = 0;
}

function buildSectionLookup() {
    STATE.assessmentSections.forEach(section => {
        STATE.sectionsById[section.section_id] = section;
    });
}

function buildQuestionLookup() {
    STATE.profileQuestions.forEach(section => {
        (section.questions || []).forEach(question => {
            STATE.questionIndex[question.key] = question;
        });
    });
    STATE.assessmentSections.forEach(section => {
        (section.questions || []).forEach(question => {
            STATE.questionIndex[question.key] = question;
        });
    });
}

function splitSections() {
    STATE.lifestyleSections = STATE.assessmentSections.filter(section =>
        SECTION_MAP.LIFESTYLE.includes(section.section_id)
    );
    STATE.mentalHealthSections = STATE.assessmentSections.filter(section =>
        SECTION_MAP.MENTAL_HEALTH.includes(section.section_id)
    );
}

function calculateQuestionCount() {
    let total = 0;
    STATE.profileQuestions.forEach(section => { total += (section.questions || []).length; });
    STATE.assessmentSections.forEach(section => { total += (section.questions || []).length; });
    STATE.totalQuestions = total;
}

function getProfileQuestions() { return STATE.profileQuestions; }

function getLifestyleSections() { return STATE.lifestyleSections; }
function getMentalHealthSections() { return STATE.mentalHealthSections; }

/* ==========================================================================
   Module 4
   --------------------------------------------------------------------------
   Rendering Engine
   ========================================================================== */

function renderAssessment() {
    Logger.log("Rendering assessment...");
    renderProfile();
    renderLifestyle();
    renderMentalHealth();
    updateProgress();
}

function renderProfile() {
    const profileContainer = document.getElementById("step1Questions");
    if (!profileContainer) return;
    clearElement(profileContainer);
    const sections = getProfileQuestions();
    sections.forEach(section => {
        profileContainer.appendChild(renderSection(section));
    });
}

function renderLifestyle() {
    const lifestyleContainer = document.getElementById("step2Questions");
    if (!lifestyleContainer) return;
    clearElement(lifestyleContainer);
    const sections = getLifestyleSections();
    sections.forEach(section => {
        lifestyleContainer.appendChild(renderSection(section));
    });
}

function renderMentalHealth() {
    const mentalContainer = document.getElementById("step3Questions");
    if (!mentalContainer) return;
    clearElement(mentalContainer);
    const sections = getMentalHealthSections();
    sections.forEach(section => {
        mentalContainer.appendChild(renderSection(section));
    });
}

function renderSection(section) {
    const wrapper = createElement("div", "assessment-section");
    if (section.section_title) {
        const heading = createElement("h3", "section-title");
        heading.textContent = section.section_title;
        wrapper.appendChild(heading);
    }
    if (section.description) {
        const description = createElement("p", "section-description");
        description.textContent = section.description;
        wrapper.appendChild(description);
    }
    (section.questions || []).forEach(question => {
        wrapper.appendChild(renderQuestion(question));
    });
    return wrapper;
}

function renderQuestion(question) {
    const card = createElement("div", "question-card");
    card.dataset.key = question.key;
    const label = createElement("label", "question-label");
    label.setAttribute("for", question.key);
    label.textContent = question.label || "";

    if (question.required) {
        const required = createElement("span", "required");
        required.textContent = " *";
        label.appendChild(required);
    }
    card.appendChild(label);

    const controlWrapper = createElement("div", "question-control");
    controlWrapper.appendChild(createControl(question));
    card.appendChild(controlWrapper);

    if (question.help_text) {
        const help = createElement("small", "question-help");
        help.textContent = question.help_text;
        card.appendChild(help);
    }
    return card;
}

/* ==========================================================================
   Module 5
   --------------------------------------------------------------------------
   Control Factory
   ========================================================================== */

function createControl(question) {
    const type = (question.type || "text").toLowerCase();
    switch (type) {
        case "text":
        case "email":
        case "number":
        case "date":
        case "time":
            return createInput(question);
        case "textarea":
            return createTextarea(question);
        case "select":
            return createSelect(question);
        case "radio":
            return createRadioGroup(question);
        case "checkbox":
            return createCheckboxGroup(question);
        case "slider":
        case "scale":
        case "likert":
            return createSlider(question);
        default:
            return createInput(question);
    }
}

function createInput(question) {
    const input = createElement("input", "assessment-input");
    input.type = question.type || "text";
    input.id = question.key;
    input.name = question.key;
    input.placeholder = question.placeholder || "";
    if (question.required) input.required = true;
    if (question.min !== undefined) input.min = question.min;
    if (question.max !== undefined) input.max = question.max;
    if (question.step !== undefined) input.step = question.step;
    if (question.default !== undefined) input.value = question.default;
    return input;
}

function createTextarea(question) {
    const textarea = createElement("textarea", "assessment-textarea");
    textarea.id = question.key;
    textarea.name = question.key;
    textarea.rows = question.rows || 5;
    textarea.placeholder = question.placeholder || "";
    if (question.required) textarea.required = true;
    return textarea;
}

function createSelect(question) {
    const select = createElement("select", "assessment-select");
    select.id = question.key;
    select.name = question.key;
    if (question.required) select.required = true;
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = question.placeholder || "Select an option";
    select.appendChild(placeholder);
    (question.options || []).forEach(option => {
        const opt = document.createElement("option");
        if (typeof option === "object") {
            opt.value = option.value;
            opt.textContent = option.label;
        } else {
            opt.value = option;
            opt.textContent = option;
        }
        select.appendChild(opt);
    });
    return select;
}

function createRadioGroup(question) {
    const wrapper = createElement("div", "option-group");
    (question.options || []).forEach(option => {
        const label = createElement("label", "option-item");
        const input = document.createElement("input");
        input.type = "radio";
        input.name = question.key;
        input.id = `${question.key}_${String(option.value || option).replace(/\s+/g, "_")}`;
        input.value = typeof option === "object" ? option.value : option;
        if (question.required) input.required = true;

        const span = document.createElement("span");
        span.textContent = typeof option === "object" ? option.label : option;
        label.appendChild(input);
        label.appendChild(span);
        wrapper.appendChild(label);
    });
    return wrapper;
}

function createCheckboxGroup(question) {
    const wrapper = createElement("div", "option-group");
    (question.options || []).forEach(option => {
        const label = createElement("label", "option-item");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.name = question.key;
        input.id = `${question.key}_${String(option.value || option).replace(/\s+/g, "_")}`;
        input.value = typeof option === "object" ? option.value : option;

        const span = document.createElement("span");
        span.textContent = typeof option === "object" ? option.label : option;
        label.appendChild(input);
        label.appendChild(span);
        wrapper.appendChild(label);
    });
    return wrapper;
}

function createSlider(question) {
    const wrapper = createElement("div", "slider-container");
    const slider = document.createElement("input");
    slider.type = "range";
    slider.className = "assessment-slider";
    slider.id = question.key;
    slider.name = question.key;
    slider.min = question.min ?? 0;
    slider.max = question.max ?? 10;
    slider.step = question.step ?? 1;
    slider.value = question.default ?? question.min ?? 0;

    const value = createElement("span", "slider-value");
    value.textContent = slider.value;
    slider.addEventListener("input", () => {
        value.textContent = slider.value;
        updateProgress();
    });
    wrapper.appendChild(slider);
    wrapper.appendChild(value);
    return wrapper;
}

/* ==========================================================================
   Module 6
   --------------------------------------------------------------------------
   Navigation Layer
   ========================================================================== */

function initialiseNavigation() {
    document
        .querySelectorAll(".next-step-btn")
        .forEach(btn => {
            btn.addEventListener("click", handleNextStep);
        });

    document
        .querySelectorAll(".prev-step-btn")
        .forEach(btn => {
            btn.addEventListener("click", handlePreviousStep);
        });
}

function showStep(step) {
    STATE.currentStep = step;
    document.querySelectorAll(".assessment-step").forEach(section => {
        section.classList.remove("active-step");
        section.style.display = "none";
    });
    const activeStep = document.getElementById(`step-${step}`);
    if (activeStep) {
        activeStep.classList.add("active-step");
        activeStep.style.display = "block";
    }
    updateStepIndicator();
    updateProgress();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function handleNextStep(event) {
    event.preventDefault();

    if (!validateStep(STATE.currentStep)) {
        return;
    }

    saveDraft();

    const nextStep = Number(
        event.currentTarget.dataset.next
    );

    if (!nextStep) return;

    showStep(nextStep);
}

function handlePreviousStep(event) {
    event.preventDefault();
    saveDraft();
    const previous = Number(event.currentTarget.dataset.prev);
    if (previous >= STEP.PROFILE && previous <= STEP.TOTAL) {
        showStep(previous);
    }
}

function updateStepIndicator() {
    if (!DOM.stepPills || DOM.stepPills.length === 0) return;
    DOM.stepPills.forEach((pill, index) => {
        const pillStep = index + 1;
        pill.classList.remove("active", "completed");
        if (pillStep === STATE.currentStep) {
            pill.classList.add("active");
        } else if (pillStep < STATE.currentStep) {
            pill.classList.add("completed");
        }
    });
}

/* ==========================================================================
   Module 7
   --------------------------------------------------------------------------
   Validation Layer
   ========================================================================== */

function validateStep(step) {
    const container = document.getElementById(`step-${step}`);
    if (!container) return true;
    clearValidationErrors();

    const requiredQuestions = container.querySelectorAll("[required]");
    for (const field of requiredQuestions) {
        if (!validateField(field)) {
            markFieldInvalid(field);
            field.scrollIntoView({ behavior: "smooth", block: "center" });
            try { field.focus(); } catch (_) {}
            notify("Please answer all required questions before continuing.", "warning");
            return false;
        }
    }
    return true;
}

function validateField(field) {
    if (!field) return true;
    const type = (field.type || "").toLowerCase();

    if (type === "radio") {
        return !!document.querySelector(`input[name="${field.name}"]:checked`);
    }
    if (type === "checkbox") {
        return document.querySelectorAll(`input[name="${field.name}"]:checked`).length > 0;
    }
    if (field.tagName === "SELECT") {
        return field.value !== "";
    }
    if (field.tagName === "TEXTAREA") {
        return field.value.trim().length > 0;
    }
    if (type === "number") {
        if (field.value === "") return false;
        const value = Number(field.value);
        if (Number.isNaN(value)) return false;
        if (field.min !== "" && value < Number(field.min)) return false;
        if (field.max !== "" && value > Number(field.max)) return false;
        return true;
    }
    if (type === "range") return true;
    
    // Bulletproof string value fallback checks
    return field.value && typeof field.value.trim === 'function' ? field.value.trim() !== "" : !!field.value;
}

function markFieldInvalid(field) {
    if (!field) return;
    field.classList.add("input-error");
}

function removeFieldError(field) {
    if (!field) return;
    field.classList.remove("input-error");
}

function clearValidationErrors() {
    document.querySelectorAll(".input-error").forEach(el => el.classList.remove("input-error"));
}

function validateEntireAssessment() {
    for (let step = STEP.PROFILE; step <= STEP.TOTAL; step++) {
        if (!validateStep(step)) {
            showStep(step);
            return false;
        }
    }
    return true;
}

/* ==========================================================================
   Module 8
   --------------------------------------------------------------------------
   Payload Builder
   ========================================================================== */

function buildPayload() {
    const profile = {};
    const assessment = {};

    (STATE.profileQuestions || []).forEach(section => {
        (section.questions || []).forEach(question => {
            if (question.key === "city" || question.key === "college") return;
            profile[question.key] = getQuestionValue(question);
        });
    });

    (STATE.assessmentSections || []).forEach(section => {
        (section.questions || []).forEach(question => {
            assessment[question.key] = getQuestionValue(question);
        });
    });

    return { profile, assessment };
}

function getQuestionValue(question) {
    const key = question.key;
    const type = (question.type || "text").toLowerCase();

    if (type === "radio") {
        const checked = document.querySelector(`input[name="${key}"]:checked`);
        return checked ? (isNaN(checked.value) || checked.value === "" ? checked.value : Number(checked.value)) : null;
    }
    if (type === "checkbox") {
        return Array.from(document.querySelectorAll(`input[name="${key}"]:checked`)).map(item => 
            isNaN(item.value) || item.value === "" ? item.value : Number(item.value)
        );
    }
    if (["slider", "scale", "likert", "range"].includes(type)) {
        const slider = document.getElementById(key);
        return slider ? Number(slider.value) : null;
    }

    const field = document.getElementById(key);
    if (!field) return null;

    const trimmedValue = field.value.trim();
    if (trimmedValue === "") return null; // Convert blank entries to null so the backend handles nullable states correctly

    // Force conversion if the entry is strictly numeric, even if the element type is a select dropdown or standard text
    if (!isNaN(trimmedValue) && trimmedValue !== "") {
        return Number(trimmedValue);
    }

    return trimmedValue;
}

/* ==========================================================================
   Module 9
   --------------------------------------------------------------------------
   Submission Layer
   ========================================================================== */

async function submitAssessment(event) {
    if (event) event.preventDefault();
    if (STATE.submitting) return;
    if (!validateEntireAssessment()) return;

    STATE.submitting = true;
    showLoader("Submitting assessment...");

    try {
        const payload = buildPayload();
        const response = await fetch(API.SUBMIT, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
                "Accept": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const json = await response.json();
        if (!response.ok || !json.success) {
            throw new Error(json.message || "Assessment submission failed.");
        }
        clearDraft();
        handleSubmissionSuccess(json);
    } catch (error) {
        console.error(error);
        notify(error.message || "Unable to submit assessment.", "error");
    } finally {
        STATE.submitting = false;
        hideLoader();
    }
}

function handleSubmissionSuccess(response) {
    Logger.log("Submission successful. Redirecting user to analysis dashboard...");
    
    // Check if the backend gave an explicit URL redirect, otherwise default straight to '/dashboard/'
    if (response.redirect_url) { 
        window.location.href = response.redirect_url; 
        return; 
    }
    if (response.dashboard_url) { 
        window.location.href = response.dashboard_url; 
        return; 
    }
    
    // Direct absolute fallback redirection to dashboard route
    window.location.href = "/dashboard/";
}

function getCSRFToken() {
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrf) return csrf.value;
    const cookie = document.cookie.split(";").map(c => c.trim()).find(c => c.startsWith("csrftoken="));
    return cookie ? cookie.substring("csrftoken=".length) : "";
}

/* ==========================================================================
   Module 10
   --------------------------------------------------------------------------
   Draft Management Layer
   ========================================================================== */

function saveDraft() {
    try {
        const payload = buildPayload();
        localStorage.setItem(STORAGE.DRAFT, JSON.stringify(payload));
    } catch (error) {
        console.warn("Unable to save assessment draft.", error);
    }
}

function restoreDraft() {
    try {
        const raw = localStorage.getItem(STORAGE.DRAFT);
        if (!raw) return;
        const draft = JSON.parse(raw);
        restoreGroupAnswers(draft.profile || {});
        restoreGroupAnswers(draft.assessment || {});
        updateProgress();
    } catch (error) {
        console.warn("Unable to restore assessment draft.", error);
    }
}

function clearDraft() {
    localStorage.removeItem(STORAGE.DRAFT);
}

function restoreGroupAnswers(group) {
    Object.entries(group).forEach(([key, value]) => {
        if (value === null || value === undefined) return;
        const radio = document.querySelector(`input[name="${key}"][value="${value}"]`);
        if (radio) { radio.checked = true; return; }

        if (Array.isArray(value)) {
            value.forEach(item => {
                const cb = document.querySelector(`input[name="${key}"][value="${item}"]`);
                if (cb) cb.checked = true;
            });
            return;
        }

        const field = document.getElementById(key);
        if (field) {
            field.value = value;
            if (field.type === "range") {
                const label = field.parentElement.querySelector(".slider-value");
                if (label) label.textContent = value;
            }
        }
    });
}

/* ==========================================================================
   Module 11
   --------------------------------------------------------------------------
   Progress Management Engine
   ========================================================================== */

function updateProgress() {
    const percent = calculateProgress();
    if (DOM.progressBar) {
        DOM.progressBar.style.width = `${percent}%`;
        DOM.progressBar.setAttribute("aria-valuenow", percent);
    }
}

function calculateProgress() {
    const percentage = ((STATE.currentStep - 1) / (STEP.TOTAL - 1)) * 100;
    return Math.min(100, Math.max(0, Math.round(percentage)));
}

/* ==========================================================================
   Module 12
   --------------------------------------------------------------------------
   Result Display Pipeline
   ========================================================================== */

function displayResult(result) {
    if (!DOM.resultCard || !result) return;
    DOM.resultCard.style.display = "block";
    setResultValue("stressLevel", result.stress_level ?? result.stress ?? "--");
    setResultValue("burnoutScore", result.burnout_score ?? result.burnout ?? "--");
    setResultValue("wellnessScore", result.wellness_score ?? result.wellness ?? "--");
    setResultValue("mentalStatus", result.mental_health_status ?? result.status ?? "--");
    setResultText("supportMessage", result.support_message || "Assessment completed successfully.");
    setResultList("musicList", result.recommended_music || []);
    setResultList("activityList", result.recommended_activities || []);
    DOM.resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

function setResultValue(id, value) { const el = byId(id); if (el) el.textContent = value; }
function setResultText(id, text) { const el = byId(id); if (el) el.textContent = text; }
function setResultList(id, items) {
    const list = byId(id); if (!list) return; list.innerHTML = "";
    if (!items.length) { const li = document.createElement("li"); li.textContent = "None."; list.appendChild(li); return; }
    items.forEach(i => { const li = document.createElement("li"); li.textContent = i; list.appendChild(li); });
}

/* ==========================================================================
   Module 13
   --------------------------------------------------------------------------
   Shared Utility Functions
   ========================================================================== */

function notify(message, type = "info") {
    console.log(`[${type.toUpperCase()}]`, message);
    if (type === "error" || type === "warning") alert(message);
}

function debounce(callback, delay = 300) {
    let timeout = null;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => callback.apply(this, args), delay);
    };
}

function createElement(tag, className = "") {
    const el = document.createElement(tag);
    if (className) el.className = className;
    return el;
}

function clearElement(element) {
    if (!element) return;
    while (element.firstChild) element.removeChild(element.firstChild);
}

/* ==========================================================================
   Module 14
   --------------------------------------------------------------------------
   Unified System Application Bootstrap
   ========================================================================== */

function registerGlobalEvents() {
    if (DOM.form) {
        DOM.form.addEventListener("submit", submitAssessment);
    }
    const liveSave = debounce(() => {
        saveDraft();
        updateProgress();
    }, 300);
    document.addEventListener("input", liveSave);
    document.addEventListener("change", liveSave);
    window.addEventListener("beforeunload", saveDraft);
}

async function bootstrapAssessment() {
    if (STATE.initialized) return;
    try {
        cacheDOM();
        verifyDOM();
        registerGlobalEvents();
        
        // Fetch and load structural data first
        await loadQuestions();
        
        // Attach handlers AFTER elements settle in the DOM lifecycle
        initialiseNavigation();
        
        restoreDraft();
        showStep(STEP.PROFILE);
        STATE.initialized = true;
    } catch (error) {
        Logger.error("Failed executing assessment initialization:", error);
    }
}

document.addEventListener("DOMContentLoaded", bootstrapAssessment);