from flask import Flask, request, render_template, redirect, url_for, flash, session
import pickle
import numpy as np
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Load models
def load_models():
    try:
        nb_model = pickle.load(open('naive_bayes_model.pkl', 'rb'))
        rf_model = pickle.load(open('random_forest_model.pkl', 'rb'))
    except Exception as e:
        print(f"Error loading models: {e}")
        raise
    return nb_model, rf_model

nb_model, rf_model = load_models()

# In-memory user store for demo purposes (replace with a database in production)
users = {}

# Crop and fertilizer mappings
crop_dict = { 
    1: 'rice', 2: 'maize', 3: 'jute', 4: 'cotton', 5: 'coconut', 
    6: 'papaya', 7: 'orange', 8: 'apple', 9: 'muskmelon', 10: 'watermelon', 
    11: 'grapes', 12: 'mango', 13: 'banana', 14: 'pomegranate', 
    15: 'lentil', 16: 'blackgram', 17: 'mungbean', 18: 'mothbeans', 
    19: 'pigeonpeas', 20: 'kidneybeans', 21: 'chickpea', 22: 'coffee'
}

fertilizer_dict = {
    0: 'Urea', 1: 'DAP', 2: 'Fourteen-Thirty Five-Fourteen', 
    3: 'Twenty Eight-Twenty Eight', 4: 'Seventeen-Seventeen-Seventeen', 
    5: 'Twenty-Twenty', 6: 'Ten-Twenty Six-Twenty Six', 
    7: 'Twenty Twenty - Zero Thirteen', 8: 'Mira - 71'
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/schemes')
def schemes():
    schemes_info = [
        {
            "title": "PM-KISAN",
            "description": "The PM-KISAN scheme, officially known as the Pradhan Mantri Kisan Samman Nidhi, is a significant initiative launched by the Government of India to provide direct financial assistance to small and marginal farmers. Under this scheme, eligible farmers receive an annual income support of Rs. 6,000, which is disbursed in three equal installments of Rs. 2,000 each..."
        },
        {
            "title": "Pradhan Mantri Fasal Bima Yojana",
            "description": "The Pradhan Mantri Fasal Bima Yojana (PMFBY) is a comprehensive crop insurance scheme designed to provide financial coverage to farmers against crop loss due to natural calamities, pests, and diseases..."
        },
        {
            "title": "Soil Health Card Scheme",
            "description": "The Soil Health Card Scheme is an innovative initiative by the Government of India aimed at promoting sustainable agriculture through soil health management..."
        }
    ]
    return render_template('schemes.html', schemes=schemes_info)
crop_images = {
    "wheat": "https://www.nestle-cereals.com/uk/sites/g/files/qirczx836/files/2022-07/wheat-facts.jpg.jpg",
    "rice": "https://static.toiimg.com/thumb/imgsize-23456,msid-112658458,width-600,resizemode-4/112658458.jpg",
    "maize": "https://i0.wp.com/blog.bijak.in/wp-content/uploads/2023/05/MAIZE-02.png?resize=940%2C519&ssl=1",
    "kidneybeans":"https://be-still-farms.com/cdn/shop/articles/different-dry-legumes-eating-healthy_2000x.jpg?v=1705056365",
    "pigeonpeas" :"https://foodprint.org/wp-content/uploads/2021/03/AdobeStock_279377700_1920x960_RFE.jpg",
    "mothbeans":"https://www.checkyourfood.com/content/blob/Ingredients/Moth-beans-nutritional-information-calories.jpg",
    "mungbean" :"https://cdn-prod.medicalnewstoday.com/content/images/articles/324/324156/mung-beans.jpg",
    "blackgram" :"https://lh5.googleusercontent.com/proxy/jzmBst1rJZVAEcW5tFPZoDDusB_cbdDhOHDcn79-S2aw9QxcqOhJniN4L_W4EY76OqJjH_tuef1KY23IcaRogb4lThS5lYfX7f3gyGUr0XVPwzc_uUfw0ZIEsg4",
    "lentil": "https://www.allrecipes.com/thmb/UeFtapHyGFBo4Lx-72GxgjrOGnk=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/13978-lentil-soup-DDMFS-4x3-edfa47fc6b234e6b8add24d44c036d43.jpg",
    "pomegranate":"https://www.onehappydish.com/wp-content/uploads/2022/04/how-to-cut-a-pomegranate-recipe.jpg",
    "banana":"https://cdn-prod.medicalnewstoday.com/content/images/articles/271/271157/bananas-chopped-up-in-a-bowl.jpg",
    "mango":"https://ichef.bbci.co.uk/images/ic/1200x675/p06hk0h6.jpg",
    "grapes":"https://www.thespruceeats.com/thmb/l1_lV7wgpqRArWBwpG3jzHih_e8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/what-are-grapes-5193263-hero-01-80564d77b6534aa8bfc34f378556e513.jpg",
    "watermelon":"https://hips.hearstapps.com/hmg-prod/images/fresh-ripe-watermelon-slices-on-wooden-table-royalty-free-image-1684966820.jpg",
    "muskmelon":"https://m.media-amazon.com/images/I/31o6kOLfraS._AC_UF1000,1000_QL80_.jpg",
    "apple":"https://post.medicalnewstoday.com/wp-content/uploads/sites/3/2022/07/what_to_know_apples_green_red_1296x728_header-1024x575.jpg",
    "orange":"https://cdn-prod.medicalnewstoday.com/content/images/articles/272/272782/oranges-in-a-box.jpg",
    "papaya":"https://cdn.britannica.com/31/157531-050-25D8087E/Papaya-fruit.jpg",
    "cotton":"https://textileengineering.net/wp-content/uploads/2023/01/Cotton-Fibre.jpg",
    "jute":"https://pellibags.com.au/cdn/shop/articles/jute_2277d98c-7df3-4e20-8cd8-1c5835b546aa_1445x.jpg?v=1689415411",
    "coconut":"https://m.media-amazon.com/images/I/71rIiMZClzL._AC_UF1000,1000_QL80_.jpg",
    "chickpea":"https://post.medicalnewstoday.com/wp-content/uploads/sites/3/2022/04/chickpeas_closeup_1296x728_header-1024x575.jpg",
    "coffee" : "https://images.unsplash.com/photo-1524350876685-274059332603?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y29mZmVlJTIwYmVhbnxlbnwwfHwwfHx8MA%3D%3D"
    # Add more crops and their image paths here
}

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        try:
            # Extracting input data from the form
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            # Preprocess the data and predict
            crop_features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            crop_prediction_num = nb_model.predict(crop_features)[0]
            crop_name = crop_dict.get(crop_prediction_num, "Unknown Crop")
            crop_image_url = crop_images.get(crop_name, "path/to/default_image.jpg")  # Default image if not found

            fertilizer_features = np.array([[N, P, K]])
            fertilizer_prediction = rf_model.predict(fertilizer_features)[0]
            fertilizer_name = fertilizer_dict.get(fertilizer_prediction, "Unknown Fertilizer")

            return render_template('prediction.html', crop_prediction=crop_name, fertilizer_prediction=fertilizer_name, crop_image=crop_image_url)
        except Exception as e:
            return render_template('prediction.html', error=str(e))

    return render_template('prediction.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the user already exists
        if username in users:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Check if the passwords match
        if password == confirm_password:
            # Store the user in the dictionary
            users[username] = {
                'email': email,
                'password': password  # In practice, you should hash the password
            }
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))  # Redirect to login or another page
        else:
            flash('Passwords do not match. Please try again.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user exists and the password matches
        if username in users and users[username]['password'] == password:
            session['username'] = username  # Log the user in
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

# Add a route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the session variable
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
