# User Story Management & Feedback Application

## Overview

A Streamlit-based web application for product owners to manage, validate, and provide feedback on user stories. This app integrates with the MonolithicCoffeeMakerAgent project's ROADMAP and bug tracking systems.

**Related**: US-111, SPEC-111

## Features

### 📊 Dashboard (Main Page)
- View all user stories from ROADMAP.md
- Filter by status (Complete, In Progress, Planned)
- Filter by priority (HIGH, MEDIUM, LOW)
- Search by title/content
- Quick validation controls
- Create bug tickets inline
- Provide feedback and ratings

### 📸 Screenshots Page
- Upload screenshots of implemented features
- Add annotations and notes to screenshots
- Link screenshots to specific user stories
- Tag screenshots for categorization
- View all uploaded screenshots in a grid
- Delete screenshots

### ✅ Validation Tracking Page
- Overview of validation status across all stories
- Quick validation for pending stories
- Detailed validation with confidence levels
- Validation notes and comments
- Export validation reports (CSV/PDF)

### 🐛 Bug Tickets Page
- View all bug tickets from the database
- Create new bug tickets linked to user stories
- Filter by status, priority, and category
- Update bug status
- View bug analytics and resolution velocity
- Integration with BugTrackingSkill

## Installation & Usage

### Prerequisites

Ensure you have the MonolithicCoffeeMakerAgent project set up with:
- Python 3.11+
- Poetry installed
- Streamlit installed: `poetry add streamlit`
- Pillow installed: `poetry add pillow`

### Running the App

From the project root directory:

```bash
# Activate poetry environment
poetry shell

# Run the app
streamlit run streamlit_apps/user_story_management/app.py
```

The app will open in your default web browser at `http://localhost:8501`

### Alternative: Run with Poetry

```bash
poetry run streamlit run streamlit_apps/user_story_management/app.py
```

## Project Structure

```
streamlit_apps/user_story_management/
├── app.py                          # Main application
├── README.md                       # This file
├── pages/
│   ├── 1_📸_Screenshots.py        # Screenshots upload and management
│   ├── 2_✅_Validation_Tracking.py # Validation tracking
│   └── 3_🐛_Bug_Tickets.py        # Bug tickets management
└── uploads/                        # Uploaded screenshots directory
```

## Key Features Detail

### User Story Validation

1. **Quick Validation**: Mark stories as validated directly from the dashboard
2. **Detailed Validation**: Add confidence levels (1-5) and notes
3. **Validation Status**: Track which stories need review

### Feedback System

- **Ratings**: 1-5 star ratings for implementation quality
- **Comments**: Text feedback on results and process
- **Validation**: Yes/No/Partial implementation status

### Bug Creation

Create bug tickets directly from user stories with:
- Auto-linking to the user story that revealed the bug
- Priority assessment (Critical/High/Medium/Low)
- Category selection (crash/performance/ui/logic/etc.)
- Reproduction steps
- Integration with BugTrackingSkill and database

### Screenshot Management

- Upload PNG, JPG, JPEG, GIF files
- Add titles and annotations
- Link to specific user stories
- Tag for categorization
- View in sortable grid

## Technical Integration

### RoadmapParser Integration

The app uses `coffee_maker.autonomous.roadmap_parser.RoadmapParser` to:
- Parse ROADMAP.md
- Extract user stories and priorities
- Get status information
- Support filtering and searching

### BugTrackingSkill Integration

Uses `coffee_maker.utils.bug_tracking_helper` to:
- Create bug tickets in the database
- Link bugs to user stories
- Query existing bugs
- Update bug status
- View bug analytics

### Database Integration

Connects to `data/orchestrator.db` for:
- Bug tracking (bugs table)
- Bug analytics views
- Validation tracking (future enhancement)

## Usage Examples

### Creating a Bug Ticket

1. Navigate to the user story in the dashboard
2. Click "🐛 Create Bug"
3. Fill in title, description, priority, and category
4. Submit - bug is automatically linked to the user story

### Uploading Screenshots

1. Go to the "📸 Screenshots" page
2. Upload your screenshot file
3. Link to a user story (optional)
4. Add title and notes
5. Add tags for categorization
6. Save

### Validating User Stories

1. Go to "✅ Validation Tracking"
2. Select a user story needing validation
3. Choose validation status
4. Set confidence level (1-5)
5. Add validation notes
6. Save validation

## Data Persistence

- **Bug Tickets**: Stored in SQLite database (`data/orchestrator.db`)
- **Screenshots**: Stored in `streamlit_apps/user_story_management/uploads/`
- **Screenshot Metadata**: Stored as `.meta.txt` files alongside images
- **Validation Data**: Currently in-memory (future: database integration)

## Future Enhancements

- [ ] Persist validation data to database
- [ ] Add DoD (Definition of Done) management page
- [ ] Export validation reports to CSV/PDF
- [ ] Add user authentication
- [ ] Integration with GitHub Issues
- [ ] Real-time collaboration features
- [ ] Notification system for new bugs/validations
- [ ] Dashboard analytics widgets

## Troubleshooting

### ROADMAP.md Not Found

Ensure you're running from the project root and `docs/roadmap/ROADMAP.md` exists.

### Bug Tracking Skill Error

Ensure the BugTrackingSkill is properly initialized:
- Check `data/orchestrator.db` exists
- Verify `.claude/skills/shared/bug-tracking/bug_tracking.py` exists

### Upload Directory Permissions

Ensure `streamlit_apps/user_story_management/uploads/` is writable.

## Support

For issues or questions:
- Check US-111 in ROADMAP.md
- Review SPEC-111 for technical details
- Check `.claude/skills/shared/bug-tracking/` for bug tracking implementation

## Version

**Version**: 1.0.0
**Created**: 2025-10-21
**Author**: code_developer (autonomous)
**Related**: US-111, SPEC-111
