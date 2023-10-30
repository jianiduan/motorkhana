from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
                                         password=connect.dbpass, host=connect.dbhost, \
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    return redirect(url_for("listdrivers"))


@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    connection.execute("SELECT * FROM driver;")
    driverList = connection.fetchall()
    return render_template("driverlist.html", driver_list=driverList)


@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list=courseList)


@app.route("/graph")
def showgraph():
    top5_dict = {}
    connection = getCursor()
    connection.execute("SELECT * FROM driver;")
    driverList = connection.fetchall()
    for driver in driverList:
        dr_id = driver[0]
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (dr_id,))
        runList = connection.fetchall()

        result_dict = {}
        for run in runList:
            crs_id = run[1]
            result_dict[crs_id] = []

        for run in runList:
            crs_id = run[1]
            result_list = result_dict[crs_id]
            result_list.append([run[3], run[4], run[5]])
            result_dict[crs_id] = result_list

        result_list = []
        for key, value in result_dict.items():
            for i in range(0, len(value)):
                if value[i][0]:
                    if value[i][1]:
                        end_time = value[i][0] + 5 * value[i][1] + 10 * value[i][2]
                    else:
                        end_time = value[i][0] + 10 * value[i][2]
                else:
                    end_time = None
                value[i].append(end_time)
            if value[0][-1] and value[1][-1]:
                course_end = min(value[0][-1], value[1][-1])
            elif value[0][-1]:
                course_end = value[0][-1]
            elif value[1][-1]:
                course_end = value[1][-1]
            else:
                course_end = 'DNF'
                break
            result_list.append({key: course_end})
        if len(result_list) == 6:
            values = [value for item in result_list for value in item.values()]
            overall_time = round(sum(values), 2)
            top5_dict[driver[0]] = overall_time
        else:
            pass

    top5_list = sorted(top5_dict.items(), key=lambda x: x[1])[0:5]
    top5_name_list = []
    for item in top5_list:
        connection.execute("SELECT * FROM driver WHERE driver_id = %s;", (item[0],))
        driver = connection.fetchone()
        top5_name_list.append(driver[1] + " " + driver[2])
    max_time = max(top5_dict.values())
    range_list = [200, max_time]
    return render_template("top5graph.html", bestDriverList=top5_name_list, resultsList=top5_list,
                           range_list=range_list)


@app.route("/total_grade")
def total_grade():
    grade_dict = {}
    connection = getCursor()
    connection.execute("SELECT * FROM driver;")
    driverList = connection.fetchall()
    course_grade_list = []
    for driver in driverList:
        dr_id = driver[0]
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (dr_id,))
        runList = connection.fetchall()

        result_dict = {}
        for run in runList:
            crs_id = run[1]
            result_dict[crs_id] = []

        for run in runList:
            crs_id = run[1]

            result_list = result_dict[crs_id]

            result_list.append([run[3], run[4], run[5]])

            result_dict[crs_id] = result_list

        result_list = []
        for key, value in result_dict.items():
            for i in range(0, len(value)):
                if value[i][0]:
                    if value[i][1]:
                        end_time = value[i][0] + 5 * value[i][1] + 10 * value[i][2]
                    else:
                        end_time = value[i][0] + 10 * value[i][2]
                else:
                    end_time = None
                value[i].append(end_time)

            if value[0][-1] and value[1][-1]:
                course_end = min(value[0][-1], value[1][-1])
            elif value[0][-1]:
                course_end = value[0][-1]
            elif value[1][-1]:
                course_end = value[1][-1]
            else:
                course_end = 'DNF'

            result_list.append({key: course_end})
        grade_list = []
        for item in result_list:
            grade_list.append(list(item.values())[0])

        course_grade_list.append(grade_list)

        try:
            values = [value for item in result_list for value in item.values()]
            overall_time = round(sum(values), 2)
            grade_dict[driver[0]] = overall_time
        except:
            grade_dict[driver[0]] = 100000

    grade_list = sorted(grade_dict.items(), key=lambda x: x[1])
    grade_name_list = []
    car_name_list = []
    for item in grade_list:
        connection.execute("SELECT * FROM driver WHERE driver_id = %s;", (item[0],))
        driver = connection.fetchone()
        grade_name_list.append(driver[1] + " " + driver[2])

        car_id = driver[-1]
        connection.execute("SELECT * FROM car WHERE car_num = %s;", (car_id,))
        car = connection.fetchone()
        car_name_list.append(car[1])

    id_list, scores = zip(*grade_list)
    scores = list(scores)
    scores = [score if score != 100000 else "dnf" for score in scores]
    course_name_list = []
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    for course in courseList:
        course_name_list.append(course[1])
    result_list = list(zip(id_list, grade_name_list, car_name_list, course_grade_list, scores))

    return render_template("total_grade.html", result_list=result_list, course_name_list=course_name_list)


