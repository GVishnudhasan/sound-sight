import cv2
import numpy as np
import pyttsx3
import textgen

#textpart
img_size=None
engine=pyttsx3.init()

# cvpart
print("Loading YOLO ...")
net=cv2.dnn.readNet("yolov3.cfg","yolov3.weights")
#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
classes=[]
with open("coco.names", "r") as f:
    classes=[line.strip() for line in f.readlines()]
layer_names=net.getLayerNames()
output_layers=[layer_names[i-1] for i in net.getUnconnectedOutLayers()]      
print("YOLO loaded")

# object detection
def detect_objects(img_path, img_show=False, img_highlight=False):
    print("Detecting objects ...")
    objs=[]
    cv2.destroyAllWindows()

    img=cv2.imread(img_path)
    #img=cv2.resize(img,(500,500))
    height, width, channels = img.shape
    img_size=(width,height) #for text
    blob=cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outs=net.forward(output_layers)

    class_ids=[]
    confidences=[]
    boxes=[]
    for out in outs:
        for detection in out:
            scores=detection[5:]
            class_id=np.argmax(scores)
            confidence=scores[class_id]
            if confidence > 0.5:
                center_x=int(detection[0]*width)
                center_y=int(detection[1]*height)
                w=int(detection[2]*width)
                h=int(detection[3]*height)

                x=int(center_x - w /2)
                y=int(center_y - h /2)

                boxes.append([x,y,w,h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes=cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    colors=np.random.uniform(0,255,size=(len(classes),3))
    
    for i in range(len(boxes)):
        if i in indexes:
            x,y,w,h=boxes[i]
            label=str(classes[class_ids[i]])

            objs.append(dict(cls=label, x=x, y=y, w=w, h=h))

            # rectagle highlighting
            if img_highlight :
                color=colors[class_ids[i]]
                cv2.rectangle(img,(x,y),(x+w, y+h), color,2)
                cv2.putText(img, label, (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 1/2, color, 2)

    print("Object detection complete")
    if img_show :
        cv2.imshow("Image", img)
        cv2.waitKey(1000)
    
    return objs

while True :
    img_path=input("image :")
    if img_path=='' :
        break

    objs=detect_objects(img_path)
    gentext=textgen.getText(objs)    
    print("Generated Text :\n"+gentext+'\n')
    engine.say(gentext)
    engine.runAndWait()
