"""Cover-letter templates (initial submission, revision, transfer, resubmission) and rendering."""
import datetime
import string

REQUIRED = {
    "initial": ["journal", "editor", "title", "article_type", "corresponding_author", "summary", "significance"],
    "revision": ["journal", "editor", "title", "manuscript_id", "corresponding_author", "changes_summary"],
    "transfer": ["journal", "editor", "title", "previous_journal", "corresponding_author", "summary"],
    "resubmission": ["journal", "editor", "title", "manuscript_id", "corresponding_author", "changes_summary"],
}

TEMPLATES = {
    "initial": """$date

$editor
$journal

Dear $editor,

We are pleased to submit our $article_type entitled "$title" for consideration for publication in $journal.

$summary

$significance
$fit_paragraph$reviewers_paragraph
We confirm that this manuscript is original, has not been published previously, and is not under consideration for publication elsewhere. All authors have approved the manuscript and agree with its submission to $journal.$data_statement$funding_statement
$coi_statement

Thank you for considering our work. We look forward to hearing from you.

Sincerely,

$corresponding_author
$affiliation
$email
""",
    "revision": """$date

$editor
$journal

Dear $editor,

Thank you for the opportunity to revise our manuscript "$title" (manuscript ID $manuscript_id). We are grateful to the reviewers for their constructive comments, which have improved the paper.

$changes_summary

A detailed point-by-point response to all comments is provided in the accompanying response letter, and all changes are highlighted in the marked-up manuscript.
$coi_statement

We hope the revised manuscript is now suitable for publication in $journal.

Sincerely,

$corresponding_author
$affiliation
$email
""",
    "transfer": """$date

$editor
$journal

Dear $editor,

We wish to submit our manuscript "$title" for consideration in $journal. The manuscript was previously reviewed at $previous_journal$previous_outcome.

$summary
$changes_paragraph$fit_paragraph
We confirm that the manuscript is not under consideration elsewhere and that all authors approve this submission.
$coi_statement

Sincerely,

$corresponding_author
$affiliation
$email
""",
    "resubmission": """$date

$editor
$journal

Dear $editor,

Please find enclosed a substantially revised version of our manuscript "$title" (previous ID $manuscript_id), which we are resubmitting following your earlier decision.

$changes_summary

We believe these changes fully address the concerns raised and hope you will consider the manuscript for review.
$coi_statement

Sincerely,

$corresponding_author
$affiliation
$email
""",
}


def validate(meta, kind="initial"):
    """Return a list of problems: missing required fields and common oversights."""
    if kind not in TEMPLATES:
        raise ValueError("unknown letter type %r" % kind)
    problems = ["missing field: %s" % f for f in REQUIRED[kind] if not str(meta.get(f, "")).strip()]
    if kind == "initial" and len(str(meta.get("summary", "")).split()) > 200:
        problems.append("summary is long (>200 words); editors skim cover letters")
    for r in meta.get("suggested_reviewers", []):
        if not r.get("email"):
            problems.append("suggested reviewer %s has no e-mail" % r.get("name", "?"))
    if "conflicts" not in meta:
        problems.append("no conflicts of interest statement given (use \"conflicts\": \"none\")")
    return problems


def _reviewers(meta):
    out = ""
    sug = meta.get("suggested_reviewers", [])
    if sug:
        out += "\nWe suggest the following potential reviewers, who have no conflicts of interest with the authors:\n"
        for r in sug:
            out += "- %s, %s%s%s\n" % (r.get("name", ""), r.get("affiliation", ""),
                                       " (%s)" % r["email"] if r.get("email") else "",
                                       " - %s" % r["expertise"] if r.get("expertise") else "")
    opp = meta.get("opposed_reviewers", [])
    if opp:
        out += "\nWe request that the following individuals not review this manuscript due to potential conflicts: %s.\n" % \
               "; ".join(r if isinstance(r, str) else r.get("name", "") for r in opp)
    return out


def render(meta, kind="initial", today=None):
    """Fill the template for `kind` with metadata (missing optional parts are omitted)."""
    if kind not in TEMPLATES:
        raise ValueError("unknown letter type %r" % kind)
    m = {k: v for k, v in meta.items() if isinstance(v, str)}
    m.setdefault("editor", "Editor")
    m["date"] = meta.get("date") or (today or datetime.date.today()).strftime("%d %B %Y").lstrip("0")
    m["fit_paragraph"] = ("\n%s\n" % meta["fit"]) if meta.get("fit") else ""
    m["reviewers_paragraph"] = _reviewers(meta)
    m["data_statement"] = (" " + meta["data_availability"]) if meta.get("data_availability") else ""
    m["funding_statement"] = (" " + meta["funding"]) if meta.get("funding") else ""
    c = str(meta.get("conflicts", "")).strip()
    m["coi_statement"] = ("\nThe authors declare no competing interests." if c.lower() in ("none", "no", "")
                          else "\nCompeting interests: %s" % c)
    m["previous_outcome"] = (" (%s)" % meta["previous_outcome"]) if meta.get("previous_outcome") else ""
    m["changes_paragraph"] = ("\n%s\n" % meta["changes_summary"]) if meta.get("changes_summary") and kind == "transfer" else ""
    for f in ("affiliation", "email", "summary", "significance", "changes_summary", "article_type",
              "manuscript_id", "previous_journal"):
        m.setdefault(f, "")
    text = string.Template(TEMPLATES[kind]).safe_substitute(m)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text
