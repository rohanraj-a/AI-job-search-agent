import re
import pandas as pd
import streamlit as st
from matching import score_job_match

st.set_page_config(page_title="AI Job-Search Agent", page_icon="💼", layout="wide")
st.title("💼 AI Job-Search Agent")
st.write("Find jobs, analyze requirements, and track your applications.")

# ---------------- SESSION STATE ----------------
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "my_skills" not in st.session_state:
    st.session_state.my_skills = ""
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# ---------------- SKILL DETECTION ----------------
SKILL_ALIASES = {
    "excel": ["excel", "ms excel", "microsoft excel"],
    "power bi": ["power bi", "microsoft power bi"],
    "sql": ["sql"],
    "mysql": ["mysql", "my sql"],
    "nosql": ["nosql", "no sql"],
    "power query": ["power query"],
    "kpi analysis": ["kpi analysis", "key performance indicator analysis"],
    "data visualization": ["data visualization", "data visualisation"],
    "stakeholder management": ["stakeholder management", "stakeholder communication"],
}

REQUIRED_SKILLS = [
    "sql", "excel", "power bi", "python", "pandas", "numpy", "tableau",
    "power query", "dax", "statistics", "machine learning", "large datasets",
    "communication", "data cleaning", "data visualization", "data analysis",
    "dashboard reporting", "sales reporting", "sales analytics",
    "business analysis", "business intelligence", "kpi analysis",
    "performance analysis", "market research", "report automation",
    "data validation", "stakeholder management"
]

CANDIDATE_DEFAULT_LEVELS = {
    "sql": "Strong",
    "excel": "Strong",
    "power bi": "Basic",
    "python": "Basic",
    "pandas": "Basic",
    "numpy": "Basic",
}


def canonical_skill(skill):
    cleaned = skill.strip().lower()
    for canonical, aliases in SKILL_ALIASES.items():
        if cleaned == canonical or cleaned in aliases:
            return canonical
    return cleaned


def find_matched_skills(description, skills_to_find):
    description = description.lower()
    matched = []
    for skill in skills_to_find:
        canonical = canonical_skill(skill)
        aliases = SKILL_ALIASES.get(canonical, [canonical])
        aliases = list(set(aliases + [canonical]))
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"
            if re.search(pattern, description):
                matched.append(canonical)
                break
    return matched



def suggest_requirement_settings(description, skill):
    """Suggest Must/Nice and Basic/Strong using JD sections and wording."""

    lines = description.lower().splitlines()

    nice_headings = [
        "good to have",
        "preferred skills",
        "preferred qualifications",
        "desirable skills",
        "additional skills",
        "bonus skills"
    ]

    must_headings = [
        "required skills",
        "requirements",
        "must have",
        "mandatory skills",
        "essential skills",
        "qualifications required"
    ]

    current_section = ""
    skill_section = ""

    # Identify the section containing the skill.
    for line in lines:
        clean_line = re.sub(
            r"^[\s\-•*]+|[\s*]+$",
            "",
            line.lower()
        ).strip()

        clean_line = clean_line.replace("**", "").replace("__", "")
        clean_line = clean_line.replace("*", "").replace("_", "")

        if clean_line.endswith(":"):
            heading = clean_line.rstrip(":").strip()

            if any(word in heading for word in nice_headings):
                current_section = "Nice"

            elif any(word in heading for word in must_headings):
                current_section = "Must"

        if find_matched_skills(clean_line, [skill]):
            skill_section = current_section
            break

    # Check explicit wording near the skill.
    sentences = re.split(r"[.!?\n;]+", description.lower())

    context = next(
        (
            sentence for sentence in sentences
            if find_matched_skills(sentence, [skill])
        ),
        description.lower()
    )

    nice_words = [
        "preferred", "preferably", "nice to have",
        "advantage", "desirable", "a plus",
        "good to have", "added advantage"
    ]

    must_words = [
        "required", "must have", "essential",
        "mandatory", "must-have"
    ]

    if any(word in context for word in nice_words):
        suggested_type = "Nice"
        type_note = "Suggested Nice from explicit JD wording."

    elif any(word in context for word in must_words):
        suggested_type = "Must"
        type_note = "Suggested Must from explicit JD wording."

    elif skill_section:
        suggested_type = skill_section
        type_note = f"Suggested {skill_section} from JD section heading."

    else:
        suggested_type = "Must"
        type_note = "No clear section found; suggested Must. Please review."

    basic_words = [
        "basic knowledge", "basic understanding",
        "basic proficiency", "beginner",
        "familiarity", "working knowledge",
        "intermediate proficiency"
    ]

    strong_words = [
        "strong knowledge", "strong understanding",
        "strong proficiency", "advanced proficiency",
        "advanced knowledge", "expert knowledge",
        "in-depth knowledge"
    ]

    if any(word in context for word in basic_words):
        suggested_level = "Basic"
        level_note = "Suggested Basic from JD wording."

    elif any(word in context for word in strong_words):
        suggested_level = "Strong"
        level_note = "Suggested Strong from JD wording."

    else:
        suggested_level = "Strong"
        level_note = "No Basic wording found; suggested Strong. Please review."

    return (
        suggested_type,
        suggested_level,
        type_note,
        level_note
    )



