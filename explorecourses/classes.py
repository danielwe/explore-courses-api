"""
Implements classes representing elements of the ExploreCourses catalog

Includes:
  - Course
    - LearningObjective
    - Section
      - Schedule
        - Instructor
      - Attribute
    - AdministrativeInformation
    - Tag
  - School
    - Department

"""

from dataclasses import dataclass
from functools import total_ordering
from typing import FrozenSet, Optional, Tuple
from xml.etree.ElementTree import Element


def _bool_or_none(condition: str, true: str, false: str) -> Optional[bool]:
    if condition == true:
        return True
    if condition == false:
        return False
    return None


@dataclass(frozen=True)
class Department:
    """A department at the university"""

    longname: str
    name: str

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Department from an XML element"""
        return cls(elem.get("longname"), elem.get("name"))


@dataclass(frozen=True)
class School:
    """A school at the university"""

    name: str
    departments: FrozenSet[Department]

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new School from an XML element"""
        return cls(
            elem.get("name"),
            frozenset(Department.from_xml(dept) for dept in elem.findall("department")),
        )

    def department(self, name: str) -> Department:
        """
        Find department within the school

        Args:
            name (str): Full name or subject code identifying the department

        Returns:
            Department: The mathcing department

        """
        lname = name.lower()
        for dept in self.departments:
            if lname in (dept.longname.lower(), dept.name.lower()):
                return dept
        raise ValueError(f"no department named '{name}'")


@dataclass(frozen=True)
class LearningObjective:
    """A learning objective for a course"""

    requirement_code: str
    description: str

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new LearningObjective from an XML element"""
        return cls(elem.findtext("requirementCode"), elem.findtext("description"))


@dataclass(frozen=True)
class Instructor:
    """An instructor for a section"""

    name: str
    first_name: str
    middle_name: str
    last_name: str
    sunet: str
    role: str

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Instructor from an XML element"""
        return cls(
            elem.findtext("name"),
            elem.findtext("firstName"),
            elem.findtext("middleName"),
            elem.findtext("lastName"),
            elem.findtext("sunet"),
            elem.findtext("role"),
        )


@dataclass(frozen=True)
class Schedule:
    """A schedule for a section"""

    start_date: str
    end_date: str
    start_time: str
    end_time: str
    location: str
    days: Tuple[str]
    instructors: FrozenSet[Instructor]

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Schedule from an XML element"""
        return cls(
            elem.findtext("startDate"),
            elem.findtext("endDate"),
            elem.findtext("startTime"),
            elem.findtext("endTime"),
            elem.findtext("location"),
            tuple(elem.findtext("days").split()),
            frozenset(Instructor.from_xml(instr) for instr in elem.find("instructors")),
        )


@dataclass(frozen=True)
class Attribute:
    """An attribute of a course or section"""

    name: str
    value: str
    description: str
    catalog_print: bool
    schedule_print: bool

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Attribute from an XML element"""
        return cls(
            elem.findtext("name"),
            elem.findtext("value"),
            elem.findtext("description"),
            elem.findtext("catalogPrint") == "true",
            elem.findtext("schedulePrint") == "true",
        )


