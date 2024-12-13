from pymongo import MongoClient
from bson.objectid import ObjectId
from tabulate import tabulate
from datetime import datetime

# Database connection
def connect_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["cms_hclTraining"]

# Course Management
def add_course():
    course_name = input("Enter course name: ")
    capacity = int(input("Enter course capacity: "))
    credits = int(input("Enter course credits: "))
    day = input("Enter day of the week: ")
    time = input("Enter time slot (e.g., 10:00 AM - 12:00 PM): ")
    room = input("Enter room number: ")

    db = connect_db()
    course = {
        "course_name": course_name,
        "capacity": capacity,
        "credits": credits,
        "schedule": {
            "day": day,
            "time": time,
            "room": room
        }
    }
    db.Courses.insert_one(course)
    print("Course added successfully!")

#list course
def list_courses():
    db = connect_db()
    courses = db.Courses.find()
    table = []
    for course in courses:
        table.append([
            str(course["_id"]), course["course_name"], course["capacity"], course["credits"],
            f"{course['schedule']['day']} {course['schedule']['time']} ({course['schedule']['room']})"
        ])
    print(tabulate(table, headers=["ID", "Name", "Capacity", "Credits", "Schedule"], tablefmt="grid"))

# Student Management
def register_student():
    name = input("Enter student name: ")
    email = input("Enter student email: ")

    db = connect_db()
    student = {
        "name": name,
        "email": email,
        "enrolled_courses": []
    }
    db.Students.insert_one(student)
    print("Student registered successfully!")

#list student
def list_students():
    db = connect_db()
    students = db.Students.find()
    table = []
    for student in students:
        table.append([str(student["_id"]), student["name"], student["email"]])
    print(tabulate(table, headers=["ID", "Name", "Email"], tablefmt="grid"))

# Enrollment Management
def enroll_student():
    student_id = input("Enter student ID: ")
    course_id = input("Enter course ID: ")

    db = connect_db()

    # Find course and check capacity
    course = db.Courses.find_one({"_id": ObjectId(course_id)})
    if not course or course["capacity"] <= 0:
        print("Error: Course is full or does not exist.")
        return

    # Find student
    student = db.Students.find_one({"_id": ObjectId(student_id)})
    if not student:
        print("Error: Student does not exist.")
        return

    # Enroll student and update course capacity
    db.Students.update_one(
        {"_id": ObjectId(student_id)},
        {"$push": {"enrolled_courses": {"course_id": course_id, "course_name": course["course_name"]}}}
    )

    db.Courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$inc": {"capacity": -1}}
    )

    # Store the actual ObjectIds in the Enrollments collection
    db.Enrollments.insert_one({
        "student_id": ObjectId(student_id), 
        "course_id": ObjectId(course_id), 
        "timestamp": datetime.now().isoformat()
    })

    print("Student enrolled successfully!")
#list all enrollment

def list_enrollments():
    db = connect_db()
    enrollments = db.Enrollments.aggregate([
        {
            "$lookup": {
                "from": "Students",
                "localField": "student_id",
                "foreignField": "_id",
                "as": "student_details"
            }
        },
        {
            "$unwind": "$student_details" 
        }, 
        {
            "$lookup": {
                "from": "Courses",
                "localField": "course_id",
                "foreignField": "_id",
                "as": "course_details"
            }
        },
        {
            "$unwind": "$course_details" 
        },
        {
            "$project": {
                "student_name": "$student_details.name",
                "course_name": "$course_details.course_name",
                "timestamp": 1
            }
        }
    ])

    table = []
    for enrollment in enrollments:
        table.append([enrollment["student_name"], enrollment["course_name"], enrollment["timestamp"]])

    print(tabulate(table, headers=["Student Name", "Course Name", "Enrollment Date"], tablefmt="grid"))

# Reports
def generate_report():
    list_enrollments()

# Main Menu+
def main():
    while True:
        print("\n=== Course Registration and Scheduling System ===")
        print("1. Add Course")
        print("2. List Courses")
        print("3. Register Student")
        print("4. List Students")
        print("5. Enroll Student")
        print("6. List Enrollments")
        print("7. Generate Report")
        print("8. Exit")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            add_course()
        elif choice == 2:
            list_courses()
        elif choice == 3:
            register_student()
        elif choice == 4:
            list_students()
        elif choice == 5:
            enroll_student()
        elif choice == 6:
            list_enrollments()
        elif choice == 7:
            generate_report()
        elif choice == 8:
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()