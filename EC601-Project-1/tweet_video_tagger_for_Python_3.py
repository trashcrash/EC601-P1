'''
    Copyright 2018 Chunshu Wu happycwu@bu.edu

    This program downloads images from a user in twitter,
    converts the images to a video, then uses google video
    intelligence to create a name tag list of the segments
    in the video

'''
from twitter import *
import urllib
import os
from google.cloud import videointelligence
import io

FRAMERATE = 0.3
IMAGE_LIST_NAME = 'tweet_image_list.txt'
IMAGE_INITIAL_NAME = "twitter_image_"

def get_all_tweets(screen_name, number_of_tweets):

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
    
    new_tweets = api.statuses.user_timeline(screen_name = screen_name, count = number_of_tweets)

    # Write tweet objects to txt file. Ref: The example script

    file = open(IMAGE_LIST_NAME, 'w') 
    print('\n****************************************')
    print ("\nWriting tweet objects to txt please wait...")

    # This part is messy... It's like there are dictionaries in a dictionary which is inside a list.
    # The for loop picks the picture URLs from the data
    
    for status in new_tweets:
        try:
            file.write(str(status[u'entities'][u'media'][0][u'media_url'])+'\n')

    # Simply skip the tweet if there are no pictures in a tweet. 
    
        except KeyError:
            continue
    
    # Close the file
        
    print ("Done\n")
    print('****************************************')
    file.close()

    # Read image URLs from file

    with open(IMAGE_LIST_NAME) as f:
        lines = f.readlines()

    # Download the images and name them in sequence
    
    file_count = 0
    for line in lines:
        file_count += 1
        urllib.request.urlretrieve(line, IMAGE_INITIAL_NAME + str(file_count)+".jpg")
    
# Generate the video out of the images, return the name of the video
    
def generate_video(output_name, start_number = None):
    if start_number == None:
        start_number = 1
    # Run ffmpeg in Windows

    print("\nConverting images to an mp4 video")
    os.system('ffmpeg -loglevel panic -framerate '+str(FRAMERATE)+' -i '+IMAGE_INITIAL_NAME+'%d.jpg \
                -c:v libx264 -r 30 -s 800*600 -pix_fmt yuv420p '+output_name+'.mp4')

    # Terminate the program if there is no picture to convert
    with open(IMAGE_LIST_NAME) as f:
        if f.readline() == '':
            print("\n***No image is detected in the user's twitter***")
            print("***The video can not be created, terminating the program.***\n")
            print('****************************************')
            clean_up()
            raise SystemExit()
    print("Conversion completed\n")
    print('****************************************')

        # Check if output_name.mp4 exists

    if not os.path.isfile(output_name + '.mp4'):
        print('\n***Label analysis failure, no mp4 file is found***\n')
        print('****************************************')
        clean_up()
        raise SystemExit()

    return output_name

# Analyze the video, must be authenticated in advance

def analyze_labels_file(path):

    # [START video_analyze_labels]

    """Detect labels given a file path."""
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.LABEL_DETECTION]
    with io.open(path, 'rb') as movie:
        input_content = movie.read()
    operation = video_client.annotate_video(
        features=features, input_content=input_content)
    print('\nProcessing video for label annotations (This may take a while):')
    result = operation.result(timeout=300)
    print('Finished processing\n')
    print('****************************************')

    # Process shot level label annotations

    label_count = 0
    print('\nGenerating a report')
    shot_labels = result.annotation_results[0].shot_label_annotations
    file = open('Label Analysis Result.txt', 'w')
    file.write('Probable contents in the video (NOT following the picture order): \n\n')
    for i, shot_label in enumerate(shot_labels):
        label_count += 1
        file.write('    ' + str(label_count) + '\t{}'.format(
            shot_label.entity.description) + '\n')
    file.write('\n\n')
    file.write('Details are listed below\n\n')
    for i, shot_label in enumerate(shot_labels):
        file.write('Shot label description: {}'.format(
            shot_label.entity.description) + '\n')
        for category_entity in shot_label.category_entities:
            file.write('\tLabel category description: {}'.format(
                category_entity.description) + '\n')
        for i, shot in enumerate(shot_label.segments):
            start_time = (shot.segment.start_time_offset.seconds +
                          shot.segment.start_time_offset.nanos / 1e9)
            end_time = (shot.segment.end_time_offset.seconds +
                        shot.segment.end_time_offset.nanos / 1e9)
            positions = '{}Picture number {}'.format('', int(round(end_time*FRAMERATE)))
            confidence = shot.confidence
            file.write('\tSegment {}: {}'.format(i+1, positions) + '\n')
            file.write('\tConfidence: {}'.format(confidence) + '\n')
        file.write('\n')
    file.close()
    print('Report generated\n')
    print('****************************************')
    
    # [END video_analyze_labels]
def clean_up():
    print("\nInitiating cleaning process")
    for file_name in os.listdir('.'):
        if 'twitter_image_' in file_name:
            os.remove(file_name)
    for file_name in os.listdir('.'):
        if file_name == 'tweet_image_list.txt':
            os.remove(file_name)
    print("Cleaning completed\n")
    print('****************************************')
    
if __name__ == '__main__':
    number_of_tweets = input('Please enter the number of tweets you wish to scan (max = 200).')
    get_all_tweets("@KimKardashian", number_of_tweets)
    video_name = generate_video('out', 1)    
    analyze_labels_file(video_name+'.mp4')
    clean_up()
    print('\nAll done!')
