
import unittest
from matching import score_job_match


class TestJobMatchScoring(unittest.TestCase):

    def test_must_basic_candidate_basic(self):
        requirements = [
            {
                "name": "Excel",
                "type": "Must",
                "level_needed": "Basic",
                "your_level": "Basic",
            }
        ]

        result = score_job_match(requirements)

        self.assertEqual(result["earned_points"], 2.0)
        self.assertEqual(result["maximum_points"], 2.0)
        self.assertEqual(result["percentage"], 100.0)
        self.assertEqual(result["decision"], "Fit")

    def test_must_strong_candidate_basic(self):
        requirements = [
            {
                "name": "SQL",
                "type": "Must",
                "level_needed": "Strong",
                "your_level": "Basic",
            }
        ]

        result = score_job_match(requirements)

        self.assertEqual(result["earned_points"], 1.0)
        self.assertEqual(result["maximum_points"], 2.0)
        self.assertEqual(result["percentage"], 50.0)
        self.assertEqual(result["decision"], "Not fit")

    def test_nice_basic_candidate_none(self):
        requirements = [
            {
                "name": "Tableau",
                "type": "Nice",
                "level_needed": "Basic",
                "your_level": "None",
            }
        ]

        result = score_job_match(requirements)

        self.assertEqual(result["earned_points"], 0.0)
        self.assertEqual(result["maximum_points"], 1.0)
        self.assertEqual(result["percentage"], 0.0)
        self.assertEqual(result["decision"], "Not fit")

    def test_complete_example_72_2_percent(self):
        requirements = [
            {
                "name": "Excel",
                "type": "Must",
                "level_needed": "Basic",
                "your_level": "Basic",
            },
            {
                "name": "Power BI",
                "type": "Must",
                "level_needed": "Basic",
                "your_level": "Basic",
            },
            {
                "name": "Large datasets",
                "type": "Must",
                "level_needed": "Basic",
                "your_level": "None",
            },
            {
                "name": "SQL",
                "type": "Nice",
                "level_needed": "Basic",
                "your_level": "Basic",
            },
            {
                "name": "Python",
                "type": "Nice",
                "level_needed": "Strong",
                "your_level": "Basic",
            },
            {
                "name": "Communication",
                "type": "Nice",
                "level_needed": "Basic",
                "your_level": "Basic",
            },
        ]

        result = score_job_match(requirements)

        self.assertEqual(result["earned_points"], 6.5)
        self.assertEqual(result["maximum_points"], 9.0)
        self.assertEqual(result["percentage"], 72.2)
        self.assertEqual(result["decision"], "Fit")


if __name__ == "__main__":
    unittest.main()
