"""
Helper module for loading configuration from course.yaml and .env files.
Provides intelligent fallback: course.yaml takes precedence over .env
"""
import os
import yaml
from dotenv import load_dotenv


def load_course_id(course_yaml_path="course.yaml"):
    """
    Load COURSE_ID from course.yaml, falling back to environment variable.

    Args:
        course_yaml_path: Path to course.yaml file

    Returns:
        str: The course ID

    Raises:
        ValueError: If course ID cannot be found
    """
    # First try to load from course.yaml
    if os.path.exists(course_yaml_path):
        try:
            with open(course_yaml_path, "r") as f:
                config = yaml.safe_load(f)
                if config and "course_id" in config:
                    course_id = config["course_id"]
                    if course_id and course_id != "YOUR_COURSE_ID_HERE":
                        return str(course_id)
        except Exception as e:
            print(f"Warning: Could not read course_id from {course_yaml_path}: {e}")

    # Fall back to environment variable
    load_dotenv()
    course_id = os.getenv("COURSE_ID")
    if course_id:
        return course_id

    raise ValueError(
        "COURSE_ID not found. Please either:\n"
        "  1. Set COURSE_ID in course.yaml, or\n"
        "  2. Set COURSE_ID in .env file"
    )


def load_canvas_config():
    """
    Load Canvas API configuration from .env

    Returns:
        tuple: (API_URL, API_KEY)

    Raises:
        ValueError: If required env vars are missing
    """
    load_dotenv()
    api_url = os.getenv("CANVAS_API_URL")
    api_key = os.getenv("CANVAS_API_KEY")

    if not api_url or not api_key:
        raise ValueError("Missing CANVAS_API_URL or CANVAS_API_KEY in .env")

    return api_url, api_key
