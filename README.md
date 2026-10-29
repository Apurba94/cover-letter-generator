# cover-letter-generator

**Write a complete, professional cover letter for an initial submission, revision,
transfer or resubmission from one small JSON file, with all the statements editors expect.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Cover letters repeat the same structure every time: what the paper is, why it matters, why this
journal, originality and approval statements, conflicts of interest, data availability, suggested
and opposed reviewers. Forgetting one of them delays handling. Keeping the facts in JSON makes letters
reproducible and easy to adapt when transferring between journals.

## Features

- Four letter types: `initial`, `revision`, `transfer`, `resubmission`
- Required-field validation and checks for common oversights (no COI statement, reviewer without
  e-mail, overly long summary); `--strict` fails on problems
- Optional sections appear only when given: journal fit, data availability, funding, suggested and
  opposed reviewers, previous journal outcome
- Custom templates with `$field` placeholders

## Usage

```bash
pip install .
cover-letter-generator examples/initial.json -o cover_letter.txt
cover-letter-generator revision.json -t revision --strict
cover-letter-generator meta.json --template my_lab_template.txt
```

Always personalise the generated text; editors appreciate a specific, concise letter.

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
