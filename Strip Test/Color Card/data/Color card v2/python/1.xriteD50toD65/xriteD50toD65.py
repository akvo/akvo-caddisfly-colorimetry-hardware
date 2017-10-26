#################################################################################################
# This programme takes a file exported by xrite I photo pro software, and
# converts the lab values from D50 illuminant to D65 illuminant.
#
# The programme looks for files in the /input folder. It checks it is a valid M1 xrite file.
# The output is written to the /output folder. D65 is added to the name.
#
# author: M.T. Westra
# date: 3-8-2016
# version: 1.0
#################################################################################################
import os
import LabD50toLabD65
import datetime

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

for inputFile in os.listdir(INPUTDIR):
    if 'DS_Store' in inputFile:
        continue
    fileName = INPUTDIR + inputFile
    print "file name: " + fileName

    try:
        f = open(INPUTDIR + inputFile, 'r')
    except IOError:
        print("can't open file " + fileName)

    lines = f.readlines()

    # check if file starts with "CGATS.17"
    if "CGATS.17" not in lines[0]:
        print("Expected file to start with CGATS.17. Skipping file")
        continue

    # check if we used measurement condition M1
    if "MeasurementCondition=M1" not in lines[5]:
        print("Expected file to have Measurement condition M1. Skipping file")
        continue

    # check if we have D50 illumnation
    if "ILLUMINATION_NAME\t\"D50\"" not in lines[6]:
        print("Expected file to have Illumination name D50. Skipping file")
        continue

    # find the location of the Lab data
    dataFormatIndex = findIndex(lines,"BEGIN_DATA_FORMAT") + 1
    dataFormat = lines[dataFormatIndex].split()

    try:
        LAB_L_index = dataFormat.index("LAB_L")
    except ValueError:
        print "Lab data not found. Skipping file"
        continue

    # Find beginning and end of data
    try:
        dataStartIndex = findIndex(lines,"BEGIN_DATA\n")
        dataEndIndex = findIndex(lines,"END_DATA\n")
    except ValueError:
        print "Data not found. Skipping file"
        continue

    # do transform from D50 to D65
    newData=[]
    for index in range(dataStartIndex + 1, dataEndIndex):
        row = lines[index].split()
        CIE_D50_L = float(row[LAB_L_index])
        CIE_D50_a = float(row[LAB_L_index + 1])
        CIE_D50_b = float(row[LAB_L_index + 2])

        [X_D50,Y_D50,Z_D50] = LabD50toLabD65.LabD50toXYZD50(CIE_D50_L,CIE_D50_a,CIE_D50_b)
        [X_D65,Y_D65,Z_D65] = LabD50toLabD65.XYZD50toXYZD65(X_D50,Y_D50,Z_D50)
        # [CIE_D65_L,CIE_D65_a,CIE_D65_b] = LabD50toLabD65.XYZD65toLabD65(X_D65,Y_D65,Z_D65)
        # newData.append([row[0],row[1],CIE_D65_L,CIE_D65_a,CIE_D65_b])
        newData.append([row[0],row[1],X_D65,Y_D65,Z_D65])

    # rewrite lines in place, and export all
    lines[5] = "MEASUREMENT_SOURCE\t\"MeasurementCondition=M1\tFilter=D65\n"
    lines[6] = "ILLUMINATION_NAME\t\"D65\"\n"
    lines[8] = "FILTER\t\"D65\"\n"
    lines[9] = "WEIGHTING_FUNCTION\t\"ILLUMINANT,\t D65\"\n"
    lines[14] = "AKVO - TRANSFERED TO D65 COLOUR SPACE\t" + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n"
    lines[15] = "NUMBER_OF_FIELDS\t5\n"
    lines[17] = "SAMPLE_ID\tSAMPLE_NAME\tX\tY\tZ\n"

    for index in range(dataStartIndex + 1, dataEndIndex):
        dInd = index - dataStartIndex - 1
        lines[index] = str(newData[dInd][0]) + "\t" + str(newData[dInd][1]) + "\t" + "%.3f" % newData[dInd][2] + "\t" + "%.3f" % newData[dInd][3] + "\t" + "%.3f" % newData[dInd][4] + "\n"

    # create new name
    fSplit = inputFile.split('.')
    fNew = fSplit[0] + "-D65." + fSplit[1]

    fo = open(OUTPUTDIR + fNew, 'w')
    for line in lines:
        fo.write(str(line))
    fo.close()
