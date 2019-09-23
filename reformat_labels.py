#! /usr/bin/env python
# coding=utf-8

import argparse
import logging
import os
import os.path
import xml.etree.ElementTree as et

from math import fabs


def initialize_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--images", help="Folder path of images", required=True)
    parser.add_argument("-l", "--labels", help="Folder path of labels / Or file path if only one file", required=True)
    parser.add_argument("-c", "--classes",
                        help="File containing classes (one class by line / must be the same class name that in label files)",
                        required=True)
    parser.add_argument("-o", "--output", help="File path for the result file", required=True)
    parser.add_argument("-xml", help="To specify if input labels are VOC XML format", action="store_true")
    parser.add_argument("--normalized", help="Normalized coordinates for output file", action="store_true")
    parser.add_argument("--centered", help="Centered coordinates, x_center, y_center, width, height for output file",
                        action="store_true")
    parser.add_argument("-csv", help="To specify if input labels are single CSV file format", action="store_true")
    parser.add_argument("-yolo", help="To specify if input labels are YOLO format")
    parser.add_argument("-vgg", help="To specify if input labels are VGG JSON format")
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


def initialize_transco_dictionary(classes_file_path):
    transco_dict = {}

    class_number = 0
    with open(classes_file_path, 'r') as file:
        for line in file:
            transco_dict[line.strip()] = class_number
            class_number += 1

    return transco_dict


def array_to_ouput_file(arguments, all_labels):
    transco_dict = initialize_transco_dictionary(arguments.classes)

    # Convert dict to file accepted by YOLO
    with open(arguments.output, 'w') as file:
        for one_file_labels in all_labels:
            # Image path
            file.write(one_file_labels['file'] + " ")

            # Loop over every object in the file and write xmin, xmax, ymin, ymax, classid
            for item in one_file_labels['objects']:
                if arguments.normalized and arguments.centered:
                    file.write(str(item['box']['center_x_n']) + ",")
                    file.write(str(item['box']['center_y_n']) + ",")
                    file.write(str(item['box']['width_n']) + ",")
                    file.write(str(item['box']['height_n']) + ",")
                    file.write(str(transco_dict[item['name']]) + " ")
                elif arguments.normalized:
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


def compute_normalized_centered(object_dictionary, width, height):
    object_dictionary['xmin_n'] = object_dictionary['xmin'] / width
    object_dictionary['ymin_n'] = object_dictionary['ymin'] / height
    object_dictionary['xmax_n'] = object_dictionary['xmax'] / width
    object_dictionary['ymax_n'] = object_dictionary['ymax'] / height

    object_dictionary['center_x'] = (object_dictionary['xmin'] + object_dictionary['xmax']) / 2
    object_dictionary['center_y'] = (object_dictionary['ymin'] + object_dictionary['ymax']) / 2
    object_dictionary['center_x_n'] = (object_dictionary['xmin_n'] + object_dictionary[
        'xmax_n']) / 2
    object_dictionary['center_y_n'] = (object_dictionary['ymin_n'] + object_dictionary[
        'ymax_n']) / 2

    object_dictionary['width'] = fabs(object_dictionary['xmax'] - object_dictionary['xmin'])
    object_dictionary['height'] = fabs(object_dictionary['ymax'] - object_dictionary['ymin'])
    object_dictionary['width_n'] = fabs(object_dictionary
                                        ['xmax_n'] - object_dictionary['xmin_n'])
    object_dictionary['height_n'] = fabs(object_dictionary['ymax_n'] - object_dictionary['ymin_n'])


def handle_csv_format(arguments):
    """
    Function that will handle a CSV file (label input)

    Input file CSV example:
    Label1,333,284,56,61,myimg.png,400,400
    Label1,234,263,66,41,myimg.png,400,400
    Label2,193,73,916,577,nuggets.png,1280,720
    Label3,412,337,663,324,Capture.PNG,1203,661

    :param arguments: arguments given in cmd line
    :return: a file written with labels in format for YOLOv3
    """

    logging.info("Handling CSV Format")

    all_labels = []

    if os.path.isfile(arguments.labels):
        with open(arguments.labels, 'r') as file:
            previous_file = None
            labels = {}
            for line in file:
                logging.debug("Handling {}".format(line))
                name, xmin, ymin, xmax, ymax, filename, width, height = line.strip().split(',')
                if filename.strip() == previous_file:
                    obj_dict = {'name': name, 'box': {'xmin': float(xmin), 'ymin': float(ymin), 'xmax': float(xmax),
                                                      'ymax': float(ymax)}}
                    compute_normalized_centered(obj_dict['box'], int(width), int(height))
                    labels['objects'].append(obj_dict)

                else:
                    if previous_file is not None:
                        all_labels.append(labels)

                    size_dict = {'width': int(width), 'height': int(height)}
                    labels = {'file': os.path.join(arguments.images, filename), 'size': size_dict, 'objects': []}

                    obj_dict = {'name': name, 'box': {'xmin': float(xmin), 'ymin': float(ymin), 'xmax': float(xmax),
                                                      'ymax': float(ymax)}}
                    compute_normalized_centered(obj_dict['box'], int(width), int(height))
                    labels['objects'].append(obj_dict)

                previous_file = filename.strip()

            # Don't forget to append the last image
            all_labels.append(labels)

    array_to_ouput_file(arguments, all_labels)


def handle_vgg_format():
    raise NotImplementedError("Function not implemented yet")


def handle_voc_format(arguments):
    logging.info("Handling VOC XML Format")

    all_labels = []

    for f in os.listdir(arguments.labels):
        if os.path.isfile(os.path.join(arguments.labels, f)):
            logging.debug("Handling {} file".format(os.path.join(arguments.labels, f)))

            tree = et.parse(os.path.join(arguments.labels, f))
            root = tree.getroot()

            size = root.find('size')
            size_dict = {}
            for size_item in size:
                size_dict[size_item.tag] = float(size_item.text)

            # Dictionary that will contain everything for this file
            labels = {'file': os.path.join(arguments.images, f.replace("xml", "jpg")), 'size': size_dict}
            logging.debug(
                "Retrieving size from the file. Width : {}, Height: {}, Depth: {}".format(labels['size']['width'],
                                                                                          labels['size']['height'],
                                                                                          labels['size']['depth']))

            labels['objects'] = []

            for obj in root.findall('object'):
                obj_dict = {}
                name = obj.find('name')
                obj_dict[name.tag] = name.text

                bbox = obj.find('bndbox')
                box = {}
                xmin = bbox.find('xmin')
                box[xmin.tag] = float(xmin.text)
                ymin = bbox.find('ymin')
                box[ymin.tag] = float(ymin.text)
                xmax = bbox.find('xmax')
                box[xmax.tag] = float(xmax.text)
                ymax = bbox.find('ymax')
                box[ymax.tag] = float(ymax.text)

                obj_dict['box'] = box

                compute_normalized_centered(obj_dict['box'], labels['size']['width'], labels['size']['height'])

                logging.debug(obj_dict)
                labels['objects'].append(obj_dict)

            all_labels.append(labels)

    array_to_ouput_file(arguments, all_labels)


def main():
    arguments = initialize_parser()
    initialize_logging(arguments.verbose)
    if arguments.xml:
        handle_voc_format(arguments)
    elif arguments.csv:
        handle_csv_format(arguments)


if __name__ == '__main__':
    main()
