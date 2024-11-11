from api import app, db, UserModel

# Data dummy untuk pengguna yang ingin kita masukkan
dummy_users = [
    {"name": "Alice Johnson", "email": "alice@example.com"},
    {"name": "Bob Smith", "email": "bob@example.com"},
]

def add_dummy_data():
    with app.app_context():
        db.create_all()  # Membuat tabel di database jika belum ada
        for user_data in dummy_users:
            # Cek apakah pengguna dengan email yang sama sudah ada di database
            existing_user = UserModel.query.filter_by(email=user_data["email"]).first()
            if not existing_user:
                user = UserModel(name=user_data["name"], email=user_data["email"])
                db.session.add(user)
        db.session.commit()
        print("Database berhasil dibuat dan data dummy berhasil ditambahkan!")

if __name__ == "__main__":
    add_dummy_data()
