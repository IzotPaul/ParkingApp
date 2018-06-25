from __future__ import division
import pylab as pl
import numpy as np
import cv2

def captch_ex(file_name):
	img = cv2.imread(file_name)

	cv2.imwrite(file_name + "1.jpg", img)
	# Resize image to 800x600 grayscale
	img = cv2.resize(img, (800, 600))
	img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	cv2.imwrite(file_name + "2.jpg", img2gray)
	ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
	img_and = cv2.bitwise_and(img2gray, img2gray, mask=mask)
	ret, new_img = cv2.threshold(img_and, 180, 255, cv2.THRESH_BINARY)

	cv2.imwrite(file_name + "3.jpg", new_img)
	# Apply morphological tranformation - Dilate
	kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2)) 
	dilated = cv2.dilate(new_img, kernel, iterations=9) 

	cv2.imwrite(file_name + "4.jpg", dilated)

	_, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	images = [[0 for i in range(28 * 28)] for j in range(8)]
	for contour in contours:
		# Get rectangle bounding contour
		[x, y, width, height] = cv2.boundingRect(contour)

		# Ignore false positive that are either too big or too small to
		# contain a license plate, or the ratio is off
		ratio = width / height
		if ((width < 100 or width > 300) or
			(height < 30 or height > 100) or
			(ratio < 3 or ratio > 6)):
			continue

		# Crop license plate and resize
		cropped = img2gray[y : y +  height , x : x + width]
		cropped_res = cv2.resize(cropped, (224, 28))

		print (width, height, width/height)

		# Crop each letter from the license plate
		for i in range(8):
			crop_letter = cropped_res[0 : height , i * 28 : (i + 1) * 28]
			for xl in range(28):
				for yl in range(28):
					images[i][xl * 28 + yl] = crop_letter[xl][yl]

		s = "cropped/" + file_name
		cv2.imwrite(s , cropped_res)

		cv2.rectangle(img, (x, y), (x + width, y + height), (255, 0, 255), 2)

		# Stop at first matched rectangle
		break

	# Return the array of letters (as a vector each letter)
	return images

captch_ex("IMG_4.jpg")