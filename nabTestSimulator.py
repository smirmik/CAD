# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Contextual Anomaly Detector - Open Source Edition
# Copyright (C) 2016, Mikhail Smirnov   smirmik@gmail.com
# https://github.com/smirmik/CAD
#
# This program is free software: you can redistribute it and/or modify it under
# the terms  of  the  GNU Affero Public License version 3  as  published by the
# Free Software Foundation.
#
# This program is distributed  in  the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero Public License for more details.
#
# You should have received a copy of the  GNU Affero Public License  along with
# this program.  If not, see http://www.gnu.org/licenses.
#
# ------------------------------------------------------------------------------


import csv
import datetime
import os
import math


from CAD_OSE import CAD_OSE


if __name__ == '__main__':

    testSet = 1

    baseDataDir = "../NAB/data"
    
    baseResultsDir = "../NAB/results"
    nullResultsDir = baseResultsDir + "/null"

    
    numResultTypes = 1
    numReturnedAnomalyValues = 1 
    startAnomalyValueNumber = 0

    
    if testSet == 1 :
        maxLeftSemiContextsLenght = 7
        maxActiveNeuronsNum = 15     
        numNormValueBits = 3
        baseThreshold = 0.75

    elif testSet == 0 :
        maxLeftSemiContextsLenght = 8
        maxActiveNeuronsNum = 16    
        numNormValueBits = 3
        baseThreshold = 1.0


    projectDirDescriptors = []
    for valuesVersion in xrange(numResultTypes) :
        projectDirDescriptors.append("CAD-{0:%Y%m%d%H%M}-Set{1:1d}".format(datetime.datetime.now(), testSet))
            

    dataDirTree = os.walk(baseDataDir)

    dirNames = []
    fullFileNames = []
    
    for i, dirDescr in enumerate(dataDirTree) :
        if i == 0 :
            dirNames = dirDescr[1]
        else :
            for fileName in dirDescr[2] :
                fullFileNames.append(dirDescr[0] + "/" + fileName)
            
    for projDirDescr in projectDirDescriptors :
        for directory in dirNames :
            os.makedirs(baseResultsDir +"/" + projDirDescr + "/" + directory )
    
    for fileNumber, fullFileName in enumerate(fullFileNames, start=1) : 

        print("-----------------------------------------") 
        print("[ " + str(fileNumber) + " ] " + fullFileName)
       
        minValue = float("inf")
        maxValue = -float("inf")
        with open(fullFileName, 'rb') as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',')
            next(csvReader)
            for rowNumber, row in enumerate(csvReader, start = 1):
                inputDataValue = float(row[1])
                minValue = min(inputDataValue, minValue)
                maxValue = max(inputDataValue, maxValue)

        learningPeriod = min( math.floor(0.15 * rowNumber), 0.15 * 5000)
      
        print("minValue = " + str(minValue) + " : maxValue = " + str(maxValue))
                                 
        cad = CAD_OSE   (  
                        minValue = minValue,
                        maxValue = maxValue,
                        baseThreshold = baseThreshold,
                        restPeriod = learningPeriod / 5.0,
                        maxLeftSemiContextsLenght = maxLeftSemiContextsLenght,
                        maxActiveNeuronsNum = maxActiveNeuronsNum,
                        numNormValueBits = numNormValueBits
                    )

        anomalyMassiv = []
        numSteps = 0    

        outFileDsc = fullFileName[len(baseDataDir)+1:].split("/")

        labelsFile = open(nullResultsDir + "/" + outFileDsc[0] + "/" + "null_" + outFileDsc[1], 'rb')
        csvLabelsReader = csv.reader(labelsFile, delimiter=',')
        next(csvLabelsReader)
        
        with open(fullFileName, 'rb') as csvfile:
            csvReader = csv.reader(csvfile, delimiter=',')
            next(csvReader)
            for row in csvReader:
                numSteps+=1
                currentLabel = next(csvLabelsReader)[3]
                
                inputDataDate =  datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") 
                inputDataValue = float(row[1])
                inputData = {"timestamp" : inputDataDate, "value" : inputDataValue}
                
                results = cad.getAnomalyScore(inputData)
                anomalyMassiv.append([numSteps, row[0], row[1], currentLabel, [results]])


        for i, projDirDescr in enumerate(projectDirDescriptors, start=startAnomalyValueNumber) :
            newFileName = baseResultsDir + "/" + projDirDescr + "/" + outFileDsc[0] + "/" + projDirDescr + "_" + outFileDsc[1] 
            with open(newFileName, 'w') as csvOutFile:
                csvOutFile.write("timestamp,value,anomaly_score,label\n")
                for anomalyScores in anomalyMassiv:
                    csvOutFile.write(anomalyScores[1]+ "," + anomalyScores[2] + "," + str(anomalyScores[4][i]) + "," + anomalyScores[3] + "\n")
            print ("saved to: " + newFileName)


