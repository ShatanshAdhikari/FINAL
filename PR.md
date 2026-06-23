# Light Mode Fixes

## Branch
`feat/light-mode-fixes` → `main`

## Problem
Switching to light mode produced a broken UI:
- The logo (white on transparent) disappeared against the light background
- Input boxes and placeholders were invisible due to insufficient contrast
- Hover effects used `bg-white/5` (near-transparent white) — invisible on light backgrounds
- Several text values used `text-gray-300` (near-white) — unreadable in light mode
- Card and box outlines were too faint to distinguish on white surfaces

## Changes

### `frontend/src/assets/logo-light.png`
Added a dedicated dark logo (black + orange) for light mode.

### `frontend/src/index.css`
- Updated `--bg-nested` to `#ffffff` and `--border-input` to `#9ca3af` so input fields are clearly visible in light mode
- Darkened `--border` to `#9ca3af` and `--border-subtle` to `#d1d5db` so card outlines are clearly visible
- Added `--text-placeholder` variable with theme-specific values
- Added global `::placeholder` rule using `--text-placeholder`

### `frontend/src/components/Layout.jsx`
- Swaps logo based on active theme (`logoDark` / `logoLight`)
- Replaced all `hover:bg-white/5` with `hover:bg-[var(--bg-muted)]`

### `frontend/src/pages/Login.jsx`
- Swaps logo based on active theme
- Fixed gradient button text to `text-white` (was `text-[var(--text-primary)]` which becomes dark in light mode)

### `frontend/src/pages/Dashboard.jsx`, `CalorieTracker.jsx`, `Onboarding.jsx`
- Replaced `text-gray-300` with `text-[var(--text-primary)]` for readable text in both modes

### `frontend/src/pages/WorkoutPlan.jsx`, `AdminPanel.jsx`
- Replaced `hover:bg-white/5` with `hover:bg-[var(--bg-muted)]`

### `frontend/src/components/ErrorBoundary.jsx`
- Replaced hardcoded `text-white` and `bg-white/10` with theme variables

## Test
Run `docker compose up --build` and toggle between dark and light mode to verify.
