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

__version__ = "2.0.0"

__author__ = (
    "Jeremy Ephron <jeremye@stanford.edu>, Daniel Wennberg <daniel.wennberg@gmail.com>"
)

__all__ = [
    "CourseConnection",
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
]
