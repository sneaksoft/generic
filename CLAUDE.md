# Task: Resolve conflicts: f/issue_bf8e1981ebee/compute-001

**Task ID:** conflict-work_62271ea40464-96d31053

## Description

## Conflict Resolution Required

Branch `f/issue_bf8e1981ebee/compute-001` has merge conflicts with main.

### Conflicting Files
  - `__pycache__/auth_routes.cpython-311.pyc`
  - `__pycache__/oauth_config.cpython-311.pyc`
  - `__pycache__/test_auth_routes.cpython-311-pytest-9.0.2.pyc`

### Steps
1. `git fetch origin main`
2. `git rebase origin/main`
3. Resolve conflicts in each file (remove `<<<<<<<`, `=======`, `>>>>>>>` markers)
4. `git add <file> && git rebase --continue` for each file
5. `git push --force-with-lease origin f/issue_bf8e1981ebee/compute-001`
6. Call `claudevn_complete_task` when done

Do NOT create new features or modify behavior.

## Skills

You are a conflict resolution specialist. Rebase the current branch onto main, resolve all merge conflicts, and push. Do NOT add features.

## Context

**Repository:** http://serving:8002/git/proj_8df0f4d56dc7_repo_f89c156f.git
**Base Branch:** main

## Branch Assignment

- **Branch:** `f/issue_bf8e1981ebee/compute-001`
- **Base:** `main`
- Push command: `git push origin f/issue_bf8e1981ebee/compute-001`

## Scope

Focus ONLY on what the task description asks for. Do not:
- Add functionality beyond what is requested
- Write comprehensive test suites — only write Tier 1 tests (mockable unit tests covering new functionality)
- Create detailed documentation unless documentation is the task
- Refactor or improve unrelated code
