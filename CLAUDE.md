# Task: Resolve conflicts: f/issue_7c6407ec89f4/compute-002

**Task ID:** conflict-work_04a70bb992e9-d19d51ec

## Description

## Conflict Resolution Required

Branch `f/issue_7c6407ec89f4/compute-002` has merge conflicts with main.

### Conflicting Files
  - `CLAUDE.md`

### Steps
1. `git fetch origin main`
2. `git rebase origin/main`
3. Resolve conflicts in each file (remove `<<<<<<<`, `=======`, `>>>>>>>` markers)
4. `git add <file> && git rebase --continue` for each file
5. `git push --force-with-lease origin f/issue_7c6407ec89f4/compute-002`
6. Call `claudevn_complete_task` when done

Do NOT create new features or modify behavior.

## Skills

You are a conflict resolution specialist. Rebase the current branch onto main, resolve all merge conflicts, and push. Do NOT add features.

## Context

**Repository:** http://serving:8002/git/proj_8df0f4d56dc7_repo_f89c156f.git
**Base Branch:** main

## Branch Assignment

- **Branch:** `f/issue_7c6407ec89f4/compute-002`
- **Base:** `main`
- Push command: `git push origin f/issue_7c6407ec89f4/compute-002`

## Scope

Focus ONLY on what the task description asks for. Do not:
- Add functionality beyond what is requested
- Write comprehensive test suites — only write Tier 1 tests (mockable unit tests covering new functionality)
- Create detailed documentation unless documentation is the task
- Refactor or improve unrelated code
