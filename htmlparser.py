from lxml import html
import sys
import MySQLdb

filename = sys.argv[1]
tablename = sys.argv[2]
data = open(filename).read()

#Fetch the html file in a tree structure using `html.fromstring()`
tree = html.fromstring(data)

#Use xpath to navigate through the html elements

#Fetch a list of elements with bold font and font size 10 px. Header elements are identified by bold font
header_lines = tree.xpath('//span[contains(@style, "font-family: b\'Courier-Bold\'; font-size:10px")]')
#Fetch a list of elements with normal/regular font size, these are the values for header
values_lines = tree.xpath('//span[contains(@style, "r\'; font-size:")]') 
 

#Connect to db
server = "localhost"
user = "ramya"
pwd = "1234"
database = "myfirstsql"

db = MySQLdb.connect(server,user,pwd,database )
#setup cursor
cursor = db.cursor()



########SUPPORTING FUNCTIONS & VARIABLES

#Dict to store header & values
myresults = dict()
#Supporting variables to understand the iteration through header values
previous,j = "",0



def striptext(content):
	''' Strips the text content within a span element

	content: lxml.html.HtmlElement
	'''
	return [x.strip() for x in content.xpath('.//text()')]

def list2str(inputlist):
	''' Picks element in the inputlist to form a string
	It's easier to use a string field for column update 
	in MYSQL.

	inputlist: list
	'''
	return " ".join(str(x) for x in inputlist)

def create_table():
	#Creates a MYSQL table based on the tablename provided
    try:
        createquery = "CREATE TABLE IF NOT EXISTS "+tablename+" (filename varchar(50) primary key )"
        cursor.execute(createquery)
    except:
        print("TABLE already exists!")


def insert_rows():
	#Inserting a new row for each new file encountered
    filename_query = "INSERT INTO "+tablename+" (filename) values ('" + filename + "')"
    cursor.execute(filename_query)


def add_col():
	#Update a row with column names.Header values are set as Column names.
    for index in myresults:
        try:
        	#Remove trailing space & `:`
            colname = myresults[index]["header"].strip(':').strip()
            updatequery = "ALTER TABLE "+tablename+" ADD `"+colname+"` text"
            cursor.execute(updatequery)
        except:
    	    print("colname already present!")


def update_col_values():
	'''Update the columns in a row with relevant values from file

	'''

	for index in myresults:
		try:
			colvalue = myresults[index]["value"]
			colname = myresults[index]["header"].strip(':').strip()
			updatequery ="UPDATE "+tablename+" SET `"+colname+ "` = '"+colvalue+"' WHERE filename = '"+filename+"'"
			cursor.execute(updatequery)
			db.commit()
		except:
			print("error in updating  ", colvalue)
			


#########################################

'''Following piece iterates through the header line elements,
and strips through the text content to get header & text values.
For Service Description field content overflows to more than one `div`,
altering the mapping between header and values. For this purpose header 
field is tracked separately. Similarly the last header field has two
header values clubbed into one, due to `div` arrangement. Code tracks
this well, extracts the merged header values and picks the value by
modifying the index.

Finally `myresults` dict has header and values put together for each file 
in the following format:

{
	0: {
		'header': 'Service Request Date :',
		'value': '03/08/2017'
	},
	1: {
		'header': 'SRN :',
		'value': 'U16571275'
	},
	2: {
		'header': 'Payment made into :',
		'value': 'ICICI BANK'
	},
	3: {
		'header': 'Received From : Name : Address :',
		'value': 'Zauba Technologies and Data Services Privat No 1/10, II Floor, Near Gate No 9 APMC Yard, Yeshwanthpur Bangalore , Karnataka India - 00560022'
	},
	4: {
		'header': 'Full Particulars of Remittance Service Type:',
		'value': 'Fee for inspection of Public documents'
	},
	5: {
		'header': 'Service Description',
		'value': 'Inspection of Public documents of KEYSTONE REALTORS PRIVATE LIMITED ( U45200MH1995PTC094208  )'
	},
	6: {
		'header': 'Type of Fee',
		'value': 'Normal'
	},
	7: {
		'header': 'Amount(Rs.)',
		'value': '100.00'
	},
	8: {
		'header': 'Total',
		'value': '100.00'
	},
	9: {
		'header': 'Mode of Payment:',
		'value': 'Credit Card/Prepaid Card - ICICI Bank'
	},
	10: {
		'header': 'Received Payment Rupees:',
		'value': 'One Hundred Only'
	}
}

'''

for i, header_line in enumerate(header_lines):
    if not i==len(header_lines)-1:
        span_id = header_line.xpath('.//@style')[0]
        header_text =list2str(striptext(header_line))
        value_text = list2str(striptext(values_lines[i+j]))
        if header_text == 'Service Description':
        	#Service description overflows to mutiple lines.
        	#Values from the subsequent lines are appended
    	    value_text += list2str(striptext(values_lines[i+1]))
    	    j= 1
    	    previous = "Service Description"
    	    if not value_text.endswith(')'):
    		    value_text += list2str(striptext(values_lines[i+2]))
    		    j = 2
    		    previous = "Service Description"
        previous = header_text
        myresults[i] = dict(header=header_text,value=value_text)
       
    else:
        #Within the last element two headers are present
        #Extract the fields separately and update values
        span_id = header_line.xpath('.//@style')[0]
        span_text = striptext(header_line)
        
        for k,element in enumerate(span_text):
        	header_text = element
        	
        	if k==len(span_text)-1:
        		#Due to service description overflowing to mutiple lines,
        		#...header index and value index doesn't match
        		#...this is coupled with two headers using the same index
        		value_text = list2str(striptext(values_lines[len(values_lines)-3]))
        	else:
        		value_text = list2str(striptext(values_lines[len(values_lines)-2]))
        	
        	myresults[i+k]=dict(header=header_text,value=value_text)
        	



#print(myresults)
create_table()
insert_rows()
add_col()
update_col_values()

db.close()