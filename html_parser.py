from bs4 import BeautifulSoup
from datetime import datetime
import json



class Class:
    def __init__(self, start_time, end_time, day_of_week, location):
        self.start_time = start_time
        self.end_time = end_time
        self.day_of_week = day_of_week
        self.location = location

class Section:
    def __init__(self, crn, course):  # Add 'course' parameter
        self.crn = crn
        self.course = course  # Store reference to the Course object
        self.classes = []

class Course:
    def __init__(self, name):
        self.name = name
        self.sections = []

# Parse HTML content
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all course blocks
    course_blocks = soup.find_all(class_="courseBlock")

    courses = []
    for block in course_blocks:
        course_name_full = block.find(class_="subjectAndNumberTag").text.strip()
        course_name, crn = course_name_full.split('-')  # Split course name and CRN
        time_info = block.find(class_="extraInfoTime").text.strip().split('-')
        start_time = time_info[0]
        end_time = time_info[1]
        day_of_week = block.parent['id'][:3]  # Extract day of the week from parent column id
        location = block.find(class_="extraInfoBuilding").text.strip()
        
        # Create Class object
        class_info = Class(start_time, end_time, day_of_week, location)
        
        # Check if Course object already exists
        course = next((c for c in courses if c.name == course_name), None)
        if not course:
            course = Course(course_name)
            courses.append(course)
        
        # Check if Section object already exists
        section = next((s for s in course.sections if s.crn == crn), None)
        if not section:
            section = Section(crn, course)  # Pass 'course' to Section constructor
            course.sections.append(section)

        
        # Add Class to Section
        section.classes.append(class_info)
    
    return courses


def generate_schedules(courses):
    def backtrack(schedule, index):
        if index == len(courses):
            # Check if the schedule is valid (no overlapping class times)
            if is_valid(schedule):
                valid_schedules.append(schedule.copy())
            return
        
        for section in courses[index].sections:
            # Try adding each section of the current course to the schedule
            schedule.append(section)
            backtrack(schedule, index + 1)
            schedule.pop()  # Backtrack
        
    def is_valid(schedule):
        # Convert day abbreviations to full names
        day_mapping = {'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday'}
        
        # Initialize a dictionary to store class times for each day
        class_times = {day: [] for day in day_mapping.values()}
        
        # Iterate over each section in the schedule
        for section in schedule:
            for class_info in section.classes:
                day = day_mapping[class_info.day_of_week]
                start_time = datetime.strptime(class_info.start_time, '%I:%M%p').time()
                end_time = datetime.strptime(class_info.end_time, '%I:%M%p').time()
                # Check for overlapping class times
                for existing_start, existing_end in class_times[day]:
                    if (start_time < existing_end and end_time > existing_start):
                        return False  # Overlapping class times
                class_times[day].append((start_time, end_time))
        
        return True  # No overlapping class times
    
    valid_schedules = []
    backtrack([], 0)
    return valid_schedules

def print_courses(courses):
    # Print information of each course
    for course in courses:
        print("Course:", course.name)
        for section in course.sections:
            print("  Section CRN:", section.crn)
            for class_info in section.classes:
                print("    Class Time:", class_info.start_time, "-", class_info.end_time)
                print("    Day of the Week:", class_info.day_of_week)
                print("    Location:", class_info.location)
                print()


def print_schedules(possible_schedules):
    for i, schedule in enumerate(possible_schedules, start=1):
        print("Schedule", i)
        for section in schedule:
            print("Course:", section.course.name)  # Access course name via the associated Course object
            print("Section CRN:", section.crn)
            for class_info in section.classes:
                print("  Class Time:", class_info.start_time, "-", class_info.end_time)
                print("  Day of the Week:", class_info.day_of_week)
                print("  Location:", class_info.location)
            print()
        print("-" * 40)

def convert_to_json(possible_schedules):
    schedules_json = []
    for schedule in possible_schedules:
        schedule_data = []
        for section in schedule:
            section_data = {
                "course_name": section.course.name,
                "section_crn": section.crn,
                "classes": []
            }
            for class_info in section.classes:
                class_data = {
                    "start_time": class_info.start_time,
                    "end_time": class_info.end_time,
                    "day_of_week": class_info.day_of_week,
                    "location": class_info.location
                }
                section_data["classes"].append(class_data)
            schedule_data.append(section_data)
        schedules_json.append(schedule_data)
    return schedules_json

#function to read files
def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_json_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Sample HTML content (replace with your actual HTML content)
html_content = read_html_file('schedule.html')
# Now you have a list of possible schedules where none of the class times overlap.


# Parse HTML and get courses
courses = parse_html(html_content)
print_courses(courses)

print('-----------------------------------------------------------------------------------------------------------------------')


# Now you can work with the 'courses' list containing Course objects and their respective Sections and Classes.
# Generate possible schedules
possible_schedules = generate_schedules(courses)
schedules_json = convert_to_json(possible_schedules)
write_json_file(schedules_json, 'schedules.json')
print_schedules(possible_schedules)
