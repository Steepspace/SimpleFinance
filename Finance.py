#!/bin/python3
import sqlite3
from datetime import date, datetime

con = sqlite3.connect("Finance.db")
# con = sqlite3.connect(":memory:")
c = con.cursor()
# Creat Initial Tables
with con:
    c.executescript("""CREATE TABLE IF NOT EXISTS Person (id INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT UNIQUE);
                       CREATE TABLE IF NOT EXISTS Money (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pid INTEGER, amount REAL, reason TEXT, paid INTEGER DEFAULT 0, FOREIGN KEY (pid) REFERENCES Person (id));""")

# Insert
def insertPerson(name):
    with con:
        c.execute("INSERT INTO Person (firstname) VALUES (?)", (name,))
    return getPersonId(name)

def insertMoney(name, amount, reason, date_t=date.today(), paid=0):
    pid = getPersonId(name)
    if pid is None:
        pid = insertPerson(name)

    with con:
        c.execute("INSERT INTO Money (pid, amount, reason, date, paid) VALUES (?, ?, ?, ?, ?)",
                  (pid, amount, reason, date_t.__str__(), paid))

# Update
def updatePaid(items):
    with con:
        for item in items:
            c.execute("SELECT paid FROM Money WHERE id=?", (item,))
            p = c.fetchone()[0]
            if p == 0:
                c.execute("UPDATE Money SET paid=1 WHERE id=?", (item,))
            else:
                c.execute("UPDATE Money SET paid=0 WHERE id=?", (item,))

def updateAll(name):
    pid = getPersonId(name)
    with con:
        c.execute("UPDATE Money SET paid=1 WHERE pid=?", (pid,))

# Delete
def deleteMoneyInstance(items):
    with con:
        for item in items:
            c.execute("DELETE FROM Money WHERE id=?", (item,))

# Get
def getPerson():
    c.execute("SELECT * FROM Person")
    return c.fetchall()

def getPersonId(name):
    c.execute("SELECT id FROM Person WHERE firstname=?", (name,))
    res = c.fetchone()
    return None if res is None else res[0]

def getMoney():
    c.execute("SELECT Money.id, date, firstname, amount, reason, paid FROM Money JOIN Person ON Money.pid = Person.id ORDER BY date")
    return c.fetchall()

def getMoneyReport():
    c.execute("""SELECT firstname, SUM(amount)
                 FROM Money JOIN Person ON Money.pid = Person.id
                 WHERE paid=0
                 GROUP BY (firstname)
                 ORDER BY SUM(amount)""")
    return c.fetchall()

def getMoneyReportForPerson(name, getAll=False):
    if getAll:
        c.execute("""SELECT Money.id, date, amount, reason
                     FROM Money JOIN Person ON Money.pid = Person.id
                     WHERE firstname=?
                     ORDER BY date""", (name,))
    else:
        c.execute("""SELECT Money.id, date, amount, reason
                     FROM Money JOIN Person ON Money.pid = Person.id
                     WHERE firstname=? AND paid=0
                     ORDER BY date""", (name,))
    return c.fetchall()

while(1):
    print("Choose from options below:")
    print("1) Insert instance into database.",
          "2) Get all instances from database.",
          "3) Update paid status of an instance.",
          "4) Delete instance from database.",
          "5) Generate net report.",
          "6) Get person list.",
          "7) Generate net report for specific person.",
          "8) Mark all instances of user as paid.",
          "9) Quit.", sep='\n')
    option = int(input("Enter option: "))

    if option == 1:
        temp = input("Format: name amount mm/dd/yy paid reason (default date=today and paid=0)\n   --> ").split("\"")
        Uinput = temp[0].split()
        Uinput.insert(2, temp[1])
        num_inputs = len(Uinput)
        print("-----------------------------")
        if num_inputs < 3 or num_inputs > 5:
            print("ERROR: Too many/few inputs")
            print("--------------------------")
            continue
        if num_inputs == 3:
            insertMoney(Uinput[0], float(Uinput[1]), Uinput[2])
        else:
            Udate = datetime.strptime(Uinput[3], '%m/%d/%y').date()
            if num_inputs == 4:
                insertMoney(Uinput[0], float(Uinput[1]), Uinput[2], Udate)
            else:
                insertMoney(Uinput[0], float(Uinput[1]), Uinput[2], Udate, Uinput[4])
        print("Successfully inserted amount!")
        print("-----------------------------")
        continue

    elif option == 2:
        print("---------------------------------")
        for x in getMoney():
            if len(x[4]) > 50:
                x = list(x)
                x[4] = x[4][:50]
                x = tuple(x)
            print("%4d | %10s | %-10s | %7.2f | %-50s | %d" % x)
        print("---------------------------------")
        continue

    elif option == 3:
        temp = input("Format: Instance ID (toggle paid)\n   --> ")
        Uinput = list(map(int,temp.split()))
        updatePaid(Uinput)
        print("---------------------------------")
        print("Successfully updated paid status!")
        print("---------------------------------")
        continue

    elif option == 4:
        temp = input("Format: Instance ID\n   --> ")
        Uinput = list(map(int,temp.split()))
        deleteMoneyInstance(Uinput)
        print("-------------------------------------")
        print("Successfully deleted money instances!")
        print("-------------------------------------")
        continue

    elif option == 5:
        print("-----------------")
        for x in getMoneyReport():
            print("%-10s | %7.2f" % x)
        print("-----------------")
        continue

    elif option == 6:
        print("--------------")
        for x in getPerson():
            print("%d | %-10s" % x)
        print("--------------")
        continue

    elif option == 7:
        Uinput = input("Format: name getAll (default getAll=0 (False))\n   --> ").split()
        num_inputs = len(Uinput)
        print("---------------------------------")
        if num_inputs < 1 or num_inputs > 2:
            print("ERROR: Too many/few inputs")
            print("--------------------------")
            continue
        if getPersonId(Uinput[0]) is None:
            print("ERROR: User does not exist!")
            print("--------------------------")
            continue
        if num_inputs == 1:
            for x in getMoneyReportForPerson(Uinput[0]):
                print("%4d | %10s | %7.2f | %-50s" % x)
        else:
            for x in getMoneyReportForPerson(Uinput[0], bool(int(Uinput[1]))):
                print("%4d | %10s | %7.2f | %-50s" % x)
        print("---------------------------------")
        continue

    elif option == 8:
        Uinput = input("Format: name\n   --> ")
        if getPersonId(Uinput) is None:
            print("ERROR: User does not exist!")
            print("--------------------------")
            continue
        updateAll(Uinput)
        print("-------------------------------------")
        print("Successfully updated instances for %s!" % Uinput)
        print("-------------------------------------")
        continue

    elif option == 9:
        print("-------")
        print("Exiting")
        print("-------")
        break

    else:
        print("-------------------------")
        print("Invalid input! Try again!")
        print("-------------------------")
        continue

con.close()
