import streamlit as st
import pandas as pd
import re
from matching import score_job_match

st.set_page_config(
    page_title="AI Job-Search Agent",
    page_icon="💼",
    layout="wide"
)

st.title("💼 AI Job-Search Agent")
st.write("Find jobs, analyze requirements, and track your applications.")

# Store information for the current session
if "profile" not in st.session_state:
    st.session_state.profile = {}

if "jobs" not in st.session_state:
    st.session_state.jobs = []

if "my_skills" not in st.session_state:
    st.session_state.my_skills = "SQL, Excel, Power BI, Python, Pandas"


# Skill aliases: different names for the same skill
SKILL_ALIASES = {
    "excel": ["excel", "ms excel", "microsoft excel"],
    "power bi": ["power bi", "microsoft power bi"],
    "sql": ["sql"],
    "mysql": ["mysql", "my sql"],
    "nosql": ["nosql", "no sql"],
}

def find_matched_skills(description, candidate_skills):
    """Find candidate skills using complete words and known aliases."""
    description = description.lower()
    matched = []

    for skill in candidate_skills:
        skill = skill.strip().lower()
        if not skill:
            continue

        aliases = SKILL_ALIASES.get(skill, [skill])

        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            if re.search(pattern, description):
                matched.append(skill)
                break

    return matched

# ---------------- CANDIDATE PROFILE ----------------
st.header("1. Candidate Profile")

with st.form("profile_form"):
    name = st.text_input(
        "Your name",
        value=st.session_state.profile.get("Name", "")
    )

    target_role = st.selectbox(
        "Target job role",
        ["Data Analyst", "Power BI Analyst", "BI Analyst", "Data Scientist"],
        index=(
            ["Data Analyst", "Power BI Analyst", "BI Analyst", "Data Scientist"]
            .index(st.session_state.profile["Target Role"])
            if st.session_state.profile.get("Target Role")
            in ["Data Analyst", "Power BI Analyst", "BI Analyst", "Data Scientist"]
            else 0
        )
    )

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

# ---------------- SKILLS ----------------
st.header("2. Your Skills")

st.write("Enter your skills separated by commas.")
st.session_state.my_skills = st.text_input(
    "Skills",
    value=st.session_state.my_skills
)

# ---------------- ADD JOB ----------------
st.header("3. Add a Job Posting")

