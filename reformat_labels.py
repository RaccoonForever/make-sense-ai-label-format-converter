#! /usr/bin/env python
# coding=utf-8

import argparse
import logging
import os
import os.path
import xml.etree.ElementTree as ET 

def initialize_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--images", help="Folder path of images", required=True)
	parser.add_argument("-l", "--labels", help="Folder path of labels", required=True)
	parser.add_argument("-c", "--classes", help="File containing classes (one class by line)", required=True)
	parser.add_argument("-o", "--output", help="File path or name for the result", required=True)
	parser.add_argument("-xml", help="To specify if input labels are xml format", action="store_true")
	parser.add_argument("--normalize", help="Normalized coordinates", action="store_true")
	parser.add_argument("--centered", help="Centered coordinates, x_center, y_center, width, height")
	parser.add_argument("-csv", help="To specify if input labels are csv format", action="store_true")
	parser.add_argument("-v", "--verbose", help="To specify if you want more verbosity on logs", action="store_true")
	args = parser.parse_args()

	return args

def initialize_logging(verbosity):
	if verbosity:
		logging.basicConfig(level=logging.DEBUG)
		logging.info("Logging set to DEBUG")
	else:
		logging.basicConfig(level=logging.INFO)
		logging.info("Logging set to INFO")

def initialize_transco_dictionnary(classes_file_path):
	transco_dict = {}

	class_number = 0
	with open(classes_file_path, 'r') as file:
		for line in file:
			transco_dict[line.strip()] = class_number
			class_number += 1

	return transco_dict

def handle_csv_format(arguments):
	raise NotImplementedError("Function not implemented yet")

def handle_vgg_format(arguments):
	raise NotImplementedError("Function not implemented yet")

def handle_voc_format(arguments):
	logging.info("Handling XML Format")

	transco_dict = initialize_transco_dictionnary(arguments.classes)
	all_labels = []

	for f in os.listdir(arguments.labels):
		if os.path.isfile(os.path.join(arguments.labels, f)):
			logging.debug("Handling {} file".format(os.path.join(arguments.labels, f)))

			tree = ET.parse(os.path.join(arguments.labels, f))
			root = tree.getroot()

			size = root.find('size')
			size_dict = {}
			for size_item in size:
				size_dict[size_item.tag] = size_item.text

			# Dictionnary that will contain everything for this file
			labels = {}
			labels['file'] = os.path.join(arguments.images, f.replace("xml", "jpg"))
			labels['size'] = size_dict
			logging.debug("Retrieving size from the file. Width : {}, Height: {}, Depth: {}".format(labels['size']['width'], labels['size']['height'], labels['size']['depth']))

			labels['objects'] = []

			for obj in root.findall('object'):
				obj_dict = {}
				name = obj.find('name')
				obj_dict[name.tag] = name.text

				bbox = obj.find('bndbox')
				box = {}
				xmin = bbox.find('xmin')
				box[xmin.tag] = float(xmin.text)
				box[xmin.tag + "_n"] = float(int(xmin.text)/int(labels['size']['width']))
				ymin = bbox.find('ymin')
				box[ymin.tag] = float(ymin.text)
				box[ymin.tag + "_n"] = float(int(ymin.text)/int(labels['size']['height']))
				xmax = bbox.find('xmax')
				box[xmax.tag] = float(xmax.text)
				box[xmax.tag + "_n"] = float(int(xmax.text)/int(labels['size']['width']))
				ymax = bbox.find('ymax')
				box[ymax.tag] = float(ymax.text)
				box[ymax.tag + "_n"] = float(int(ymax.text)/int(labels['size']['height']))

				# Compute center
				box['center_x_n'] = (box[xmin.tag+"_n"] + box[xmax.tag+"_n"])/2.0
				box['center_y_n'] = (box[ymin.tag+"_n"] + box[ymax.tag+"_n"])/2.0
				box['width_n'] = box[xmax.tag+"_n"] - box[xmin.tag+"_n"]
				box['height_n'] = box[ymax.tag+"_n"] - box[ymin.tag+"_n"]

				box['center_x'] = (box[xmin.tag] + box[xmax.tag])/2.0
				box['center_y'] = (box[ymin.tag] + box[ymax.tag])/2.0
				box['width'] = box[xmax.tag] - box[xmin.tag]
				box['height'] = box[ymax.tag] - box[ymin.tag]

				obj_dict['box'] = box

				logging.debug(obj_dict)
				labels['objects'].append(obj_dict)

			all_labels.append(labels)

	# Convert dict to file accepted by YOLO

	with open(arguments.output, 'w') as file:
		for one_file_labels in all_labels:
			# Image path
			file.write(one_file_labels['file'] + " ")

			# Loop over every object in the file and write xmin, xmax, ymin, ymax, classid
			for item in one_file_labels['objects']:
				if arguments.normalize and arguments.centered:
					file.write(str(item['box']['center_x_n']) + ",")
					file.write(str(item['box']['center_y_n']) + ",")
					file.write(str(item['box']['width_n']) + ",")
					file.write(str(item['box']['height_n']) + ",")
					file.write(str(transco_dict[item['name']]) + " ")
				elif arguments.normalize:
					file.write(str(item['box']['xmin_n']) + ",")
					file.write(str(item['box']['ymin_n']) + ",")
					file.write(str(item['box']['xmax_n']) + ",")
					file.write(str(item['box']['ymax_n']) + ",")
					file.write(str(transco_dict[item['name']]) + " ")
				elif arguments.centered:
					file.write(str(int(item['box']['center_x'])) + ",")
					file.write(str(int(item['box']['center_y'])) + ",")
					file.write(str(int(item['box']['width'])) + ",")
					file.write(str(int(item['box']['height'])) + ",")
					file.write(str(transco_dict[item['name']]) + " ")
				else:
					file.write(str(int(item['box']['xmin'])) + ",")
					file.write(str(int(item['box']['ymin'])) + ",")
					file.write(str(int(item['box']['xmax'])) + ",")
					file.write(str(int(item['box']['ymax'])) + ",")
					file.write(str(transco_dict[item['name']]) + " ")

			file.write('\n')
			 

def main():
	arguments = initialize_parser()
	initialize_logging(arguments.verbose)
	if arguments.xml:
		handle_xml_format(arguments)
	elif arguments.csv:
		handle_csv_format(arguments)

if __name__ == '__main__':
	main()