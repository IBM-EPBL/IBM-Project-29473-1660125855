from flask import Flask,render_template,request,redirect, url_for,flash
app = Flask(__name__)
import ibm_db
from flask_login import login_user, current_user, logout_user, login_required,LoginManager,UserMixin
import datetime
from sendgrid import SendGridAPIClient

from sendgrid.helpers.mail import Mail



dsn_hostname = "b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud" # e.g.: "54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud"
dsn_uid = "tmh29490"        # e.g. "abc12345"
dsn_pwd = "kuO6Gg9kukf26CAb"      # e.g. "7dBZ3wWt9XN6$o0J"

dsn_driver = "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"            # e.g. "BLUDB"
dsn_port = "32459"                # e.g. "32733" 
dsn_protocol = "TCPIP"            # i.e. "TCPIP"
dsn_security = "SSL"              #i.e. "SSL"


dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security)


print(dsn)

try:
    conn = ibm_db.connect(dsn, "", "")
    print ("Connected to database: ", dsn_database, "as user: ", dsn_uid, "on host: ", dsn_hostname)

except:
    print ("Unable to connect: ", ibm_db.conn_errormsg() )

SECRET_KEY = 'Jeevaneshwaran'


@app.route("/",methods=['GET', 'POST'])
def home():
    if request.method == 'POST':

        name=request.form.get('username')
        password=request.form.get('password')
        print(name,password)
        sql = "SELECT * FROM users WHERE user_name =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,name)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            
            return redirect(url_for('dashboard'))
            
        else:
            msg='invalid user name and password'
            return render_template('login.html',msg=msg)

    else:

        return render_template('login.html')


