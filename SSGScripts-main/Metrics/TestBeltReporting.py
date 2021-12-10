"""Pulls data from local workday file and Security Journey and outputs to OneDrive for consumption in PowerBI"""

import sys
import os
import csv
import xlrd
import requests

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import sjcttoken, sjtoken, sjenurl, sjusersurl, sjctenurl, sjctusersurl

def getdeveloperdata():
    """Pull only developers from Workday data into array"""
    #Workday export
    loc = (os.path.join(os.path.dirname(__file__),"data.xls"))
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)

    #init list
    users=[]

    #titles
    titles = []
    titles.append("Developer")
    titles.append("Developer 1")
    titles.append("Developer 2")
    titles.append("Developer 3")
    titles.append("Developer 4")
    titles.append("Developer-onsite")
    titles.append("Developer-Offshore")
    titles.append("Developer-offshore")
    titles.append("ESP DevOps Developer")
    titles.append("ETL Developer")
    titles.append("Salesforce Developer")
    titles.append("Data Science Software Engineer Lead")
    titles.append("Data Science Software Engineer Consultant")
    titles.append("API Software engineer")
    titles.append("Application Developer")
    titles.append("Software developer")
    titles.append("C# Web Developer")
    titles.append("Systems Engineer")
    titles.append("FullStack Developer")
    titles.append("Web Engineer Consultant")
    titles.append("BIRT Developer")
    titles.append("Web Consultant")
    titles.append("Web Developer (Front-End)")
    titles.append("Java Developer")
    titles.append("Senior Java Developer")

    #job families
    jobfamilies = []
    jobfamilies.append("Developing")
    jobfamilies.append("Development")
    jobfamilies.append("Data Engineering")
    jobfamilies.append("Data Science")

    #process workday data into list
    for row in range(0, sheet.nrows):
        title = sheet.cell_value(row,6)
        jobfamily = sheet.cell_value(row,8)
        if (title in titles) or (jobfamily in jobfamilies) :
            developer = "True"
        else:
            developer = "False"
        #DX chapters
        if sheet.cell_value(row,17) == "Digital Experience":
            if sheet.cell_value(row,18) == "Strategy & Program Management 1" or sheet.cell_value(row,18) == "Strategy & Program Management 2" or sheet.cell_value(row,18) == "Strategy & Program Management":
                chapter = "AVSB"
            elif sheet.cell_value(row,18) == "Workplace Solutions (1)" or sheet.cell_value(row,18) == "Workplace Solutions (2)":
                chapter = "Krank"
            elif sheet.cell_value(row,18) == "MMUS Strategic Priorities (1)" or sheet.cell_value(row,18) == "MMUS Strategic Priorities (2)":
                chapter = "M&M"
            elif sheet.cell_value(row,18) == "Mobile (Product)":
                chapter = "MoMinToo"
            elif sheet.cell_value(row,18) == "MM.Com & Content (1)" or sheet.cell_value(row,18) == "MM.Com & Content":
                chapter = "Mothership"
            elif sheet.cell_value(row,18) == "Design":
                chapter = "Product Design"
            elif sheet.cell_value(row,18) == "Dashboard & Login (1)":
                chapter = "Tamale"
            elif sheet.cell_value(row,18) == "":
                chapter = "Leadership"
            else:
                chapter = ""
        else:
            chapter = ""
        #check if contractor
        if " [C]" in sheet.cell_value(row,1):
            contractor = "True"
        else:
            contractor = "False"

        #check if intern
        if "Internal" in sheet.cell_value(row,6):
            intrn = "False"
        elif "International" in sheet.cell_value(row,6):
            intrn = "False"
        elif "Intern" in sheet.cell_value(row,6):
            intrn = "True"
        else:
            intrn = "False"

        #check if on leave
        if "(On Leave)" in sheet.cell_value(row,1):
            leave = "True"
        else:
            leave = "False"

        #populate array
        if row > 0 and developer == "True":
            users.append({
            'id': sheet.cell_value(row,0),
            'name': sheet.cell_value(row,1),
            'email': sheet.cell_value(row,4),
            'title': sheet.cell_value(row,6),
            'jobFamilyGroup': sheet.cell_value(row,7),
            'jobFamily': sheet.cell_value(row,8),
            'managerId': sheet.cell_value(row,12),
            'bg': sheet.cell_value(row,16),
            'sbu': sheet.cell_value(row,17),
            'division': sheet.cell_value(row,18),
            'department': sheet.cell_value(row,19),
            'subDepartment1': sheet.cell_value(row,20),
            'subDepartment2': sheet.cell_value(row,21),
            'subDepartment3': sheet.cell_value(row,22),
            'subDepartment4': sheet.cell_value(row,23),
            'developer' : developer,
            'chapter': chapter,
            'contractor': contractor,
            'intern': intrn,
            'onleave': leave})

    print(len(users))
    return users

