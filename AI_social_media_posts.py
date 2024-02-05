# %%
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Loading API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initializing the language model
llm = ChatOpenAI(openai_api_key=api_key, max_tokens=100, temperature=0.8)

# %%
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a CPTSD Therapist with 20 plus years experience in healing people from CPTSD."),
    ("user", "{input}"),
    
])

chain = prompt | llm


# %%
from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()
chain = chain | output_parser


# %%
import pdfplumber

# Function to read and update the current page number
def get_and_update_current_page(file_path, increment=3):
    try:
        with open(file_path, 'r') as file:
            current_page = int(file.read().strip())
    except FileNotFoundError:
        current_page = 0  # Default starting page if file not found

    new_current_page = current_page + increment

    with open(file_path, 'w') as file:
        file.write(str(new_current_page))

    return current_page, new_current_page

# Function to extract text from a specific section of the PDF
def extract_section_from_pdf(pdf_path, start_page, end_page):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[start_page:end_page]
        for page in pages:
            text += page.extract_text() + "\n"
    return text

# File to store current page number
current_page_file = 'current_page.txt'

# Getting the current page and update it for the next run
start_page, next_start_page = get_and_update_current_page(current_page_file)

book= "CPTSD.pdf"

# Extracting text from a particular section
pdf_text = extract_section_from_pdf(book, start_page, next_start_page)

# Invoking the chain with our query
response = chain.invoke({"input": "write a 20 words inspirational quote for a person suffering from cptsd that would heal them, from the following text" + pdf_text})


# %%
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import OpenAI

# equating quote to the AI response
quote = response
print(quote)
llm = OpenAI(temperature=1.0)

# Defining the prompt template for creation of the prompt that would be inserted into DALLE
prompt_template = PromptTemplate(
    input_variables=["quote"],
    template="Create an inspiring, hopeful, and positive image for instagram without including any text in the image, also do not include any human beings, just make it therapeutic and full of nature image: {quote}",
)

max_length = 1000
max_retries = 3  # Setting the maximum number of retries to 3
attempt = 0

while attempt < max_retries: # This loop is to handle the error in case DALLE is fed a prompt that does not meet the guidelines
    try:
        
        chain = LLMChain(llm=llm, prompt=prompt_template)

        
        input_data = {"quote": quote}

        
        prompt = chain.run(input_data)
        print(prompt)

        if len(prompt) >= max_length:
            prompt = prompt[:max_length]

        print(len(prompt))
        
        # Generating image url from the prompt that was output of the prompt template and the LLM
        image_url = DallEAPIWrapper().run(prompt)
        print(image_url)
        print("passed in first attempt")
        break  # If success, break out of the loop
    except Exception as e:
        attempt += 1
        print(f"Attempt {attempt} failed with error: {e}")
        
        if attempt == max_retries:
            print("Max retries reached, failing gracefully.")


# %%
import requests
from PIL import Image
from io import BytesIO
from IPython.display import display
import datetime


response = requests.get(image_url)
image_data = BytesIO(response.content)
image = Image.open(image_data)

display(image)

# Generating a unique filename with the current date and time
current_time =  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"images/image_{current_time}.jpg"  # The file will be saved with a .jpg extension

# Saving the image in the current directory with the generated unique filename

image.save(filename)



# %%
from PIL import Image, ImageDraw, ImageFont
import textwrap

def draw_multiline_text_with_frosted_background(image, text, position, font, text_color, shadow_color, shadow_offset, line_spacing=1.2):
    draw = ImageDraw.Draw(image)
    lines = textwrap.wrap(text, width=40)

    x, y = position
    shadow_x, shadow_y = shadow_offset

    # Estimating the size of the frosted background
    # Assuming average character width is roughly equal to the font size (a rough estimation)
    average_char_width = font.size 
    max_text_width = max(len(line) for line in lines) * average_char_width
    line_height = int(font.size * line_spacing)
    total_text_height = len(lines) * line_height

    frosted_background_size = (max_text_width + 20, total_text_height + 10)  # Extra padding
    frosted_background_position = (x - 1, y - 1)

    # Creating frosted background (semi-transparent rectangle)
    frosted_background = Image.new("RGBA", frosted_background_size, (255, 255, 255, 100))
    image.paste(frosted_background, frosted_background_position, frosted_background)

    for line in lines:
       # Calculating x-coordinate to center the text within the frosted background
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_centered = x + (max_text_width - text_width) / 40

  
        draw.text((x_centered + shadow_x, y + shadow_y), line, font=font, fill=shadow_color)
        
        draw.text((x_centered, y), line, font=font, fill=text_color)
        y += line_height  # Increment y position by line height

# Loading the font
font_path = 'fonts/fonts/DejaVuSerif-Bold.ttf'
my_font = ImageFont.truetype(font_path, 40)

# Shadow settings
shadow_color = "white"
shadow_offset = (1, 1)


# Using the above defined function with frosted background
draw_multiline_text_with_frosted_background(image, quote, (25, 15), my_font, 'black', shadow_color, shadow_offset)

# Generating a unique filename with the current date and time
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")  
filename = f"images/image_{current_time}.jpg"  # The file will be saved with a .jpg extension

# Saving the image in the current directory with the generated filename
image.save(filename)

display(image)


# %%
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import NoCredentialsError

# Loading the .env variables
load_dotenv()

# AWS Credentials
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
bucket_name = os.getenv('BUCKET_NAME')

file_path = filename # Local file path
s3_file_path = filename # The path where the file will be saved in S3
print(filename)
region_name='eu-central-1' 

# Initializing S3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key,region_name=region_name)

try:
    # Uploading the file
    s3_client.upload_file(file_path, bucket_name, s3_file_path)
    print("Image successfully uploaded to S3")
except FileNotFoundError:
    print("The file was not found")
except NoCredentialsError:
    print("Credentials not available")

# Generating the URL of the uploaded file
# Initializing S3 resource with explicit credentials
s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key, region_name=region_name)

s3_object = s3_resource.Object(bucket_name, s3_file_path)
s3_url = s3_object.meta.client.generate_presigned_url('get_object',
                                                          Params={'Bucket': bucket_name, 'Key': s3_file_path},
                                                          ExpiresIn=10000)  # URL expires in ~ 2.5 hours
print("Image URL:", s3_url)


# %%
import requests

print(s3_url)

# Webhook 
webhook_url = os.getenv('WEBHOOK_URL')

payload = {
    'file_url': s3_url  
}

print(payload)
response = requests.post(webhook_url, json=payload)

print(response.text)


if response.status_code == 200:
    print("Webhook notified successfully.")
else:
    print(f"Failed to notify webhook. Status code: {response.status_code}")







