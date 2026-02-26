import mysql.connector
import re
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

def get_db():
    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="*raf257SQL",
        database="us_recipes_db"
    )
    return conn


def init_db():
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("create database if not exists us_recipes_db")
    cursor.execute("use us_recipes_db")
    cursor.execute("""
                   create table if not exists recipes(id int auto_increment primary key,
                   cuisine varchar(255), title varchar(255),rating float, prep_time int,
                   cook_time int,total_time int, description text,
                   nutrients json, serves varchar(255))
                   """)
    conn.commit()
    conn.close()
    print("Database and table initialized successfully.")
    
    
def clean_value(value):
    if value in ["NaN","",None]:
        return None
    return value

def load_data():
    conn=get_db()
    cursor=conn.cursor()
    with open(r"M:\PROJECTS\Securin\test\US_recipes_null.json","r") as f:
        data=json.load(f)
    batch=[]
    for item in data.values():
        title=item.get("title")
        cuisine=item.get("cuisine")
        rating=clean_value(item.get("rating"))
        prep_time=clean_value(item.get("prep_time"))
        cook_time=clean_value(item.get("cook_time"))
        total_time=clean_value(item.get("total_time"))
        description=clean_value(item.get("description"))
        nutrients=json.dumps(clean_value(item.get("nutrients"))) if item.get("nutrients") else None
        serves=clean_value(item.get("serves"))
        batch.append((title,cuisine,rating,prep_time,cook_time,total_time,description,nutrients,serves))
    cursor.executemany("""
                    insert ignore into recipes(title,cuisine,rating,prep_time,cook_time,total_time,description,nutrients,serves)
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,batch)
    conn.commit()
    conn.close()   
    print("Data loaded successfully.")
    
    
def extract_operator(value):
    if value.startswith(">="):
        return ">=",float(value[2:])
    elif value.startswith("<="):
        return "<=",float(value[2:])
    elif value.startswith(">"):
        return ">",float(value[1:])
    elif value.startswith("<"):
        return "<",float(value[1:])
    else:
        return "=",float(value)
    
#Search endpoint with filtering and pagination
@app.route("/api/recipes",methods=["GET"])
def get_recipes():
    conn=get_db()
    cursor=conn.cursor(dictionary=True)
    page=request.args.get("page",1,type=int)    
    limit=request.args.get("limit",10,type=int)    
    offset=(page-1)*limit
    cursor.execute("select count(*) as total from recipes")
    total=cursor.fetchone()["total"]
    
    cursor.execute("select * from recipes order by rating desc limit %s offset %s",(limit,offset))
    recipes=cursor.fetchall()
    conn.close()
    return jsonify({"page":page,"limit":limit,"total":total,"data":recipes})


@app.route("/api/recipes/search",methods=["GET"])
def search_recipes():
    title=request.args.get("title")
    cuisine=request.args.get("cuisine")
    rating=request.args.get("rating")
    total_time=request.args.get("total_time")
    calories=request.args.get("calories")
    
    conn=get_db()
    cursor=conn.cursor(dictionary=True)
    
    query="select * from recipes where 1=1"
    params=[]
    
    if title:
        query+=" and title like %s"
        params.append(f"%{title}%")
    if cuisine:
        query+=" and cuisine like %s"
        params.append(f"%{cuisine}%")   
    if rating:
        op,val=extract_operator(rating)
        query+=f" and rating {op} %s"
        params.append(val)
    if total_time:
        op,val=extract_operator(total_time)
        query+=f" and total_time {op} %s"
        params.append(val)
    if calories:
        op,val=extract_operator(calories)    
        query+=f" and cast(regexp_substr(json_unquote(json_extract(nutrients,'$.calories')),'[0-9]+')as unsigned) {op} %s"
        params.append(val)
    
    cursor.execute(query,params)
    results=cursor.fetchall()
    
    conn.close()
    return jsonify(results)

    
    
if __name__=="__main__":
    #init_db()
    #load_data()
    app.run(debug=True)