# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a resume editor application designed to integrate with Dify AI workflows. It consists of:
- **Backend**: Python Flask API with SQLAlchemy ORM for resume management and PDF generation
- **Frontend**: React SPA with Vite build system and Tailwind CSS styling
- **Integration**: Receives resume data from Dify HTTP nodes and provides visual editing interface

## Core Architecture

### Backend Structure
- `app.py`: Flask application factory with CORS configuration for multi-origin access
- `models.py`: SQLAlchemy models with Resume entity storing markdown and structured JSON data
- `routes/`: API blueprints split by functionality (resume_routes, debug_routes)  
- `services/`: Business logic modules (markdown_parser, pdf_generator)

### Frontend Structure
- React Router setup with two main routes: HomePage (/) and EditPage (/edit/:id)
- Component architecture: Layout wrapper, ResumeEditor with markdown support, ResumeList
- API communication layer in `utils/api.js` with axios
- Tailwind CSS for styling with toast notifications via react-hot-toast

### Database Schema
- Single `Resume` model with fields: id, title, raw_markdown, structured_data (JSON), timestamps
- SQLite database with automatic table creation on startup

## Development Commands

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Development  
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint checking
npm run preview      # Preview build
```

### Docker Deployment
```bash
./start.sh           # Start all services
./stop.sh            # Stop all services
docker-compose logs -f  # View logs
```

## API Integration Patterns

### Dify Integration Endpoint
- POST `/api/resumes/from-dify` - Primary integration point for receiving Dify workflow data
- Expects JSON: `{"resume_markdown": "...", "title": "..."}`
- Returns resume ID and edit URL for user redirection

### Core CRUD Operations
- GET `/api/resumes` - List all resumes
- GET `/api/resumes/{id}` - Get specific resume with structured data
- PUT `/api/resumes/{id}` - Update resume content
- GET `/api/resumes/{id}/pdf` - Export to PDF (supports `smart_onepage=true` parameter)
- GET `/api/resumes/{id}/pdf?smart_onepage=true` - Export with smart one-page optimization

## Key Dependencies

### Backend
- Flask + Flask-SQLAlchemy + Flask-CORS for API layer
- reportlab for PDF generation with HarmonyOS Sans font support
- python-markdown for processing
- python-dotenv for environment configuration

### Frontend
- React 18 with React Router for SPA navigation
- Vite as build tool with ESLint configuration
- axios for HTTP client, react-markdown for rendering
- lucide-react for icons, react-hot-toast for notifications

## Environment Configuration

### Backend (.env)
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///resume_editor.db  
HOST=0.0.0.0
PORT=8080
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8080
```

## Docker Network Setup

- Configured to connect to external `dify_default` network for Dify integration
- Internal `resume_network` for service communication
- Health checks configured for backend service
- Persistent volume for SQLite database storage

## Font Configuration

### PDF Font Setup
- Primary font: HarmonyOS Sans (Simple Chinese)
- Font files located in: `backend/fonts/HarmonyOS Sans/HarmonyOS_Sans_SC/`
- Supported weights: Regular, Bold, Medium, Light
- Automatic fallback to system fonts if HarmonyOS Sans unavailable
- Font registration occurs at service startup

### Font Weights Used
- NameTitle: Bold weight for resume name/header
- SectionTitle: Medium weight for section headings  
- JobTitle: Medium weight for job/education titles
- ModernBodyText: Regular weight for body content
- ContactInfo: Regular weight for contact details

## Smart One-Page Feature

### Overview
Intelligent PDF compression system that automatically adjusts font sizes, spacing, and margins to fit resume content within a single A4 page while maintaining readability.

### Implementation Details
- **Content Analysis**: `_analyze_content_requirements()` estimates total height requirements
- **Smart Compression**: `_create_optimized_styles()` generates scaled-down styles when needed
- **Dynamic Adjustments**: Font sizes reduced by 15% max, spacing reduced up to 40%
- **Margin Optimization**: Page margins reduced by up to 20% when necessary

### Usage
- Frontend: Export dropdown menu with "智能一页导出" option
- API: Add `smart_onepage=true` parameter to PDF export endpoint
- Automatic: System detects if content exceeds one page and applies optimizations

### Algorithm Features
- **Adaptive Compression Strategy**: Two-tier compression based on content density
  - Standard compression (ratio ≥ 0.75): Font scale 85-95%, spacing scale 60-90%
  - Aggressive compression (ratio < 0.75): Font scale 75%+, spacing scale 45%+
- **Header-Specific Optimization**: Independent scaling for title elements
  - Name title: Minimum 18pt font size with optimized leading
  - Contact info: Minimum 8pt with reduced spacing
- **Granular Element Control**: Individual font size minimums for readability
  - Body text: 8pt minimum, section titles: 12pt minimum
  - Bullet points: 8pt minimum with reduced indentation
- **Smart Spacing Reduction**: Up to 55% spacing compression while maintaining hierarchy
- **Enhanced Margin Optimization**: Dynamic margin reduction based on compression needs

## Testing Files

Several testing scripts available in root directory:
- `test_backend.py`, `test_dify_connection.py` - Backend API testing
- `check_status.py`, `service_manager.py` - Service management utilities
- Various manual test scripts for specific functionality verification