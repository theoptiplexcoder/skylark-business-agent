# Product Requirements Document (PRD)

# Monday.com Business Intelligence AI Agent

**Version:** 1.0

**Project Duration:** 6 Hours (Assignment)

**Frontend:** Streamlit

**Backend:** FastAPI

**Deployment:** Streamlit (Render), FastAPI (Render) *(or Streamlit Community Cloud + Render if preferred)*

---

# 1. Document Summary

## Overview

The Monday.com Business Intelligence AI Agent is an AI-powered conversational analytics assistant that enables founders, executives, and business leaders to obtain real-time business insights from monday.com without manually creating reports or dashboards.

The system dynamically retrieves data from monday.com boards, cleans and normalizes inconsistent business data, performs cross-board analysis, and generates executive-level insights in natural language.

Unlike traditional dashboards that require users to interpret charts, the AI agent understands business questions, performs the required analysis, and delivers actionable recommendations.

---

## Problem Statement

Business users currently need to:

- Export data manually
- Clean inconsistent records
- Join multiple datasets
- Create ad-hoc reports
- Handle missing information

This process is slow, repetitive, and error-prone.

The goal of this application is to replace manual reporting with an AI-powered conversational business analyst.

---

## Objectives

The application should:

- Connect directly to monday.com
- Read live board data dynamically
- Never use hardcoded CSV files
- Handle messy business data gracefully
- Answer natural language business questions
- Analyze data across multiple boards
- Explain confidence and data quality issues
- Generate leadership summaries

---

## Primary Users

- Founder
- CEO
- COO
- Sales Manager
- Operations Manager

---

## Success Metrics

- Live monday.com integration
- Less than 10 second response time
- Cross-board analytics
- Graceful handling of incomplete data
- Executive-quality responses
- Deployable online

---

# 2. Application Flow

```
User

↓

Open Streamlit App

↓

Ask Business Question

↓

FastAPI receives request

↓

Query Understanding

↓

Determine Required Boards

↓

Fetch Live Data from Monday.com

↓

Normalize Data

↓

Business Analytics Engine

↓

LLM Insight Generation

↓

Return Executive Response

↓

Display Metrics + Insights
```

---

## User Flow

### Step 1

User opens the Streamlit application.

---

### Step 2

The application authenticates with the FastAPI backend.

---

### Step 3

User asks a question.

Example:

> How is our pipeline performing in the Energy sector this quarter?

---

### Step 4

The backend analyzes:

- Intent
- Business entities
- Time period
- Sector
- Metrics requested

---

### Step 5

The Planner Agent determines which boards are required.

Examples:

- Deals Board
- Work Orders Board

---

### Step 6

The Monday API Connector retrieves live board data.

---

### Step 7

The Data Cleaning Engine normalizes:

- Dates
- Currency
- Text
- Missing values
- Duplicate records

---

### Step 8

The Analytics Engine calculates:

- Revenue
- Pipeline health
- Conversion rate
- Work order status
- Sector performance

---

### Step 9

The LLM generates executive insights.

---

### Step 10

The Streamlit interface displays:

- Answer
- KPIs
- Recommendations
- Data quality warnings

---

# 3. Application Architecture

```
                Streamlit Frontend
                      │
                      │ REST API
                      ▼
                FastAPI Backend
                      │
      ┌───────────────┴────────────────┐
      │                                │
      ▼                                ▼
 Query Understanding           Monday API Client
      │                                │
      ▼                                ▼
 Analytics Engine          GraphQL / MCP Connector
      │                                │
      └───────────────┬────────────────┘
                      ▼
             Data Cleaning Engine
                      ▼
             Insight Generation
                      ▼
                JSON Response
                      ▼
              Streamlit Dashboard
```

---

## Components

### 1. Streamlit Frontend

Responsibilities

- Chat interface
- KPI cards
- Tables
- Charts
- Conversation history
- Leadership update page

---

### 2. FastAPI Backend

Responsibilities

- REST API
- AI orchestration
- Authentication
- Business logic
- Error handling

---

### 3. Monday Connector

Responsibilities

- Authenticate
- Fetch boards
- Read columns
- Read items
- Pagination
- Retry logic

---

### 4. Data Cleaning Engine

Responsibilities

- Normalize dates
- Normalize currency
- Handle missing values
- Remove duplicates
- Standardize text

---

### 5. Analytics Engine

Responsibilities

- Pipeline analysis
- Revenue analysis
- Operational metrics
- Cross-board joins
- Trend analysis

---

### 6. AI Insight Generator

Responsibilities

- Executive summary
- Recommendations
- Risks
- Opportunities
- Confidence score

---

# 4. API Structure & Documentation

## Base URL

```
/api/v1
```

---

## POST /chat

### Description

Ask a conversational business question.

### Request

```json
{
    "message": "How is our energy sector pipeline?"
}
```

### Response

```json
{
    "answer": "...",
    "insights": [],
    "metrics": {},
    "warnings": [],
    "confidence": 0.95
}
```

---

## GET /boards

Returns available monday.com boards.

---

## GET /metrics

Returns dashboard KPIs.

Example

