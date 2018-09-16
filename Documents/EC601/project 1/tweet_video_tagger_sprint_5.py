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

    api = Twitter(
        auth = OAuth(
                    access_token_key,
                    access_token_secret,
                    consumer_key,
                    consumer_secret,))

    # Get an information list of most recent tweets (max = 200)
    
    new_tweets = api.statuses.user_timeline(screen_name = screen_name, count = 100)

    # Write tweet objects to txt file. Ref: The example script

    
    
    file_name = 'tweet_image_list.txt'
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
        urllib.urlretrieve(line, "twitter_image_"+str(file_count)+".jpg")
    
# Generate the video out of the images, return the name of the video
    
def generate_video(output_name, start_number = None, framerate = None):
    image_initial_name = "twitter_image_"
    if start_number == None:
        start_number = 1
    if framerate == None:
        framerate = 1/3
    # e.g. image_3.jpg image_initial_name = 'image_'
    # Run ffmpeg in Windows
    
    os.system('ffmpeg -framerate '+str(framerate)+' -i '+image_initial_name+'%d.jpg \
                -c:v libx264 -r 30 -s 800*600 -pix_fmt yuv420p '+output_name+'.mp4')

    # Terminate the program if there is no picture to convert
    if not os.path.isfile(output_name+'.mp4'):
        print("\n***No image is detected in the user's twitter***")
        print("\n***The video can not be created, terminating the program.***")
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
    result = operation.result(timeout=90)
    print('\nFinished processing.')

    # Process video/segment level label annotations

    segment_labels = result.annotation_results[0].segment_label_annotations    
    for i, segment_label in enumerate(segment_labels):
        print('Video label description: {}'.format(
            segment_label.entity.description))
        for category_entity in segment_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))
        for i, segment in enumerate(segment_label.segments):
            start_time = (segment.segment.start_time_offset.seconds +
                          segment.segment.start_time_offset.nanos / 1e9)
            end_time = (segment.segment.end_time_offset.seconds +
                        segment.segment.end_time_offset.nanos / 1e9)
            positions = '{}s to {}s'.format(start_time, end_time)
            confidence = segment.confidence
            print('\tSegment {}: {}'.format(i, positions))
            print('\tConfidence: {}'.format(confidence))
        print('\n')

    # Process shot level label annotations
    
    shot_labels = result.annotation_results[0].shot_label_annotations
    for i, shot_label in enumerate(shot_labels):
        print('Shot label description: {}'.format(
            shot_label.entity.description))
        for category_entity in shot_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))
        for i, shot in enumerate(shot_label.segments):
            start_time = (shot.segment.start_time_offset.seconds +
                          shot.segment.start_time_offset.nanos / 1e9)
            end_time = (shot.segment.end_time_offset.seconds +
                        shot.segment.end_time_offset.nanos / 1e9)
            positions = '{}s to {}s'.format(start_time, end_time)
            confidence = shot.confidence
            print('\tSegment {}: {}'.format(i, positions))
            print('\tConfidence: {}'.format(confidence))
        print('\n')

    # Process frame level label annotations

    frame_labels = result.annotation_results[0].frame_label_annotations
    for i, frame_label in enumerate(frame_labels):
        print('Frame label description: {}'.format(
            frame_label.entity.description))
        for category_entity in frame_label.category_entities:
            print('\tLabel category description: {}'.format(
                category_entity.description))

        # Each frame_label_annotation has many frames,
        # here we print information only about the first frame.
        
        frame = frame_label.frames[0]
        time_offset = frame.time_offset.seconds + frame.time_offset.nanos / 1e9
        print('\tFirst frame time offset: {}s'.format(time_offset))
        print('\tFirst frame confidence: {}'.format(frame.confidence))
        print('\n')

    # [END video_analyze_labels]
def clean_up():
    print("Initiating cleaning process\n")
    for file_name in os.listdir('.'):
        if 'twitter_image_' in file_name:
            os.remove(file_name)
            print(file_name + " removed")
    for file_name in os.listdir('.'):
        if file_name == 'tweet_image_list.txt':
            os.remove(file_name)
            print(file_name + " removed")
    
if __name__ == '__main__':
    get_all_tweets("@KimKardashian")
    video_name = generate_video('out', 1, 0.3)    
    analyze_labels_file(video_name+'.mp4')
    clean_up()
