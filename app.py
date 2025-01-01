import os
import random
import shutil
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Path configuration
IMAGE_FOLDER = './static/images' # Manually set for test/actual images folder


# HELPER FUNCTIONS

# Start new round with selected images from previous
def start_new_round():
    global images, selected_images, round_number, round_images_count, bracket_data, round_matches, images_left
    round_number += 1
    if selected_images != []:
        # Dont shuffle images if round >= 2
        images = selected_images.copy()
        selected_images = []
    round_images_count = images_left = len(images)
    # Create matches for first round (randomized)
    if round_number == 1:
        for img in images:
            add_to_bracket(img, 1)
    round_matches = bracket_data[round_number].copy() # Copy of matches for this round (to delete as we go)

#Clear folders and reset tournament state
def reset_tournament():
    global images, selected_images, round_number, round_images_count, bracket_data, round_matches, images_left
    round_number = 0
    # Reload and shuffle original images
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith('jpeg')]
    random.shuffle(images)
    round_images_count = images_left = len(images) # Tracks how many images are left at the start of each round
    selected_images = []
    bracket_data = {1: []}
    round_matches = []
    start_new_round()

# Move img into next available bracket spot in round
def add_to_bracket(img, round):
    global bracket_data
    if round not in bracket_data:
        bracket_data[round] = []
    for i in range(len(bracket_data[round])):
        if bracket_data[round][i][1] == None:
            bracket_data[round][i] = (bracket_data[round][i][0], img)
            return
    bracket_data[round].append((img, None))


@app.route('/')
def index():
    global images, selected_images, round_number, round_images_count, bracket_data, round_matches, images_left
    # Done with this round's matches
    if images_left == 0:
        # Round is over
        if len(selected_images) < 2:
            # Tournament is over
            return render_template('end.html', winner=selected_images[0])
        else:
            start_new_round()
            return redirect(url_for('index'))
    elif images_left == 1:
        # Odd number of images in this round - give it a bye and move to next round
        selected_images.append(round_matches[0][0])
        add_to_bracket(round_matches[0][0], round_number+1)
        start_new_round()
        return redirect(url_for('index'))
    else:
        # At least one more match to run this round
        match = round_matches[0]
        img1, img2 = match
        round_matches.remove(match)
        return render_template(
            'index.html',
            img1=img1,
            img2=img2,
            round_number=round_number,
            images_left=images_left,
            round_images_count = round_images_count
        )

@app.route('/choose', methods=['POST'])
def choose():
    global images, bracket_data, selected_images, images_left
    chosen_image = request.form['image']
    img1 = request.form['image1']
    img2 = request.form['image2']
    
    if img1 in images:
        images.remove(img1)
    if img2 in images:
        images.remove(img2)
    
    images_left -= 2
    selected_images.append(chosen_image)
    add_to_bracket(chosen_image, round_number+1)
 
    return redirect(url_for('index'))

@app.route('/bracket', methods=['GET'])
def bracket():
    global bracket_data
    return render_template('bracket.html', bracket_data=bracket_data)

@app.route('/reset', methods=['GET'])
def reset():
    reset_tournament()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Set global variables and initialize tournament
    reset_tournament()
    app.run(port=8000, debug=True)
