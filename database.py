import mysql.connector
from mysql.connector import Error

# ==============================================================================
# DISCRETE MATHEMATICS FORMAL DEFINITION:
# S = Set of Students = { 1260, 1262, ..., 1549 }
# C = Set of Courses  = { C01, C02, C03, C04, C05 }
# R ⊆ S × C (Binary Enrollment Relation from S to C)
# Each enrollment tuple (s, c) represents an ordered pair in relation R.
# ==============================================================================

# Centralized Database Configuration Details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sriram@3355"
DB_NAME = "student_course_db"

# Set S: All 48 Students (student_id = actual Roll Number)
INITIAL_STUDENTS = [
    ("1260", "BHAVISHYA CHOUDHARY"),
    ("1262", "BHAVY JAIN"),
    ("1270", "DUKE DHAWAN"),
    ("1271", "EKAKSH JEENA"),
    ("1282", "JASLEEN KAUR BHINDER"),
    ("1283", "JASON MATHEW"),
    ("1284", "KALI JINDAL"),
    ("1287", "KASHISH DAGAR"),
    ("1291", "KUMAR VIJAY"),
    ("1296", "LIPISHA CHAWLA"),
    ("1298", "LIPIKA"),
    ("1299", "NAITIK"),
    ("1302", "NEETI OJHA"),
    ("1307", "RATTAN KUMAR"),
    ("1310", "KARTIK SAINI"),
    ("1319", "TRIPTI RAWAT"),
    ("1326", "YASHIKA VERMA"),
    ("1331", "RIYA GOYAL"),
    ("1332", "KANAK"),
    ("1341", "ADITYA"),
    ("1345", "TAMANNA SINGH"),
    ("1347", "IPPILI SRIRAM"),
    ("1349", "ASHISH"),
    ("1404", "MARISETTY VENKATA RAM"),
    ("1503", "PUSHKAR RAI"),
    ("1506", "DHRUV"),
    ("1508", "SWASTI THAKUR"),
    ("1511", "PALLE JASWANTH REDDY"),
    ("1512", "KANAN SATIJA"),
    ("1513", "GAURI"),
    ("1516", "PRINCE SAINI"),
    ("1519", "KAYAKURALA ESHWAR KUMAR"),
    ("1520", "ROHIT GUSAIN"),
    ("1524", "OJAL SHARMA"),
    ("1530", "KRISH KUMAR"),
    ("1531", "KANGNA CHAUHAN"),
    ("1532", "UTKARSH RAWAT"),
    ("1533", "RAMAN RAJ"),
    ("1537", "PALAK VERMA"),
    ("1541", "BOYA SAI CHARAN"),
    ("1542", "PRINCE SHARMA"),
    ("1543", "PRATHAM SAINI"),
    ("1544", "NIKHIL CHANDELA"),
    ("1545", "KANAK"),
    ("1546", "ANSH GUPTA"),
    ("1547", "SHAURYAMAAN SACHDEVA"),
    ("1548", "PRINCE JADOUN"),
    ("1549", "SHIVAM SINGH")
]

# Set C: 5 Core Courses (course_id = C01, C02, C03, C04, C05)
INITIAL_COURSES = [
    ("C01", "DBMS", 3),
    ("C02", "Machine Learning", 4),
    ("C03", "Java", 3),
    ("C04", "Discrete Mathematics", 4),
    ("C05", "Artificial Intelligence", 4)
]