with st.form("job_form", clear_on_submit=True):
    company = st.text_input("Company name")
    job_role = st.text_input("Job title")
    job_location = st.text_input("Job location")
    job_link = st.text_input("Job application URL")
    description = st.text_area(
        "Job description",
        height=180,
        placeholder="Paste the job description here..."
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
        st.success("Job posting added successfully.")
    else:
        st.warning("Enter the company, job title, and job description.")



def suggest_requirement_settings(description, skill):
    """Suggest requirement type and required level from JD wording."""

    sentences = re.split(r"[.!?\n;]+", description.lower())

    context = next(
        (
            sentence for sentence in sentences
            if find_matched_skills(sentence, [skill])
        ),
        description.lower()
    )

    # Requirement type suggestions
    nice_words = [
        "preferred",
        "preferably",
        "nice to have",
        "advantage",
        "desirable",
        "a plus",
        "good to have",
        "added advantage"
    ]

    must_words = [
        "required",
        "must have",
        "essential",
        "mandatory",
        "must-have"
    ]

    if any(word in context for word in nice_words):
        suggested_type = "Nice"
        type_note = "Suggested Nice from JD wording. Please review."

    elif any(word in context for word in must_words):
        suggested_type = "Must"
        type_note = "Suggested Must from JD wording. Please review."

    else:
        suggested_type = "Must"
        type_note = "No clear wording found; suggested Must. Please review."

    # Required skill level suggestions
    basic_words = [
        "basic knowledge",
        "basic understanding",
        "basic proficiency",
        "basic to intermediate",
        "basic/intermediate",
        "beginner",
        "familiarity",
        "working knowledge",
        "intermediate proficiency",
        "intermediate knowledge",
        "intermediate understanding"
    ]

    strong_words = [
        "strong knowledge",
        "strong understanding",
        "strong proficiency",
        "advanced proficiency",
        "advanced knowledge",
        "expert knowledge",
        "in-depth knowledge",
        "highly proficient"
    ]

    if any(word in context for word in basic_words):
        suggested_level = "Basic"
        level_note = "Suggested Basic from JD wording. Please review."

    elif any(word in context for word in strong_words):
        suggested_level = "Strong"
        level_note = "Suggested Strong from JD wording. Please review."

    else:
        suggested_level = "Strong"
        level_note = (
            "No Basic requirement found; suggested Strong. "
            "Please review."
        )

    return (
        suggested_type,
        suggested_level,
        type_note,
        level_note
    )



# ---------------- SEARCH JOBS ----------------
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

if st.session_state.get("search_done", False):
    filtered_jobs = []

    for job in st.session_state.jobs:
        searchable = (
            job["Company"] + " " +
            job["Role"] + " " +
            job["Location"] + " " +
            job["Description"]
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
                f"{number}. {job['Role']} — {job['Company']}"
            ):
                st.write("**Location:**", job["Location"])
                st.write("**Job description:**", job["Description"])

                if job["Link"].startswith(("https://", "http://")):
                    st.link_button("Open job posting", job["Link"])
                elif job["Link"]:
                    st.write("Job link:", job["Link"])
                else:
                    st.caption("No application link provided.")

                # Simple keyword-based skill comparison
                
                # Detect skills mentioned in the job description
                required_skills = [
                    "sql", "excel", "power bi", "python",
                    "pandas", "numpy", "tableau", "power query",
                    "dax", "statistics", "machine learning",
                    "large datasets", "communication"
                ]

                candidate_skills = [
                    skill.strip().lower()
                    for skill in st.session_state.my_skills.split(",")
                    if skill.strip()
                ]

                job_skills = {
                    skill
                    for skill in required_skills
                    if find_matched_skills(job["Description"], [skill])
                }

                matched = sorted(job_skills & set(candidate_skills))
                missing = sorted(job_skills - set(candidate_skills))

                # Default candidate skill levels
                candidate_default_levels = {
                    "sql": "Strong",
                    "excel": "Strong",
                    "power bi": "Basic",
                    "python": "Basic",
                    "pandas": "Basic",
                    "numpy": "Basic",
                }

                st.write("**Skills found in the description:**")
                st.write(
                    ", ".join(sorted(job_skills))
                    or "No recognized skills found."
                )

                st.write("**Matching skills:**")
                st.write(", ".join(matched) or "No matches detected.")

                st.write("**Potential skill gaps:**")
                st.write(", ".join(missing) or "No gaps detected.")

                st.subheader("Review Job Requirements")

                st.info(
                    "The app suggests Must/Nice and Basic/Strong "
                    "from the job description. Review and change "
                    "these values before calculating your score."
                )

                requirements = []

                with st.form(f"requirement_review_{number}"):

                    for skill in sorted(job_skills):

                        (
                            suggested_type,
                            suggested_level,
                            type_note,
                            level_note
                        ) = suggest_requirement_settings(
                            job["Description"], skill
                        )

                        default_candidate_level = (
                            candidate_default_levels.get(skill, "None")
                            if skill in candidate_skills
                            else "None"
                        )

                        st.markdown(f"**{skill.title()}**")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            requirement_type = st.selectbox(
                                "Requirement type",
                                ["Must", "Nice"],
                                index=["Must", "Nice"].index(
                                    suggested_type
                                ),
                                key=f"type_{number}_{skill}"
                            )
                            st.caption(type_note)

                        with col2:
                            level_needed = st.selectbox(
                                "Level required by job",
                                ["Basic", "Strong"],
                                index=["Basic", "Strong"].index(
                                    suggested_level
                                ),
                                key=f"needed_{number}_{skill}"
                            )
                            st.caption(level_note)

                        with col3:
                            your_level = st.selectbox(
                                "Your skill level",
                                ["None", "Basic", "Strong"],
                                index=["None", "Basic", "Strong"].index(
                                    default_candidate_level
                                ),
                                key=f"your_{number}_{skill}"
                            )

                        requirements.append({
                            "name": skill,
                            "type": requirement_type,
                            "level_needed": level_needed,
                            "your_level": your_level
                        })

                        st.divider()

                    calculate_score = st.form_submit_button(
                        "Calculate Match Score"
                    )

                if calculate_score and requirements:

                    result = score_job_match(requirements)

                    st.subheader("Job Match Result")

                    st.metric(
                        "Match score",
                        f"{result['percentage']:.1f}%"
                    )

                    st.write(
                        "**Decision:**",
                        result["decision"]
                    )

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
            st.write(", ".join(missing) or "No gaps detected by this basic check.")
    else:
        st.info(
            "No matching saved jobs. Add a posting above or change your filters."
        )

st.divider()
st.caption(
    "Prototype v0.2 | Search currently covers job postings added in this session."
)