# ---------------- 1. CANDIDATE PROFILE ----------------
st.header("1. Candidate Profile")
role_options = ["Data Analyst", "Power BI Analyst", "BI Analyst", "Data Scientist"]
saved_role = st.session_state.profile.get("Target Role", "Data Analyst")
role_index = role_options.index(saved_role) if saved_role in role_options else 0

with st.form("profile_form"):
    name = st.text_input("Your name", value=st.session_state.profile.get("Name", ""))
    target_role = st.selectbox("Target job role", role_options, index=role_index)
    location = st.text_input(
        "Preferred job location",
        value=st.session_state.profile.get("Location", "Bengaluru")
    )
    save_profile = st.form_submit_button("Save Profile")

if save_profile:
    if name.strip() and location.strip():
        st.session_state.profile = {
            "Name": name.strip(),
            "Target Role": target_role,
            "Location": location.strip()
        }
        st.success("Candidate profile saved for this session.")
    else:
        st.warning("Enter your name and preferred location.")

# ---------------- 2. CANDIDATE SKILLS ----------------
st.header("2. Your Skills")
st.write("Enter your actual skills separated by commas. Be honest about your proficiency.")
st.session_state.my_skills = st.text_input(
    "Skills",
    value=st.session_state.my_skills,
    placeholder="Example: SQL, Excel, Power BI, Python"
)
candidate_skills = sorted({
    canonical_skill(skill)
    for skill in st.session_state.my_skills.split(",")
    if skill.strip()
})
if not candidate_skills:
    st.info("Enter your skills above before calculating job match scores.")

# ---------------- 3. ADD A JOB ----------------
st.header("3. Add a Job Posting")
with st.form("job_form", clear_on_submit=True):
    company = st.text_input("Company name")
    job_role = st.text_input("Job title")
    job_location = st.text_input("Job location")
    job_link = st.text_input("Job application URL")
    description = st.text_area(
        "Job description",
        height=180,
        placeholder="Paste the complete job description here..."
    )
    add_job = st.form_submit_button("Add Job")

if add_job:
    if company.strip() and job_role.strip() and description.strip():
        st.session_state.jobs.append({
            "Company": company.strip(),
            "Role": job_role.strip(),
            "Location": job_location.strip(),
            "Link": job_link.strip(),
            "Description": description.strip()
        })
        st.session_state.search_done = True
        st.success("Job posting added successfully.")
    else:
        st.warning("Enter the company, job title, and job description.")

# ---------------- 4. SEARCH JOBS ----------------
st.header("4. Search Your Job Listings")
search_text = st.text_input(
    "Search by role, company, location, or keyword",
    value=st.session_state.profile.get("Target Role", "")
)
location_filter = st.text_input(
    "Filter by location",
    value=st.session_state.profile.get("Location", "")
)
if st.button("Search Jobs"):
    st.session_state.search_done = True