def get_db_connection(include_db=True):
    """
    Centralized MySQL database connection function.
    """
    try:
        if include_db:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def init_db():
    """
    Creates database 'student_course_db', tables, and seeds 48 students & 5 courses.
    """
    conn = get_db_connection(include_db=False)
    if not conn:
        print("Could not connect to MySQL server. Please verify MySQL service is running.")
        return False

    cursor = conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4;")
        conn.close()

        conn = get_db_connection(include_db=True)
        if not conn:
            return False
        cursor = conn.cursor()

        # Check legacy table structure
        cursor.execute("SHOW TABLES LIKE 'students';")
        if cursor.fetchone():
            cursor.execute("SHOW COLUMNS FROM students LIKE 'student_id';")
            col_info = cursor.fetchone()
            if col_info and ('int' in str(col_info[1]).lower() or 'auto_increment' in str(col_info[5]).lower()):
                cursor.execute("DROP TABLE IF EXISTS enrollments;")
                cursor.execute("DROP TABLE IF EXISTS students;")
                cursor.execute("DROP TABLE IF EXISTS courses;")

        # Table for Set S: Students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        # Table for Set C: Courses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id VARCHAR(20) PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                credits INT NOT NULL DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        # Table for Relation R ⊆ S × C: Enrollments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) NOT NULL,
                course_id VARCHAR(20) NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_enrollment (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)

        # Insert Students & Courses while avoiding duplicates
        cursor.executemany("INSERT IGNORE INTO students (student_id, name) VALUES (%s, %s);", INITIAL_STUDENTS)
        cursor.executemany("INSERT IGNORE INTO courses (course_id, course_name, credits) VALUES (%s, %s, %s);", INITIAL_COURSES)

        conn.commit()
        return True

    except Error as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_students():
    """
    Fetches all 48 students (Set S) from the database.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, name FROM students ORDER BY student_id ASC;")
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching students: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_courses():
    """
    Fetches all 5 courses (Set C) from the database.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT course_id, course_name, credits FROM courses ORDER BY course_id ASC;")
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching courses: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def enroll_student_in_courses(student_id, course_ids):
    """
    Inserts student-course ordered pairs (s, c) into relation R ⊆ S × C.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return 0, "Database connection error."

    try:
        cursor = conn.cursor()
        insert_query = "INSERT IGNORE INTO enrollments (student_id, course_id) VALUES (%s, %s);"
        pairs_to_insert = [(student_id, c_id) for c_id in course_ids]
        
        cursor.executemany(insert_query, pairs_to_insert)
        conn.commit()
        
        inserted_count = cursor.rowcount
        return inserted_count, "Enrollment successful."
    except Error as e:
        print(f"Error enrolling student: {e}")
        return 0, f"Database error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_enrollments():
    """
    Fetches all current ordered pairs in relation R ⊆ S × C.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                e.enrollment_id,
                s.student_id,
                s.name AS student_name,
                c.course_id,
                c.course_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY s.student_id ASC, c.course_id ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching enrollments: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_students_by_course(course_id):
    """
    Helper function to get all students enrolled in a specific course_id.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.student_id, s.name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            WHERE e.course_id = %s
            ORDER BY s.student_id ASC;
        """
        cursor.execute(query, (course_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching course students: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def compute_set_operation(course_a, course_b, operation):
    """
    Computes Set Theory operations between students of Course A and Course B:
    - UNION (A ∪ B)
    - INTERSECTION (A ∩ B)
    - DIFFERENCE (A - B)
    - SYMMETRIC DIFFERENCE (A △ B) = (A - B) ∪ (B - A)
    """
    students_a = get_students_by_course(course_a)
    students_b = get_students_by_course(course_b)

    dict_a = {s['student_id']: s['name'] for s in students_a}
    dict_b = {s['student_id']: s['name'] for s in students_b}

    set_a = set(dict_a.keys())
    set_b = set(dict_b.keys())

    if operation == 'union':
        res_ids = sorted(list(set_a.union(set_b)))
        notation = f"{course_a} ∪ {course_b}"
        explanation = f"Students enrolled in {course_a} OR {course_b} (Set Union A ∪ B)"
    elif operation == 'intersection':
        res_ids = sorted(list(set_a.intersection(set_b)))
        notation = f"{course_a} ∩ {course_b}"
        explanation = f"Students enrolled in BOTH {course_a} AND {course_b} (Set Intersection A ∩ B)"
    elif operation == 'difference':
        res_ids = sorted(list(set_a.difference(set_b)))
        notation = f"{course_a} − {course_b}"
        explanation = f"Students enrolled in {course_a} but NOT in {course_b} (Set Difference A − B)"
    elif operation == 'symmetric_difference':
        # Symmetric Difference: A △ B = (A - B) ∪ (B - A)
        diff_a_b = set_a.difference(set_b)
        diff_b_a = set_b.difference(set_a)
        res_ids = sorted(list(diff_a_b.union(diff_b_a)))
        notation = f"{course_a} △ {course_b}"
        explanation = f"Students enrolled in {course_a} OR {course_b} but NOT BOTH (Symmetric Difference A △ B = (A − B) ∪ (B − A))"
    else:
        return [], "", ""

    all_dict = {**dict_a, **dict_b}
    result_list = []
    for s_id in res_ids:
        source_note = ""
        if operation == 'symmetric_difference':
            if s_id in set_a and s_id not in set_b:
                source_note = f"{course_a} Only"
            elif s_id in set_b and s_id not in set_a:
                source_note = f"{course_b} Only"
        result_list.append({
            'student_id': s_id,
            'name': all_dict[s_id],
            'source': source_note
        })
    return result_list, notation, explanation

def get_venn_data(course_a_id, course_b_id):
    """
    Returns student sets and details for Venn Visualizer between Course A and Course B:
    - Left-only (A - B)
    - Intersection (A ∩ B)
    - Right-only (B - A)
    - Union (A ∪ B)
    """
    students_a = get_students_by_course(course_a_id)
    students_b = get_students_by_course(course_b_id)

    dict_a = {s['student_id']: s['name'] for s in students_a}
    dict_b = {s['student_id']: s['name'] for s in students_b}

    set_a = set(dict_a.keys())
    set_b = set(dict_b.keys())

    left_ids = sorted(list(set_a - set_b))
    intersect_ids = sorted(list(set_a & set_b))
    right_ids = sorted(list(set_b - set_a))
    union_ids = sorted(list(set_a | set_b))

    all_dict = {**dict_a, **dict_b}

    def format_list(id_list):
        return [{'student_id': s_id, 'name': all_dict[s_id]} for s_id in id_list]

    course_a_info = {"course_id": course_a_id, "course_name": course_a_id}
    course_b_info = {"course_id": course_b_id, "course_name": course_b_id}

    all_courses = get_all_courses()
    for c in all_courses:
        if c['course_id'] == course_a_id:
            course_a_info = c
        if c['course_id'] == course_b_id:
            course_b_info = c

    return {
        "course_a": course_a_info,
        "course_b": course_b_info,
        "left_only": format_list(left_ids),
        "intersection": format_list(intersect_ids),
        "right_only": format_list(right_ids),
        "union": format_list(union_ids),
        "counts": {
            "left_only": len(left_ids),
            "intersection": len(intersect_ids),
            "right_only": len(right_ids),
            "union": len(union_ids),
            "course_a_total": len(set_a),
            "course_b_total": len(set_b)
        }
    }

def compute_cartesian_product(student_id_param, course_id_param):
    """
    Computes Cartesian Product ordered pairs (student_id, course_id)
    between selected student set and course set.
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        if student_id_param == 'ALL':
            cursor.execute("SELECT student_id, name FROM students ORDER BY student_id ASC;")
            students = cursor.fetchall()
        else:
            cursor.execute("SELECT student_id, name FROM students WHERE student_id = %s;", (student_id_param,))
            students = cursor.fetchall()

        if course_id_param == 'ALL':
            cursor.execute("SELECT course_id, course_name FROM courses ORDER BY course_id ASC;")
            courses = cursor.fetchall()
        else:
            cursor.execute("SELECT course_id, course_name FROM courses WHERE course_id = %s;", (course_id_param,))
            courses = cursor.fetchall()

        cursor.execute("SELECT student_id, course_id FROM enrollments;")
        enrolled_pairs = set((row['student_id'], row['course_id']) for row in cursor.fetchall())

        cartesian_pairs = []
        for s in students:
            for c in courses:
                s_id = s['student_id']
                c_id = c['course_id']
                is_enrolled = (s_id, c_id) in enrolled_pairs
                cartesian_pairs.append({
                    'student_id': s_id,
                    'student_name': s['name'],
                    'course_id': c_id,
                    'course_name': c['course_name'],
                    'pair_str': f"({s_id}, {c_id})",
                    'is_enrolled': is_enrolled
                })

        return cartesian_pairs
    except Error as e:
        print(f"Error computing Cartesian Product: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_relation_analysis():
    """
    Performs Mathematical Relation Analysis on Enrollment Relation R ⊆ S × C:
    1. Complete Relation R as ordered pairs R = {(student_id, course_id), ...}
    2. Domain(R): All students having at least one enrollment
    3. Range(R): All courses having at least one enrolled student
    4. Total number of ordered pairs |R|
    5. Course-wise enrollment report
    6. Student-wise enrollment report
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return {
            "r_pairs": [],
            "r_set_str": "R = ∅",
            "total_pairs": 0,
            "domain": [],
            "domain_count": 0,
            "range": [],
            "range_count": 0,
            "course_summary": [],
            "student_summary": []
        }

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Complete Relation R as ordered pairs
        cursor.execute("SELECT student_id, course_id FROM enrollments ORDER BY student_id ASC, course_id ASC;")
        enrolled_rows = cursor.fetchall()
        r_pairs = [f"({r['student_id']}, {r['course_id']})" for r in enrolled_rows]
        r_set_str = "R = { " + ", ".join(r_pairs) + " }" if r_pairs else "R = ∅"

        # 2. Domain(R): Students with at least 1 enrollment
        cursor.execute("""
            SELECT DISTINCT s.student_id, s.name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            ORDER BY s.student_id ASC;
        """)
        domain_students = cursor.fetchall()

        # 3. Range(R): Courses with at least 1 student enrolled
        cursor.execute("""
            SELECT DISTINCT c.course_id, c.course_name
            FROM courses c
            JOIN enrollments e ON c.course_id = e.course_id
            ORDER BY c.course_id ASC;
        """)
        range_courses = cursor.fetchall()

        # 4. Course-wise enrollment report
        cursor.execute("""
            SELECT 
                c.course_id, 
                c.course_name, 
                COUNT(e.student_id) AS student_count
            FROM courses c
            LEFT JOIN enrollments e ON c.course_id = e.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id ASC;
        """)
        course_summary = cursor.fetchall()

        # 5. Student-wise enrollment report
        cursor.execute("""
            SELECT 
                s.student_id, 
                s.name AS student_name, 
                COUNT(e.course_id) AS course_count
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            GROUP BY s.student_id, s.name
            ORDER BY s.student_id ASC;
        """)
        student_summary = cursor.fetchall()

        return {
            "r_pairs": r_pairs,
            "r_set_str": r_set_str,
            "total_pairs": len(r_pairs),
            "domain": domain_students,
            "domain_count": len(domain_students),
            "range": range_courses,
            "range_count": len(range_courses),
            "course_summary": course_summary,
            "student_summary": student_summary
        }
    except Error as e:
        print(f"Error computing relation analysis: {e}")
        return {
            "r_pairs": [],
            "r_set_str": "R = ∅",
            "total_pairs": 0,
            "domain": [],
            "domain_count": 0,
            "range": [],
            "range_count": 0,
            "course_summary": [],
            "student_summary": []
        }
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def compute_symmetric_difference(course_a_id, course_b_id):
    """
    Computes Symmetric Difference A △ B = (A - B) ∪ (B - A) between Course A and Course B:
    - Only in Course A (A - B)
    - Only in Course B (B - A)
    - Students enrolled in exactly ONE course (A △ B)
    - Excluded students enrolled in both courses (A ∩ B)
    """
    students_a = get_students_by_course(course_a_id)
    students_b = get_students_by_course(course_b_id)

    dict_a = {s['student_id']: s['name'] for s in students_a}
    dict_b = {s['student_id']: s['name'] for s in students_b}

    set_a = set(dict_a.keys())
    set_b = set(dict_b.keys())

    only_a_ids = sorted(list(set_a - set_b))
    only_b_ids = sorted(list(set_b - set_a))
    intersect_ids = sorted(list(set_a & set_b))
    sym_diff_ids = sorted(list((set_a - set_b) | (set_b - set_a)))

    all_dict = {**dict_a, **dict_b}

    all_courses = get_all_courses()
    course_a_name = course_a_id
    course_b_name = course_b_id
    for c in all_courses:
        if c['course_id'] == course_a_id:
            course_a_name = c['course_name']
        if c['course_id'] == course_b_id:
            course_b_name = c['course_name']

    return {
        "course_a": {"course_id": course_a_id, "course_name": course_a_name},
        "course_b": {"course_id": course_b_id, "course_name": course_b_name},
        "only_a": [{'student_id': s_id, 'name': all_dict[s_id], 'enrolled_in': f"{course_a_name} ({course_a_id})"} for s_id in only_a_ids],
        "only_b": [{'student_id': s_id, 'name': all_dict[s_id], 'enrolled_in': f"{course_b_name} ({course_b_id})"} for s_id in only_b_ids],
        "both_excluded": [{'student_id': s_id, 'name': all_dict[s_id], 'enrolled_in': 'Both Courses'} for s_id in intersect_ids],
        "symmetric_difference": [
            {
                'student_id': s_id,
                'name': all_dict[s_id],
                'enrolled_in': f"{course_a_name} ({course_a_id}) Only" if s_id in set_a else f"{course_b_name} ({course_b_id}) Only",
                'membership': f"s ∈ ({course_a_id} − {course_b_id})" if s_id in set_a else f"s ∈ ({course_b_id} − {course_a_id})"
            }
            for s_id in sym_diff_ids
        ],
        "counts": {
            "course_a_total": len(set_a),
            "course_b_total": len(set_b),
            "only_a": len(only_a_ids),
            "only_b": len(only_b_ids),
            "both_excluded": len(intersect_ids),
            "total_symmetric_diff": len(sym_diff_ids)
        },
        "notation": f"{course_a_id} △ {course_b_id}",
        "formula": f"({course_a_id} − {course_b_id}) ∪ ({course_b_id} − {course_a_id})"
    }

def get_relation_matrix():
    """
    Computes the Binary Relation Matrix M_R for Enrollment Relation R ⊆ S × C:
    Rows: All Students (Set S)
    Columns: All Courses (Set C)
    m_ij = 1 if (s_i, c_j) ∈ R (student is enrolled in course)
    m_ij = 0 if (s_i, c_j) ∉ R (student is not enrolled)
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return {
            "students": [],
            "courses": [],
            "matrix": [],
            "total_entries": 0,
            "total_ones": 0,
            "total_zeros": 0,
            "course_totals": {}
        }

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, name FROM students ORDER BY student_id ASC;")
        students = cursor.fetchall()

        cursor.execute("SELECT course_id, course_name, credits FROM courses ORDER BY course_id ASC;")
        courses = cursor.fetchall()

        cursor.execute("SELECT student_id, course_id FROM enrollments;")
        enrolled_rows = cursor.fetchall()
        enrolled_set = set((r['student_id'], r['course_id']) for r in enrolled_rows)

        matrix = []
        course_totals = {c['course_id']: 0 for c in courses}
        total_ones = 0

        for s in students:
            s_id = s['student_id']
            row_cells = []
            row_enrolled_count = 0

            for c in courses:
                c_id = c['course_id']
                is_enrolled = (s_id, c_id) in enrolled_set
                val = 1 if is_enrolled else 0
                if is_enrolled:
                    row_enrolled_count += 1
                    course_totals[c_id] += 1
                    total_ones += 1

                row_cells.append({
                    "course_id": c_id,
                    "course_name": c['course_name'],
                    "value": val,
                    "is_enrolled": is_enrolled
                })

            matrix.append({
                "student_id": s_id,
                "student_name": s['name'],
                "cells": row_cells,
                "row_total": row_enrolled_count
            })

        total_entries = len(students) * len(courses)
        total_zeros = total_entries - total_ones

        return {
            "students": students,
            "courses": courses,
            "matrix": matrix,
            "total_entries": total_entries,
            "total_ones": total_ones,
            "total_zeros": total_zeros,
            "course_totals": course_totals
        }
    except Error as e:
        print(f"Error computing relation matrix: {e}")
        return {
            "students": [],
            "courses": [],
            "matrix": [],
            "total_entries": 0,
            "total_ones": 0,
            "total_zeros": 0,
            "course_totals": {}
        }
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_domain_and_range():
    """
    Computes Domain(R) and Range(R) dynamically from the enrollments table in MySQL:
    Domain(R) = { s ∈ S | ∃ c ∈ C such that (s, c) ∈ R } (all enrolled students)
    Range(R)  = { c ∈ C | ∃ s ∈ S such that (s, c) ∈ R } (all courses with enrolled students)
    """
    conn = get_db_connection(include_db=True)
    if not conn:
        return {
            "domain": [],
            "domain_count": 0,
            "range": [],
            "range_count": 0,
            "total_students": 0,
            "total_courses": 0
        }

    try:
        cursor = conn.cursor(dictionary=True)

        # Domain(R): Students enrolled in at least one course
        cursor.execute("""
            SELECT 
                s.student_id, 
                s.name, 
                COUNT(e.course_id) AS enrolled_courses_count,
                GROUP_CONCAT(c.course_name ORDER BY c.course_id SEPARATOR ', ') AS enrolled_courses_list
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN courses c ON e.course_id = c.course_id
            GROUP BY s.student_id, s.name
            ORDER BY s.student_id ASC;
        """)
        domain_students = cursor.fetchall()

        # Range(R): Courses in which at least one student is enrolled
        cursor.execute("""
            SELECT 
                c.course_id, 
                c.course_name, 
                c.credits,
                COUNT(e.student_id) AS enrolled_students_count
            FROM courses c
            JOIN enrollments e ON c.course_id = e.course_id
            GROUP BY c.course_id, c.course_name, c.credits
            ORDER BY c.course_id ASC;
        """)
        range_courses = cursor.fetchall()

        # Total counts in universe S and C
        cursor.execute("SELECT COUNT(*) AS total_s FROM students;")
        total_s = cursor.fetchone()['total_s']
        cursor.execute("SELECT COUNT(*) AS total_c FROM courses;")
        total_c = cursor.fetchone()['total_c']

        return {
            "domain": domain_students,
            "domain_count": len(domain_students),
            "range": range_courses,
            "range_count": len(range_courses),
            "total_students": total_s,
            "total_courses": total_c
        }
    except Error as e:
        print(f"Error computing domain and range: {e}")
        return {
            "domain": [],
            "domain_count": 0,
            "range": [],
            "range_count": 0,
            "total_students": 0,
            "total_courses": 0
        }
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_db()
