# PR Continuity & Triage Policy

## Overview
This document outlines the standard procedure for managing pull requests (PRs) in the Docvert repository. Our goal is to ensure smooth delivery without blocking merges on intermittent failures or non-essential gates, while upholding our strict quality standards.

## Canonical PR Policy
- **One PR per logical change**: Each feature, bug fix, or refactor should be contained in a single canonical PR.
- **Continuity**: If a PR is abandoned or blocked, a new PR can take over its work (restacking), but the old PR must be cleanly closed to prevent duplicates.
- **Review Gates**:
  - All PRs require passing CI (100% test coverage).
  - CodeRabbit AI review must be completed.
  - If AI review requests changes, they must be addressed unless explicitly overridden by an administrator due to a false positive.
  - Reviews should not be arbitrarily dismissed.

## PR Stack & Split
- If a PR grows too large (>500 lines of non-generated code), split it into logical chunks (e.g., core changes, parser updates, CLI updates).
- Stack PRs logically using base branches if there are dependencies.

## Auto-Merge
- **Auto-merge on approval**: After a PR is APPROVED, mergeable, required checks pass, and the AI review gate succeeds, `gh pr merge --auto` will be enabled.
- **Merge Strategy**: Use `Squash and merge` by default to keep the `main` branch history clean, unless a multi-commit history is explicitly desired for a large feature branch.