@app.route("/register",methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name')
        user_name=request.form.get('lastname')
        email=request.form.get('gmail')
        phone=request.form.get('ph_no')
        password=request.form.get('password')
        confirm=request.form.get('confirm_password')
        print(confirm)
        if password==confirm:
            
            sql ="SELECT  id FROM users ORDER BY ID DESC limit 1"
            stm=ibm_db.exec_immediate(conn,sql)
            while ibm_db.fetch_row(stm) != False:
                count=ibm_db.result(stm,0)
                print(count)

            
            insert=f"insert into users values ({int(count)+1}, '{name}', '{user_name}', '{email}', '{password}', '{phone}')"
            table=ibm_db.exec_immediate(conn,insert)
            return redirect(url_for('home'))

        else:
            msg='invalid user name and password'
            return render_template('register.html',msg=msg)
        

    else:
        return render_template('register.html')

@app.route("/searchproduct",methods=['GET', 'POST'])
def searchproduct():
    if request.method == 'POST':
        Product=request.form.get('search')
        sql = "SELECT * FROM products WHERE product =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,Product)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        return render_template('searchproduct.html',product=account)
    else:
        return render_template('searchproduct.html')


@app.route("/viewbill",methods=['GET', 'POST'])
def viewbill():
    sql ="SELECT  * FROM billing"
   
    stmt = ibm_db.exec_immediate(conn, sql)
    
    bill=[]
    amount=0
    
    while ibm_db.fetch_row(stmt) != False:
        dic=dict()
        dic['invoice']=ibm_db.result(stmt, 1)
        dic['product']=ibm_db.result(stmt, 3)
        dic['price']=ibm_db.result(stmt, 4)
        price=ibm_db.result(stmt, 4)
        dic['quantity']=ibm_db.result(stmt,5)
        quantity=ibm_db.result(stmt,5)
        dic['total']=int(price)*int(quantity)
        total=int(price)*int(quantity)
        amount +=total
        bill.append(dic)
        
    print(bill)
    print(amount)
    return render_template('viewbill.html',datas=bill)

@app.route("/minimum",methods=['GET', 'POST'])
def minimum():
    sql ="SELECT  * FROM products"
    # stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt,1,name)
    # ibm_db.bind_param(stmt,2,password)
    stmt = ibm_db.exec_immediate(conn, sql)
    
    datas=[]
    while ibm_db.fetch_row(stmt) != False:
        dic=dict()
        dic['product']=ibm_db.result(stmt, 0)
        dic['stock']=ibm_db.result(stmt, 1)
        dic['price']=ibm_db.result(stmt, 2)
        dic['alert']=ibm_db.result(stmt, 3)
        datas.append(dic)
    print(datas)
        # ibm_db.execute(stmt)
        # account = ibm_db.fetchall(stmt)
        # print (account)
    return render_template('minimum.html',datas=datas)

@app.route("/dashboard",methods=['GET', 'POST'])
def dashboard():
    sql ="SELECT  * FROM products"
    stmt = ibm_db.exec_immediate(conn, sql)
    
    datas=[]
    low=0
    count=0
    while ibm_db.fetch_row(stmt) != False:
        dic=dict()
        dic['product']=ibm_db.result(stmt, 0)
        dic['stock']=ibm_db.result(stmt, 1)
        stock=ibm_db.result(stmt, 1)
        dic['price']=ibm_db.result(stmt, 2)
        dic['alert']=ibm_db.result(stmt, 3)
        alert=ibm_db.result(stmt, 3)
        if int(stock)< int(alert):
            low += 1
        datas.append(dic)
        count+=1
    print(datas)
    sql ="SELECT  * FROM billing"
   
    stmt = ibm_db.exec_immediate(conn, sql)
    
    bill=[]
    amount=0
    bill_count=0
    while ibm_db.fetch_row(stmt) != False:
        dic=dict()
        dic['invoice']=ibm_db.result(stmt, 1)
        dic['product']=ibm_db.result(stmt, 3)
        dic['price']=ibm_db.result(stmt, 4)
        price=ibm_db.result(stmt, 4)
        dic['quantity']=ibm_db.result(stmt,5)
        quantity=ibm_db.result(stmt,5)
        dic['total']=int(price)*int(quantity)
        total=int(price)*int(quantity)
        amount +=total
        bill_count+=1
        bill.append(dic)
        
    print(bill)
    print(amount)
    return render_template('dashboard.html',datas=datas,low=low,amount=amount,count=count,bill_count=bill_count)

@app.route("/billing",methods=['GET', 'POST'])
def billing():
    date=datetime.datetime.today().date()
    if request.method == 'POST':
        invoice=request.form.get('invoice')
        date=request.form.get('date')
        product=request.form.get('product')
        quantity=request.form.get('quantity')
        price=request.form.get('price')
        insert=f"insert into billing values ( {invoice[-1]}, '{invoice}', '{date}', '{product}', {int(quantity)}, {int(price)})"
        table=ibm_db.exec_immediate(conn,insert)
        sql = "SELECT * FROM products WHERE product =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,product)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        try:
            count=account['STOCK']
            alert=account['Alert']
            update_count=int(count)-int(quantity)
            if int(update_count) < int(alert):
                print('email code')

                #write sendgrid email code here
                
                message = Mail(

                    from_email='jeffreylawrence2121@gmail.com',     
                    to_emails='mjeevan5791@gmail.com',     
                    subject='Sending with Twilio SendGrid is Fun',

                    html_content='<strong>and easy to do anywhere, even with Python</strong>')
                try:     
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))     
                    response = sg.send(message) 
                    print(response.status_code) 
                    print(response.body) 
                    print(response.headers) 
                except Exception as e: 
                        print(e)



            update=f"UPDATE products SET  stock = {update_count} WHERE  product = '{product}'"
            table=ibm_db.exec_immediate(conn,update)
            return redirect(url_for('dashboard'))
        except:

            return redirect(url_for('dashboard'))

    else:
        return render_template('billing.html',date=date,invoice=invoice_no())


@app.route("/addproduct",methods=['GET', 'POST'])
def addproduct():
    if request.method == 'POST':
        Product=request.form.get('Product')
        Stock=request.form.get('Stock')
        Price=request.form.get('Price')
        Alert=request.form.get('Alert')
        print(Product,Stock,Price,Alert)
        insert=f"insert into products values ( '{Product}', {int(Stock)}, {int(Price)}, {int(Alert)})"
        table=ibm_db.exec_immediate(conn,insert)
        
        return redirect(url_for('dashboard'))
    else:
        return render_template('addproduct.html')


def invoice_no():
    sql ="SELECT  id FROM billing ORDER BY ID DESC limit 1"
    stm=ibm_db.exec_immediate(conn,sql)
    while ibm_db.fetch_row(stm) != False:
        count=ibm_db.result(stm,0)
    if count:
        return f'bill00{int(count)+1}'
    else:
        return 'bill001'


app.run(debug=True)
