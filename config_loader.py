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


def load_zotero_config(course_yaml_path="course.yaml"):
    """
    Load Zotero API configuration from .env and collection ID from course.yaml.

    Args:
        course_yaml_path: Path to course.yaml file

    Returns:
        tuple: (API_KEY, USER_ID, COLLECTION_ID)

    Raises:
        ValueError: If required credentials are missing
    """
    load_dotenv()
    api_key = os.getenv("ZOTERO_API_KEY")
    user_id = os.getenv("ZOTERO_USER_ID")

    if not api_key or not user_id:
        raise ValueError("Missing ZOTERO_API_KEY or ZOTERO_USER_ID in .env")

    collection_id = None
    if os.path.exists(course_yaml_path):
        try:
            with open(course_yaml_path, "r") as f:
                config = yaml.safe_load(f)
                if config and "zotero_collection_id" in config:
                    val = config["zotero_collection_id"]
                    if val and val != "YOUR_COLLECTION_ID_HERE":
                        collection_id = str(val)
        except Exception as e:
            print(f"Warning: Could not read zotero_collection_id from {course_yaml_path}: {e}")

    return api_key, user_id, collection_id


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
