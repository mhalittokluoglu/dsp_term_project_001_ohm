import face_recognition
import numpy as np
image0 = face_recognition.load_image_file('./Known_Images/Image_1.jpg')
image_encoding0 = face_recognition.face_encodings(image0)[0]

image1 = face_recognition.load_image_file('./Known_Images/Image_2.jpg')
image_encoding1 = face_recognition.face_encodings(image1)[0]

image2 = face_recognition.load_image_file('./Known_Images/Image_3.jpg')
image_encoding2 = face_recognition.face_encodings(image2)[0]

image3 = face_recognition.load_image_file('./Known_Images/Image_4.jpg')
image_encoding3 = face_recognition.face_encodings(image3)[0]


encodings = np.append(image_encoding0,image_encoding1)
encodings = np.append(encodings,image_encoding2)


image_names = ['Person1','Person2','Person3', 'Person4']
