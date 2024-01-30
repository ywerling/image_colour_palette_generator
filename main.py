import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from wtforms import StringField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired,  NumberRange
import numpy as np
import cv2
from sklearn.cluster import KMeans


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
REGEX_IMAGE = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)"
IMAGE_PATH = "static/img"

#creates the flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = '34223hhdMefwD234F3'
app.config['UPLOAD_PATH'] = IMAGE_PATH
bootstrap = Bootstrap5(app)

class GetImageForm(FlaskForm):
    # image_name = FileField("Select image", [Regexp(REGEX_IMAGE)])
    image_name = FileField("Select image")
    num_colors = IntegerField("Number of colors", [NumberRange(min=1, max=20)])
    submit = SubmitField("Get image")

def prepare_image(image):
    # Convert the image to a 2D array of pixels
    pixels = image.reshape((-1, 3))

    # Convert to floating point
    pixels = np.float32(pixels)

    return pixels

def get_main_colors(image, clusters=3):
    """
    compute the main colors of an image
    :param image: image to be analysed
    :param clusters: number of colors
    :return: BGR (Blue, Green and Red) arrays - NumPy array of colors (type: numpy.ndarray)
    """
    # Create cluster using kmeans
    kmeans = KMeans(n_clusters=clusters)
    kmeans.fit(image)

    # Retrieve the dominant colors
    colours = kmeans.cluster_centers_

    # Convert the pixel values to integer
    return colours.astype(int)

def get_image_colors(filename, number_of_colors):
    """
    Get the various colors of the image and return the main one
    :param filename: image to analyse
    :param number_of_colors: number of colors returned
    :return: NumPy array of colors in BGR (type: numpy.ndarray)
    """
    # read the image and convert it to a NumPy array
    image_path = IMAGE_PATH + '/' + filename
    # print(f"Path: {image_path}")
    image = cv2.imread(image_path)

    prepared_image = prepare_image(image)
    main_colors = get_main_colors(prepared_image, number_of_colors)

    # convert numpy array to array of arrays
    colors = []
    for color in main_colors:
        # print(color.astype(int).tolist())
        colors.append(color.astype(int).tolist())
    return colors

@app.route("/colors", methods=['GET'])
def colors():
    main_colors = request.args['main_colors']
    print(type(main_colors))
    return render_template('colors.html', main_colors=main_colors)

#start page of the webapplication
@app.route("/", methods=['GET', 'POST'])
def home():
    form = GetImageForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if form.image_name:
                num_colors = form.num_colors.data
                file = request.files['image_name']
                image_data = file.read()
                filename = secure_filename(file.filename)
                # open file in binary mode to be able to write binary data
                open(os.path.join(IMAGE_PATH, filename), 'wb').write(image_data)
                main_colors = get_image_colors(filename, num_colors)
                print(type(main_colors))
                print(main_colors)
                print(main_colors[1][2])
                return redirect(url_for("colors", main_colors=main_colors))

    return render_template('index.html', form=form)

#ensures that the application keeps running
if __name__ == "__main__":
    #remove the debug=True statement before deploment
    app.run(debug=True)