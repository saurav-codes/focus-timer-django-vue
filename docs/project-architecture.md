# Sunsama Clone Project Architecture

## Overview
This document outlines the architecture for our Sunsama clone productivity application built with Django and Vue.js 3. The application features a Kanban board and Calendar view for task management with drag-and-drop functionality.

## Tech Stack
- **Frontend**: Vue.js 3, Pinia, Vue Router
- **Backend**: Django, Django REST Framework
- **UI Components**: Custom components with Lucide icons
- **Styling**: Custom CSS with utility classes

## Core Features
1. **Dual View System**
   - Kanban-focused view
   - Calendar-focused view

2. **Task Management**
   - Create, edit, delete tasks
   - Drag-and-drop between columns
   - Task completion with visual indicators
   - Task ordering within columns

3. **Column Types**
   - Brain Dump column (for quick task capture)
   - Date-based Kanban columns
   - Today's Tasks column

4. **Calendar Integration**
   - Day view (in Kanban-focused layout)
   - Week view (in Calendar-focused layout)
   - Task time blocks with resizing capability

## Data Models

### Task
- Title (required)
- Description (optional)
- Status (todo, in_progress, done)
- Order (for sorting within columns)
- Created At (timestamp)

## Component Architecture

### Shared Components
1. **TaskCard**
   - Displays task information
   - Provides edit/delete actions
   - Shows completion status
   - Draggable

2. **KanbanColumn**
   - Displays tasks for a specific date/category
   - Handles task sorting
   - Accepts drag-and-drop

3. **BrainDumpColumn**
   - Special column for capturing quick tasks
   - Has "Add Task" button with keyboard shortcut hint
   - Supports drag-out to other columns

4. **TaskCreationPopup**
   - Notion/Spotlight-style modal popup for quick task creation
   - Triggered by 'a' keyboard shortcut
   - Shows keyboard shortcut hints (Enter to save, Esc to close)
   - Supports task duration customization via dropdown menu
   - Provides real-time visual feedback of selected duration

5. **CalendarComponent**
   - Configurable view (day/week)
   - Displays tasks as time blocks
   - Supports task resizing
   - Accepts task drops

### View Components
1. **KanbanPlannerView**
   - Brain Dump Column (left)
   - 3 Kanban Columns (center, date-based)

2. **CalendarPlannerView**
   - Brain Dump Column (left)
   - Week View Calendar (center)
   - Single Kanban Column for current day (right & toggleable )

## State Management

### TaskStore (Pinia)
- **State**
  - columns: Array of column objects with date and tasks
  - brainDumpTasks: Array of tasks
  - calendarTasks: Array of tasks with time information

- **Actions**
  - fetchTasks: Load tasks from backend
  - createTask: Add new task
  - updateTask: Modify existing task
  - deleteTask: Remove task
  - moveTaskToColumn: Change task column
  - moveTaskToCalendar: Place task on calendar
  - reorderTasks: Change task order within column
  - toggleTaskCompletion: Mark task as done/undone

## API Endpoints

### Tasks
- GET /api/tasks/ - List all tasks
- POST /api/tasks/ - Create new task
- GET /api/tasks/{id}/ - Retrieve task
- PUT /api/tasks/{id}/ - Update task
- PATCH /api/tasks/{id}/ - Partial update task
- DELETE /api/tasks/{id}/ - Delete task

## User Interaction Flows

### Task Creation
1. User triggers task creation through one of two methods:
   - Clicks the "Add Task" button in the Brain Dump column
   - Presses the 'a' keyboard shortcut (when not focused in an input field)
2. A centered modal popup appears (Notion/Spotlight style)
3. User enters task description in the input field
4. User can customize task duration (optional):
   - Click on the duration button (defaults to "30m")
   - Use the hours/minutes selectors in the dropdown
   - Changes are applied immediately
5. Task can be saved by:
   - Pressing Enter key
   - Clicking outside the popup (auto-saves if input has content)
6. User can cancel task creation by:
   - Pressing Escape key
   - Clicking the close button
7. On save, task is created with specified duration and added to the Brain Dump column
8. UI is updated immediately (optimistic update) while backend request is processed

### Task Movement
1. User drags task from source column
2. Task can be dropped into:
   - Another Kanban column
   - Calendar (as time block)
3. Task is removed from source column
4. Backend is updated with new task location

### Task Completion
1. User hovers over task
2. Checkbox appears
3. User clicks checkbox
4. Task is visually marked as complete (strikethrough, muted)
5. Backend is updated with completion status

## Future Enhancements
1. **User Authentication & Teams**
   - Multi-user support
   - Team collaboration
   - Permission system

2. **Integrations**
   - Two-way sync with external task managers
   - Calendar app integration (Google, Outlook)
   - Email integration (Gmail)

3. **Advanced Features**
   - Keyboard shortcuts
   - Time tracking
   - Task prioritization
   - Offline support
   - Filtering and search

4. **UI Enhancements**
   - Responsive design
   - Dark/light theme
   - Customizable columns

## Implementation Phases

### Phase 1: Core Functionality
- Basic task management
- Kanban and Calendar views
- Drag-and-drop between columns

### Phase 2: Enhanced User Experience
- Task details view
- Visual polish
- Performance optimization

### Phase 3: Advanced Features
- Integrations
- Multi-user support
- Time tracking

## Development Best Practices
1. **Component Design**
   - Single responsibility principle
   - Reusable components
   - Props validation

2. **State Management**
   - Centralized Pinia store
   - Optimistic UI updates
   - Error handling

3. **API Communication**
   - Consistent error handling
   - Loading states
   - Request debouncing

4. **Performance**
   - Lazy loading components
   - Pagination for large data sets
   - Efficient rendering

5. **Testing**
   - Unit tests for components
   - Integration tests for views
   - API endpoint tests
