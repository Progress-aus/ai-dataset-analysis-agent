# AI Dataset Analysis Agent

A small tool I built to speed up the most repetitive part of dataset comparison — figuring out what changed between two files and what it actually means.

## The context

In my case study practice and university project work, I kept noticing the same pattern: someone gets two datasets (last quarter vs this quarter, planned vs actual, two stores' data), and the first hour goes into structural checks — different columns, missing rows, date format mismatches — before any real analysis can start.

I wanted to see if I could compress that into something faster, and push the output past the "what happened" stage into "what it probably means."

## What the tool does

It has two modes:

**Gap Analysis** — flags structural differences between two datasets. Missing columns, type mismatches, coverage gaps. Useful for the cleanup stage before analysis.

**Comparison Analysis** — runs variance numbers on two periods or segments, surfaces the biggest changes, and uses Claude AI to generate a written interpretation of the results.

The user uploads two CSVs through a Streamlit web interface and gets back a structured report.

## Data used for testing

- **Alcohol industry data** — brand and sales records I'd already been working with for a strategic case study on declining Gen-Z consumption in Australia
- **Nike retail data (synthetic but realistic)** — store-level performance comparing Q1 vs Q2 2025

Both stressed different things: the alcohol data had schema inconsistencies across sources; the Nike data was clean but had a non-obvious variance story (the headline number masked store-by-store differences).

## How I approached it

I'm a Business IT student, not a developer. I designed the architecture, wrote the business logic spec, decided what counts as a meaningful change, and validated the output against the test data. The Python implementation was written with substantial help from AI coding tools (Claude). I directed the build, iterated, and broke things deliberately to test edge cases.

This reflects how I think a lot of analyst work is moving — the bottleneck shifts from writing code line-by-line to knowing what to build and being able to specify it precisely.

## Tech

Python, Pandas, Streamlit, Claude API. Outputs JSON and CSV.

## How to run it

\`\`\`
git clone https://github.com/Progress-aus/ai-dataset-analysis-agent

cd ai-dataset-analysis-agent

pip install -r requirements.txt

streamlit run app.py
\`\`\`

You'll need a Claude API key set as an environment variable.

## About me

I'm Progress Pandey, finishing a Bachelor of Information Technology (Business major) at Sydney International School of Technology and Commerce in June 2026. Looking for Junior BA / Data Analyst roles in Sydney.

- LinkedIn: [progress-pandey](https://www.linkedin.com/in/progress-pandey/)
- Email: progresspandey299@gmail.com
