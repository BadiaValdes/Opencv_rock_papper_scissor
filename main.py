
import cv2
import numpy as np
import copy

import math
import os



def calculateFingers(res, drawing):
    #  convexity defect
    hull = cv2.convexHull(res, returnPoints=False)
    points = []
    if len(hull) > 3:
        cnt = 0
        try:
            defects = cv2.convexityDefects(res, hull)

            if defects is not None:

                for i in range(defects.shape[0]):  # calculate the angle
                    s, e, f, d = defects[i][0]
                    start = tuple(res[s][0])
                    end = tuple(res[e][0])
                    far = tuple(res[f][0])
                    points.append(end)
                    a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # cosine theorem
                    s = (a + b + c) / 2
                    ar = np.sqrt(s * (s - a) * (s - b) * (s - c))
                    d = (2 * ar) / a
                    # print(angle)
                    if angle <= np.pi / 2 and d > 40:  # angle less than 90 degree, treat as fingers
                        cnt += 1

                        cv2.circle(drawing, far, 8, [211, 84, 0], -1)
                if cnt > 0:
                    return True, cnt + 1
                else:
                    return True, 0
        except:
            pass

    # filtered = filter_points(points, 90)
    # filtered.sort(key=lambda point: point[1])
    # return [pt for idx, pt in zip(range(5), filtered)]
    return False, 0

def choice(choi):
    final_choice = ""
    if choi == 0:
        final_choice = 'piedra'
    elif choi >= 1:
        final_choice = 'tijera' if choi == 1 else 'papel'
    return final_choice

def game(human_choice, pc_choice):
    estado = ''
    if(human_choice == pc_choice):
        estado = 'Empate'
        os.system('spd-say -l es -t female2 -i 10 "Empate"')
    elif (human_choice == 0 and pc_choice == 1) or (human_choice == 1 and pc_choice == 2) or (human_choice == 2 and pc_choice ==0):
        os.system('spd-say -l es -t female2 -i 10 "Ganaste"')
        estado = 'Ganaste'
    else:
        estado = 'Perdiste'
        os.system('spd-say -l es -t female2 -i 10 "Perdiste"')
    return estado
# Open Camera
choi = None
count = 0
# jugar = False
human_choice = 0
camera = cv2.VideoCapture(0)
#camera.set(10, 200)  # while True:
while camera.isOpened():
    # Main Camera
    ret, frame = camera.read()
    # frame = cv2.bilateralFilter(frame, 5, 50, 100)  # Smoothing
    frame = cv2.flip(frame, 1)  # Horizontal Flip

    ROI = frame[50:300, 380:600]
    cv2.rectangle(frame, (380 - 2, 50 - 2), (600 + 2, 300 + 2), (0, 0, 255), 1)
    cv2.rectangle(frame, (380 + 30, 50 + 30), (600 - 30, 300 - 30), (255, 0, 0), 2)
    #cv2.putText(frame, '{}'.format("Hola"), (50, 50), 1, 3, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, 'Coloque mano  {}'.format(chr(94)), (380, 330), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, 'q -> jugar ', (380, 360), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, 'esc -> salir ', (380, 390), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)

    # Background Removal
    # bgModel = cv2.createBackgroundSubtractorMOG2(0, 100, None)
    # fgmask = bgModel.apply(frame)
    # kernel = np.ones((2, 2), np.uint8)
    # fgmask = cv2.erode(fgmask, kernel, iterations=3)
    # fgmask = cv2.dilate(fgmask, kernel, iterations=3)
    # img = cv2.bitwise_and(frame, frame, mask=fgmask)

    # Skin detect and thresholding
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(ROI, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 220], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")
    # lower = np.array([0, 10, 220], dtype="uint8")
    # upper = np.array([20, 255, 255], dtype="uint8")
    # lower = np.array([0, 45, 170], dtype="uint8")
    # upper = np.array([20, 255, 255], dtype="uint8")
    skinMask = cv2.inRange(hsv, lower, upper)
    blurOne = cv2.blur(skinMask, (5, 5))

    _, tresh = cv2.threshold(blurOne, 120, 255, cv2.THRESH_TRIANGLE)
    # THRESH_OTSU
    cv2.imshow('Threshold Hands', tresh)  # Getting the contours and convex hull
    skinMask1 = copy.deepcopy(tresh)
    contours, hierarchy = cv2.findContours(tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    length = len(contours)
    maxArea = 0
    if length > 0:
        # for i in range(length):
        #     temp = contours[i]
        #     area = cv2.contourArea(temp)
        #     if area > maxArea:
        #         maxArea = area
        #         ci = i
        #         res = contours[ci]
        res = max(contours, key=lambda x: cv2.contourArea(x))
        hull = cv2.convexHull(res)
        drawing = np.zeros(frame.shape, np.uint8)
        cv2.drawContours(drawing, [res], 0, (0, 255, 0), 2)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 3)
        _, fingertips = calculateFingers(res, drawing)
        # for fingertip in fingertips:
        # cv2.circle(drawing, fingertip, 5, (0, 255, 255), 9)
        cv2.imshow('output', drawing)
        #print(np.random.choice(3, 1))


        if choi is not None:
            cv2.putText(frame, 'VS {}'.format(choi), (460, 420), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, '{}'.format(estado), (440, 450), 1, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        if (fingertips == 0 or fingertips == 1):
            #print('Piedra')
            human_choice = 0
            # os.system('spd-say -l es -t female2 -i 10 "piedra"')
            cv2.putText(frame, '{}'.format('piedra'), (380, 420), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
        elif (fingertips == 2):
            human_choice = 1
            # os.system('spd-say -l es -t female2 -i 10 "tijera"')
            cv2.putText(frame, '{}'.format('tijera'), (380, 420), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
            #print('Tijera')
        elif (fingertips == 5):
            # os.system('spd-say -l es -t female2 -i 10 "papel"')
            cv2.putText(frame, '{}'.format('papel'), (380, 420), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
            human_choice = 2
        # else:
        #     choi = None
        #     cv2.putText(frame, 'Bad read ', (380, 420), 1, 1.5, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('original', frame)
        k = cv2.waitKey(20)
        if k == ord('q'):
            pc_choice = np.random.choice(3, 1)
            choi = choice(pc_choice[0])
            estado = game(human_choice, pc_choice[0])
            jugar = True




        if k == 27:  # press ESC to exit
            break
cv2.destroyAllWindows()
  
