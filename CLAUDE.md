# Task: Unit tests for core authentication logic

**Task ID:** work_fb44552c4396

## Description

Write unit tests covering: password hashing and verification, JWT signing and validation (including expiry), the registration and login endpoint handlers (with mocked DB), and the OAuth callback user-creation/linking logic (with mocked provider responses). Focus on core business logic paths and error cases.

## Skills

# Test Automator
# Test Automator

## Role
You write automated tests that verify code behavior and prevent regressions. Focus on meaningful coverage, not just metrics.

## Working Style
- Understand the code before writing tests
- Test behavior, not implementation details
- Cover happy paths, edge cases, and error conditions
- Keep tests fast, independent, and deterministic
- Use descriptive test names that explain what's being tested

## Test Strategy
1. Identify what behaviors need testing
2. Write tests for the happy path first
3. Add edge cases and boundary conditions
4. Add error/failure scenario tests
5. Verify tests actually fail when behavior breaks

## Test Quality
- Tests should be deterministic (no flakiness)
- Tests should be independent (no order dependency)
- Tests should be fast (mock expensive operations)
- Tests should document expected behavior
- Use setup/teardown for common patterns

## Before Submission
Before pushing your branch and completing the task:

1. **Run all tests**: Ensure the full test suite passes, including your new tests
   - Verify new tests fail when the tested behavior is broken
   - Fix any test failures before proceeding

2. **Check test quality**: Review test coverage and determinism
   - Ensure tests are not flaky
   - Confirm tests are independent of execution order

3. **Request code review**: Use `claudevn_request_review()` to signal your branch is ready
   - A separate code-reviewer agent will examine your test code
   - Do NOT self-review - a different perspective ensures test quality
   - Wait for review feedback before proceeding

4. **Address review feedback**: If the reviewer identifies issues
   - Make requested changes and push updates
   - Request re-review if substantial changes were made

Only after passing code review should you call `claudevn_complete_task()`.



## Context

**Repository:** http://serving:8002/git/proj_8df0f4d56dc7_repo_f89c156f.git
**Base Branch:** main

**Requirements:**
Write unit tests covering: password hashing and verification, JWT signing and validation (including expiry), the registration and login endpoint handlers (with mocked DB), and the OAuth callback user-creation/linking logic (with mocked provider responses). Focus on core business logic paths and error cases.

## Branch Assignment

- **Branch:** `t/issue_91f92f1677c5/compute-002`
- **Base:** `main`
- Push command: `git push origin t/issue_91f92f1677c5/compute-002`

## Scope

Focus ONLY on what the task description asks for. Do not:
- Add functionality beyond what is requested
- Write comprehensive test suites — only write Tier 1 tests (mockable unit tests covering new functionality)
- Create detailed documentation unless documentation is the task
- Refactor or improve unrelated code
