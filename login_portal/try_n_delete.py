#libraries 1
from fileinput import filename
import os
import string
import pymysql
from flask import Flask, render_template, request, redirect, flash, send_file, session
from passlib.hash import sha256_crypt
import gc
from werkzeug.utils import secure_filename
import csv
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from PIL import Image
import pafy
import plotly.express as px
import io,random
from werkzeug.utils import secure_filename
import pandas
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.naive_bayes import MultinomialNB
from test_utils import *

#libraries 2
import pandas as pd
# from flask import Flask, render_template, request
from numpy import *
from sklearn import linear_model



#create app1
app1 = Flask(__name__)
app1.debug = True
app1.secret_key = 'some secret key'

#create app2
app2 = Flask(__name__)


#sql_connection
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='Quiz_Database',
    port=3306,
    use_unicode=True,
    charset="utf8"
)



#to start all
@app1.route("/")
def home():
    return render_template("/home.html")



#Home, About us, Contact us page
@app1.route("/aboutus.html")
def aboutus():
    return render_template("/aboutus.html")

@app1.route("/contactus.html")
def contactus():
    return render_template("/contactus.html")

@app1.route("/home.html")
def intro():
    return render_template("/home.html")




@app1.route("/signup.html")
def index():
    return render_template("/signup.html")


@app1.route('/post_user', methods=['POST'])  # sign up function
def post_user():
    if request.method == 'POST':
        cursor = connection.cursor()
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        utype = "Applicant"
        x = cursor.execute("select * from login where u_email='" + email + "'")
        if int(x) > 0:
            flash("That username is already taken, please choose another")
            return redirect("/signup.html")
        else:
            if request.form['password'] == request.form['con_password']:
                sql = """ALTER TABLE login AUTO_INCREMENT = 100"""
                cursor.execute(sql)
                com = """insert into login (u_email,password,user_type) values (%s, %s, %s)"""
                cursor.execute(com, (email, password, utype))
                query = "select * from login where u_email='" + email + "'"
                cursor.execute(query)
                data = cursor.fetchone()[0]
                connection.commit()
                session['logged_in'] = True
                session['username'] = email
                session['id'] = data
                cursor.close()
                return render_template("/profile.html")
            else:
                flash("Password not same")
                return redirect("/signup.html")



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app1.route('/post_profile', methods=['POST'])  # profile completion function
def post_profile():
    id = session['id']
    if request.method == 'POST':
        cursor = connection.cursor()
        firstnme = request.form['frst_name']
        lst_nme = request.form['lst_name']
        dob = request.form['dob']
        gender = request.form['optradio']
        cntno = request.form['phn_no']
        email = session['username']
        institute = request.form['inst']
        clas = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pin = request.form['pin_code'] 
        cv = request.files['cv']
        
        com = "insert into student_profile (stud_id,stud_first_name,stud_last_name,stud_dob,stud_gender,cnt_number,stud_email,stud_inst,stud_class,stud_house,stud_city,stud_country, pin_code)	values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(com,
                       (session['id'], firstnme, lst_nme, dob, gender, cntno, email, institute, clas, house, city, country, pin))
        connection.commit()
        if cv and allowed_file(cv.filename):
            filename = secure_filename(cv.filename)
            cv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['cv'] = secure_filename(cv.filename)
            
        flash("Thanks for registering!")
        return redirect("/studenthome.html")
    connection.close()

@app1.route("/update_profile", methods=['post'])  # student profile update
def update_user():
    if request.method == 'POST':
        uid = session['username']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        institute = request.form['inst']
        clasnme = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pincode = request.form['pin_code']
        qry = "update student_profile set stud_first_name='" + frst_name + "',stud_last_name='" + lst_name + "',cnt_number='" + phone_no + "', stud_inst='" + institute + "', stud_class='" + clasnme + "',stud_house='" + house + "',stud_city='" + city + "',stud_country='" + country + "', pin_code='" + pincode + "' where stud_email='" + uid + "'"
        cursor = connection.cursor()
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/studenthome.html")
    else:
        return render_template("/studenthome.html")



#Login

@app1.route('/check_user', methods=['POST'])  # login function
def check_user():
    if request.method == 'POST':
        email = request.form['email']
        user_password = request.form['password']
        cursor = connection.cursor()
        com = "select * from login where u_email='" + email + "'"
        result = cursor.execute(com)
        cursor.close()
        if not result:
            flash("Invalid Login")
            return render_template("/login.html")
        else:
            cursor = connection.cursor()
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            data = cursor.fetchone()[2]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            utype = cursor.fetchone()[3]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            uid = cursor.fetchone()[0]
            cursor.close()
            if utype == "Applicant":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "Applicant"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/studenthome.html")
                else:
                    flash("Invalid Login")
                gc.collect()
                return redirect("/login.html")
            elif utype == "admin":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "admin"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/adminhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect("/login.html")
            elif utype == "personnel":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "personnel"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/instructorhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect('/login.html')



@app1.route("/login.html")
def login():
    return render_template("/login.html")



#Logout
@app1.route('/logout')
def logout():
    session.pop('user', None)
    return render_template("/login.html")


@app1.route('/logoutprofile', methods=['POST'])  # if not registered
def logoutprofile():
    id = session['username']
    cursor = connection.cursor()
    cmd = "delete from login where u_email = '" + id + "' "
    cursor.execute(cmd)
    connection.commit()
    session.pop('user', None)
    cursor.close()
    flash("Sorry registration unsuccessful")
    return render_template("/signup.html")

#Home tab
@app1.route("/studenthome.html")
def stud_home():
    return render_template("/studenthome.html")



