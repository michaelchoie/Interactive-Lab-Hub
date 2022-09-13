import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789
from datetime import datetime, timedelta

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# NEW
# these setup the code for our buttons and the backlight and tell the pi to treat the GPIO pins as digitalIO vs analogIO
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


# NEW
# Graduation Date = May 20, 2023
graduationDate = datetime.strptime("06/20/2023", "%m/%d/%Y")
cornellTech = None

while not cornellTech:
    try:
        # Confirm if student is Cornellian!
        cornellTech = input("Hi, I am your personal accountability clock. You are a student at Cornell Tech? \n")
    except ValueError:
        print("whoops!")


# NEW
# Main Loop
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py 
    DATE = time.strftime("%m/%d/%Y")
    TIME = time.strftime("%H:%M:%S")

    if buttonA.value and buttonB.value: # none pressed
        y = top
        draw.text((x,y), DATE, font=font_large, fill="#FFFFFF")
        y += font_large.getsize(DATE)[1]
        draw.text((x,y), TIME, font=font_large, fill="#FFFFFF")
        y += font_large.getsize(TIME)[1]
        y += font.getsize(DATE)[1]
        draw.text((x,y), "A: Weekends Left!", font=font, fill="#FFFFFF")
        y += font.getsize(DATE)[1]
        draw.text((x,y), "B: Weekend Activity!", font=font, fill="#FFFFFF")
        y += font.getsize(TIME)[1]

    else:
        backlight.value = True  # turn on backlight

    if not buttonA.value and not buttonB.value:  # both pressed
        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        height = disp.width  # we swap height/width to rotate it to landscape!
        width = disp.height
        image = Image.new("RGB", (width, height))
        rotation = 90

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        disp.image(image, rotation)
        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        top = padding
        bottom = height - padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0

    if buttonB.value and not buttonA.value:  # just button A pressed
        disp.fill(color565(0, 255, 0))
        y = top
        draw.text((x,y), "You have...", font=font, fill="#FFFFFF")
        y += font.getsize("You have...")[1]

        remainingWeeks = round((graduationDate - datetime.strptime(DATE, "%m/%d/%Y")).total_seconds()/(60*60*24*7))
        draw.text((x,y),f"{remainingWeeks} Weeks", font=font_large, fill="#FFFFFF")
        y += font_large.getsize("50 Weeks")[1]

        #draw.text((x,y), DATE, font=font, fill="#FFFFFF")
        draw.text((x,y), "Until you graduate!", font=font, fill="#FFFFFF")
        y += font.getsize("Until you graduate!")[1]
        
        y += font.getsize("Until you graduate!")[1]
        draw.text((x,y), "Time to Party!", font=font_large, fill="#FFFFFF")
        y += font_large.getsize("Time to Party!")[1]


    if buttonA.value and not buttonB.value:  # just button B pressed
        image = Image.open("dancing.jpeg")
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width

        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))


    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)
