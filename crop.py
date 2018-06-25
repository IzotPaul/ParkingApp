import numpy as np
import cv2

def crop_plate_letters(file_name):
	img = cv2.imread(file_name)

	# Resize image to 800x600 grayscale
	img = cv2.resize(img, (800, 600))
	img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
	img_and = cv2.bitwise_and(img2gray, img2gray, mask=mask)
	ret, new_img = cv2.threshold(img_and, 180, 255, cv2.THRESH_BINARY)

	# Modify the orientation of dilution
	kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 1)) 
	# Apply morphological tranformation - Dilate
	dilated = cv2.dilate(new_img, kernel, iterations=9) 

	_, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

	letters = [[0 for i in range(28 * 28)] for j in range(8)]
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

		# Crop each letter from the license plate
		for i in range(8):
			crop_letter = cropped_res[0 : height , i * 28 : (i + 1) * 28]
			for xl in range(28):
				for yl in range(28):
					letters[i][xl * 28 + yl] = crop_letter[xl][yl]

		# Stop at first matched rectangle
		break

	# Return the array of letters (as a vector each letter)
	return letters


def labels_to_letters(labels):
	result = ""

	for label in labels:
		if (label < 10):
			result += str(label)
		elif (label == 61):
			result += "-"
		else:
			result += chr(label + 55)

	return result