if st.session_state.search_done:
    filtered_jobs = []
    for job in st.session_state.jobs:
        searchable = (
            job["Company"] + " " + job["Role"] + " " +
            job["Location"] + " " + job["Description"]
        ).lower()
        matches_text = (
            not search_text.strip()
            or search_text.strip().lower() in searchable
        )
        matches_location = (
            not location_filter.strip()
            or location_filter.strip().lower() in job["Location"].lower()
        )
        if matches_text and matches_location:
            filtered_jobs.append(job)

    st.write(f"Found {len(filtered_jobs)} matching saved job(s).")

    if filtered_jobs:
        for number, job in enumerate(filtered_jobs, start=1):
            with st.expander(
                f"{number}. {job['Role']} — {job['Company']}",
                expanded=True
            ):
                st.write("**Location:**", job["Location"])
                st.write("**Job description:**", job["Description"])

                if job["Link"].startswith(("https://", "http://")):
                    st.link_button("Open job posting", job["Link"])
                elif job["Link"]:
                    st.write("Job link:", job["Link"])
                else:
                    st.caption("No application link provided.")

                # Automatically detect requirements from the JD.
                job_skills = sorted(set(
                    find_matched_skills(job["Description"], REQUIRED_SKILLS)
                ))
                matched = sorted(set(job_skills) & set(candidate_skills))
                missing = sorted(set(job_skills) - set(candidate_skills))

                st.write("**Skills found in the description:**")
                if job_skills:
                    st.write(", ".join(job_skills))
                else:
                    st.warning(
                        "No recognised requirements found automatically. "
                        "Add requirements manually below."
                    )

                st.write("**Matching skills:**")
                st.write(", ".join(matched) if matched else "No matches detected.")

                st.write("**Potential skill gaps:**")
                if missing:
                    st.write(", ".join(missing))
                elif job_skills:
                    st.success("No gaps detected by this basic keyword check.")
                else:
                    st.caption(
                        "Cannot identify skill gaps until requirements are added."
                    )

                # Manual input is OUTSIDE the form, so it appears immediately.
                st.subheader("Add Manual Requirements")
                st.caption(
                    "Add requirements missed by automatic detection. "
                    "Separate multiple requirements with commas."
                )
                manual_text = st.text_input(
                    "Missing job requirements (comma-separated)",
                    key=f"manual_requirements_{number}",
                    placeholder="Sales reporting, KPI analysis, Market research"
                )
                manual_requirements = sorted({
                    skill.strip().lower()
                    for skill in manual_text.split(",")
                    if skill.strip()
                })

                all_job_skills = sorted(set(job_skills).union(manual_requirements))

                st.write("**Requirements to review and score:**")
                if all_job_skills:
                    st.write(", ".join(all_job_skills))
                else:
                    st.info("Add at least one manual requirement to continue.")

                st.subheader("Review Job Requirements")
                st.info(
                    "Review the suggested requirement type and required level. "
                    "Select your own skill level honestly."
                )

                if all_job_skills:
                    requirements = []
                    with st.form(f"requirement_review_{number}"):
                        for skill_index, skill in enumerate(all_job_skills):
                            (
                                suggested_type,
                                suggested_level,
                                type_note,
                                level_note
                            ) = suggest_requirement_settings(job["Description"], skill)

                            default_candidate_level = CANDIDATE_DEFAULT_LEVELS.get(
                                skill, "None"
                            )

                            st.markdown(f"**{skill.title()}**")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                requirement_type = st.selectbox(
                                    "Requirement type",
                                    ["Must", "Nice"],
                                    index=["Must", "Nice"].index(suggested_type),
                                    key=f"type_{number}_{skill_index}"
                                )
                                st.caption(type_note)

                            with col2:
                                level_needed = st.selectbox(
                                    "Level required by job",
                                    ["Basic", "Strong"],
                                    index=["Basic", "Strong"].index(suggested_level),
                                    key=f"needed_{number}_{skill_index}"
                                )
                                st.caption(level_note)

                            with col3:
                                your_level = st.selectbox(
                                    "Your skill level",
                                    ["None", "Basic", "Strong"],
                                    index=["None", "Basic", "Strong"].index(
                                        default_candidate_level
                                    ),
                                    key=f"your_{number}_{skill_index}"
                                )

                            requirements.append({
                                "name": skill,
                                "type": requirement_type,
                                "level_needed": level_needed,
                                "your_level": your_level
                            })
                            st.divider()

                        calculate_score = st.form_submit_button("Calculate Match Score")

                    if calculate_score:
                        result = score_job_match(requirements)
                        st.subheader("Job Match Result")
                        st.metric("Match score", f"{result['percentage']:.1f}%")
                        st.write("**Decision:**", result["decision"])
                        st.write(
                            "**Score details:**",
                            f"{result['earned_points']:g} / "
                            f"{result['maximum_points']:g} points"
                        )
                        st.write("**Requirement breakdown:**")
                        st.dataframe(
                            pd.DataFrame(result["breakdown"]),
                            use_container_width=True,
                            hide_index=True
                        )
                        if result["percentage"] < 70:
                            st.warning(
                                "This job is below the 70% Fit threshold. "
                                "Review the gaps before applying."
                            )
                        else:
                            st.success(
                                "This job meets the 70% Fit threshold. "
                                "Review the complete job description before applying."
                            )
    else:
        st.info("No matching saved jobs. Add a posting above or change your filters.")

st.divider()
st.caption(
    "Prototype v0.3 | Job postings are stored only in the current session. "
    "Skill detection is keyword-based and requires candidate review."
)