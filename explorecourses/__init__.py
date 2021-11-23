"""Stanford ExploreCourses API"""

from explorecourses.course_connection import CourseConnection
from explorecourses.classes import (
    Course,
    LearningObjective,
    Section,
    Schedule,
    Instructor,
    Attribute,
    AdministrativeInformation,
    Tag,
    School,
    Department,
)
from explorecourses.merged_course import MergedCourse, merge_crosslistings

__version__ = "2.0.0"

__author__ = (
    "Jeremy Ephron <jeremye@stanford.edu>, Daniel Wennberg <daniel.wennberg@gmail.com>"
)

__all__ = [
    "CourseConnection",
    "MergedCourse",
    "Course",
    "LearningObjective",
    "Section",
    "Schedule",
    "Instructor",
    "Attribute",
    "AdministrativeInformation",
    "Tag",
    "School",
    "Department",
    "merge_crosslistings",
]
