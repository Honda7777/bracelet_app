from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bracelet_secret_key')


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "postgresql://neondb_owner:npg_3OCrnX0WYHkT@ep-ancient-haze-agk3hsyl-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

@app.route('/')
def home():
    return render_template('home.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is None:
            # Redirect to register if user not found
            return redirect(url_for('register'))

        if check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Invalid password!"

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username already exists!")

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, age=int(age))
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error="Registration failed. Please try again.")
    
    return render_template('register.html')

@app.route('/get_data')
def get_data():
    if 'username' not in session:
        return jsonify({
            "Username": "Guest",
            "Age": "Not set",
            "Gender": "Not set",
            "Weight": "Not set",
            "Height": "Not set",
        })

    user = User.query.filter_by(username=session['username']).first()
    if user:
        return jsonify({
            "Username": user.username,
            "Age": user.age if user.age is not None else "Not set",
            "Gender": user.gender if user.gender else "Not set",
            "Weight": user.weight if user.weight is not None else "Not set",
            "Height": user.height if user.height is not None else "Not set",
        })
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/change-username', methods=['GET', 'POST'])
def change_username():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            new_username = request.form.get('new_username')
            current_password = request.form.get('current_password')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_username.html', error="User not found!")
            if not check_password_hash(user.password, current_password or ''):
                return render_template('change_username.html', error="Current password is incorrect!")
            if not new_username:
                return render_template('change_username.html', error="Please provide a new username.")
            existing = User.query.filter_by(username=new_username).first()
            if existing:
                return render_template('change_username.html', error="Username already taken! Please choose a different one.")
            old_username = user.username
            user.username = new_username
            db.session.commit()
            session['username'] = new_username
            return render_template('change_username.html', success=f"Username successfully changed from '{old_username}' to '{new_username}'!")
        except Exception:
            return render_template('change_username.html', error="Failed to change username. Please try again.")
    return render_template('change_username.html')


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_password.html', error="User not found!")
            if not check_password_hash(user.password, current_password or ''):
                return render_template('change_password.html', error="Current password is incorrect!")
            if (new_password or '') != (confirm_password or ''):
                return render_template('change_password.html', error="New passwords do not match!")
            if not new_password or len(new_password) < 4:
                return render_template('change_password.html', error="New password must be at least 4 characters long!")
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return render_template('change_password.html', success="Password successfully changed!")
        except Exception:
            return render_template('change_password.html', error="Failed to change password. Please try again.")
    return render_template('change_password.html')


@app.route('/change-age', methods=['GET', 'POST'])
def change_age():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            age = request.form.get('age')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_age.html', error="User not found!")
            if age is None or age == "":
                return render_template('change_age.html', error="Please provide a valid age.")
            user.age = int(age)
            db.session.commit()
            return render_template('change_age.html', success="Age updated successfully!")
        except Exception:
            return render_template('change_age.html', error="Failed to update age. Please try again.")
    return render_template('change_age.html')


@app.route('/change-gender', methods=['GET', 'POST'])
def change_gender():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            gender = request.form.get('gender')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_gender.html', error="User not found!")
            user.gender = gender or None
            db.session.commit()
            return render_template('change_gender.html', success="Gender updated successfully!")
        except Exception:
            return render_template('change_gender.html', error="Failed to update gender. Please try again.")
    return render_template('change_gender.html')


@app.route('/change-weight', methods=['GET', 'POST'])
def change_weight():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            weight = request.form.get('weight')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_weight.html', error="User not found!")
            if weight is None or weight == "":
                return render_template('change_weight.html', error="Please provide a valid weight.")
            user.weight = int(weight)
            db.session.commit()
            return render_template('change_weight.html', success="Weight updated successfully!")
        except Exception:
            return render_template('change_weight.html', error="Failed to update weight. Please try again.")
    return render_template('change_weight.html')


@app.route('/change-height', methods=['GET', 'POST'])
def change_height():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            height = request.form.get('height')
            user = User.query.filter_by(username=session['username']).first()
            if not user:
                return render_template('change_height.html', error="User not found!")
            if height is None or height == "":
                return render_template('change_height.html', error="Please provide a valid height.")
            user.height = int(height)
            db.session.commit()
            return render_template('change_height.html', success="Height updated successfully!")
        except Exception:
            return render_template('change_height.html', error="Failed to update height. Please try again.")
    return render_template('change_height.html')
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user = User.query.filter_by(username=session['username']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields if provided
        if 'age' in data and data['age']:
            user.age = int(data['age'])
        
        if 'gender' in data:
            user.gender = data['gender'] if data['gender'] else None
        
        if 'weight' in data and data['weight']:
            user.weight = int(data['weight'])
        
        if 'height' in data and data['height']:
            user.height = int(data['height'])
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/migrate_db')
def migrate_db():
    try:
        with db.engine.connect() as connection:
            # Ensure columns exist for new profile fields
            needed_columns = {
                'age': 'INTEGER',
                'gender': 'VARCHAR(20)',
                'weight': 'INTEGER',
                'height': 'INTEGER',
            }
            added = []
            for col, coltype in needed_columns.items():
                res = connection.execute(db.text(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='user' AND column_name='{col}'
                """))
                if not res.fetchone():
                    connection.execute(db.text(f"ALTER TABLE \"user\" ADD COLUMN {col} {coltype}"))
                    added.append(col)
            connection.commit()
            if added:
                return f"Database migration successful! Added columns: {', '.join(added)}."
            return "All columns already exist. No migration needed."
    except Exception as e:
        return f"Database migration failed: {e}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
