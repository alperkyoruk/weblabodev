from flask import Flask, request, jsonify, session, g, render_template, redirect, url_for
from flask_restful import Resource, Api
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "mysecretkey"
api = Api(app)
CORS(app)

# SQLite veritabanı bağlantısı ve tablosu
DATABASE = "database.db"

def connect_db():
    return sqlite3.connect(DATABASE)

def create_users_table():
    with app.app_context():
        db = get_db()
        db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
        )
        db.commit()

def get_db():
    if not hasattr(g, "db"):
        g.db = connect_db()
    return g.db

@app.route('/')
def index():
    return render_template('index.html')

# Kayıt olma işlemi
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return {"message": "Kullanıcı zaten kayıtlı."}, 400
        
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        
        return {"message": "Kayıt başarılı."}, 201

# Giriş yapma işlemi
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        
        if not user:
            return {"message": "Geçersiz kullanıcı adı veya şifre."}, 401
        
        session['user'] = username
        render_template('success.html')
        return {"message": "Giriş başarılı."}
       

# Çıkış yapma işlemi
class Logout(Resource):
    def delete(self):
        if 'user' in session:
            session.pop('user')
        return {"message": "Çıkış başarılı."}

# Özel rota
class PrivateRoute(Resource):
    def get(self):
        if 'user' in session:
            return {"message": "Bu özel rota yalnızca oturum açmış kullanıcılar tarafından erişilebilir."}
        return {"message": "Oturum açmış bir kullanıcı bulunamadı."}, 401

# API URL yapılandırması
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(PrivateRoute, '/private_route')

@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)