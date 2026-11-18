from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import (
    init_db, 
    get_db_connection, 
    get_all_students, 
    get_all_courses, 
    enroll_student_in_courses, 
    get_all_enrollments,
    compute_set_operation,
    compute_cartesian_product,
    get_relation_analysis,
    get_venn_data,
    get_relation_matrix,
    get_domain_and_range,
    compute_symmetric_difference
)

app = Flask(__name__)
app.secret_key = 'discrete_mathematics_enrollment_key'

# Initialize database schema, 48 students, and 5 courses on startup
try:
    init_db()
except Exception as e:
    print(f"Database initialization warning: {e}")

@app.route('/', methods=['GET'])
def index():
    """
    Renders the main Discrete Mathematics Student Course Enrollment page.
    Passes Students Set S, Courses Set C, Relation R, Relation Analysis, Venn Data,
    Relation Matrix M_R, and Domain & Range to the template.
    """
    students = get_all_students()
    courses = get_all_courses()
    enrollments = get_all_enrollments()
    analysis = get_relation_analysis()
    initial_venn = get_venn_data('C01', 'C02')
    relation_matrix = get_relation_matrix()
    domain_range = get_domain_and_range()
    
    return render_template(
        'index.html',
        students=students,
        courses=courses,
        enrollments=enrollments,
        analysis=analysis,
        initial_venn=initial_venn,
        relation_matrix=relation_matrix,
        domain_range=domain_range,
        set_result=None,
        cartesian_result=None
    )

@app.route('/enroll', methods=['POST'])
def enroll():
    """
    Route for processing student course enrollment.
    Adds ordered pairs (s, c) to relation R ⊆ S × C.
    """
    student_id = request.form.get('student_id')
    course_ids = request.form.getlist('course_ids')

    if not student_id:
        flash("Please select a student from the dropdown.", "error")
        return redirect(url_for('index'))

    if not course_ids:
        flash("Please select at least one course checkbox to enroll.", "error")
        return redirect(url_for('index'))

    count, message = enroll_student_in_courses(student_id, course_ids)

    if count > 0:
        flash(f"Successfully added {count} ordered pair(s) (s, c) to Relation R ⊆ S × C!", "success")
    else:
        flash("Student is already enrolled in the selected course(s). No duplicate pair added.", "info")

    return redirect(url_for('index'))

@app.route('/set-operation', methods=['POST'])
def set_operation():
    """
    Computes Union (A ∪ B), Intersection (A ∩ B), Difference (A - B),
    or Symmetric Difference (A △ B) between Course A and Course B.
    """
    course_a = request.form.get('course_a')
    course_b = request.form.get('course_b')
    operation = request.form.get('operation')

    students = get_all_students()
    courses = get_all_courses()
    enrollments = get_all_enrollments()
    analysis = get_relation_analysis()
    initial_venn = get_venn_data('C01', 'C02')
    relation_matrix = get_relation_matrix()
    domain_range = get_domain_and_range()

    if not course_a or not course_b or not operation:
        flash("Please select Course A, Course B, and a Set Operation.", "error")
        return redirect(url_for('index'))

    if course_a == course_b:
        flash("Please select two different courses. Course A and Course B cannot be the same.", "error")
        return redirect(url_for('index'))

    result_list, notation, explanation = compute_set_operation(course_a, course_b, operation)

    return render_template(
        'index.html',
        students=students,
        courses=courses,
        enrollments=enrollments,
        analysis=analysis,
        initial_venn=initial_venn,
        relation_matrix=relation_matrix,
        domain_range=domain_range,
        set_result=result_list,
        set_notation=notation,
        set_explanation=explanation,
        selected_course_a=course_a,
        selected_course_b=course_b,
        selected_op=operation,
        cartesian_result=None
    )

@app.route('/cartesian-product', methods=['POST'])
def cartesian_product():
    """
    Computes Cartesian Product ordered pairs (student_id, course_id) for S' × C'.
    """
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')

    students = get_all_students()
    courses = get_all_courses()
    enrollments = get_all_enrollments()
    analysis = get_relation_analysis()
    initial_venn = get_venn_data('C01', 'C02')
    relation_matrix = get_relation_matrix()
    domain_range = get_domain_and_range()

    if not student_id or not course_id:
        flash("Please select a Student and a Course for Cartesian Product.", "error")
        return redirect(url_for('index'))

    cartesian_list = compute_cartesian_product(student_id, course_id)

    return render_template(
        'index.html',
        students=students,
        courses=courses,
        enrollments=enrollments,
        analysis=analysis,
        initial_venn=initial_venn,
        relation_matrix=relation_matrix,
        domain_range=domain_range,
        set_result=None,
        cartesian_result=cartesian_list,
        selected_cartesian_student=student_id,
        selected_cartesian_course=course_id
    )

@app.route('/api/venn-data')
def venn_data_api():
    """
    API endpoint returning Venn Diagram data for two selected courses.
    Query parameters: course_a, course_b
    """
    course_a = request.args.get('course_a', 'C01')
    course_b = request.args.get('course_b', 'C02')
    data = get_venn_data(course_a, course_b)
    return jsonify(data)

@app.route('/api/relation-analysis')
def get_relation_analysis_api():
    """
    API endpoint returning relation analysis metrics (Domain, Range, R pairs, summaries).
    """
    analysis = get_relation_analysis()
    return jsonify(analysis)

@app.route('/api/status')
def status():
    """
    API endpoint returning discrete math metadata, connectivity, and set sizes.
    """
    students = get_all_students()
    courses = get_all_courses()
    enrollments = get_all_enrollments()
    
    set_metadata = {
        "status": "Online",
        "system_name": "Student Course Enrollment System Using Set Theory and Relations",
        "semester": "3rd Semester CSE",
        "subject": "Discrete Mathematics",
        "definitions": {
            "set_S": "Set of 48 Students S = {1260, 1262, ..., 1549}",
            "set_C": "Set of 5 Courses C = {C01, C02, C03, C04, C05}",
            "relation_R": "Enrollment Relation R ⊆ S × C",
            "cartesian_product_cardinality": f"|S × C| = {len(students)} × {len(courses)} = {len(students) * len(courses)} ordered pairs"
        },
        "set_S_count": len(students),
        "set_C_count": len(courses),
        "relation_R_count": len(enrollments),
        "database_connected": False
    }
    
    conn = get_db_connection()
    if conn:
        set_metadata["database_connected"] = True
        conn.close()

    return jsonify(set_metadata)

@app.route('/api/relation-matrix')
def relation_matrix_api():
    """
    API endpoint returning the complete Binary Relation Matrix M_R data.
    """
    matrix_data = get_relation_matrix()
    return jsonify(matrix_data)

@app.route('/api/domain-range')
def domain_range_api():
    """
    API endpoint returning Domain(R) and Range(R) sets and counts.
    """
    dr_data = get_domain_and_range()
    return jsonify(dr_data)

@app.route('/api/symmetric-difference')
def symmetric_difference_api():
    """
    API endpoint returning Symmetric Difference A △ B = (A - B) ∪ (B - A).
    Query parameters: course_a, course_b
    """
    course_a = request.args.get('course_a', 'C01')
    course_b = request.args.get('course_b', 'C02')
    
    if not course_a or not course_b:
        return jsonify({"error": "Please provide both course_a and course_b parameters."}), 400

    if course_a == course_b:
        return jsonify({"error": "Course A and Course B must be different courses. Cannot compute symmetric difference on identical courses."}), 400

    data = compute_symmetric_difference(course_a, course_b)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