@app.route("/driver_detail", methods=["GET", "POST"])
def driver_detail():
    if request.method == "POST":
        driver_id = request.form["driver_id"]
        connection = getCursor()

        connection.execute("SELECT * FROM driver;")
        driverList = connection.fetchall()

        connection.execute("SELECT * FROM driver WHERE driver_id = %s;", (driver_id,))
        driver = connection.fetchone()

        car_id = driver[-1]
        connection.execute("SELECT * FROM car WHERE car_num = %s;", (car_id,))
        car = connection.fetchone()

        title = str(driver[0]) + " " + driver[1] + " " + driver[2] + " " + car[1] + " " + car[2]

        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (driver_id,))
        runList = connection.fetchall()

        result_dict = {}
        for run in runList:
            crs_id = run[1]
            connection.execute("SELECT * FROM course WHERE course_id = %s;", (crs_id,))
            course = connection.fetchone()
            result_dict[course[1]] = []

        for run in runList:
            crs_id = run[1]
            connection.execute("SELECT * FROM course WHERE course_id = %s;", (crs_id,))
            course = connection.fetchone()
            if course[1] not in result_dict:
                result_dict[course[1]] = []

            result_list = result_dict[course[1]]

            result_list.append([run[3], run[4], run[5]])

            result_dict[course[1]] = result_list

        result_list = []
        for key, value in result_dict.items():
            for i in range(0, len(value)):
                if value[i][0]:
                    if value[i][1]:
                        end_time = value[i][0] + 5 * value[i][1] + 10 * value[i][2]
                    else:
                        end_time = value[i][0] + 10 * value[i][2]
                else:
                    end_time = None
                value[i].append(end_time)
            if value[0][-1] and value[1][-1]:
                course_end = min(value[0][-1], value[1][-1])
            elif value[0][-1]:
                course_end = value[0][-1]
            elif value[1][-1]:
                course_end = value[1][-1]
            else:
                course_end = 'DNF'

            result_list.append([key, *value[0], *value[1], course_end])
        return render_template("driverdetail.html", driver_list=driverList, title=title, result_list=result_list,
                               driver=driver)

    else:

        connection = getCursor()
        connection.execute("SELECT * FROM driver;")
        driverList = connection.fetchall()

        car_id = driverList[0][-1]
        connection.execute("SELECT * FROM car WHERE car_num = %s;", (car_id,))
        car = connection.fetchone()
        title = str(driverList[0][0]) + " " + driverList[0][1] + " " + driverList[0][2] + " " + car[1] + " " + car[2]
        dr_id = driverList[0][0]
        connection.execute("SELECT * FROM run WHERE dr_id = %s;", (dr_id,))
        runList = connection.fetchall()

        result_dict = {}
        for run in runList:
            crs_id = run[1]
            connection.execute("SELECT * FROM course WHERE course_id = %s;", (crs_id,))
            course = connection.fetchone()
            result_dict[course[1]] = []

        for run in runList:
            crs_id = run[1]
            connection.execute("SELECT * FROM course WHERE course_id = %s;", (crs_id,))
            course = connection.fetchone()
            if course[1] not in result_dict:
                result_dict[course[1]] = []

            result_list = result_dict[course[1]]

            result_list.append([run[3], run[4], run[5]])

            result_dict[course[1]] = result_list

        result_list = []
        for key, value in result_dict.items():
            for i in range(0, len(value)):
                if value[i][0]:
                    if value[i][1]:
                        end_time = value[i][0] + 5 * value[i][1] + 10 * value[i][2]
                    else:
                        end_time = value[i][0] + 10 * value[i][2]
                else:
                    end_time = None
                value[i].append(end_time)
            if value[0][-1] and value[1][-1]:
                course_end = min(value[0][-1], value[1][-1])
            elif value[0][-1]:
                course_end = value[0][-1]
            elif value[1][-1]:
                course_end = value[1][-1]
            else:
                course_end = 'DNF'
            result_list.append([key, *value[0], *value[1], course_end])
        return render_template("driverdetail.html", driver_list=driverList, title=title, result_list=result_list,
                               driver=driverList[0])


