from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
import sys
import psycopg2

# Database connection
db_connection = psycopg2.connect(
    dbname='apiDB',
    user='postgres',
    password='0586',
    host='localhost',
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# spcall = stored procedure call
def spcall(query, param, commit=False):
    try:
        cursor = db_connection.cursor()
        cursor.callproc(query, param)
        res = cursor.fetchall()
        if commit:
            db_connection.commit()
        return res
    except:
        res = [("Error, " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),)]
    return res


# Print All Courses
@app.route('/')
def home():
    try:
        courses = spcall('get_courses', param=None)[0][0]  # Access the inner list of dictionaries
        print(courses)
        return render_template('home.html', courses=courses)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('home'))
    
# Delete Course
@app.route('/courses/<course_id>/delete', methods=['POST'])
def delete_course(course_id):
    try:
        res = spcall('delete_course_by_id', (course_id,), commit=True)
        flash("Course Deleted Successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('home'))

# Add Course
@app.route('/course', methods=['POST'])
def create_course():
    data = request.form
    course = data.get('course')
    try:
        res = spcall('insert_course', (course,), commit=True)
        print(res)
        flash("Course Created Successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('home'))


#CURRENTLY WORKING ON
    
# Get Specific Course
@app.route('/courses/<course_id>', methods=['GET'])
def get_specific_course(course_id):
    try:
        res = spcall('get_course_by_id', (course_id,))
        if res:
            course_details = res[0][0]
            return render_template('all_courses.html', course=course_details)
        else:
            flash(f"No course found with ID {course_id}", "warning")
            return redirect(url_for('get_course'))
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('home'))


#Update Course with Course ID
@app.route('/course/<course_id>', methods=['PUT'])
def update_course(course_id):
    data = request.get_json()
    course_id = data.get('course_id')
    course_name = data.get ('course_name')
    # print(course, course_id)
    try:
        # data = request.get_json()
        # course = data.get('course')
        # print(course, course_id)
        if course_id:
            res = spcall('update_course_by_id', (course_id, course_name), commit=True)
            print (res)
            return jsonify({"status": "ok", 
                'message': 'course updated successfully'})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)


