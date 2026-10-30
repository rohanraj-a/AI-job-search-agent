
from decimal import Decimal, ROUND_HALF_UP


def score_job_match(requirements):
    """
    Calculate a job match score.

    Each requirement must contain:
    - name: requirement name
    - type: Must or Nice
    - level_needed: Basic or Strong
    - your_level: None, Basic or Strong

    Formula:
    Points = weight * min(your level, required level) / required level
    """

    requirement_weights = {
        "Must": 2,
        "Nice": 1,
    }

    skill_levels = {
        "None": 0,
        "Basic": 1,
        "Strong": 2,
    }

    earned_points = Decimal("0")
    maximum_points = Decimal("0")
    breakdown = []

    for requirement in requirements:
        name = requirement["name"]
        requirement_type = requirement["type"]
        level_needed = requirement["level_needed"]
        your_level = requirement["your_level"]

        if requirement_type not in requirement_weights:
            raise ValueError(
                f"Invalid requirement type: {requirement_type}"
            )

        if level_needed not in ("Basic", "Strong"):
            raise ValueError(
                f"Invalid required level: {level_needed}"
            )

        if your_level not in skill_levels:
            raise ValueError(
                f"Invalid candidate level: {your_level}"
            )

        weight = Decimal(str(requirement_weights[requirement_type]))
        required_points = Decimal(str(skill_levels[level_needed]))
        candidate_points = Decimal(str(skill_levels[your_level]))

        earned = (
            weight * min(candidate_points, required_points)
            / required_points
        )

        maximum = weight

        earned_points += earned
        maximum_points += maximum

        breakdown.append({
            "requirement": name,
            "type": requirement_type,
            "level_needed": level_needed,
            "your_level": your_level,
            "earned": float(earned),
            "maximum": float(maximum),
        })

    percentage = (
        (earned_points / maximum_points * Decimal("100"))
        .quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if maximum_points > 0
        else Decimal("0.0")
    )

    return {
        "earned_points": float(earned_points),
        "maximum_points": float(maximum_points),
        "percentage": float(percentage),
        "decision": "Fit" if percentage >= 70 else "Not fit",
        "breakdown": breakdown,
    }
