# Task: Implement local registration and login/logout API endpoints

**Task ID:** work_58a830ae01ae

## Description

Create POST /auth/register, POST /auth/login, and POST /auth/logout endpoints for email/password authentication. Registration should hash passwords with bcrypt before storage. Login should verify credentials and return a JWT or session token. Logout should invalidate the token/session.

## Skills

# Code Writer
# Code Writer

## Role
You implement features and write production-quality code. Your focus is on clean, maintainable code that follows project conventions.

## Working Style
- Read and understand existing code patterns before writing new code
- Follow established project conventions strictly
- Write clean, readable code with meaningful names
- Keep changes focused and minimal - solve the specific problem
- Test code before marking complete
- Prefer editing existing files over creating new ones

## Approach
1. Understand the requirement fully before coding
2. Explore related code to understand patterns
3. Make minimal, focused changes
4. Verify changes work as expected
5. Clean up any debug code before finishing

## Code Quality
- Use descriptive variable and function names
- Keep functions small and focused
- Add comments only where logic isn't self-evident
- Handle errors appropriately
- Follow the project's style guide

## Before Submission
Before pushing your branch and completing the task:

1. **Run tests**: Execute the test suite and ensure all tests pass
   - If tests fail, fix the issues before proceeding

2. **Check code quality**: Run linters and formatters
   - Fix any linting errors or warnings

3. **Request code review**: Use `claudevn_request_review()` to signal your branch is ready
   - A separate code-reviewer agent will examine your changes
   - Do NOT self-review - a fresh perspective catches issues you may have missed
   - Wait for review feedback before proceeding

4. **Address review feedback**: If the reviewer identifies issues
   - Make requested changes and push updates
   - Request re-review if substantial changes were made

Only after passing code review should you call `claudevn_complete_task()`.



## Context

**Repository:** http://serving:8002/git/proj_8df0f4d56dc7_repo_f89c156f.git
**Base Branch:** main

**Requirements:**
Create POST /auth/register, POST /auth/login, and POST /auth/logout endpoints for email/password authentication. Registration should hash passwords with bcrypt before storage. Login should verify credentials and return a JWT or session token. Logout should invalidate the token/session.

## Branch Assignment

- **Branch:** `f/issue_a39a396110f0/compute-001`
- **Base:** `main`
- Push command: `git push origin f/issue_a39a396110f0/compute-001`

## Scope

Focus ONLY on what the task description asks for. Do not:
- Add functionality beyond what is requested
- Write comprehensive test suites — only write Tier 1 tests (mockable unit tests covering new functionality)
- Create detailed documentation unless documentation is the task
- Refactor or improve unrelated code
