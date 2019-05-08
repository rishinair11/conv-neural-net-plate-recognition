import os
import time
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import DetectChars
import DetectPlates
import PossiblePlate

# module level variables 
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

def main(image):
    global showSteps
    CnnClassifier = DetectChars.loadCNNClassifier()

    if CnnClassifier == False:
        print("\nerror: CNN training was not successful\n")
        return 

    #Convert from PIL format to OPENCV format 
    imgOriginalScene = cv2.imread(image)
        
    h, w = imgOriginalScene.shape[:2]
    # As the image may be blurr so   sharpen the image.
    #kernel_shapening4 = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
    #imgOriginalScene = cv2.filter2D(imgOriginalScene,-1,kernel_shapening4)
    
    #imgOriginalScene = cv2.resize(imgOriginalScene,(1000,600),interpolation = cv2.INTER_LINEAR)
    
    imgOriginalScene = cv2.resize(imgOriginalScene, (0, 0), fx = 1.4, fy = 1.4,interpolation=cv2.INTER_CUBIC)
    
    #imgOriginalScene = cv2.fastNlMeansDenoisingColored(imgOriginalScene,None,10,10,7,21)
    
    #imgOriginal = imgOriginalScene.copy()
    
    if imgOriginalScene is None:                            
        print("\nerror: image not read from file \n\n")      
        os.system("pause")                                  
        return                                              

    # detect plates, create list of combinations of contours that may be a plate.                                                                                
    listOfPossiblePlates = DetectChars.detectCharsInPlates(DetectPlates.detectPlatesInScene(imgOriginalScene))        # detect chars in plates
    if showSteps == True:
        Image.fromarray(imgOriginalScene,'RGB').show()
        

    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        print("\nno license plates were detected\n")             
        response = ' '
        return response,imgOriginalScene
    else:                                                       
        # atleast one plate found
        # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
        licPlate = listOfPossiblePlates[0]

        if showSteps == True:
            Image.fromarray(licPlate.imgPlate).show()

        if len(licPlate.strChars) == 0:                     
            print("\nno characters were detected\n\n")       
            return ' ',imgOriginalScene                                       

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)

        if showSteps == True:
            writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)           
            Image.fromarray(imgOriginalScene).show()                
            cv2.imwrite("imgOriginalScene.png", imgOriginalScene)           
            input('Press any key to continue...')                    

    return licPlate.strChars

def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect (minimum area)

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)

def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      
    fltFontScale = float(plateHeight) / 30.0                    
    intFontThickness = int(round(fltFontScale * 1.5))           

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        

    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         

    if intPlateCenterY < (sceneHeight * 0.75):                                                  
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      
    else:                                                                                       
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      

    textSizeWidth, textSizeHeight = textSize                

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          

    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
    print(licPlate.strChars)


if __name__ == "__main__":
    print(main('images/ZZX9483.jpg'))
    
    # i = 0
    # length = 0
    # score = 0
    # start = time.time()
    # result = []
    # count = 0
    # os.chdir('Test_dataset')
    # for f in os.listdir():
    #     y_test,ext = os.path.splitext(f)
    #     y_pred,_ = main(f)
    #     length = length + len(y_test)
    #     if len(y_test)<len(y_pred):
    #         y_test = y_test + ' '*(len(y_pred)-len(y_test))
    #         count = count + 1
    #     else:
    #         y_pred = y_pred + ' '*(len(y_test)-len(y_pred))
    #         count = count + 1
    #     y_test = np.array(list(str(y_test)))
    #     y_pred = np.array(list(str(y_pred)))
    #     print(y_test,' ',y_pred)
    #     score = score + (y_test == y_pred).sum()
    #     count = 0
    #     for t in y_pred:
    #         if t in y_test:
    #             score = score + 1
    #             count = count + 1
    #     accuracy = (score*100)/length
    #     new = 'Accuarcy at the '+str(i)+' th image '+f+ ' is :'+str(accuracy)
    #     print(new,'\n','The count is: ',count)
    #     result.append(result)
    #     i = i + 1
    # print('time taken :',time.time() - start)
    # print(result)