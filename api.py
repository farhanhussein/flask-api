from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 
api = Api(app)

class UserModel(db.Model): 
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self): 
        return f"User(name={self.name}, email={self.email})"

# Request parser untuk input data user
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Nama tidak boleh kosong")
user_args.add_argument('email', type=str, required=True, help="Email tidak boleh kosong")

# Parser untuk pembaruan nama atau email parsial
update_args = reqparse.RequestParser()
update_args.add_argument('name', type=str, help="Nama tidak boleh kosong")
update_args.add_argument('email', type=str, help="Email tidak boleh kosong")

# Mendefinisikan field untuk respons API
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
}

# Field untuk respons hanya email
email_fields = {
    'email': fields.String
}

# Field untuk respons hanya nama
name_fields = {
    'name': fields.String
}

# Endpoint untuk menangani beberapa pengguna
class Users(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = UserModel.query.all() 
        return users, 200
    
    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        if UserModel.query.filter_by(email=args["email"]).first():
            abort(409, message="Email sudah digunakan")
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user) 
        db.session.commit()
        return user, 201

# Endpoint untuk menangani pengguna individu
class User(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User tidak ditemukan")
        return user, 200
    
    @marshal_with(user_fields)
    def patch(self, id):
        args = update_args.parse_args()
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User tidak ditemukan")
        
        # Perbarui data hanya jika disediakan
        if args["name"]:
            user.name = args["name"]
        if args["email"]:
            user.email = args["email"]
        db.session.commit()
        return user, 200
    
    def delete(self, id):
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User tidak ditemukan")
        
        db.session.delete(user)
        db.session.commit()
        return jsonify(message="User berhasil dihapus"), 204

# Endpoint untuk pencarian user berdasarkan nama
class SearchUsersByName(Resource):
    @marshal_with(user_fields)
    def get(self):
        name_query = request.args.get('name')
        if name_query:
            users = UserModel.query.filter(UserModel.name.like(f"%{name_query}%")).all()
            if not users:
                abort(404, message="Nama tidak ditemukan")
            return users, 200
        abort(400, message="Parameter 'name' diperlukan")

# Endpoint untuk mengambil user berdasarkan email
class UserByEmail(Resource):
    @marshal_with(user_fields)
    def get(self, email):
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            abort(404, message="User dengan email ini tidak ditemukan")
        return user, 200

# Endpoint untuk menampilkan hanya email
class UserEmail(Resource):
    @marshal_with(email_fields)
    def get(self):
        users = UserModel.query.all()
        return users, 200

# Endpoint untuk menampilkan hanya nama
class UserName(Resource):
    @marshal_with(name_fields)
    def get(self):
        users = UserModel.query.all()
        return users, 200

# Menambahkan route ke API
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')
api.add_resource(UserByEmail, '/api/users/email/<string:email>')  # Endpoint untuk pencarian berdasarkan email
api.add_resource(SearchUsersByName, '/api/users/search')  # Endpoint pencarian berdasarkan nama
api.add_resource(UserEmail, '/api/users/emails')  # Endpoint untuk menampilkan hanya email
api.add_resource(UserName, '/api/users/names')  # Endpoint untuk menampilkan hanya nama

@app.route('/')
def home():
    return '<h1>Selamat datang di Flask REST API</h1>'

if __name__ == '__main__':
    # Menjalankan fungsi untuk menambahkan data dummy sebelum menjalankan aplikasi
    from create_db import add_dummy_data
    add_dummy_data()  # Memanggil fungsi untuk menambahkan data pengguna
    
    app.run(debug=True)