@dataclass(frozen=True)
class Section:
    """A section of a course"""

    class_id: int
    term: str
    term_id: int
    subject: str
    code: str
    units: str
    section_number: str
    component: str
    num_enrolled: int
    max_enrolled: int
    num_waitlist: int
    max_waitlist: int
    enroll_status: str
    add_consent: str
    drop_consent: str
    instruction_mode: str
    course_id: int
    schedules: FrozenSet[Schedule]
    # current_class_size: int  # Redundant, possibly deprecated
    # max_class_size: int
    # current_waitlist_size: int
    # max_waitlist_size: int
    notes: str
    attributes: FrozenSet[Attribute]

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Section from an XML element"""
        return cls(
            int(elem.findtext("classId")),
            elem.findtext("term"),
            int(elem.findtext("termId")),
            elem.findtext("subject"),
            elem.findtext("code"),
            elem.findtext("units"),
            elem.findtext("sectionNumber"),
            elem.findtext("component"),
            int(elem.findtext("numEnrolled")),
            int(elem.findtext("maxEnrolled")),
            int(elem.findtext("numWaitlist")),
            int(elem.findtext("maxWaitlist")),
            elem.findtext("enrollStatus"),
            elem.findtext("addConsent"),
            elem.findtext("dropConsent"),
            elem.findtext("instructionMode"),
            int(elem.findtext("courseId")),
            frozenset(Schedule.from_xml(sched) for sched in elem.find("schedules")),
            # int(elem.findtext("currentClassSize")),  # Redundant, possibly deprecated
            # int(elem.findtext("maxClassSize")),
            # int(elem.findtext("currentWaitlistSize")),
            # int(elem.findtext("maxWaitlistSize")),
            elem.findtext("notes"),
            frozenset(Attribute.from_xml(attr) for attr in elem.find("attributes")),
        )


@dataclass(frozen=True)
class AdministrativeInformation:
    """Administrative information about a course"""

    course_id: int
    effective_status: str
    offer_number: int
    academic_group: str
    academic_organization: str
    academic_career: str
    final_exam_flag: Optional[bool]
    catalog_print: bool
    schedule_print: bool
    max_units_repeat: int
    max_times_repeat: int

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new AdministrativeInformation from an XML element"""
        return cls(
            int(elem.findtext("courseId")),
            elem.findtext("effectiveStatus"),
            int(elem.findtext("offerNumber")),
            elem.findtext("academicGroup"),
            elem.findtext("academicOrganization"),
            elem.findtext("academicCareer"),
            _bool_or_none(elem.findtext("finalExamFlag"), "Y", "N"),
            elem.findtext("catalogPrint") == "Y",
            elem.findtext("schedulePrint") == "Y",
            int(elem.findtext("maxUnitsRepeat")),
            int(elem.findtext("maxTimesRepeat")),
        )


@dataclass(frozen=True)
class Tag:
    """A tag for a course"""

    organization: str
    name: str

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new Tag from an XML element"""
        return cls(elem.findtext("organization"), elem.findtext("name"))


@total_ordering
@dataclass(frozen=True)
class Course:
    """A course from the catalog"""

    year: str
    subject: str
    code: str
    title: str
    description: str
    gers: FrozenSet[str]
    repeatable: bool
    grading: str
    units_min: int
    units_max: int
    remote: Optional[bool]
    learning_objectives: FrozenSet[LearningObjective]
    sections: FrozenSet[Section]
    administrative_information: AdministrativeInformation
    attributes: FrozenSet[Attribute]
    tags: FrozenSet[Tag]

    @classmethod
    def from_xml(cls, elem: Element):
        """Construct new AdministrativeInformation from an XML element"""
        return cls(
            elem.findtext("year"),
            elem.findtext("subject"),
            elem.findtext("code"),
            elem.findtext("title"),
            elem.findtext("description"),
            frozenset(elem.findtext("gers").split(", ")),
            elem.findtext("repeatable") == "true",
            elem.findtext("grading"),
            int(elem.findtext("unitsMin")),
            int(elem.findtext("unitsMax")),
            _bool_or_none(elem.findtext("remote"), "true", "false"),
            frozenset(
                LearningObjective.from_xml(lo) for lo in elem.find("learningObjectives")
            ),
            frozenset(Section.from_xml(section) for section in elem.find("sections")),
            AdministrativeInformation.from_xml(elem.find("administrativeInformation")),
            frozenset(Attribute.from_xml(attr) for attr in elem.find("attributes")),
            frozenset(Tag.from_xml(tag) for tag in elem.find("tags")),
        )

    @property
    def course_code(self):
        """Course code"""
        return f"{self.subject} {self.code}"

    @property
    def course_id(self):
        """Unique course id"""
        return self.administrative_information.course_id

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
