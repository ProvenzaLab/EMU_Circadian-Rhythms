from pathlib import Path
import pandas as pd
from scipy.signal import decimate
import numpy as np
import os
from scipy.io import loadmat


fileCnt = 1
saveindex = 1
saveNum = 1
patientSwitchSaveIndex = []
numPatients = 1


LeftAll = [] #A list of 2D matrices that contain all electrodes for each 20 min interval
RightAll = []
DateTimes = []
TimeStamps = []


#prompt = 'Intervals of 10 or 20 (1/2): '
#interv = int(input(prompt))

#if interv ==1:
    #intervNum = 10
#if interv ==2:
    #intervNum = 20

folderPath = "/projects/np66/tm/TRD011"
files = os.listdir(folder)

for fileNum, fileName in enumerate(files): 
    nsxPath = os.path.join(folderPath, fileName)

    nsxDataPre = loadmat(nsxPath) 
    nsx = nsxDataPre['PHI_removed_ns'][0,0]
    metaTag = nsx['MetaTags'][0,0]

    file_ext = ''.join(metaTag['FileExt'][0])

    Date_timeOrg = ''.join(metaTag['DateTime'][0])
    Date_time = Date_timeOrg.split(" ")[0]
   
    time_stamp = Date_timeOrg.split(" ")[1]







    try:
        if '.ns5' in file_ext:
            fs = 30000
        if '.ns3' in file_ext:
            fs = 2000

    except Exception as e:
        print('Caught')
        continue
    print('File successfully loaded.')

    try:
        
        ## Find electrodes that denote Left and Right and separate them out + save out their names
        leftElectrodeIdx = [] #array = each row is an electrode; column 0 is the name, column 1 is the index in the original struct/dictionary
        rightElectrodeIdx = []
        for electrode in range(nsx['ElectrodesInfo']['Label'].shape[1]): #Number of electrodes
            electrodeName = nsx['ElectrodesInfo']['Label'][0,electrode]
            if 'L' in electrodeName[0]: #check if first letter is L for left hemisphere
                leftElectrodeIdx.append([electrodeName,electrode]) #store both the electrode name and its index
            if 'R' in electrodeName[0]: #check if first letter is R for right hemisphere
                rightElectrodeIdx.append([electrodeName,electrode])

        leftDownArr = []
        rightDownArr = []
        
        #Downsampling data to 200 Hz
        if fs == 2000:
            leftDownArr = []
            rightDownArr = []
            for electrode in range(leftElectrodeIdx.shape[0]): #left electrode loop
                currArr = nsx['Data'][leftElectrodeIdx[electrode,1]]
                df = pd.DataFrame(currArr)
                leftDownArr = df.interpolate(method='linear')
                leftDownArr = np.array(leftDownArr)
                leftDownArr = decimate(leftDownArr,4)
    
            for electrode in range(rightElectrodeIdx.shape[0]): #right electrode loop
                currArr = nsx['Data'][rightElectrodeIdx[electrode,1]]
                df = pd.DataFrame(currArr)
                rightDownArr = df.interpolate(method='linear')
                rightDownArr = np.array(rightDownArr)
                rightDownArr = decimate(rightDownArr,4)
            

        if fs == 30000:
            leftDownArr = []
            rightDownArr = []
            for electrode in range(leftElectrodeIdx.shape[0]): #left electrode loop
                currArr = nsx['Data'][leftElectrodeIdx[electrode,1]]
                df = pd.DataFrame(currArr)
                leftDownArr = df.interpolate(method='linear')
                leftDownArr = np.array(leftDownArr)
                leftDownArr = decimate(leftDownArr,60)
    
            for electrode in range(rightElectrodeIdx.shape[0]): #right electrode loop
                currArr = nsx['Data'][rightElectrodeIdx[electrode,1]]
                df = pd.DataFrame(currArr)
                rightDownArr = df.interpolate(method='linear')
                rightDownArr = np.array(rightDownArr)
                rightDownArr = decimate(rightDownArr,60)
            


        #FIND way to organize all data
        LeftAll.append(leftDownArr) #A list of 2D matrices that contain all electrodes for each 20 min interval
        RightAll.append(rightDownArr)
        DateTimes.append(Date_time)
        TimeStamps.append(time_stamp)


    except Exception as e:
        continue
           
           
               
            
    


