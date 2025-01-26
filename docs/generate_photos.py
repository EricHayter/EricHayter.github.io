import os
from datetime import datetime

def get_image_date(image_path):
    # Get the file's creation time (or modification time if not available)
    timestamp = os.path.getmtime(image_path)
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

def generate_html_for_images(directory):
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Scan the directory for image files
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Check if the file is an image based on the extension
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
            # Get the image date
            image_date = get_image_date(file_path)
            
            # Print out the HTML block in one line
            print(f'<figure><img src="content/{filename}" id="photo"><figcaption>[{image_date}].</figcaption></figure>')

# Example usage
directory = 'content/trip-photos/'  # Replace with your directory path
generate_html_for_images(directory)

