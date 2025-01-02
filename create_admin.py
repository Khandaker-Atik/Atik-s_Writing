from app import app, db, bcrypt
from models import User

with app.app_context():
    username = 'atik'
    password = 'theuser'
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    admin = User(username=username, password=hashed_password)
    db.session.add(admin)
    db.session.commit()
    print('Admin user created.')