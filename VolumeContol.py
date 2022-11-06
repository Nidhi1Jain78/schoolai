#importing all the data

import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller
import pyautogui
#golobal variables
mp_draw = mp.solutions.drawing_utils
keyboard = Controller()
cap = cv2.VideoCapture(0)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)
tipIds = [4, 8, 12, 16, 20]

# Define a function to count fingers
def countFingers(image, hand_landmarks, handNo=0):
    if hand_landmarks:
        # Get all Landmarks of the FIRST Hand VISIBLE
        landmarks = hand_landmarks[handNo].landmark
        # Count Fingers        
        fingers = []
        for lm_index in tipIds:
                # Get Finger Tip and Bottom y Position Value
                finger_tip_y = landmarks[lm_index].y 
                finger_bottom_y = landmarks[lm_index - 2].y

                # Check if ANY FINGER is OPEN or CLOSED
                if lm_index !=4:
                    if finger_tip_y < finger_bottom_y:
                        fingers.append(1)
                        # print("FINGER with id ",lm_index," is Open")

                    if finger_tip_y > finger_bottom_y:
                        fingers.append(0)
                        # print("FINGER with id ",lm_index," is Closed")

        totalFingers = fingers.count(1)
        # PLAY or PAUSE a Video
        if totalFingers == 4:
            state = "Play"

        if totalFingers == 0 and state == "Play":
            state = "Pause"
            keyboard.press(Key.space)

        finger_tip_y = (landmarks[8].y)*height
        if totalFingers==2:
            if finger_tip_y>height-250:
                print("decrease volume")
                pyautogui.press("volumedown")
            if finger_tip_y<height-250:
                print("increase volume")
                pyautogui.press("volumeup")

        # Move Video FORWARD & BACKWARDS    
        finger_tip_x = (landmarks[8].x)*width        
        if totalFingers==1:
            if finger_tip_x<width-400:
                print("play backwards")
                keyboard.press(Key.left)
            if finger_tip_x>width-50:
                print("play forward")
                keyboard.press(Key.right)
        
# Define a function to 
def drawHandLanmarks(image, hand_landmarks):
    # Darw connections between landmark points
    if hand_landmarks:

      for landmarks in hand_landmarks:
               
        mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

while True:
    success, image = cap.read()

    image = cv2.flip(image, 1)
    
    # Detect the Hands Landmarks 
    results = hands.process(image)

    # Get landmark position from the processed result
    hand_landmarks = results.multi_hand_landmarks

    # Draw Landmarks
    drawHandLanmarks(image, hand_landmarks)

    # Get Hand Fingers Position        
    countFingers(image, hand_landmarks)

    cv2.imshow("Media Controller", image)

    # Quit the window on pressing Sapcebar key
    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
# for dislike and like
finger_tips =[8, 12, 16, 20]
thumb_tip= 4
while True:
    ret,img = cap.read()
    img = cv2.flip(img, 1)
    h,w,c = img.shape
    results = hands.process(img)
    if results.multi_hand_landmarks:
        for hand_landmark in results.multi_hand_landmarks:
            #accessing the landmarks by their position
            lm_list=[]
            for id ,lm in enumerate(hand_landmark.landmark):
                lm_list.append(lm)

            #array to hold true or false if finger is folded    
            finger_fold_status =[]
            for tip in finger_tips:
                #getting the landmark tip position and drawing blue circle
                x,y = int(lm_list[tip].x*w), int(lm_list[tip].y*h)
                cv2.circle(img, (x,y), 15, (255, 0, 0), cv2.FILLED)

                #writing condition to check if finger is folded i.e checking if finger tip starting value is smaller than finger starting position which is inner landmark. for index finger    
                #if finger folded changing color to green
                if lm_list[tip].x < lm_list[tip - 3].x:
                    cv2.circle(img, (x,y), 15, (0, 255, 0), cv2.FILLED)
                    finger_fold_status.append(True)
                else:
                    finger_fold_status.append(False)

            print(finger_fold_status)

             #checking if all fingers are folded
            if all(finger_fold_status):
                #checking if the thumb is up
                if lm_list[thumb_tip].y < lm_list[thumb_tip-1].y < lm_list[thumb_tip-2].y:
                    print("LIKE")  
                    cv2.putText(img ,"LIKE", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

                #check if thumb is down
                if lm_list[thumb_tip].y > lm_list[thumb_tip-1].y > lm_list[thumb_tip-2].y:
                    print("DISLIKE")   
                    cv2.putText(img ,"DISLIKE", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            mp_draw.draw_landmarks(img, hand_landmark,
            mp_hands.HAND_CONNECTIONS, mp_draw.DrawingSpec((0,0,255),2,2),
            mp_draw.DrawingSpec((0,255,0),4,2))
    

    cv2.imshow("hand tracking", img)
    cv2.waitKey(1)
