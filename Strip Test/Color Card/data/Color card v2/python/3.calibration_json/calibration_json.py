#################################################################################################
# This programme takes a single xrite file representing the measurements of a calibration card,
# and converts the lab values into json. It creates the 'calValues' property in json format
# The json can be inserted into the calibration file used by the caddisfly app.
#
# The programme looks for the first file in the /input folder.
# The output is written to the /output folder to the file json.txt
#
# The programme skips the item J2, as this is the patch where the Akvo logo is located.
#
# author: M.T. Westra
# date: 4-8-2016
# version: 1.0
#################################################################################################

import os
import sys

CURRPATH = os.path.dirname(os.path.abspath(__file__))
INPUTDIR = CURRPATH + '/input/'
OUTPUTDIR = CURRPATH + '/output/'

def findIndex(lines,strg):
    num = 0
    for line in lines:
        if strg in line:
            return num
        else:
            num = num + 1
    return -1

print "This programme turns a calibration card xrite measurement file with D65 illuminant"
print "into JSON format, which can be included in the calibration file."
print "!!IMPORTANT!!: the programme skips the element with key J2, as this is the location of the"
print "Akvo logo, and should therefore be exluded from the calibration. NOTE: not true anymore"

# empty output directory first
for the_file in os.listdir(OUTPUTDIR):
    print the_file
    file_path = os.path.join(OUTPUTDIR, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
            print "deleting file"
    except Exception as e:
        print(e)

# find first file in input directory. Skip DS_Store files
for inputFile in os.listdir(INPUTDIR):
    if 'DS_Store' in inputFile:
        continue
    break

if len(inputFile) == 0:
    print "no input file found"
    sys.exit(0)

try:
    f = open(INPUTDIR + inputFile, 'r')
except IOError:
    print("can't open file " + fileName)

lines = f.readlines()

# check if file starts with "CGATS.17"
if "CGATS.17" not in lines[0]:
    print("Expected file to start with CGATS.17. Halting")
    sys.exit(0)

# check if we used measurement condition M1
if "MeasurementCondition=M1" not in lines[5]:
    print("Expected file to have Measurement condition M1. Halting")
    sys.exit(0)

# check if we have D65 illumnation
if "ILLUMINATION_NAME\t\"D65\"" not in lines[6]:
    print("Expected file to have Illumination name D65. Halting")
    sys.exit(0)

# find the location of the Lab data
dataFormatIndex = findIndex(lines,"BEGIN_DATA_FORMAT") + 1
dataFormat = lines[dataFormatIndex].split()

try:
    X_index = dataFormat.index("X")
except ValueError:
    print "Lab data not found. Halting"
    sys.exit(0)

# Find beginning and end of data
try:
    dataStartIndex = findIndex(lines,"BEGIN_DATA\n")
    dataEndIndex = findIndex(lines,"END_DATA\n")
except ValueError:
    print "Data not found. Halting"
    sys.exit(0)

# create result file
fNew = "json.txt"
fo = open(OUTPUTDIR + fNew, 'w')

fo.write("\"calValues\":[")
for index in range(dataStartIndex + 1, dataEndIndex):
    row = lines[index].split()
    result = "{\"l\":\"" + row[1] + "\",\"X\":\"" + row[X_index] + "\",\"Y\":\"" + row[X_index + 1] + "\",\"Z\":\"" + row[X_index + 2] + "\"" + "}"
    if index == dataEndIndex - 1:
        fo.write(result + "\n")
    else:
        fo.write(result + ",\n")
fo.write("]")
fo.close()
