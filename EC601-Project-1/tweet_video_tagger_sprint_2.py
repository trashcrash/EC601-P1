''' This program downloads images from a user in twitter,
    converts the images to a video, then uses google video
    intelligence to create a name tag list of the segments
    in the video

'''
from twitter import *
import urllib
import os
from google.cloud import videointelligence
import io
        
def get_all_tweets(screen_name):

    # Twitter Authentication

    consumer_key = ""
    consumer_secret = ""
    access_token_key = ""
    access_token_secret = ""

    api = Twitter(
        auth = OAuth(
                    access_token_key,
                    access_token_secret,
                    consumer_key,
                    consumer_secret,))

    # Get an information list of most recent tweets (max = 200)
    
    new_tweets = api.statuses.user_timeline(screen_name = screen_name, count = 10)

    # Write tweet objects to txt file. Ref: The example script
    
    file_name = 'tweet1.txt'
    file = open(file_name, 'w') 
    print "Writing tweet objects to txt please wait..."

    # This part is messy... It's like there are dictionaries in a dictionary which is inside a list.
    # The for loop picks the picture URLs from the data
    
    for status in new_tweets:
        try:
            file.write(str(status[u'entities'][u'media'][0][u'media_url'])+'\n')

    # Simply skip the tweet if there are no pictures in a tweet. 
    
        except KeyError:
            continue
    
    # Close the file
        
    print "Done"
    file.close()

    # Read image URLs from file

    with open(file_name) as f:
        lines = f.readlines()

    # Download the images and name them in sequence
    
    file_count = 0
    for line in lines:
        file_count += 1
        urllib.urlretrieve(line, "image_"+str(file_count)+".jpg")
    
# Generate the video out of the images, return the name of the video
    
def generate_video(output_name, image_initial_name = None, start_number = None, framerate = None):
    if image_initial_name == None:
        image_initial_name = "image_"
    if start_number == None:
        start_number = 1
    if framerate == None:
        framerate = 1/3
    return output_name

# Analyze the video, must be authenticated in advance

def analyze_labels_file(path):

    
    
if __name__ == '__main__':
    get_all_tweets("@Ibra_official")
    video_name = generate_video('out', "image_", 1, 0.3)    
    analyze_labels_file(video_name+'.mp4')
