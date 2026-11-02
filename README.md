# AI-Based LLM Security Firewall

A research prototype for detecting potentially malicious prompts and
screening them before they reach a Large Language Model (LLM).

This project was developed as a **7th-semester minor project** focused
on prompt injection, jailbreak attempts, and the trade-off between
security and usability.

## Project Overview

The framework provides an external input-screening layer. It compares
rule-based, classical machine-learning, transformer-based, and hybrid
approaches for binary prompt classification.

The current protected-chat implementation uses DistilBERT to decide
whether a prompt should be sent to a local Ollama model. A separate
hybrid analysis endpoint combines detector flags using an OR policy.

> This is an experimental prototype, not a production security product.
> It can produce false positives and false negatives and does not guarantee
> protection against all attacks.

## Implemented Features

- Rule-based detection with heuristic categories and matched-rule evidence
- TF-IDF + Logistic Regression detection
- TF-IDF + Linear SVM comparison baseline
- Fine-tuned DistilBERT binary classifier
- Hybrid OR analysis combining rule, Logistic Regression, and DistilBERT flags
- FastAPI analysis and protected-chat endpoints
- Local LLM integration using Ollama and `llama3.2:1b`
- React dashboard for hybrid analysis and protected chat
- Validation and held-out test comparison
- Controlled firewall-on versus firewall-off marker-leakage experiments
- Backend automated tests

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Classical ML | Scikit-learn, TF-IDF |
| Transformer | PyTorch, Hugging Face Transformers, DistilBERT |
| Frontend | React, Vite, CSS |
| Local LLM | Ollama, `llama3.2:1b` |
| Testing | pytest |
| Version control | Git and GitHub |

## Architecture

```text
                         ┌─ Rule-based detector ─────┐
User prompt ── Analyze ──┼─ Logistic Regression ────┼─ OR policy + evidence
                         └─ DistilBERT ──────────────┘

User prompt ── Protected Chat ── DistilBERT policy
                                    │
                       ┌────────────┴────────────┐
                     BLOCK                    ALLOW
                 No LLM call          Ollama → LLM response
```

**Important:** The dashboard's hybrid analysis and protected chat use
different policies. Their decisions can differ.

## Repository Structure

```text
backend/
  app/                    FastAPI application and detectors
  tests/                  Backend tests
  requirements.txt

frontend/                 React + Vite dashboard

ml/
  datasets/               Local dataset files
  evaluation/             Evaluation scripts
  saved_models/           Local trained model artifacts
  scripts/                Dataset preparation and audit scripts
  training/               Classical ML training scripts

research/
  experiments/            Controlled experiment cases and summary
  results/                Aggregate evaluation results
  policy_freeze.md        Pre-test policy and evaluation plan
```

## Prerequisites

- Python and a compatible set of packages from `backend/requirements.txt`
- Node.js and npm
- Ollama installed locally
- Trained model artifacts and processed datasets restored locally

The development environment used Windows and Python 3.12.4.

### Model and Dataset Files

Dataset files and trained model artifacts are excluded from Git. A fresh
clone does **not** include them. Restore them from your own trusted backups
before running the relevant endpoints or evaluation scripts:

```text
ml/saved_models/logistic_regression.joblib
ml/saved_models/linear_svm.joblib
ml/saved_models/distilbert_detector/

ml/datasets/processed/train.csv
ml/datasets/processed/validation.csv
ml/datasets/processed/test.csv
```

The DistilBERT folder must contain the saved model and tokenizer files.
Load `.joblib` files only from trusted sources. Model artifacts should be
used with compatible library versions.

