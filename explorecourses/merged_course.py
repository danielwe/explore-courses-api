"""
Implements the MergedCourse class, which computes and represents merged course listings

"""

from dataclasses import dataclass
from collections import defaultdict
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
    """Container and unified representation of multiple listings of a course"""

    year: str
    title: str
    description: str
    repeatable: bool
    grading: str
    units_min: int
    units_max: int
    learning_objectives: FrozenSet[LearningObjective]
    attributes: FrozenSet[Attribute]
    _listings: Tuple[Course]

    _crosslist_codes_pattern = re.compile(r" \([^)]*\)$")

    @classmethod
    def from_listings(cls, listings: Iterable[Course]):
        """Construct new MergedCourse from a collection of Course objects"""
        listings = tuple(sorted(set(listings)))
        base = listings[0]
        rest = listings[1:]

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
            base.title[:title_stop],
            base.description,
            base.repeatable,
            base.grading,
            base.units_min,
            base.units_max,
            base.learning_objectives,
            base.attributes,
            listings,
        )

    def __getitem__(self, index):
        return self._listings[index]

    def __len__(self):
        return len(self._listings)

    @property
    def course_code(self):
        """Course codes for all listings"""
        return tuple(f"{listing.subject} {listing.code}" for listing in self)

    @property
    def course_id(self):
        """Unique course id"""
        return self[0].administrative_information.course_id

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
    course_groups = defaultdict(list)
    for course in courses:
        course_groups[(course.year, course.course_id)].append(course)
    return [MergedCourse.from_listings(group) for group in course_groups.values()]