#Profile tab
@app1.route("/viewprofile")  # student profile view
def view_user():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from student_profile where stud_email= '" + uid + "'"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/viewprofile.html", data=res)

@app1.route("/studeditprofile/<id>")  # student profile edit
def studeditprofile(id):
    cursor = connection.cursor()
    command = "select * from student_profile where stud_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/studeditprofile.html", data=res)



#Assesment tab
@app1.route("/startquiz.html")
def startquiz():
    return render_template("/startquiz.html")
    

data = pd.read_csv("login_portal\dataset.csv")
array = data.values

for i in range(len(array)):
    if array[i][0] == "Male":
        array[i][0] = 1
    else:
        array[i][0] = 0

df = pd.DataFrame(array)

maindf = df[[0, 1, 2, 3, 4, 5, 6]]
mainarray = maindf.values

temp = df[7]
train_y = temp.values
train_y = temp.values

for i in range(len(train_y)):
    train_y[i] = str(train_y[i])

mul_lr = linear_model.LogisticRegression(
    multi_class="multinomial", solver="newton-cg", max_iter=1000
)
mul_lr.fit(mainarray, train_y)


@app2.route("/", methods=["POST", "GET"])
def home():
    print("Accessed home route")
    if request.method == "GET":
        return render_template("personality_index.html")

    else:
        age = int(request.form["age"])
        if age < 17:
            age = 17
        elif age > 28:
            age = 28

        inputdata = [
            [
                request.form["gender"],
                age,
                9 - int(request.form["openness"]),
                9 - int(request.form["neuroticism"]),
                9 - int(request.form["conscientiousness"]),
                9 - int(request.form["agreeableness"]),
                9 - int(request.form["extraversion"]),
            ]
        ]

        for i in range(len(inputdata)):
            if inputdata[i][0] == "Male":
                inputdata[i][0] = 1
            else:
                inputdata[i][0] = 0

        df1 = pd.DataFrame(inputdata)
        testdf = df1[[0, 1, 2, 3, 4, 5, 6]]
        maintestarray = testdf.values

        y_pred = mul_lr.predict(maintestarray)
        for i in range(len(y_pred)):
            y_pred[i] = str((y_pred[i]))
        DF = pd.DataFrame(y_pred, columns=["Predicted Personality"])
        DF.index = DF.index + 1
        DF.index.names = ["Person No"]

        return render_template(
            "personality_result.html", per=DF["Predicted Personality"].tolist()[0]
        )


@app2.route("/personality_learn")
def learn():
    return render_template("personality_learn.html")


@app2.route("/personality_working")
def working():
    return render_template("personality_working.html")



# Handling error 404
@app2.errorhandler(404)
def not_found_error(error):
    return render_template("personality_error.html", code=404, text="Page Not Found"), 404


# Handling error 500
@app2.errorhandler(500)
def internal_error(error):
    return render_template("personality_error.html", code=500, text="Internal Server Error"), 500







#Tell us more tab
@app1.route("/adddesc", methods=['POST', 'GET'])
def adddesc():
    cursor = connection.cursor()
    if request.method == "POST":
        command = "select count(*) from student_description where stud_id =%s"
        cursor.execute(command, session['id'])
        res = cursor.fetchone()[0]
        if res == 0:
            desc1 = request.form['des1']
            desc2 = request.form['des2']
            desc3 = request.form['des3']
            id = session['id']
            command = "insert into student_description (stud_id,descrip1,descrip2,descrip3) values(%s,%s,%s,%s)"
            cursor.execute(command, (id, desc1, desc2, desc3))
            connection.commit()
            cursor.close()
            return render_template("/studenthome.html")
        else:
            flash("You have already aswered to these questions")
            return render_template("/studentdescription.html")
    else:
        cursor = connection.cursor()
        command = "select count(*) from student_description where stud_id =%s"
        cursor.execute(command, session['id'])
        res = cursor.fetchone()[0]
        cursor.close()
        if res == 0:
            return render_template("/studentdescription.html")
        else:
            flash("You have already answered to these questions")
            return render_template("/studentdescription.html")



#Report tab
@app1.route("/reportgeneration")
def reportgeneration():
    cursor = connection.cursor()
    command = "select stud_first_name, stud_last_name, stud_class, science, humanities, commerce, aptitude, total from student_profile where stud_id =%s "
    cursor.execute(command, session['id'])
    res = cursor.fetchall()
    cursor.close()
    return render_template("/reportgeneration.html", data=res)




#Settings tab
@app1.route("/settings.html")
def settings():
    return render_template("/settings.html")



#Change password
@app1.route('/change_password', methods=['POST'])  
def change_password():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = session['username']
        newpassword = sha256_crypt.encrypt(request.form['password1'])
        if request.form['password1'] == request.form['password2']:
            com = "update login set password ='" + newpassword + "' where u_email = '" + uid + "' "
            cursor.execute(com)
            connection.commit()
            flash("Password updated")
            return redirect("/settings.html")
        else:
            flash("Password Does not Match")
            return redirect("/settings.html")



#Delete account
@app1.route('/delete_user', methods=['POST'])  
def delete_user():
    if request.method == 'POST':
        uid = session['username']
        cursor = connection.cursor()
        command = "delete from student_profile where stud_email = '" + uid + "'"
        cursor.execute(command)
        query = "delete from login where u_email= '" + uid + "'"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        session.pop('user', None)
        return redirect("/home.html")

    else:
        flash("Wrong password")
        return redirect("/settings.html")






















if __name__ == "__main__":
    app1.run()
    app2.run(host="0.0.0.0", port=8080)