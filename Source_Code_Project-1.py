import cv2
import numpy as np
import pyttsx3
from collections import Counter
from module import findnameoflandmark, findpostion, speak
import time
#import os
import RPi.GPIO as GPIO
#import subprocess
import smbus2
import time
from RPLCD.i2c import CharLCD
# Initialize the text-to-speech engine with SAPI5 driver (default for Windows)
engine = pyttsx3.init(driverName='espeak') # Use SAPI5 for Windows
29
# Set properties to make sure the speech is clear and not too fast or slow
engine.setProperty('rate', 150) # Speed of speech
engine.setProperty('volume', 1) # Volume level (0.0 to 1.0)
# Initialize video capture
cap = cv2.VideoCapture(0)
tip = [4, 8, 12, 16, 20] # Indices for the tips of the fingers, including the thumb
tipname = ["Thumb", "Index finger", "Middle finger", "Ring finger", "Pinky finger"] #
Names for the finger tips
#//////////// camera /////////////
import smtplib
import warnings
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
warnings.filterwarnings("ignore")
sender_email = " "
receiver_emails = [""]
sender_password = ""
smtp_server = ""
smtp_port = 587
duration = 5
start_time = time.time()
#/////////// lcd /////////////
# Set up the I2C LCD
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)
#motor pins
Alert = 17
LED = 27
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
# Set up GPIO pins for motor control
30
GPIO.setup(Alert,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string(f"Hand")
lcd.cursor_pos = (1, 0)
lcd.write_string(f"Gesture")
time.sleep(2)
# Function to determine which message to speak based on finger positions
def determine_message(finger_states):
messages = {
(1, 1, 0, 0, 0): "Take me to the washroom",
(1, 1, 1, 0, 0): "I need to listen to music",
(1, 1, 1, 1, 0): "I need medicine",
(1, 1, 1, 1, 1): "I need to go out",
(0, 0, 0, 0, 0): "Take me to the bath",
(1, 0, 0, 0, 0): "I need food",
(0, 1, 0, 0, 0): "I need water",
(0, 0, 1, 0, 0): "I need a doctor",
(0, 0, 0, 1, 0): "I need juice",
(0, 0, 0, 0, 1): "I need fresh air",
}
# Return the corresponding message for the finger states
return messages.get(tuple(finger_states), "Gesture not recognized")
frame_count = 0 # To control how often the gesture is processed
last_message = "" # Keep track of the last message spoken
def capture_photo():
#cap.release()
#time.sleep(2)
#camera = cv2.VideoCapture(0) # Adjust the index if you have multiple cameras
if not cap.isOpened():
31
print("Error: Unable to open camera.")
return
return_value, image = cap.read()
if not return_value:
print("Error: Failed to capture image.")
#cap.release()
return
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"photo_{timestamp}.jpg"
cv2.imwrite(filename, image)
#cap.release()
return filename
defsend_mail(subject, attachment=None):
print("Sending mail")
time.sleep(2)
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = ", ".join(receiver_emails)
msg['Subject'] = "-= Alert =-"
# Add a text description with a map link
body_text = f"thieft detected at {datetime.now().strftime('%Y-%m-%d
%H:%M:%S')}.\n\nPlease find attached photo."
msg.attach(MIMEText(body_text, 'plain'))
if attachment:
with open(attachment, 'rb') as fp:
img_data = MIMEImage(fp.read())
msg.attach(img_data)
# Establish a connection to the SMTP server
with smtplib.SMTP(smtp_server, smtp_port) as server:
server.starttls()
server.login(sender_email, sender_password)
server.sendmail(sender_email, receiver_emails, msg.as_string())
32
print("Mailsent")
time.sleep(2)
'''
while True:
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
# Check if frame is valid
if not ret:
print("Failed to capture frame. Skipping iteration.")
continue
'''
# Example of running the main program
while True:
ret, frame = cap.read()
frame1 = cv2.resize(frame, (640, 480))
frame_count += 1
if frame_count % 5 == 0: # Skip frames to process only every 5th frame
# Find positions and names of landmarks
a = findpostion(frame1)
b = findnameoflandmark(frame1)
if len(b) != 0 and len(a) != 0:
finger_states = []
# Check each finger (thumb and others)
for id in range(5):
if id == 0: # Thumb check (reverse the logic)
finger_up = a[4][1] > a[3][1] # Reverse the condition for thumb
else: # Other fingers check
finger_up = a[tip[id]][2] < a[tip[id] - 2][2]
finger_states.append(1 if finger_up else 0)
# Print the finger states for debugging
#for id, state in enumerate(finger_states):
#print(f"{tipname[id]}: {'up' if state else 'down'}")
33
# Determine the message based on finger states
message = determine_message(finger_states)
# Print the matched message
print(f"Message: {message}")
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string(f"{message}")
if message != last_message: # Avoid repeating the same message
print(message)
engine.say(message) # Speak the message
engine.runAndWait() # Wait for the speech to finish
last_message = message # Update last spoken message
# Count up and down fingers
c = Counter(finger_states)
up = c[1]
down = c[0]
print(f"Up: {up}, Down: {down}") #to remove printing up and down
cv2.imshow("Frame", frame1)
key = cv2.waitKey(1) & 0xFF
if GPIO.input(Alert) == GPIO.LOW:
engine = pyttsx3.init(driverName='espeak')
engine.setProperty('rate', 150) # Speed of speech
engine.setProperty('volume', 1) # Volume level (0.0 to 1.0)
message = "Help Im in Danger"
print(f"Message: {message}")
engine.say(message)
engine.runAndWait()
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string(f"Capturing photo..")
lcd.cursor_pos = (1, 0)
#lcd.write_string(f"{message}")
34
lcd.write_string(f"Danger")
GPIO.output(LED, GPIO.HIGH)
print("Capturing photo...")
photo_filename = capture_photo() # Capture photo
send_mail("Emergency alert", photo_filename) # Send email with photo attachment
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string(f"sent photo...")
GPIO.output(LED, GPIO.LOW)
if key == ord("q"):
speak(f"Sir, you have {up} fingers up and {down} fingers down")
if key == ord("s"):
break
cap.release()
cv2.destroyAllWindows()