```json
{
    "pipeline_value": 1500000,
    "active_work_orders": 42,
    "win_rate": 0.36,
    "completion_rate": 0.82
}
```

---

## POST /leadership-update

Generates executive update.

Request

```json
{
    "period":"Q2"
}
```

Response

```json
{
    "summary":"...",
    "wins":[],
    "risks":[],
    "recommendations":[]
}
```

---

## GET /health

Health check endpoint.

---

## Internal Services

### MondayService

```
fetch_boards()

fetch_items()

fetch_columns()
```

---

### CleaningService

```
normalize_dates()

normalize_currency()

normalize_text()

fill_missing_values()
```

---

### AnalyticsService

```
pipeline_health()

sector_analysis()

revenue_summary()

forecast()

operational_metrics()
```

---

### InsightService

```
generate_summary()

generate_recommendations()

generate_leadership_update()
```

---

# 5. Technology Stack

## Frontend

| Technology | Purpose |
|------------|----------|
| Streamlit | User Interface |
| Plotly | Interactive Charts |
| Pandas | Tables |
| streamlit-chat | Chat Components |

---

## Backend

| Technology | Purpose |
|------------|----------|
| FastAPI | REST API |
| Python 3.12 | Backend |
| Pydantic | Validation |
| Uvicorn | Server |

---

## AI

| Technology | Purpose |
|------------|----------|
| OpenAI GPT-5.5 | Primary LLM |
| LangChain | Tool Calling |
| LangGraph *(optional)* | Agent Workflow |

---

## Data Processing

| Technology | Purpose |
|------------|----------|
| Pandas | Cleaning |
| NumPy | Analytics |
| DuckDB | Fast SQL Analytics |

---

## Monday Integration

| Technology | Purpose |
|------------|----------|
| Monday GraphQL API | Live Data |
| MCP (Optional) | Native AI Integration |

---

## Deployment

| Technology | Purpose |
|------------|----------|
| Render | FastAPI Backend |
| Render / Streamlit Community Cloud | Streamlit Frontend |
| Vercel *(optional static landing page only)* | Landing/Docs |

> **Note:** Vercel does **not** natively host Streamlit applications. For a Streamlit UI, deploy it on **Render** or **Streamlit Community Cloud**, while the FastAPI backend runs on **Render**. If you want to use Vercel, use it only for a static landing page or migrate the frontend to Next.js.

---

## Development Tools

| Technology | Purpose |
|------------|----------|
| GitHub | Version Control |
| Docker | Containerization |
| Postman | API Testing |
| Ruff | Linting |
| Black | Formatting |

---

# 6. Phase-by-Phase Development Plan

---

## Phase 1 — Project Setup

### Goal

Create the application foundation.

### Tasks

- Initialize repository
- Create Streamlit app
- Create FastAPI backend
- Configure environment variables
- Configure Docker
- Configure deployment

### Deliverables

- Running frontend
- Running backend

---

## Phase 2 — Monday.com Integration

### Goal

Connect to monday.com.

### Tasks

- Authentication
- GraphQL client
- Fetch boards
- Read items
- Read columns
- Pagination
- Error handling

### Deliverables

- Live data retrieval

---

## Phase 3 — Data Cleaning

### Goal

Handle messy business data.

### Tasks

- Missing values
- Date normalization
- Currency parsing
- Duplicate removal
- Standardize text

### Deliverables

- Clean business dataset

---

## Phase 4 — Conversational AI

### Goal

Build the business assistant.

### Tasks

- Prompt engineering
- Intent detection
- Query planning
- Tool calling
- Clarification questions

### Deliverables

- Conversational AI

---

## Phase 5 — Business Intelligence

### Goal

Generate executive metrics.

### Tasks

- Revenue
- Pipeline
- Conversion
- Sector analysis
- Cross-board joins
- Operational KPIs

### Deliverables

- Business analytics engine

---

## Phase 6 — Leadership Updates

### Goal

Generate executive reports.

### Tasks

- Executive summary
- Risks
- Opportunities
- Recommendations
- Markdown export

### Deliverables

- Leadership update generator

---

## Phase 7 — Deployment & Documentation

### Goal

Finalize the assignment.

### Tasks

- Deploy backend
- Deploy frontend
- Write README
- Write Decision Log
- Test API
- Package source code

### Deliverables

- Hosted application
- README
- Decision Log
- ZIP archive

---

# Future Enhancements

- Multi-board support
- Scheduled leadership reports
- PDF export
- Slack integration
- Email summaries
- KPI dashboards
- Multi-tenant support
- Historical trend analysis
- Predictive forecasting
- Role-based access control

---

# Non-Functional Requirements

- Read-only access to monday.com
- Response time under 10 seconds
- Graceful API failure handling
- Explain missing or incomplete data
- Secure API key management
- Modular architecture
- Easily extensible analytics pipeline
- Cloud deployable
- Mobile-friendly Streamlit interface

---

# Deliverables Checklist

- Hosted Streamlit application
- Hosted FastAPI backend
- Live monday.com integration
- Conversational BI assistant
- Cross-board analytics
- Leadership update generator
- README with setup instructions
- Decision Log (≤2 pages)
- Source code ZIP
