from pathlib import Path
import pandas as pd
from scipy.signal import decimate
import numpy as np
import os
import brpylib.py


fileCnt = 1
saveindex = 1
saveNum = 1
patientSwitchSaveIndex = []
numPatients = 1
patientID = 'DBSTRD011'

LeftMatrix = []
RightMatrix = []
TimeStampMatrix = []
TimeStampNum = 1
DateTimeMatrix = []
DateTimeNum = 1

patientPath = #Jordan you need to link to ELIAS

LeftAll = [] #A list of 2D matrices that contain all electrodes for each 20 min interval
LeftAll_avg = []

RightAll = []
RightAll_avg = []

prompt = 'Intervals of 10 or 20 (1/2): '
interv = int(input(prompt))

if interv ==1:
    intervNum = 10
if interv ==2:
    intervNum = 20

for i, folder in enumerate(fileList):
    if os.path.isdir(folder) and '.' not in folder: 
       ns3_path = Path(patient_path) / file_list[folder].name
       ns3List = os.listdir(ns3_path)

       for j, file in enumerate(ns3List):
           
           if not ('.ns3' in file or '.ns5' in file): #checks if we are pulling either a .ns3 or .ns5, otherwise skip
               continue


           try:
                if '.ns5' in file.name:
                   fs = 30000
                if '.ns3' in file.name:
                   fs = 2000
                datafile = Path(ns3_path)/file
                ns3Data = NsxFile(datafile)
                NsxFile.datafile.close() #BlackRock recommends to close it after extracting data

           except Exception as e:
               print('Caught')
               continue
           print('File successfully loaded.')

           allElectrodes = {}
           try:
               for x, electrode in enumerate(ns3Data.ElectrodesInfo):
                   allElectrodes[electrodeList] = ns3Data.ElectrodeInfo[electrodeList].Label

           except Exception as e:
               continue
           
           LeftElectrodeIDs = [i for i, name in enumerate(allElectrodes) if 'LdPF-ACC' in name]
           RightElectrodeIDs = [i for i, name in enumerate(allElectrodes) if 'RdPF-ACC' in name]
           allElectrodes = [] #clear space
           del allElectrodes

           try:
               leftDownArr = []
               rightDownArr = []
               
               #Downsampling data to 200 Hz
               if fs == 2000:
                   leftDownArr = decimate(ns3Data.Data[LeftElectrodeIDs,:],4, axis=1)
                   df = pd.DataFrame(leftDownArr)
                   leftDownArr = df.interpolate(method='linear', axis=1) #interpolate across NaNs
                   leftDownArr = np.array(leftDownArr)
                   leftDownArr_avg = np.mean(leftDownArr, axis=0)
            
                   rightDownArr = decimate(ns3Data.Data[RightElectrodeIDs,:],4, axis=1)
                   df = pd.DataFrame(rightDownArr)
                   rightDownArr = df.interpolate(method='linear',axis=1) #interpolate across NaNs
                   rightDownArr = np.array(rightDownArr)
                   rightDownArr_avg = np.mean(rightDownArr, axis=0)

               if fs == 30000:
                   leftDownArr = decimate(ns3Data.Data[LeftElectrodeIDs,:],60, axis=1)
                   df = pd.DataFrame(leftDownArr)
                   leftDownArr = df.interpolate(method='linear',axis =1) #interpolate across NaNs
                   leftDownArr = np.array(leftDownArr)
                   leftDownArr_avg = np.mean(leftDownArr, axis=0)

                   rightDownArr = decimate(ns3Data.Data[RightElectrodeIDs,:],60, axis=1)
                   df = pd.DataFrame(rightDownArr)
                   rightDownArr = df.interpolate(method='linear',axis=1) #interpolate across NaNs
                   rightDownArr = np.array(rightDownArr)
                   rightDownArr_avg = np.mean(rightDownArr, axis=0)

               #FIND way to organize all data
               LeftAll_avg.append(leftDownArr_avg) #A list of 2D matrices that contain all electrodes for each 20 min interval
               LeftAll.append(leftDownArr)

               RightAll_avg.append(rightDownArr_avg)
               RightAll.append(rightDownArr)

           except Exception as e:
               del LeftLFPArray
               del RightLFPArray
               continue
           
           
               
            
    


