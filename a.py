import RPi.GPIO as GPIO
import moment,os,pygame
from picamera import PiCamera
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import texttospeech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'YOUR_GCLOUD_JSON_CREDENTIALS'
client = vision.ImageAnnotatorClient()
camera = PiCamera()
camera.resolution = (512,512)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(37,GPIO.IN)
GPIO.setup(35,GPIO.OUT) 
GPIO.setup(33,GPIO.OUT) 
GPIO.setup(31,GPIO.OUT) 
GPIO.setup(29,GPIO.OUT)
pygame.mixer.init()

print("Press Start button to read out the page")
flag=0
light_on=0
file_playing=0
def synthesize_text(text,audioname):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.types.SynthesisInput(text=text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(input_text, voice, audio_config)
    with open(audioname, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file {}'.format(audioname))
while True: 
    try:
        capture_button = GPIO.input(16)
        pause_button = GPIO.input(18)
        if capture_button == False:
            time.sleep(1)
            flag=0
            print('Capturing new image....')
            image_name = "Book-"+datetime.datetime.now().strftime("%H-%M-%S")+".jpg"
            camera.start_preview()
            time.sleep(2)
            camera.capture(image_name)
            print("Image clicked . . .")
            with open(image_name, 'rb') as image_file:
                content = image_file.read()
            print("Sending Image to OCR . . ")
            image = types.Image(content=content)
            response = client.document_text_detection(image=image)
            labels = response.full_text_annotation
            s=""
            for i in labels.text.split():
                s+=i+" "
                t=""
                for i in s.split():
                    temp=i[0].upper()
                    temp2=i[1:].lower()
                    t+=temp+temp2+" "
            
            print("\n"+t)
            t+=". ,End Of Page Mr. X"
            print("Converting your text to sound . . .")
            audioname="Book-"+datetime.datetime.now().strftime("%H-%M-%S")+".mp3"
            synthesize_text(t,audioname)
            print("Starting audio. . .")
            print("Press pause button to Pause/Resume")
            pygame.mixer.music.load(audioname)
            pygame.mixer.music.play()
            time.sleep(4)
            file_playing=1
        if (pause_button == False):
            time.sleep(1)
            if flag==0: 
                pygame.mixer.music.pause()
                flag=1
                print("Paused. . . ")
            elif flag==1:
                pygame.mixer.music.unpause()
                flag=0
                print("Resumed. . . ")
        if GPIO.input(37) != False  and light_on==0:
            time.sleep(0.2)
            GPIO.output(35,1)
            GPIO.output(33,1)
            GPIO.output(31,1)
            GPIO.output(29,1)
            light_on=1
        if GPIO.input(37) != True and light_on==1:
            time.sleep(0.2)
            GPIO.output(35,0)
            GPIO.output(33,0)
            GPIO.output(31,0)
            GPIO.output(29,0)
            light_on=0

    except Exception as e:
        print(e)
        GPIO.cleanup()
        break