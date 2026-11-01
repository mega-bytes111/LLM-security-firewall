# Policy Freeze Before Held-Out Test Evaluation

## Project

AI-Based Security Framework for Detection and Mitigation of
Prompt Injection and Jailbreak Attacks in Large Language Models

## Evaluation status

This document records the policy and evaluation choices made after
validation analysis and before inspecting held-out test results.

The original dataset test split has been cleaned and saved as
`ml/datasets/processed/test.csv`. The audit found 116 processed test
rows and no exact text overlap between the processed splits.
Cleaning included stripping and text-based deduplication, so the
processed test set is not described as completely untouched.

## Primary policy

The provisional default policy is DistilBERT-only:

- Use the saved binary DistilBERT model.
- Predict the class with the highest model output.
- Class 1 (malicious): BLOCK.
- Class 0 (benign): ALLOW.
- No additional threshold tuning or rule override.

This is a research policy decision. The existing
`/analyze/transformer` endpoint reports a prediction; actual
enforcement requires integration with a target LLM.

## Comparison policy

The existing triple-OR hybrid is retained as a comparison:

- Run rule-based, Logistic Regression and DistilBERT detectors.
- BLOCK if any detector flags the prompt.
- Otherwise ALLOW.

The existing `/analyze/hybrid` endpoint uses this OR policy.

## Baselines and comparisons

Evaluate the following on the same processed test split:

1. Rule-based detector.
2. TF-IDF + Logistic Regression.
3. TF-IDF + Linear SVM.
4. DistilBERT.
5. Rule + Logistic Regression, OR policy.
6. Rule + DistilBERT, OR policy.
7. Rule + Logistic Regression + DistilBERT, OR policy.

Report accuracy, precision, recall, F1, FPR, FNR and confusion-matrix
counts. Measure detector latency separately, with its environment and
limitations documented.

## Selection rationale

On the 82-row validation set, DistilBERT obtained:

- Accuracy: 0.9878
- Precision: 1.0000
- Recall: 0.9667
- F1: 0.9831
- False positives: 0
- False negatives: 1

The triple-OR policy obtained:

- Accuracy: 0.9512
- Precision: 0.8824
- Recall: 1.0000
- F1: 0.9375
- False positives: 4
- False negatives: 0

The one sample labelled malicious that DistilBERT missed appears
potentially ambiguous from its available text. Its original label
remains unchanged in the reported metrics.

The validation sample is small. These results do not guarantee
real-world performance.

## Test-set use

Do not use held-out test results to tune thresholds, modify rules,
select a different policy, or retrain models while continuing to
claim the same test set as an untouched final evaluation.

If changes are made after viewing test results, document them and
use a new independent evaluation set to assess those changes.

The test set may still be used for the planned comparison of all
pre-specified methods, with all results reported honestly.

## Limitations

- Current models perform binary classification, not trained subtype
  classification.
- Rule subtypes and scores are heuristic evidence.
- Exact-text overlap checks do not detect paraphrases or translations.
- Detection and decision reporting do not by themselves enforce
  blocking before a target LLM call.