def addsjuserdata(devs):
    """Add SJ user data to array"""
    emp = getsjusers(sjusersurl,sjtoken)
    cont = getsjusers(sjctusersurl,sjcttoken)
    users = []
    for entry in emp:
        users.append(entry)
    for entry in cont:
        users.append(entry)

    for dev in devs:
        for user in users:
            if user["email"].lower() == dev["email"].lower():
                dev["security_champion"] = user["security_champion"]
                dev["total_points"] = user["total_points"]
    return devs

def getsjusers(url,token):
    """Pull user data from Security Journey"""
    sjusers = []
    headers = {'Content-Type': 'application/json', 'ApiKey': token}
    resp = requests.get(url, headers=headers)
    print(resp)
    results = resp.json()["users"]

    #parse data
    for entry in results:
        if entry["security_champion"] == "fim-securitytraining-maven":
            entry["security_champion"] = "True"
        else:
            entry["security_champion"] = "False"
        sjusers.append({
            'email': entry["email"],
            'total_points': entry["total_points"],
            'security_champion': entry["security_champion"]})
    return sjusers

def addsjenrollmentdata(devs):
    """Prepare SJ enrollment data"""
    emp = getsjenrollments(sjenurl,sjtoken)
    cont = getsjenrollments(sjctenurl,sjcttoken)
    enrollments = []
    for entry in emp:
        enrollments.append(entry)
    for entry in cont:
        enrollments.append(entry)
    results = enrollmentstodevs(devs,enrollments)
    return results

def enrollmentstodevs(devs,enrollments):
    """Add enrollments data to array"""
    for enrollment in enrollments:
        if enrollment["status"] == "abandoned":
            enrollment["status"] = "Abandoned"
        elif enrollment["status"] == "paused":
            enrollment["status"] = "Paused"
        elif enrollment["status"] == "passed":
            enrollment["status"] = "Complete"
        elif enrollment["status"] == "in_progress":
            enrollment["status"] = "In Progress"
        for dev in devs:
            if dev["email"].lower() == enrollment["email"].lower():
                if enrollment["level_name"] not in dev:
                    dev[enrollment["level_name"]] = enrollment["status"]
                elif (dev[enrollment["level_name"]] == "In Progress" or dev[enrollment["level_name"]] == "Abandoned")  and enrollment["status"] == "Complete":
                    dev[enrollment["level_name"]] = enrollment["status"]
                elif dev[enrollment["level_name"]] == "Abandoned"  and (enrollment["status"] == "Complete" or enrollment["status"] == "In Progress"):
                    dev[enrollment["level_name"]] = enrollment["status"]
                elif dev[enrollment["level_name"]] == "Paused"  and (enrollment["status"] == "Complete" or enrollment["status"] == "In Progress"):
                    dev[enrollment["level_name"]] = enrollment["status"]
    return devs

def getsjenrollments(url,token):
    """Pull enrollments data from Security Journey"""
    headers = {'Content-Type': 'application/json', 'ApiKey': token}
    resp = requests.get(url, headers=headers)
    print(resp)
    results = resp.json()["path_enrollments"]
    return results

def exporttoexcel(array):
    """export data to csv"""
    csv_columns = list(array[0].keys())
    csv_columns.append('Brown Belt')
    csv_columns.append('Black Belt')
    csv_file = "/Users/mm67226/OneDrive - MassMutual/Scripts/SoftwareSecurity/SSGScripts/Metrics/eduexport.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in array:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def cleanedata(devs):
    """Clean up data before export"""
    for dev in devs:
        dev = checkbelt(dev,"White Belt")
        dev = checkbelt(dev,"Yellow Belt")
        dev = checkbelt(dev,"Green Belt")
        dev = checkbelt(dev,"Brown Belt")
        dev = checkbelt(dev,"Black Belt")
    return devs

def checkbelt(dev,belt):
    """Replace None with Not Started status"""
    try:
        if dev[belt] is None:
            dev[belt] = "Not Started"
    except KeyError:
        dev[belt] = "Not Started"
    return dev

def main():
    """main"""
    devs = getdeveloperdata()
    devs2 = addsjuserdata(devs)
    devs3 = addsjenrollmentdata(devs2)
    devs4 = cleanedata(devs3)
    exporttoexcel(devs4)
    print("done")

main()
