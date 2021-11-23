"""
Implements the MergedCourse class, which computes and represents merged cross-listings

"""

from collections import deque
from dataclasses import dataclass
import re
from typing import FrozenSet, Iterable, List, Optional, Tuple

from explorecourses.classes import (
    LearningObjective,
    Attribute,
    Section,
    AdministrativeInformation,
    Tag,
    Course,
)


@dataclass(frozen=True)
class MergedCourse:
    """A course with all cross-listings merged"""

    year: str
    subject: Tuple[str]
    code: Tuple[str]
    title: str
    description: str
    gers: Tuple[FrozenSet[str]]
    repeatable: bool
    grading: str
    units_min: int
    units_max: int
    remote: Tuple[Optional[bool]]
    learning_objectives: FrozenSet[LearningObjective]
    sections: Tuple[FrozenSet[Section]]
    administrative_information: Tuple[AdministrativeInformation]
    attributes: FrozenSet[Attribute]
    tags: Tuple[FrozenSet[Tag]]

    _crosslist_paren = re.compile(r" \([^)]*\)$")

    @classmethod
    def from_courses(cls, courses: Iterable[Course]):
        """Construct new MergedCourse from a collection of Course objects"""
        courses = sorted(set(courses))
        base = courses[0]
        rest = courses[1:]

        title_stop = len(base.title)
        title_match = cls._crosslist_paren.search(base.title)
        if title_match is not None:
            title_stop = title_match.start()

        if not all(
            (c.year, c.administrative_information.course_id)
            == (base.year, base.administrative_information.course_id)
            for c in rest
        ):
            raise ValueError("not all entries are cross-listings of same course")
        assert all(c.title[:title_stop] == base.title[:title_stop] for c in rest)
        assert all(c.description == base.description for c in rest)
        assert all(c.repeatable == base.repeatable for c in rest)
        assert all(c.grading == base.grading for c in rest)
        assert all(c.units_min == base.units_min for c in rest)
        assert all(c.units_max == base.units_max for c in rest)
        assert all(c.learning_objectives == base.learning_objectives for c in rest)
        assert all(c.attributes == base.attributes for c in rest)

        return cls(
            base.year,
            (base.subject, *(c.subject for c in rest)),
            (base.code, *(c.code for c in rest)),
            base.title[:title_stop],
            base.description,
            (base.gers, *(c.gers for c in rest)),
            base.repeatable,
            base.grading,
            base.units_min,
            base.units_max,
            (base.remote, *(c.remote for c in rest)),
            base.learning_objectives,
            (base.sections, *(c.sections for c in rest)),
            (
                base.administrative_information,
                *(c.administrative_information for c in rest),
            ),
            base.attributes,
            (base.tags, *(c.tags for c in rest)),
        )

    @property
    def course_codes(self):
        """Course codes"""
        return tuple(f"{s} {c}" for s, c in zip(self.subject, self.code))

    @property
    def course_id(self):
        """Unique course id"""
        return self.administrative_information[0].course_id

    @classmethod
    def merge_crosslistings(cls, courses: Iterable[Course]) -> List:
        """Merge all cross-listings of the same courses in a collection of courses"""
        courses = sorted(set(courses), reverse=True)
        merged_courses = []
        while courses:
            base = courses.pop()
            group = [base]
            for course in list(courses):
                if (course.year, course.administrative_information.course_id) == (
                    base.year,
                    base.administrative_information.course_id,
                ):
                    group.append(course)
                    courses.remove(course)
            merged_courses.append(cls.from_courses(group))
        return merged_courses
