# make-sense-ai-label-format-conver

This script is to be used to convert MakeSense export formats to YoloV3 input.

Input XML example :

    <annotation>
		<folder>my-project-name</folder>
		<filename>0.jpg</filename>
		<path>/my-project-name/0.jpg</path>
		<source>
			<database>Unspecified</database>
		</source>
		<size>
			<width>3456</width>
			<height>3456</height>
			<depth>3</depth>
		</size>
		<object>
			<name>Dog</name>
			<pose>Unspecified</pose>
			<truncated>Unspecified</truncated>
			<difficult>Unspecified</difficult>
			<bndbox>
				<xmin>157</xmin>
				<ymin>153</ymin>
				<xmax>358</xmax>
				<ymax>327</ymax>
			</bndbox>
		</object>
    </annotation>`

Output file wanted :

    /my-project-name/0.jpg 157,358,153,327,0

Of course, it is going to work for more than 1 class per file.

## How to use it ?

    usage: reformat_labels.py [-h] -i IMAGES -l LABELS -c CLASSES -o OUTPUT [-xml]
                              [--normalize] [--centered CENTERED] [-csv] [-v]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i IMAGES, --images IMAGES
                            Folder path of images
      -l LABELS, --labels LABELS
                            Folder path of labels / Or file path if only one file
      -c CLASSES, --classes CLASSES
                            File containing classes (one class by line / must be the same class name that in label files)
      -o OUTPUT, --output OUTPUT
                            File path for the output file
      -xml                  To specify if input labels are xml format
      --normalize           Normalized coordinates in output file
      --centered CENTERED   Centered coordinates, x_center, y_center, width,
                            height in output file
      -csv                  To specify if input labels are csv format
      -v, --verbose         To specify if you want more verbosity on logs

