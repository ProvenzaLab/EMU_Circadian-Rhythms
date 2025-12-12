from pathlib import Path
import pandas as pd
from scipy.signal import decimate
import numpy as np
import os
from scipy.io import loadmat
import h5py


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

project_dir = os.environ.get("PROJECTS")
if project_dir is None:
    raise RuntimeError("PROJECTS environment is not set...")

folderPath = os.path.join(project_dir, "np66", "TRD011_Files")
filePathSave = os.path.join(project_dir,"np66","TRD011_Processed")


files = os.listdir(folderPath)

for fileNum, fileName in enumerate(files): 
    try:    
        nsxPath = os.path.join(folderPath, fileName)

    
    
    
        nsxDataPre = loadmat(nsxPath) 
        nsx = nsxDataPre['PHI_removed_ns'][0,0]
        metaTag = nsx['MetaTags'][0,0]

        file_ext = ''.join(metaTag['FileExt'][0])

        Date_timeOrg = ''.join(metaTag['DateTime'][0])
        Date_time = Date_timeOrg.split(" ")[0]
   
        time_stamp = Date_timeOrg.split(" ")[1]

    
        if '.ns5' in file_ext:
            fs = 30000
        if '.ns3' in file_ext:
            fs = 2000

    
        print('File successfully loaded.')

    
        
        ## Find electrodes that denote Left and Right and separate them out + save out their names
        leftElectrodeIdx = [] #array = each row is an electrode; column 0 is the name, column 1 is the index in the original struct/dictionary
        rightElectrodeIdx = []
        for electrode in range(nsx['ElectrodesInfo']['Label'].shape[1]): #Number of electrodes
            electrodeName = nsx['ElectrodesInfo']['Label'][0,electrode]
            if 'L' in electrodeName[0]: #check if first letter is L for left hemisphere
                leftElectrodeIdx.append([electrodeName,electrode]) #store both the electrode name and its index
            if 'R' in electrodeName[0]: #check if first letter is R for right hemisphere
                rightElectrodeIdx.append([electrodeName,electrode])
        
        #Downsampling data to 200 Hz
        if fs == 2000:
            leftDownArr = []
            rightDownArr = []
            for electrode in range(len(leftElectrodeIdx)): #left electrode loop
                currArrLeft = []
                currArr = []
                currArr = nsx['Data'][leftElectrodeIdx[electrode][1]]
                df = pd.DataFrame(currArr)
                currArrLeft = df.interpolate(method='linear').to_numpy().squeeze()
           
                currArrLeft = decimate(currArrLeft,4)
                leftDownArr.append(currArrLeft)

            leftDownArr = np.array(leftDownArr)
    
            for electrode in range(len(rightElectrodeIdx)): #right electrode loop
                currArrRight = []
                currArr = []
                currArr = nsx['Data'][rightElectrodeIdx[electrode][1]]
                df = pd.DataFrame(currArr)
                currArrRight = df.interpolate(method='linear').to_numpy().squeeze()
             
                currArrRight = decimate(currArrRight,4)
                rightDownArr.append(currArrRight)

            rightDownArr = np.array(rightDownArr)
            

        if fs == 30000:
            leftDownArr = []
            rightDownArr = []
            for electrode in range(len(leftElectrodeIdx)): #left electrode loop
                currArrLeft = []
                currArr = []
                currArr = nsx['Data'][leftElectrodeIdx[electrode][1]]
                df = pd.DataFrame(currArr)
                currArrLeft = df.interpolate(method='linear').to_numpy().squeeze()
              
                currArrLeft = decimate(currArrLeft,60)
                leftDownArr.append(currArrLeft)

            leftDownArr = np.array(leftDownArr)
    
            for electrode in range(len(rightElectrodeIdx)): #right electrode loop
                currArrRight = []
                currArr = []
                currArr = nsx['Data'][rightElectrodeIdx[electrode][1]]
                df = pd.DataFrame(currArr)
                currArrRight = df.interpolate(method='linear').to_numpy().squeeze()
            
                currArrRight = decimate(currArrRight,60)
                rightDownArr.append(currArrRight)

            rightDownArr = np.array(rightDownArr)
            



        #FIND way to organize all data
        LeftAll.append(leftDownArr) #A list of 2D matrices that contain all electrodes for each 20 min interval
        RightAll.append(rightDownArr)
        DateTimes.append(Date_time)
        TimeStamps.append(time_stamp)

        LeftAll = [blk.astype('float32') for blk in LeftAll]
        RightAll = [blk.astype('float32') for blk in RightAll]

        

    except Exception as e:
        continue


date_strings = np.array(DateTimes, dtype='S32')   # full "date time" strings
time_strings = np.array(TimeStamps, dtype='S16')  # "HH:MM:SS" strings


save_dir = f"{os.environ['SHARED_SCRATCH']}/jra15/TRD011_Processed"


out_path = f"{save_dir}/TRD011_all.h5"

with h5py.File(out_path, "w") as f:
    # Create groups for hemispheres
    gL = f.create_group("Left")
    gR = f.create_group("Right")

    # Iterate interval-by-interval (all lists same length)
    for i, (L, R, d, t) in enumerate(zip(LeftAll, RightAll, DateTimes, TimeStamps)):
        name = f"blk_{i:06d}"  # zero-padded, sortable name

        # Save Left interval
        dL = gL.create_dataset(name,data=L.astype("float32"),compression="gzip")

        # Save Right interval
        dR = gR.create_dataset(name,data=R.astype("float32"),compression="gzip")

        # Attach per-interval metadata as attributes
        dL.attrs["Date"] = d
        dL.attrs["Time"] = t

        dR.attrs["Date"] = d
        dR.attrs["Time"] = t

