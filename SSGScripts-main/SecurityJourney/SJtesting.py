"""Testing of Security Journey API and SSG EDU Metrics process"""

import json
import sys
import os
import requests
import pymysql.cursors

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import sjcttoken, sjtoken, SSGDBHost, SSGDBUser, SSGDBPassword, SSGDB

#DB info
mydb = pymysql.connect(
    host=SSGDBHost,
    user=SSGDBUser,
    password=SSGDBPassword,
    database=SSGDB
)
mycursor = mydb.cursor()

#headers
ctype = 'application/json'
headers = {'Content-Type': ctype, 'ApiKey': sjtoken}
ctheaders = {'Content-Type': ctype, 'ApiKey': sjcttoken}
pbiheaders = {'Content-Type': ctype}

#init arrays
sjenrollments = []
sjusers = []

#urls
enurl = 'https://massmutual.securityjourney.com/api/v2/enrollments?limit=1200000'
usersurl = 'https://massmutual.securityjourney.com/api/v2/users?limit=1200000'
ctenurl = 'https://massmutualpartners.securityjourney.com/api/v2/enrollments?limit=1200000'
ctusersurl = 'https://massmutualpartners.securityjourney.com/api/v2/users?limit=1200000'
pbiurl = 'https://api.powerbi.com/beta/649fc29a-ece3-4a3b-a3c1-680a2f035a6e/datasets/4e101663-5c7e-4c10-89a7-5fdfc080e2a3/rows?key=VtYiDKfjNud9rTw0SXigai2JNMM83HcKoK7LgoP1ZaE1TJ2Ml86UxQ1Z3nO5mmp1Yk6GKEbADFlDdZx%2Bw06Mbw%3D%3D'


#-----------------ENROLLMENTS-------------------

#call massmutual dojo enrollments api
enresp = requests.get(enurl, headers=headers)
print(enresp)
enresults = enresp.json()["path_enrollments"]

#parse data
for entry in enresults:
    #reformat status
    if entry["status"] == "in_progress":
        entry["status"] = "In Progress"
    elif entry["status"] == "passed":
        entry["status"] = "Complete"
    try:
        entry["completed_at"] = (entry["completed_at"]).split(" ")[0]
    except AttributeError:
        entry["completed_at"] = None

    #populate array
    sjenrollments.append({
        'email': entry["email"],
        'level_name': entry["level_name"],
        'role_name': entry["role_name"],
        'status': entry["status"],
        'completed_at': entry["completed_at"],
        'progress': entry["progress"],
        'progress_percent': entry["progress_percent"]})

#call contractor dojo enrollments api
ctenresp = requests.get(ctenurl, headers=ctheaders)
print(ctenresp)
ctenresults = ctenresp.json()["path_enrollments"]

#parse data
for entry in ctenresults:
    if entry["status"] == "in_progress":
        entry["status"] = "In Progress"
    elif entry["status"] == "passed":
        entry["status"] = "Complete"
    try:
        entry["completed_at"] = (entry["completed_at"]).split(" ")[0]
    except AttributeError:
        entry["completed_at"] = None

    #populate array
    sjenrollments.append({
        'email': entry["email"],
        'level_name': entry["level_name"],
        'role_name': entry["role_name"],
        'status': entry["status"],
        'completed_at': entry["completed_at"],
        'progress': entry["progress"],
        'progress_percent': entry["progress_percent"]})

#print number of enrollments
print(len(sjenrollments))

#Delete table data
deleteTable = """DROP TABLE IF EXISTS SJENROLL """
mycursor.execute(deleteTable)
mydb.commit()

#Create table
createTable = '''CREATE TABLE SJENROLL(
  email VARCHAR(128),
  level_name VARCHAR(128),
  role_name VARCHAR(128),
  status VARCHAR(128),
  completed_at VARCHAR(32),
  progress VARCHAR(128),
  progress_percent VARCHAR(128)
)'''
mycursor.execute(createTable)
mydb.commit()

#init data
data = []
for entry in sjenrollments:
    data.append([entry["email"], entry["level_name"], entry["role_name"], entry["status"], entry["completed_at"], entry["progress"], entry["progress_percent"]])

