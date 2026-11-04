
import re
import sqlite3

from database import add_student, update_student


def validate_student(student_id, name, class_name,
                     gender, phone, marks):

    if not student_id.strip():
        return False, "Please enter the Student ID."

    if not name.strip():
        return False, "Please enter the student's name."

    if not class_name.strip():
        return False, "Please select the student's class."

    if not gender.strip():
        return False, "Please select the student's gender."

    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return False, "Marks must be a valid number."

    if not 0 <= marks <= 100:
        return False, "Marks must be between 0 and 100."

    if phone.strip() and not re.fullmatch(
        r"\+?\d{7,15}", phone.strip()
    ):
        return False, "Please enter a valid phone number."

    return True, "Student information is valid."


def register_student(student_id, name, class_name,
                     gender, phone, marks):

    valid, message = validate_student(
        student_id, name, class_name,
        gender, phone, marks
    )

    if not valid:
        return False, message

    try:
        add_student(
            student_id.strip(),
            name.strip(),
            class_name.strip(),
            gender.strip(),
            phone.strip(),
            float(marks)
        )

        return True, "Student registered successfully!"

    except sqlite3.IntegrityError:
        return False, "This Student ID already exists."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def edit_student(record_id, student_id, name,
                 class_name, gender, phone, marks):

    valid, message = validate_student(
        student_id, name, class_name,
        gender, phone, marks
    )

    if not valid:
        return False, message

    try:
        update_student(
            record_id,
            student_id.strip(),
            name.strip(),
            class_name.strip(),
            gender.strip(),
            phone.strip(),
            float(marks)
        )

        return True, "Student information updated successfully!"

    except sqlite3.IntegrityError:
        return False, "This Student ID already belongs to another student."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"
