import cv2
from PIL import Image
from keras.preprocessing import image as image_utils
import numpy as np

class ImageProcessor:
    def __init__(self, xml):
        self.FACE_CASCADE = cv2.CascadeClassifier(xml)


    def get_bounds(self, path):
        """Returns the coordinates of the face"""
        gray = self.fetch_gray(path)
        faces = self.FACE_CASCADE.detectMultiScale(gray, 1.3, 6)
        x = 6
        while len(faces) == 0 and x > 0:
            x -= 1
            faces = self.FACE_CASCADE.detectMultiScale(gray, 1.3, x)
        if len(faces) < 1:
            return None
        face = faces[0]
        crop = [face[0], face[1], face[0] + face[2], face[1] + face[3]]
        return crop


    def fetch_gray(self, path):
        """Get the image in greyscale for CV2"""
        cv_img = cv2.imread(path)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        return gray


    def get_image(self, path):
        img = Image.open(path)
        return img


    def crop_face(self, img, path, padding=0):
        """Crop the image with an optional padding"""
        crop = self.get_bounds(path)
        if not crop:
            return None
        crop[0] += padding
        crop[1] += padding
        crop[2] -= padding
        crop[3] -= padding
        return img.crop(crop)

    def get_color(self, img, bound=25):
        color = img.crop((0, 0, bound, bound))
        color_arr = image_utils.img_to_array(color)
        color_mean = np.mean(color_arr.reshape(3, bound*bound), axis=1)
        color_mean *= 1/255
        return color_mean
	
    def img_to_arr(self, img, resize=True):
        if resize:
            img = img.resize((299, 299))
        img_arr = image_utils.img_to_array(img)
        img_arr[:, :, :] *= 1/255
        return img_arr
		
