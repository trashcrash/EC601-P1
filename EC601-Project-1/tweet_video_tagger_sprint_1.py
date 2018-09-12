''' This program downloads images from a user in twitter,
    converts the images to a video, then uses google video
    intelligence to create a name tag list of the segments
    in the video

'''

# Find image URLs from twitter and make a list of them, save in a txt file,
# then download them which are named as image_NUMBER
        
def get_all_tweets(screen_name):

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
