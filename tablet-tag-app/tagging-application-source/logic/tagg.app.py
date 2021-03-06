from flask import Flask, request, Response, jsonify
from flaskext.mysql import MySQL

mysql = MySQL()
app  = Flask(__name__)

DB = "smartdoor"
HOST = "10.129.23.101"
USER = "smart-door-user"
PSWD = "door!@#"

app.config['MYSQL_DATABASE_USER'] = USER
app.config['MYSQL_DATABASE_PASSWORD'] = PSWD
app.config['MYSQL_DATABASE_DB'] = DB
app.config['MYSQL_DATABASE_HOST'] = HOST
mysql.init_app(app)

con = mysql.connect() # database connection
cur = con.cursor() #dataset cursor handle

def update_presence_info(name):
	'''
		update whether user is present in the room or not
		1 - present
		0 - not present
	'''
	print "updating presence information"
	sql = "select ispresent from presence_data where name='%s'" %name
	print sql
	cur.execute(sql)
	res = cur.fetchone()
	print res
	presence_status = res[0] 
	if presence_status == 0:
		sql = "update presence_data set ispresent=1 where name='%s'" %name
	elif presence_status == 1:
		sql = "update presence_data set ispresent=0 where name='%s'" %name
	print sql
	try:
		cur.execute(sql)
		con.commit()
	except:
		con.rollback()
	
	print "presence_status updated"
	
	


def update_the_null_row(name):
	'''
		take the recent row from the mysql and upate the value
	'''
	
	con.commit()
	sql = "select * from (select * from user_data order by ts desc limit 1) as T where name is null"
	cur.execute(sql)
	res =  cur.fetchone()
	print res
	
	if res is not None:
		session_id = int(res[0]) # got the latest entry session id
		print session_id
		con.commit()
		sql = "update user_data set name='%s' where sid=%d" %(name, session_id)
		print sql
		try:
			cur.execute(sql)
			con.commit()
		except:
			con.rollback()
	
		print "Name updated ..."
		#update_presence_info(name)
		return 1
	else:
		print "Name not updated"
		return 0
	

def get_predicted_name():
		con.commit()
		sql = "select predicted_name from (select * from user_data order by ts desc limit 1) as T where T.name is null"
		cur.execute(sql)
		res = cur.fetchone()
		
		if res is not None:
			print res[0]
			return res[0]
		else:
			return ''
		

def get_occupancy_count():
	'''
		return the current occupancy count
	'''
	sql = "select count(*) from presence_data where ispresent=1"
	con.commit()
	cur.execute(sql)
	res = cur.fetchone()
	
	print res # always not none
	
	if res is not None:
		count = res[0]
		return count
	else:
		return 0


def get_accuracy():
	'''
		accuracy = (correct / total ) * 100
	'''
	total = None
	match = None
	con.commit()
	sql = "select count(*) from user_data";
	cur.execute(sql)
	res = cur.fetchone()
	if res is not None:
		total = res[0]
		print total
	else:
		return 0
	
	sql = "select count(*) from user_data where name=predicted_name"
	cur.execute(sql)
	res = cur.fetchone()
	if res is not None:
		match = res[0]
		print match
	else:
		return 0
		
	return (match  * 100/ total) 
		
		
		
@app.route('/prediction-accuracy', methods=['POST','GET'])
def prediction_accuracy_view():
	if request.method == 'GET':
			accuracy = get_accuracy()
			cb = request.args.get('callback')
			resp = "%s('%d')" %(cb, accuracy)
			return Response(resp, mimetype='application/javascript')
	elif request.method == 'POST':
			accuracy = -1
			cb = request.args.get('callback')
			resp = "%s('%d')" %(cb, accuracy)
			return Response(resp, mimetype='application/javascript')

@app.route('/current-occupancy-count', methods=['POST','GET'])
def current_occupancy_count_view():
		if request.method == 'GET':
			count = get_occupancy_count()
			cb = request.args.get('callback')
			resp = "%s('%d')" %(cb, count)
			return Response(resp, mimetype='application/javascript')
		elif request.method == 'POST':
			count = -1
			cb = request.args.get('callback')
			resp = "%s('%d')" %(cb, count)
			return Response(resp, mimetype='application/javascript')
			

@app.route('/predicted-name',methods=['POST','GET'])
def predicted_name_view():
		if request.method == 'POST':
				name = get_predicted_name()
				cb = request.args.get('callback')
				resp = "%s('%s')"%(cb, name)
				return Response(resp,mimetype='application/javascript')
				
		elif request.method == 'GET':
				name = get_predicted_name()
				cb = request.args.get('callback')
				resp = "%s('%s')"%(cb, name)
				return Response(resp,mimetype='application/javascript')
	

@app.route('/update-tag',methods=['POST','GET'])
def update_tag_view():
		if request.method == "POST":
				tag  = request.args.get('name')
				print "POST",tag
				status = update_the_null_row(tag)
				cb = request.args.get('callback')
				if status == 1:
					resp = "%s('%d')"%(cb, status)
				else:
					resp = "%s('%d')"%(cb, status)
				return Response(resp,mimetype='application/javascript')
				
		elif request.method == 'GET':
				tag  = request.args.get('name')
				print "GET",tag
				status = update_the_null_row(tag)
				cb = request.args.get('callback')
				if status == 1:
					resp = "%s('%d')"%(cb, status)
				else:
					resp = "%s('%d')"%(cb, status)
				return Response(resp,mimetype='application/javascript')

@app.route('/')
def index_view():
		return "api for tagging-app"
		
		
		
if __name__ == '__main__':
	
	app.run('0.0.0.0',port=7000, debug=True);

