# motorkhana

## Web application structure

### Public Page

#### 1. List of courses

- route：/listcourses
- function：listcourses()
- method：GET
- input：None
- data: query all courses from course table
- output：course_list
- template：courselist.html

#### 2. Driver's run details

- route：driver_detail
- function：driver_detail()
- method：GET,POST
- input：driver id or none
- data: query all driver from driver table;If the request method is POST, update the run data of the input
  driver;else,query the run of the first driver;
- output:heading,driver_list,result_list(the run overall results of the driver)
- template：driverdetail.html

#### 3.List of drivers

- route：/listdrivers
- function：listdrivers()
- method：GET
- input：None
- data: query all drivers from driver table
- output：driver_list
- template：driverlist.html

#### 4.Overall results

- route：/total_grade
- function：total_grade()
- method：GET
- input：None
- data: query all drivers from driver table; for each driver, query all runs from run table; for each run, calculate the
  total grade and sort
- output：result_list,include driver name, course name, run time, run total
- template：total_grade.html

#### 5. bar graph

- route：/graph
- function：showgraph()
- method：GET
- input：None
- data: query all drivers from driver table; for each driver, query all runs from run table; for each run, calculate the
  total grade and sort, then get the top 5 drivers
- output：bestDriverList,resultsList
- template：top5graph.html

### Admin Page

#### 1.Junior driver list

- route：/junior_driver_list
- function：junior_driver_list()
- method：GET
- input：None or keyword
- data: query all drivers that age<=18 and name contain keyword from driver table
- output：driver_list
- template：junior_driver_list.html

#### 2.Driver search

- route：/admin_driver_list()
- function：admin_driver_list()
- method：GET
- input：None or keyword
- data: query all drivers that name contain keyword from driver table
- output：driver_list
- template：admin_driver_list.html

#### 3. Edit runs

- route：/edit_runs
- function：edit_runs()
- method：GET,POST
- input：None or driver id or course_id
- data: query all drivers from driver table; query all courses from course table; query all runs from run table; if the
  request method is POST, update the run data of the input driver;else,query the run of the first driver;
- output：driver_list,course_list,run_list
- template：edit_runs.html

#### 4. Add driver

- route：/add_driver
- function：add_driver()
- method：GET,POST
- input：None or the attribute of the driver include first_name,surname,car,date_of_birth,caregiver
- data:query all drivers age > 18 from driver table as the caregiver_list; query all cars as car_list;if the request
  method is POST, insert the driver data of the input driver
- output：caregiver_list,car_list
- template：add_driver.html

#### 5. Add runs

- route：/add_runs
- function：add_run()
- method：POST
- input driver_id, course_id, run_num,seconds,cones,wd
- data: insert the run data of the input driver
- output：None
- template：redirect '/edit_runs'

## Assumptions and design decisions

- admin and driver use different base templates.

Initially, we intended to extend the same base template, but we found it a bit confusing. Therefore, we separated the
base.html for admin and driver.

- The "search drivers" functionality uses the GET method rather than POST. The GET method is more convenient, easier to
  use, and this query does not involve sensitive information. Therefore, we chose the GET method
- The "edit_runs" route utilizes both GET and POST methods. The GET method returns the default runs list for the first
  driver. The POST method receives runs information submitted from the front-end and inserts it into the database. This
  approach reduces the number of routes and makes management easier.

## Database questions

- CREATE TABLE IF NOT EXISTS car
  (
  car_num INT PRIMARY KEY NOT NULL,
  model VARCHAR(20) NOT NULL,
  drive_class VARCHAR(3) NOT NULL
  );

- FOREIGN KEY (car) REFERENCES car(car_num)
- INSERT INTO car VALUES
  (11,'Mini','FWD'),
  (17,'GR Yaris','4WD'),
- ALTER TABLE car
  MODIFY COLUMN drive_class VARCHAR(3) DEFAULT 'RWD';
- For reasons of data security and integrity, both drivers and administrators must access different routes.

If a driver were allowed to access administrator routes, they would gain the ability to modify their own results, which
is unacceptable.

Conversely, if an administrator were to access driver routes, they would lose their ability to manage driver results,
which is also unreasonable.

