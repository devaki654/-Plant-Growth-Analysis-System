import os
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import mysql.connector
import logging
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Configure upload folder and allowed file types
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the trained model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.fc1 = nn.Linear(128 * 16 * 16, 512)
        self.fc2 = nn.Linear(512, 5)  # 5 categories for example
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(2, 2)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.maxpool(x)
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.maxpool(x)
        x = x.view(-1, 128 * 16 * 16)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Load the model
model = CNNModel().to(device)
model.load_state_dict(torch.load("modelmsql.pth"))
model.eval()

# MySQL database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="plat"
    )
    return connection

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Image prediction and MySQL data fetch
def predict_image(image_path):
    # Image preprocessing
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0).to(device)
    
    # Predict the class
    with torch.no_grad():
        output = model(image)
        _, predicted_class = torch.max(output, 1)
    
    # Fetch corresponding data from MySQL
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM plant_info WHERE id = %s", (predicted_class.item(),))
    plant_data = cursor.fetchone()
    cursor.close()
    connection.close()

    return predicted_class.item(), plant_data

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Here you should verify the username and password with your database
        if username == 'admin' and password == 'password':  # Replace with actual verification
            session['logged_in'] = True  # Set session variable to indicate user is logged in
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/log')
def log():
    # Here you can implement the logic to display logs or any other information
    return render_template('log.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if user is logged in before allowing access to index page
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle the image upload
        image_file = request.files['image']
        
        # Ensure the 'uploads' directory exists
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            logger.info(f"Created upload directory: {upload_dir}")
        
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(upload_dir, filename)
        
        try:
            image_file.save(image_path)
            logger.info(f"Image saved at: {image_path}")
            
            # Predict the class and fetch data
            predicted_class, plant_data = predict_image(image_path)
            
            # Display the result
            result = {
                "predicted_class": predicted_class,
                "plant_data": plant_data
            }
            logger.info(f"Prediction result: {result}")
            return jsonify(result)
        
        except Exception as e:
            logger.error(f"Error saving image or predicting: {e}")
            return jsonify({"error": str(e)}), 500
    
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove logged_in from session
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