@app.route("/junior_driver_list", methods=["GET", "POST"])
def junior_driver_list():
    keyword = request.args.get("keyword", "")
    print(keyword)
    if not keyword:
        sql = """SELECT
         d.driver_id,
         d.first_name,
         d.surname,
         d.date_of_birth,
         d.age,
         d.car,
         CONCAT_WS(' ', c.first_name, c.surname) AS caregiver_name
         FROM driver AS d
         LEFT JOIN driver AS c ON d.caregiver = c.driver_id
         WHERE d.age IS NOT NULL
         """
        connection = getCursor()
        connection.execute(sql)
        driverList = connection.fetchall()

        return render_template("admin/junior_driver.html", driver_list=driverList)
    else:
        connection = getCursor()
        connection.execute("SELECT * FROM driver WHERE CONCAT(first_name, surname) LIKE %s;",
                           ("%" + keyword + "%",))
        driverList = connection.fetchall()
        return render_template("admin/junior_driver.html", driver_list=driverList)


@app.route("/admin_driver_list", methods=["GET", "POST"])
def admin_driver_list():
    keyword = request.args.get("keyword", "")
    if not keyword:
        sql = """SELECT
        d.driver_id,
        d.first_name,
        d.surname,
        d.date_of_birth,
        d.age,
        d.car,
        CONCAT_WS(' ', c.first_name, c.surname) AS caregiver_name
        FROM driver AS d
        LEFT JOIN driver AS c ON d.caregiver = c.driver_id
        
        ORDER BY d.age DESC, d.surname, d.first_name;
        """
        connection = getCursor()
        connection.execute(sql)
        driverList = connection.fetchall()

        return render_template("admin/admin_driver_list.html", driver_list=driverList, keyword=keyword)
    else:
        connection = getCursor()
        connection.execute("SELECT * FROM driver WHERE CONCAT(first_name, surname) LIKE %s;",
                           ("%" + keyword + "%",))
        driverList = connection.fetchall()
        return render_template("admin/admin_driver_list.html", driver_list=driverList, keyword=keyword)


@app.route("/add_driver", methods=["GET", "POST"])
def add_driver():
    if request.method == "POST":
        first_name = request.form["first_name"]
        surname = request.form["surname"]
        car = request.form["car"]

        date_of_birth = request.form["date_of_birth"]
        caregiver = request.form["caregiver"]

        if date_of_birth:

            age = datetime.now().year - int(date_of_birth[0:4])
        else:
            age = None
            date_of_birth = None
        if not caregiver:
            caregiver = None

        connection = getCursor()
        connection.execute("INSERT INTO driver (first_name, surname, date_of_birth, age, car, caregiver) VALUES (%s, "
                           "%s, %s, %s, %s, %s);", (first_name, surname, date_of_birth, age, car, caregiver,))
        return redirect(url_for("admin_driver_list"))
    else:
        connection = getCursor()
        connection.execute("SELECT * FROM driver WHERE age is null;")
        caregivers = connection.fetchall()

        # query all cars
        connection.execute("SELECT * FROM car;")
        car_list = connection.fetchall()

        return render_template("admin/add_driver.html", car_list=car_list, caregiver_list=caregivers)


