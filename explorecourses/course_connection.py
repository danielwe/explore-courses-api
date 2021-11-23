"""
Implements the CourseConnection class, the main entrypoint for the ExploreCourses API

"""

from typing import List
import xml.etree.ElementTree as ET
import requests

from explorecourses.classes import School, Course


class CourseConnection:
    """
    Main entrypoint for the Explore Courses API

    Establishes the HTTP connection and makes requests.

    """

    _URL = "https://explorecourses.stanford.edu/"

    def __init__(self):
        self._session = requests.Session()

    def find_schools(self, year=None) -> List[School]:
        """
        Find all schools at the university

        Args:
            year (Optional[str]): Academic year for which to retrive schools, e.g.,
                "2021-2022". Defaults to None, which selects the current year.

        Returns:
            List[School]: All schools at the university

        """
        payload = {"view": "xml-20200810"}
        if year is not None:
            payload["academicYear"] = year.replace("-", "")
        res = self._session.get(self._URL, params=payload)
        root = ET.fromstring(res.content)
        return [School.from_xml(school) for school in root.findall(".//school")]

    def find_school(self, name: str) -> School:
        """
        Find a school within the university by name

        Args:
            name (str): Name of the school

        Returns:
            School: The school if it exists, otherwise None

        """
        for school in self.find_schools():
            if school.name == name:
                return school
        raise ValueError(f"no school named {name}")

    def find_courses_by_subject(
        self, subject: str, *filters: str, year=None
    ) -> List[Course]:

        """
        Find all courses under a given subject

        Args:
            subject (str): Subject code, e.g., "MATH"
            *filters (str): Search filters
            year (Optional[str]): Academic year for which to retrieve courses, e.g.,
                "2021-2022". Defaults to None, which selects the current year.

        Returns:
            List[Course]: All courses offered by the department

        """
        filters = list(filters)
        filters.append(f"filter-departmentcode-{subject}")
        return self.find_courses_by_query(subject, *filters, year=year)

    def find_courses_by_query(
        self, query: str, *filters: str, year=None
    ) -> List[Course]:

        """
        Find all courses matching a search query

        Args:
            query (str): Search query
            *filters (str): Search filters
            year (Optional[str]): Academic year for which to retrieve courses, e.g.,
                "2021-2022". Defaults to None, which selects the current year.

        Returns:
            List[Course]: Courses matching the search query

        """
        payload = {
            "view": "xml-20200810",
            "filter-coursestatus-Active": "on",
            "q": query,
        }
        payload.update({f: "on" for f in filters})
        if year is not None:
            payload["academicYear"] = year.replace("-", "")
        res = self._session.get(self._URL + "search", params=payload)
        root = ET.fromstring(res.content)
        return [Course.from_xml(course) for course in root.findall(".//course")]
