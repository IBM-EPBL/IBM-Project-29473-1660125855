import ibm_db
conn=ibm_db.connect("DATABASE=Db2-rb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=60000;PROTOCOL=TCPIP;UID=tmh29490;PWD=kuO6Gg9kukf26CAb",'','')
connState = ibm_db.active(conn)
print(connState)