@app.route("/edit_runs", methods=["GET", "POST"])
def edit_runs():
    if request.method == 'POST':
        driver_id = request.form.get('driver_id')
        course_id = request.form.get('course_id')
        run_number = request.form.get('run_number')
        seconds = request.form.get('seconds')
        cones = request.form.get('cones')
        wd = request.form.get('wd')
        if not str(cones).isdigit():
            cones = None
        connection = getCursor()

        # change the run
        connection.execute("UPDATE run SET seconds = %s, cones = %s, wd = %s WHERE dr_id = %s AND crs_id = %s AND "
                           "run_num = %s;", (seconds, cones, wd, driver_id, course_id, run_number,))

        return redirect('/edit_runs')
    else:
        connection = getCursor()

        # query all drivers
        connection.execute("SELECT * FROM driver;")
        driver_list = connection.fetchall()
        # query all courses
        connection.execute("SELECT * FROM course;")
        course_list = connection.fetchall()

        driver_id = request.args.get("driver_id", "")
        course_id = request.args.get("course_id", "")

        course = None
        driver = None
        if driver_id:
            connection.execute("SELECT * FROM run WHERE dr_id = %s;", (driver_id,))
            run_list = connection.fetchall()
            connection.execute("SELECT * FROM driver where driver_id = %s;", (driver_id,))
            driver = connection.fetchone()

        elif course_id:
            connection.execute("SELECT * FROM run WHERE crs_id = %s;", (course_id,))
            run_list = connection.fetchall()
            connection.execute("SELECT * FROM course where course_id = %s;", (course_id,))
            course = connection.fetchone()
        else:
            driver_id = driver_list[0][0]
            connection.execute("SELECT * FROM run WHERE dr_id = %s;", (driver_id,))
            run_list = connection.fetchall()

            driver = driver_list[0]

        return render_template("admin/edit_runs.html", driver_list=driver_list, course_list=course_list,
                               run_list=run_list, driver=driver, course=course)


@app.route("/add_runs", methods=["GET", "POST"])
def add_run():
    if request.method == 'POST':
        driver_id = request.form.get('driver_id')  # Get the Driver ID parameter
        course_id = request.form.get('courseId')  # Get the Course ID parameter
        run_num = request.form.get('runNum')  # Get the Run Number parameter
        seconds = request.form.get('seconds')  # Get the Seconds parameter
        cones = request.form.get('cones')  # Get the Cones parameter
        wd = request.form.get('wd')
        # If Cones parameter is not a number, set it to None
        if not str(cones).isdigit():
            cones = None
        # Connect to the database and check if a row with dr_id, crs_id, and run_num exists
        connection = getCursor()
        connection.execute("SELECT * FROM run WHERE dr_id = %s AND crs_id = %s AND run_num = %s;",
                           (driver_id, course_id, run_num,))
        run = connection.fetchone()
        # If it exists, update seconds, cones, and wd
        if run:
            connection.execute("UPDATE run SET seconds = %s, cones = %s, wd = %s WHERE dr_id = %s AND crs_id = %s AND "
                               "run_num = %s;", (seconds, cones, wd, driver_id, course_id, run_num,))
        # If it doesn't exist, insert a new row
        else:
            connection.execute("INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd) VALUES (%s, %s, %s, %s, "
                               "%s, %s);", (driver_id, course_id, run_num, seconds, cones, wd,))
        return redirect('/edit_runs')
