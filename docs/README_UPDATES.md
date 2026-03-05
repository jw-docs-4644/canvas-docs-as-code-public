# Proposed README Updates

This document outlines the changes that should be made to README.md to document the multi-course configuration system.

## Overview

The codebase has been refactored to support multiple courses in a single repository. The configuration system now:
- Stores shared Canvas API credentials in a root `.env` file
- Stores per-course IDs in each course's `course.yaml` file
- Uses an intelligent fallback system for backward compatibility

## Specific Changes to README.md

### 1. Update "Setup" Section - Step 2

**Current text:**
```
2. Set up your .env file

   1. Copy .env.example to .env
   2. Get your Canvas API and save it in  .env
   3. Put the course ID of the course you want in .env as well. **Note: I highly recommend working in a sandbox course if your institution makes them available to you.
```

**Proposed replacement:**
```
2. Set up your .env file

   1. Copy .env.example to .env
   2. Get your Canvas API key and save it in .env (CANVAS_API_URL and CANVAS_API_KEY)
   3. **Note:** COURSE_ID is now stored in each course's `course.yaml` file instead of .env, so it can differ per course. See step 4 below.
```

### 2. Update "Setup" Section - Step 4 (Add to course folder instructions)

**Current text:**
```
   4. Make a copy of the course_template folder and rename it for your course.
      Your course folder should include the following sub-folders:

      - Assignments
      - Discussions
      - Pages
      - Files
```

**Proposed replacement:**
```
   4. Make a copy of the course_template folder and rename it for your course.
      Your course folder should include the following sub-folders:

      - Assignments
      - Discussions
      - Pages
      - Files

      Also, copy `course.yaml.example` to `course.yaml` and add your Canvas course ID to the `course_id` field at the top of the file. **Note: I highly recommend working in a sandbox course if your institution makes them available to you.**
```

### 3. Replace "Configuration" Section

**Current text:**
```
### Configuration

Configure the .env to store your Canvas API key and the ID number for the course you are working on.

<!-- Need to figure out how to handle course-specific ID numbers for individual courses within the Repo. -->
```

**Proposed replacement:**
```
### Configuration

**Shared credentials** (root .env):
- Store your Canvas API credentials in the root `.env` file: `CANVAS_API_URL` and `CANVAS_API_KEY`
- These are shared across all courses in the repository

**Per-course configuration** (course.yaml):
- Each course folder has its own `course.yaml` file
- Set the `course_id` field at the top to specify which Canvas course this folder syncs to
- This allows multiple course folders in the same repository without conflicts
- The scripts automatically read the course ID from `course.yaml` when available, with fallback to the environment variable for backward compatibility
```

## Implementation Notes

- These changes directly address the TODO comment in the original Configuration section
- The new approach is more flexible and allows the repository to handle multiple courses elegantly
- Backward compatibility is maintained: scripts still work if COURSE_ID is defined in .env
- The changes are clear and guide users through the new multi-course workflow
