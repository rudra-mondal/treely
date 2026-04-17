# Treely v2.0 — Deployment & Workflows Guide

This document outlines the entire software supply chain for Treely, detailing how the Continuous Integration (CI) test bots work, and giving you step-by-step instructions on updating the code on GitHub and publishing it natively to PyPI for users to install via `pip`.

## 1. How the GitHub Workflows (Bots) Work

Your repository includes two automated GitHub Action workflows under `.github/workflows/`. These run automatically in the cloud every time you interact with your code on GitHub.

### `ci.yml` (The Integrity Checker)
This is your safety net. It runs automatically every time you `push` code to the `main` (or `master`) branch, or open a Pull Request. 
- **Linting:** It first boots up a tiny Ubuntu server, installs Python 3.12, and runs `ruff check treely/`. If you broke formatting or syntax, the bot stops and fails the run.
- **Enterprise Testing:** It then invokes a full matrix of servers simultaneously. It creates instances of **Ubuntu**, **Windows**, and **macOS**, and installs Python `3.9`, `3.10`, `3.11`, and `3.12` on all of them. It runs our 138-assertion `pytest` suite across *every single environmental combination* to ensure cross-platform compatibility. 
- **Code Coverage:** Finally, it uploads the test coverage map directly to Codecov so you can see your 80%+ coverage metrics on GitHub!

### `publish.yml` (The PyPI Distributor)
This is your distribution engine. When you create a specific "Release Tag" telling GitHub a new version is ready (e.g., `v2.0.0`), this bot wakes up.
- It verifies the package structure using `build` and `twine`.
- It securely authenticates with **PyPI** using modern *Trusted Publishing (OIDC)*. This means you do not have to maintain fragile passwords or secret tokens in GitHub! It securely handshakes with PyPI on your behalf and uploads the `treely` package directly.

---

## 2. How to Push Updates to GitHub

When you have modified files locally and want to securely push them to your repository, follow these precise terminal steps:

```bash
# 1. Stage all your changed files 
git add .

# 2. Commit the changes with a clear industrial-grade message
git commit -m "Fix memory bounds, cp1252 renderer crash, and utf-16 binary filter bug"

# 3. Push the raw code to the main branch on GitHub
git push origin main
```
> [!NOTE]
> Pushing to `main` immediately triggers the `ci.yml` matrix. It will *not* trigger a PyPI release. 

---

## 3. How to Publish a New Release to PyPI

Because your `publish.yml` is robustly configured, you **do not manually upload to PyPI**. You just tell git that you are cutting a release version, and the bot handles the rest.

### Prerequisite: Register Trusted Publishing on PyPI
Before the bot can publish on your behalf, you need to link your PyPI account to your GitHub repository:
1. Log into [PyPI.org](https://pypi.org/).
2. Go to **Account Settings** -> **Publishing**.
3. Add a new **GitHub Publisher**.
4. Set the Owner to your GitHub Username, Repository to `treely`, and Workflow to `publish.yml`. (Leave the environment field blank or set to `pypi-publish`).

### Triggering the Release
When the code is ready (like it is right now!), push a tag to trigger the deployment. The tag *must* start with a `v` to trigger the workflow.

```bash
# 1. Ensure you are on the latest main branch
git pull origin main

# 2. Tag the current commit as version 2.0.0
git tag v2.0.0

# 3. Push the specific tag to GitHub
git push origin v2.0.0
```

> [!IMPORTANT]
> The exact moment you hit enter on `git push origin v2.0.0`, GitHub will launch the `publish.yml` workflow. You can watch it build the package and deploy it under the "Actions" tab on your GitHub repository. Once it finishes, anyone in the world can run `pip install treely` and get your exact updates automatically!
