from calendar import c
from doctest import script_from_examples
from sys import setswitchinterval
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
from connectToDatabase import *

total = 0

#Function to display datatable 
def logs(query):
    index = 2
    cursor = conn.cursor()
    cursor.execute(query)
    for row in cursor:
        column = 0
        for j in range(len(row)):
            e = Label(frame_tips, width=15, text=row[j], borderwidth=2, relief='ridge')
            e.grid(row=index, column=j)
            labels.append(e)
            column = column + 1
        delete = Button(frame_tips, text="Delete", command=lambda d=row[0], n=row[2] : delete_row(d,n))
        delete.grid(row=index, column=column)
        buttons.append(delete)
        index = index + 1
    cursor.close()

#Function to submit new tips entry
def submitEntry():
    cursor = conn.cursor()
    if (not validateTips()):
        return

    tips = tipsEntry.get()
    dateReceived = dateEntry.get_date()

    #Format date for appropriate MySQL date entry
    formattedDate = dateReceived.strftime('%Y-%m-%d')
    query = "INSERT INTO tips_list (amount, date_received) values (%s, %s)"

    values = (tips, formattedDate)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
    except:
        cursor.rollback()
    print("Record inserted")
    logs("SELECT * FROM tips_list")
    calculateTotal()
    
#Function to check if tips entered is valid
def validateTips():
    try:
        "{:.2f}".format(float(tipsEntry.get()))
        return True
    except ValueError:
        print("Tips earned is not a number")
        return False

#Function to delete entry from table
def delete_row(id, date):
    cursor = conn.cursor()
    message = messagebox.askyesnocancel("Delete ?","Delete id:" + str(id) + " Date: " + str(date), icon='warning', default='no')
    if message:
        cursor.execute("DELETE FROM tips_list WHERE id=" + str(id))
        messagebox.showerror("Deleted ", "No of records deleted = " + str(cursor.rowcount))

        #Reset Id counter and reassign all rows in order
        cursor.execute("SET @count = 0;")
        cursor.execute("UPDATE tips_list SET tips_list.id = @count:= @count + 1;")
        cursor.execute("ALTER TABLE tips_list AUTO_INCREMENT = 1;")
        #Restart auto increment

        conn.commit()
        cursor.close()
        destroy()
        calculateTotal()
        logs("SELECT * FROM tips_list")

#Function to calculate total tips earned by adding up all amount entries
def calculateTotal():
    global total
    total = 0
    cursor = conn.cursor()
    cursor.execute("SELECT amount from tips_list")
    for row in cursor:
        total = total + float(row[0])
    t = "Total: "
    f = str(total)
    text = t + f
    totalTipsLabel.config(text=text)
    cursor.close()

#Function to delete all rows from logs when deleting or inserting data
def destroy():
    for i in labels:
        i.destroy()
    for j in buttons:
        j.destroy()

def onFrameConfigure(canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))
    
window = Tk()
window.title("Tips Counter")
window.geometry('400x400')

tab_parent = ttk.Notebook(window)
entry_tab = Frame(tab_parent)
tips_tab = Frame(tab_parent)

tab_parent.add(entry_tab, text="New Entry")
tab_parent.add(tips_tab, text="Tips")

frame_dayOfTips = Frame(entry_tab)

#Widgets for entering data and tips earned
#region
dayLabel = Label(frame_dayOfTips, text="Date of tips")
today = date.today()
dateEntry = DateEntry(frame_dayOfTips, selectmode='day', maxdate=today)

dayLabel.grid(row=0, column=0, padx=5)
dateEntry.grid(row=0, column=1, padx=5)

tipsLabel = Label(frame_dayOfTips, text="Tips Earned")
tipsEntry = Entry(frame_dayOfTips, width=10)

tipsLabel.grid(row=1, column=0, padx=5)
tipsEntry.grid(row=1, column=1, padx=5)

submit = Button(frame_dayOfTips, text="Submit", command=submitEntry)
submit.grid(row=2, column=0, padx=5, pady=20, sticky="nsew")

frame_dayOfTips.grid(row=0,column=0, sticky='nsew')
tab_parent.pack(expand=1, fill='both')
#endregion

#Logs tab widgets
#region

frame_filters = Frame(tips_tab)
frame_filters.grid(row=0,column=0, sticky=W, padx=4, pady=5)

frame_headers = Frame(tips_tab)
frame_headers.grid(row=1, column=0,sticky="nsew", padx=4, pady=10)

#Filters for searching data
totalTipsLabel = Label(frame_filters)
totalTipsLabel.grid(row=0, column=0)

amountHighToLow = Button(frame_filters, text="Highest to Lowest", command=lambda query="SELECT * from tips_list ORDER BY amount DESC;" : logs(query))
amountHighToLow.grid(row = 1, column=0, sticky=W)

amountLowToHigh = Button(frame_filters, text="Lowest to Highest", command=lambda query="SELECT * FROM tips_list ORDER BY amount;" : logs(query))
amountLowToHigh.grid(row = 1, column=1, sticky=W, padx=2)

dateReceived = Button(frame_filters, text="Date Received", command = lambda query="SELECT * FROM tips_list ORDER BY date_received;" : logs(query))
dateReceived.grid(row=1, column=2, sticky=W)

#Columns for data table
header_id = Label(frame_headers, text="Id", width=15, borderwidth=2, relief='ridge', background='lightblue')
header_id.grid(row=0,column=0, sticky="")
header_amount = Label(frame_headers, text="Amount", width=15, borderwidth=2, relief='ridge', background='lightblue')
header_amount.grid(row=0,column=1)
header_dateReceived = Label(frame_headers, text="Date Received", width=15, borderwidth=2, relief='ridge', background='lightblue')
header_dateReceived.grid(row=0,column=2)

#Data table widgets
frame_dataTable = Frame(tips_tab)
frame_dataTable.grid(row=2, column=0)

canvas_table = Canvas(frame_dataTable, borderwidth=0)
frame_tips = Frame(canvas_table)

scrollbar = Scrollbar(frame_dataTable, orient="vertical", command= canvas_table.yview)
canvas_table.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=RIGHT, fill=Y)
canvas_table.pack(side=LEFT, fill="both", expand=True)
canvas_table.create_window((4,4), window=frame_tips, anchor="nw")

frame_tips.bind("<Configure>", lambda event, canvas=canvas_table: onFrameConfigure(canvas_table))

#endregion

labels = []
buttons = []

def calculateTotal():
    global total
    cursor = conn.cursor()
    cursor.execute("SELECT amount from tips_list")
    for row in cursor:
        total = total + float(row[0])
    t = "Total: "
    f = str(total)
    text = t + f
    totalTipsLabel.config(text=text)
    cursor.close()
        

if __name__ == "__main__":
    conn = connect()
    calculateTotal()
    logs("SELECT * FROM tips_list")
    window.mainloop()