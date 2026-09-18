# Radar — Project

Why this system exists, what it must ultimately prove, and where the
line between built and not-yet-built sits. For current per-component
state, see docs/ARCHITECTURE.md. For priorities and sequencing, see
docs/ROADMAP.md. For rationale behind any decision, see docs/adr/.
This document does not duplicate any of those three — it states only
what none of them are structured to hold.

## System Goal

Radar automatically turns changes in a chosen domain into verified
intelligence that helps a specific user make decisions cheaper or
earlier than independent research would.

## System Outcome

[OPEN — Owner]

## Current vs. Target (top-level)

Current: Radar collects changes from external sources and publishes
verified signals to a single channel. Domain scope is limited to the
AI/agent ecosystem.

Target: Radar turns raw changes into a verifiable map of domain
movement and delivers a concrete paid result to a user.

See docs/ARCHITECTURE.md for exactly which components exist today and
docs/ROADMAP.md for what's next.

## Definition of Done

[OPEN — Owner]

## Boundary: Article Pipeline

Article Pipeline is a separate distribution mechanism. Radar does not
implement, duplicate, or track its function (authoring, publication).
