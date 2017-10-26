#################################################################################################
# This programme takes a set of files exported by xrite I photo pro software, and averages
# the data points
#
# The programme looks for files in the /input folder. It checks if is a valid M1 xrite file,
# and checks the illuminant is D65.
# The output is written to the /output folder with name 'average.txt'.
#
# author: M.T. Westra
# date: 3-8-2016
# version: 1.0
#################################################################################################
import os
import sys
import datetime

CURRPATH = os.path.dirname(os.path.abspath(__file__))
INPUTDIR = CURRPATH + '/input/'
OUTPUTDIR = CURRPATH + '/output/'

# function returns true if value 1 deviates from value 2 by a certain fraction.
# Also returns false if the value of value 1 and value 2 are both smaller than 1
def deviates(value1,value2,fraction):
    fracmore = 1 + fraction
    fracless = 1 - fraction
    if abs(value1) > abs(fracmore * value2) or abs(value1) < abs(fracless * value2):
        if abs(value1 - value2) > 1:
            return True
        else:
            return False
    else:
        return False


def median(lst):
    lst = sorted(lst)
    n = len(lst)
    if n < 1:
        return None
    if n % 2 == 1:
        return lst[n//2]
    else:
        return sum(lst[n // 2 - 1 : n//2 + 1]) / 2.0


def findIndex(lines,strg):
    num = 0
    for line in lines:
        if strg in line:
            return num
        else:
            num = num + 1
    return -1


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


# first, put all files in list, and read in all files
files = []
stop = False
for inputFile in os.listdir(INPUTDIR):
    if 'DS_Store' in inputFile:
        continue
    fileName = INPUTDIR + inputFile
    print "reading in file name: " + fileName

    try:
        f = open(INPUTDIR + inputFile, 'r')
    except IOError:
        print("can't open file " + fileName)
        sys.exit(0)

    files.append(f.readlines())
    f.close()

numFiles = len(files)


# check if all files are at D65
index = 0
numPatches = []
for fc in files:
    index += 1
    # check if file starts with "CGATS.17"
    if "CGATS.17" not in fc[0]:
        print("Expected file " + str(index) + " to start with CGATS.17. Halting execution")
        sys.exit(0)

    # check if we used measurement condition M1
    if "MeasurementCondition=M1" not in fc[5]:
        print("Expected file " + str(index) + " to have Measurement condition M1. Halting execution")
        sys.exit(0)

    # check if we have D65 illumnation
    if "ILLUMINATION_NAME\t\"D65\"" not in fc[6]:
        print("Expected file " + str(index) + " to have Illumination name D65. Halting execution")
        sys.exit(0)
    # line 20 contains the NUMBER_OF_SETS. Store these.
    numPatches.append(fc[20].split()[1])

# check if all number of patches are the same
numPatch = int(numPatches[0])
for i in range(1,len(numPatches)):
    if numPatch != int(numPatches[i]):
        print "Files have different number of patches, so cannot compute average. Halting execution"
        sys.exit(0)


# find the location of the Lab data
dataFormatIndex = findIndex(files[0],"BEGIN_DATA_FORMAT") + 1
dataFormat = files[0][dataFormatIndex].split()

try:
    X_index = dataFormat.index("X")
except ValueError:
    print "XYZ data not found. Halting"
    sys.exit(0)

# Find beginning and end of data
try:
    dataStartIndex = findIndex(files[0],"BEGIN_DATA\n")
    dataEndIndex = findIndex(files[0],"END_DATA\n")
    if (numPatch != (dataEndIndex - dataStartIndex - 1)):
        print "number of data points not corect"
        sys.exit(0)
except ValueError:
    print "Data not found. Halting"
    sys.exit(0)

data=[]
num = 0


# take row by row
for i in range(dataStartIndex + 1, dataEndIndex):

    Xvalues = []
    Yvalues = []
    Zvalues = []
    # iterate over files to get values for a specific row
    for j in range(0, numFiles):
        row = files[j][i].split()
        Xvalues.append(float(row[X_index]))
        Yvalues.append(float(row[X_index + 1]))
        Zvalues.append(float(row[X_index + 2]))

    Xmedian = median(Xvalues)
    Ymedian = median(Yvalues)
    Zmedian = median(Zvalues)

    dInd = i - dataStartIndex - 1
    # overwrite data in file structure[0]
    files[0][i] = str(row[0]) + "\t" + str(row[1]) + "\t" + "%.2f" % Xmedian + "\t" + "%.2f" % Ymedian + "\t" + "%.2f" % Zmedian + "\n"

# put first file in data structure. We apply the averaging factor straight away.
# for i in range(dataStartIndex + 1, dataEndIndex):
#     row = files[0][i].split()
#     print (row)
#     data.append([row[0],row[1],float(row[X_index]) / numFiles, float(row[X_index + 1]) / numFiles, float(row[X_index + 2]) / numFiles])

#
# # add rest of files
# for i in range(1,numFiles):
#     for ii in range(0,numPatch):
#         row = files[i][dataStartIndex + 1 + ii].split()
#         data[ii][2] += float(row[X_index]) / numFiles
#         data[ii][3] += float(row[X_index + 1]) / numFiles
#         data[ii][4] += float(row[X_index + 2]) / numFiles
#
# # check if we have any outliers, defined as values that differ more than 5% from the average.
# for i in range(0,numFiles):
#     for ii in range(0,numPatch):
#         row = files[i][dataStartIndex + 1 + ii].split()
#         if deviates(float(row[X_index]),data[ii][2],0.05) or deviates(float(row[X_index + 1]),data[ii][3],0.05) or deviates(float(row[X_index + 2]),data[ii][4],0.05):
#             print "One of the values deviates more than 5% from the average. Please check."
#             print "Values for which the absolute difference is less than 1 don't count."
#             print "file number: ",i, ", row number: ", ii
#             print "Average data: ",data[ii][2], data[ii][3], data[ii][4]
#             print "Data in file: ",float(row[X_index]), float(row[X_index + 1]), float(row[X_index + 2])
#             print "Percentage difference:", "%.2f" % (100 - 100 * data[ii][2]/float(row[X_index])), "%.2f" % (100 - 100 * data[ii][3]/float(row[X_index + 1])), "%.2f" % (100 - 100 *  data[ii][4]/float(row[X_index + 2]))
#

# overwrite in memory the first file
files[0][15] = "NUMBER_OF_FIELDS\t5\n"
files[0][17] = "SAMPLE_ID\tSAMPLE_NAME\tX\tY\tY\n"

# for i in range(dataStartIndex + 1, dataEndIndex):
#     dInd = i - dataStartIndex - 1
#     files[0][i] = str(data[dInd][0]) + "\t" + str(data[dInd][1]) + "\t" + "%.2f" % data[dInd][2] + "\t" + "%.2f" % data[dInd][3] + "\t" + "%.2f" % data[dInd][4] + "\n"

files[0][19] = "AKVO - AVERAGED FILES\t" + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n"

# create result file
fNew = "average.txt"

fo = open(OUTPUTDIR + fNew, 'w')
for line in files[0]:
    fo.write(str(line))
fo.close()