#Execute query
mycursor.executemany("""INSERT INTO SJENROLL VALUES (%s,%s,%s,%s,%s,%s,%s)""", data)
mydb.commit()

#-----------------USERS-------------------

#call MassMutual dojo users api
usersresp = requests.get(usersurl, headers=headers)
print(usersresp)
usersresults = usersresp.json()["users"]

#parse data
for entry in usersresults:

    if entry["security_champion"] == "fim-securitytraining-maven":
        entry["security_champion"] = "True"

    #populate array
    sjusers.append({
        'email': entry["email"],
        'total_points': entry["total_points"],
        'security_champion': entry["security_champion"]})

#call MassMutual Partners dojo users api
ctusersresp = requests.get(ctusersurl, headers=ctheaders)
print(ctusersresp)
ctusersresults = ctusersresp.json()["users"]

#parse data
for entry in ctusersresults:

    if entry["security_champion"] == "fim-securitytraining-maven":
        entry["security_champion"] = "True"
    else:
        entry["security_champion"] = "False"

    #populate array
    sjusers.append({
        'email': entry["email"],
        'total_points': entry["total_points"],
        'security_champion': entry["security_champion"]})

print(len(sjusers))

#Delete SJUSERS table data
deleteusersTable = """DROP TABLE IF EXISTS SJUSERS """
mycursor.execute(deleteusersTable)
mydb.commit()

#Create SJUSERS table
createTable = '''CREATE TABLE SJUSERS(
  email VARCHAR(128),
  total_points VARCHAR(128),
  security_champion VARCHAR(128)
)'''
mycursor.execute(createTable)
mydb.commit()

#init data
usersdata = []
for entry in sjusers:
    usersdata.append([entry["email"], entry["total_points"], entry["security_champion"]])

#Execute query
mycursor.executemany("""INSERT INTO SJUSERS VALUES (%s,%s,%s)""", usersdata)
mydb.commit()

#-----------------SQL VIEW-------------------

#Delete view if exists
deleteView = """DROP VIEW IF EXISTS education2 """
mycursor.execute(deleteView)
mydb.commit()

#Create view
createView = '''CREATE VIEW education2 AS(
SELECT 
  Workday.id,
  Workday.name,
  Workday.email,
  Workday.title,
  Workday.jobFamilyGroup,
  Workday.jobFamily,
  Workday.managerId,
  Workday.bg,
  Workday.sbu,
  Workday.division,
  Workday.department,
  Workday.subDepartment1,
  Workday.subDepartment2,
  Workday.subDepartment3,
  Workday.subDepartment4,
  Workday.developer,
  Workday.chapter,
  Workday.contractor,
  Workday.intern,
  Workday.onleave,
  SJENROLL.level_name AS Course,
  SJENROLL.role_name,
  SJENROLL.status AS Status,
  SJENROLL.completed_at,
  SJENROLL.progress AS ModulesCompleted,
  SJENROLL.progress_percent AS Progress,
  SJUSERS.total_points AS Points,
  SJUSERS.security_champion AS Maven
FROM Workday
LEFT OUTER JOIN SJENROLL ON SJENROLL.email = Workday.email
LEFT OUTER JOIN SJUSERS ON SJUSERS.email = Workday.email
)'''
mycursor.execute(createView)
mydb.commit()

#-----------------POWERBI-------------------

#Execute query
query = "SELECT * FROM `education2`"
mycursor.execute(query)
edu = list(mycursor.fetchall())
print(len(edu))

#process to dict
users = [dict(zip([key[0] for key in mycursor.description], row)) for row in edu]

#Process export data
payload = []
for user in users:
    if user["Status"] == "" or user["Status"] is None:
        user["Status"] = "Not Started"
    if user["Course"] == "" or user["Course"] is None:
        user["Course"] = "Not Started"
    #add current user
    payload.append(user)

    #Post data if over 2500 entries
    if len(payload) > 2499:
        #Post data
        pbiresp = requests.post(pbiurl, headers=pbiheaders, data=json.dumps(payload))
        print(len(payload))
        print(pbiresp)
        #reset
        payload = []

#send remaining data
pbiresp = requests.post(pbiurl, headers=pbiheaders, data=json.dumps(payload))
print(len(payload))
print(pbiresp)

#close connections
mycursor.close()
mydb.close()
