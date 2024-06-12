import os
import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables from .env file
load_dotenv(dotenv_path='..\\Data\\.env')

# Get the WolframAlpha AppID from the environment variables
WOLFRAM_APPID = os.getenv('WOLFRAM_APPID')

def generate_image(query, output_file='output.png', crop_box=None):
    """
    Generates an image from WolframAlpha based on the query, optionally crops it, and saves it to the specified file.

    :param query: The query string for WolframAlpha.
    :param output_file: The file path where the output image will be saved.
    :param crop_box: A tuple (left, upper, right, lower) defining the box to crop the image.
    """
    # Construct the API URL
    base_url = "http://api.wolframalpha.com/v1/simple"
    params = {
        'appid': WOLFRAM_APPID,
        'i': query
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        # Open the image using PIL
        image = Image.open(BytesIO(response.content))
        
        if crop_box:
            # Crop the image using the provided crop box
            cropped_image = image.crop(crop_box)
        else:
            cropped_image = image
        
        # Save the cropped image
        cropped_image.save(output_file)
        print(f"Image saved as {output_file}")
        
        # Display the image
        cropped_image.show()
    else:
        print("Failed to get image from WolframAlpha API")

if __name__ == "__main__":
    query = input("Enter the query for WolframAlpha: ")
    # Example crop box (left, upper, right, lower)
    crop_box = (50, 50, 400, 400)  # Adjust these values based on your specific needs
    generate_image(query, crop_box=crop_box)