Dataset source:
[`deepset/prompt-injections`](https://huggingface.co/datasets/deepset/prompt-injections).
Review the dataset documentation and license before redistribution.

## Setup and Run on Windows

Run these commands from the project root unless stated otherwise.

### 1. Backend

Create and activate a virtual environment:

```powershell
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r .\backend\requirements.txt
```

Start FastAPI:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

The application loads trained detectors at startup, so their local
artifacts must be available.

### 2. Local LLM

Install Ollama from [ollama.com](https://ollama.com/download), then run:

```powershell
ollama pull llama3.2:1b
```

Verify the model:

```powershell
ollama list
ollama run llama3.2:1b "What is artificial intelligence?"
```

Ollama must be running locally for protected-chat requests that are
allowed by the firewall.

### 3. Frontend

Open a second terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually:

```text
http://localhost:5173/
```

The Vite development server proxies `/api` requests to the local FastAPI
backend. This proxy is for development; a production deployment requires
separate backend connectivity and security configuration.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Application information |
| `GET /health` | Basic application health response |
| `POST /analyze` | Rule-based analysis and heuristic decision |
| `POST /analyze/logistic` | Logistic Regression prediction |
| `POST /analyze/transformer` | DistilBERT prediction |
| `POST /analyze/hybrid` | Detector evidence and triple-OR decision |
| `POST /chat/protected` | DistilBERT-gated local LLM call |

`/health` is a basic application response; it does not establish that
Ollama is available. The hybrid endpoint returns detailed rule evidence
for research/debugging and should not be exposed publicly as-is.

## Running Tests

From the project root:

```powershell
.\backend\venv\Scripts\Activate.ps1
cd backend
python -m pytest tests/ -v
```

For the frontend, from `frontend/`:

```powershell
npm run lint
npm run build
```

## Dataset and Evaluation

The source dataset contains binary labels: `0` for benign and `1` for
malicious. Trained models do **not** perform multiclass attack-subtype
classification; rule categories provide heuristic indications only.

The prepared splits used in this project were:

| Split | Samples |
|---|---:|
| Training | 464 |
| Validation | 82 |
| Processed test | 116 |

The original test split was cleaned, including whitespace stripping and
text-based deduplication, so it is not described as completely untouched.
An audit found no exact-text overlap between processed splits. This check
does not rule out paraphrases, translations, or near-duplicates.

### Held-Out Test Results

The processed test split contained 56 benign and 60 malicious samples.
DistilBERT-only was the preselected primary policy; the OR hybrid was a
pre-specified comparison.

| Method | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Rule-based | 0.4828 | 0.0000* | 0.0000 | 0.0000 | 0 | 60 |
| Logistic Regression | 0.8621 | 0.9583 | 0.7667 | 0.8519 | 2 | 14 |
| Linear SVM | 0.8793 | 0.9792 | 0.7833 | 0.8704 | 1 | 13 |
| DistilBERT | 0.8879 | 0.9796 | 0.8000 | 0.8807 | 1 | 12 |
| Rule + LR + DistilBERT (OR) | 0.9310 | 0.9483 | 0.9167 | 0.9322 | 3 | 5 |

\* The rule-based detector made no positive predictions. Precision was
undefined mathematically and reported as zero by the evaluation script.

These results come from a small test set and should not be interpreted as
guaranteed real-world performance. Model scores are not established as
calibrated real-world attack probabilities.

## Controlled Marker-Leakage Experiments

The project also tested a synthetic marker-leakage task using the same
local LLM with the firewall OFF and ON.

| Experiment | Exact leaks OFF | Exact leaks ON | Benign blocks ON |
|---|---:|---:|---:|
| Pilot | 3/5 | 0/5 | 2/3 |
| Expanded exploratory set | 2/10 | 0/10 | 6/10 |

These are small handcrafted experiments, not representative benchmarks.
The expanded cases were created after reviewing pilot results. Exact
matching can miss partial or reformatted leakage. The experiment script
calls the detector directly rather than benchmarking the protected HTTP
endpoint end-to-end.

See `research/experiments/marker_experiment_summary.md` for setup and
limitations.

## Limitations and Future Work

- The current firewall screens direct user inputs. Indirect injection
  through retrieved documents or tool outputs needs separate checkpoints.
- Detector mistakes can block harmless requests or allow attacks through.
- The current protected-chat policy is DistilBERT-only; the hybrid endpoint
  is a separate analysis/comparison policy.
- The marker experiment measures only a specific synthetic objective.
- Broader independent evaluation, additional attack families, calibration,
  latency measurement, and false-positive analysis are future work.
- The prototype should not be publicly deployed without authentication,
  access control, logging/privacy review, and a security review.

## Research References

1. Yi Dong et al., “Safeguarding large language models: a survey,”
   *Artificial Intelligence Review*, vol. 58, article 382, 2025.
   DOI: [10.1007/s10462-025-11389-2](https://doi.org/10.1007/s10462-025-11389-2).

2. Badhan Chandra Das, M. Hadi Amini, and Yanzhao Wu, “Security and Privacy
   Challenges of Large Language Models: A Survey,” *ACM Computing Surveys*,
   vol. 57, no. 6, article 152, 2025.
   DOI: [10.1145/3712001](https://doi.org/10.1145/3712001).

These surveys provide research background; they do not independently
validate this prototype's experimental results.

## Academic Project

**Project title:** AI-Based Security Framework for Detection and
Mitigation of Prompt Injection and Jailbreak Attacks in Large Language Models

**Project type:** 7th-semester minor project
