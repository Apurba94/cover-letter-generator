import datetime
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr

from cover_letter_generator.cli import main
from cover_letter_generator.core import render, validate

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "initial.json")
with open(EXAMPLE, encoding="utf-8") as fh:
    META = json.load(fh)
D = datetime.date(2026, 3, 5)


class ValidateTests(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validate(META), [])

    def test_missing_fields_and_coi(self):
        p = validate({"journal": "J"}, "revision")
        self.assertIn("missing field: manuscript_id", p)
        self.assertTrue(any("conflicts" in x for x in p))

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            validate(META, "rejection")


class RenderTests(unittest.TestCase):
    def test_initial_letter(self):
        t = render(META, today=D)
        self.assertTrue(t.startswith("5 March 2026"))
        self.assertIn('our research article entitled "Low-cost sensors', t)
        self.assertIn("- Dr. A. Reviewer, University X (a@x.edu) - sensor calibration", t)
        self.assertIn("not review this manuscript due to potential conflicts: Dr. B. Competitor.", t)
        self.assertIn("The authors declare no competing interests.", t)
        self.assertNotIn("$", t)
        self.assertNotIn("\n\n\n", t)

    def test_optional_parts_omitted(self):
        meta = {k: META[k] for k in ("journal", "editor", "title", "article_type", "corresponding_author",
                                      "summary", "significance")}
        t = render(meta, today=D)
        self.assertNotIn("suggest the following", t)
        self.assertNotIn("$", t)

    def test_revision_and_conflict_text(self):
        meta = dict(META, manuscript_id="JER-2026-123", changes_summary="We added a validation study.",
                    conflicts="C.A. consults for SensorCo.")
        t = render(meta, "revision", today=D)
        self.assertIn("(manuscript ID JER-2026-123)", t)
        self.assertIn("Competing interests: C.A. consults for SensorCo.", t)

    def test_cli_strict(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.json")
            with open(bad, "w", encoding="utf-8") as fh:
                json.dump({"journal": "J"}, fh)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main([bad, "--strict"]), 1)
            out = os.path.join(d, "letter.txt")
            self.assertEqual(main([EXAMPLE, "-o", out]), 0)
            self.assertTrue(os.path.getsize(out) > 500)


if __name__ == "__main__":
    unittest.main()
