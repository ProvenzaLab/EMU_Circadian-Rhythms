from pathlib import Path


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

prompt = 'Intervals of 10 or 20 (1/2): '
interv = int(input(prompt))

if interv ==1:
    intervNum = 10
if interv ==2:
    intervNum = 20

for i, folder in enumerate(fileList):
    if .......
       ns3_path = Path(patient_path) / file_list[folder].name
       ns3List = ......

       for j, file in enumerate(ns3List):
           
           if ......
               continue


           try:
                if '.ns5' in file.name:
                   fs = 30000
                if '.ns3' in file.name:
                   fs = 2000
                ns3Data = openNSx.......
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
               
           except Exception as e:
               del LeftLFPArray
               continue
               
            
    


