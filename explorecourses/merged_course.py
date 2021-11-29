"""
Implements the MergedCourse class, which computes and represents merged course listings

"""

from dataclasses import dataclass
from functools import total_ordering
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


@total_ordering
@dataclass(frozen=True)
class MergedCourse:
    """Unified representation of multiple listings of a course"""

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

    _crosslist_codes_pattern = re.compile(r" \([^)]*\)$")

    @classmethod
    def from_courses(cls, courses: Iterable[Course]):
        """Construct new MergedCourse from a collection of Course objects"""
        courses = sorted(set(courses))
        base = courses[0]
        rest = courses[1:]

        title_stop = len(base.title)
        title_match = cls._crosslist_codes_pattern.search(base.title)
        if title_match is not None:
            title_stop = title_match.start()

        if any((base.year, base.course_id) != (c.year, c.course_id) for c in rest):
            raise ValueError("not all entries are listings of the same course")

        # I _think_ the following are always equal for crosslistings. The asserts are to
        # notify of exceptions such that the class layout can be adjusted accordingly.
        assert all(base.title[:title_stop] == c.title[:title_stop] for c in rest)
        assert all(base.description == c.description for c in rest)
        assert all(base.repeatable == c.repeatable for c in rest)
        assert all(base.grading == c.grading for c in rest)
        assert all(base.units_min == c.units_min for c in rest)
        assert all(base.units_max == c.units_max for c in rest)
        assert all(base.learning_objectives == c.learning_objectives for c in rest)
        assert all(base.attributes == c.attributes for c in rest)

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
    def course_code(self):
        """Course codes for all listings"""
        return tuple(f"{s} {c}" for s, c in zip(self.subject, self.code))

    @property
    def course_id(self):
        """Unique course id"""
        return self.administrative_information[0].course_id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.year, self.course_code) == (other.year, other.course_code)

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.year, self.course_code) < (other.year, other.course_code)

    def __hash__(self):
        return hash((self.year, self.course_code))


def merge_crosslistings(courses: Iterable[Course]) -> List[MergedCourse]:
    """Merge cross-listings of the same course in a collection of courses"""
    courses = set(courses)
    merged_courses = []
    while courses:
        base = courses.pop()
        group = [base]
        for course in list(courses):
            if (base.year, base.course_id) == (course.year, course.course_id):
                group.append(course)
                courses.remove(course)
        merged_courses.append(MergedCourse.from_courses(group))
    return merged_courses
