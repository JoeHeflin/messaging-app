import psycopg2

try:
	conn = psycopg2.connect("dbname=a3")
	print(conn)
	conn.close()
	print(conn)
except:
	print("Unable to connect to database")