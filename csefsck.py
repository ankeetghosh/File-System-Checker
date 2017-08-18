## Name: Ankeet Ghosh, Net Id: ag5347, University Id: N12489696, Cell Number: +1 516 498 7889

import json
import time

##Global Variables and Constants##
DevId = 20
CurrentTimeEpoch = time.time()
PATH = './FS/'
BlockSize = 4096
UsedBlockList = []

##Check if the Device Id is correct
def checkDevId():
    fuse = open(PATH + "fusedata.0", "r+")
    superBlk = fuse.read();
    print "Read super block : ", superBlk
    superBlkData = json.loads(superBlk)
    print "The Device Id : ", superBlkData['devId']
    if ( superBlkData['devId'] == DevId ):
        print "The Device Id is Correct"
    else:
        print "The Device Id is Incorrect"
        exit(1)
    fuse.close()

## Check if all times are in the past. If they are in the future, its changed to the present
def checkAllTimes():
    fuse = open(PATH + "fusedata.0", "r+")
    superBlk = fuse.read();
    superBlkData = json.loads(superBlk)
    ## Check if the creation time is correct or not, and then modified if required
    if ( superBlkData['creationTime'] < CurrentTimeEpoch ):
        print "The time in the super block information is in the past"
    else:
        superBlkData['creationTime'] = CurrentTimeEpoch
        fuse.seek(0)
        fuse.truncate()
        fuse.write(json.dumps(superBlkData));
        print "A future was being shown in super block and hence, changed"
    fuse.close()
    ## Check if the atime, mtime, ctime present in root and other blocks are correct or not, and then modified if required
    checkTimes(superBlkData["root"],'d')

    
## Check if the atime, mtime, ctime present in root and other blocks are in the past, and then modified to present time if they are in the future
def checkTimes(location,type):
    fuse = open(PATH+"fusedata."+str(location), "r+")
    blockData = fuse.read();
    blockDataJson = json.loads(blockData)
    atime = blockDataJson["atime"]
    ctime = blockDataJson["ctime"]
    mtime = blockDataJson["mtime"]
    
    if ( blockDataJson["atime"] < CurrentTimeEpoch ):
        print "The atime in the fusedata.%d file is in the past" %location
    else:
        blockDataJson["atime"] = CurrentTimeEpoch
        print "A future atime was being shown in fusedata.%d and hence, changed" %location
        fuse.seek(0)
        fuse.truncate()
        fuse.write(json.dumps(blockDataJson));
        
    if ( blockDataJson["ctime"] < CurrentTimeEpoch ):
        print "The ctime in the fusedata.%d file is in the past" %location
    else:
        blockDataJson["ctime"] = CurrentTimeEpoch
        print "A future ctime was being shown in fusedata.%d and hence, changed" %location
        fuse.seek(0)
        fuse.truncate()
        fuse.write(json.dumps(blockDataJson));

    if ( blockDataJson["mtime"] < CurrentTimeEpoch ):
        print "The mtime in the fusedata.%d file is in the past" %location
    else:
        blockDataJson["mtime"] = CurrentTimeEpoch
        print "A future mtime was being shown in fusedata.%d and hence, changed" %location
        fuse.seek(0)
        fuse.truncate()
        fuse.write(json.dumps(blockDataJson));

    fuse.close()
    
    if (type == 'd' ):
        dictLength = len(blockDataJson["filename_to_inode_dict"])
        for j in range(0, dictLength):
            if ( blockDataJson["filename_to_inode_dict"][j]["type"] == 'f' ):
                checkTimes(blockDataJson["filename_to_inode_dict"][j]["location"],'f')
            elif ( blockDataJson["filename_to_inode_dict"][j]["type"] == 'd' and blockDataJson["filename_to_inode_dict"][j]["name"] != '.' and blockDataJson["filename_to_inode_dict"][j]["name"] != '..' ):
                checkTimes(blockDataJson["filename_to_inode_dict"][j]["location"],'d')


## Check if each directory contains . and .. , and if their corresponding block numbers are correct. Also, modify their block numbers if incorrect.
def checkCorrectBlkNos():
    fuse = open(PATH + "fusedata.0", "r+")
    superBlk = fuse.read();
    superBlkData = json.loads(superBlk)
    fuse.close()
    fuse = open(PATH + "fusedata."+str(superBlkData["root"]), "r+")
    rootBlk = fuse.read();
    rootBlkData = json.loads(rootBlk)

    ## Check if the root directory contains . and .. , and if their corresponding block numbers are correct. Also, modify their block numbers if incorrect.
    dictLength = len(rootBlkData["filename_to_inode_dict"])
    for j in range(0, dictLength):
        if ( rootBlkData["filename_to_inode_dict"][j]["type"] == 'd' and rootBlkData["filename_to_inode_dict"][j]["name"] == '.' ):
            print "The root directory contains ."
            if ( rootBlkData["filename_to_inode_dict"][j]["location"] != superBlkData["root"] ):
                rootBlkData["filename_to_inode_dict"][j]["location"] = superBlkData["root"]
                print "The '.' in root block was pointing to an incorrect location and hence, corrected to %d" %superBlkData["root"]
                fuse.seek(0)
                fuse.truncate()
                fuse.write(json.dumps(rootBlkData))
            else:
                print "The block number of . corresponding to the root director is correct"
        elif ( rootBlkData["filename_to_inode_dict"][j]["type"] == 'd' and rootBlkData["filename_to_inode_dict"][j]["name"] == '..' ):
            print "The root directory contains .."
            if ( rootBlkData["filename_to_inode_dict"][j]["location"] != superBlkData["root"] ):
                rootBlkData["filename_to_inode_dict"][j]["location"] = superBlkData["root"]
                print "The '..' in root block was pointing to an incorrect location and hence, corrected to %d" %superBlkData["root"]
                fuse.seek(0)
                fuse.truncate()
                fuse.write(json.dumps(rootBlkData))
            else:
                print "The block number of .. corresponding to the root director is correct"
    fuse.close()

    for j in range(0, dictLength):
        if ( rootBlkData["filename_to_inode_dict"][j]["type"] == 'd' and rootBlkData["filename_to_inode_dict"][j]["name"] != '.' and rootBlkData["filename_to_inode_dict"][j]["name"] != '..' ):
            checkCorrectBlkNosUndrRoot(rootBlkData["filename_to_inode_dict"][j]["location"], superBlkData["root"])

## Check if all directories other than contains . and .. , and if their corresponding block numbers are correct. Also, modify their block numbers if incorrect.
def checkCorrectBlkNosUndrRoot(Location, parentLoc):
    fuse = open(PATH + "fusedata."+str(Location), "r+")
    Blk = fuse.read();
    BlkData = json.loads(Blk)

    dictLength = len(BlkData["filename_to_inode_dict"])
    for j in range(0, dictLength):
        if ( BlkData["filename_to_inode_dict"][j]["type"] == 'd' and BlkData["filename_to_inode_dict"][j]["name"] == '.' ):
            print "The directory corresponding to fusedata.%d has ." %Location
            if ( BlkData["filename_to_inode_dict"][j]["location"] != Location ):
                BlkData["filename_to_inode_dict"][j]["location"] = Location
                print "The '.' in fusedata.%d block was pointing to an incorrect location and hence, corrected to %d" %(Location,Location)
                fuse.seek(0)
                fuse.truncate()
                fuse.write(json.dumps(BlkData))
            else:
                print "The block number of . as corresponding to the directory in fusedata.%d is correct" %Location
        elif ( BlkData["filename_to_inode_dict"][j]["type"] == 'd' and BlkData["filename_to_inode_dict"][j]["name"] == '..' ):
            print "The directory corresponding to fusedata.%d has .." %Location
            if ( BlkData["filename_to_inode_dict"][j]["location"] != parentLoc ):
                BlkData["filename_to_inode_dict"][j]["location"] = parentLoc
                print "The '..' in fusedata.%d block was pointing to an incorrect location and hence, corrected to %d" %(Location,parentLoc)
                fuse.seek(0)
                fuse.truncate()
                fuse.write(json.dumps(BlkData))
            else:
                print "The block number of .. as corresponding to the directory in fusedata.%d is correct" %Location
    fuse.close();
    
    for j in range(0, dictLength):
        if ( BlkData["filename_to_inode_dict"][j]["type"] == 'd' and BlkData["filename_to_inode_dict"][j]["name"] != '.' and BlkData["filename_to_inode_dict"][j]["name"] != '..'):
            checkCorrectBlkNosUndrRoot(BlkData["filename_to_inode_dict"][j]["location"], Location)


## Check if indirect is 1, then the data in the block pointed to by location pointer is an array
## Check that the size is valid for the number of block pointers in the location array. The three possibilities are:
## a. size<blocksize  should have indirect=0 and size>0
## b. if indirect!=0, size should be less than (blocksize*length of location array)
## c. if indirect!=0, size should be greater than (blocksize*length of location array-1)
def AllLocPointArrayAndSizeChk():
    ## Find the block number of the root from the super block
    fuse = open(PATH + "fusedata.0", "r+")
    superBlk = fuse.read();
    superBlkData = json.loads(superBlk)
    fuse.close()
    ## find the blocks which contains file information, and then perform the above checks
    findFileInode(superBlkData["root"])
    
def locPointerArrayChkAndFileSizeCheck(location):
    fuse = open(PATH + "fusedata."+str(location), "r+")
    Blk = fuse.read();
    BlkData = json.loads(Blk)

   ##Check if indirect is 1
    if (BlkData["indirect"] == 1):
        fusee = open(PATH + "fusedata."+str(BlkData["location"]), "r+")
        Blk = fusee.read(); 
        Blk = Blk[1:-1]
        Block = Blk.split(',')
        lengthLocArray = len(Block)
        fusee.close()

        ## Check if the data in the block pointed to by te location pointer is an array
        flag = 1
        for i in range(0,len(Block)):
            if(Block[i].isdigit() == False):
                flag=0
                break
            
        if(flag == 1):
            print "The data in the block fusedata.%d pointed to by the location pointer is an array" %BlkData["location"]
        else:
            print "The data in the block fusedata.%d pointed to by the location pointer is not an array" %BlkData["location"]

        ## check: if size of the file is not within the range (BlockSize * lengthLocArray-1) and (BlockSize * lengthLocArray), and correct the size as required
        if(BlkData["size"] >= (BlockSize * lengthLocArray) or BlkData["size"] <= (BlockSize * (lengthLocArray-1))):
            print "The size of the file as mentioned in fusedata.%d not within the required range and hence, has been re-calculated and changed" %location
            BlkData["size"]= (BlockSize * lengthLocArray)-1
            fuse.seek(0)
            fuse.truncate()
            fuse.write(json.dumps(BlkData));
        else:
            print "The size of the file as mentioned in fusedata.%d is within the required range of (BlockSize * lengthLocArray-1) and (BlockSize * lengthLocArray)" %BlkData["location"]
        
    ## Ensure if sizeOfFile<blockSize, should have indirect=0 and size>0, else make the necessary corrections to correct the size
    if (BlkData["size"] < BlockSize):
        if (BlkData["size"]>0 and BlkData["indirect"] == 0):
            print "The file as mentioned in fusedata.% has indirect 0 when its size < block size" %location
        elif(BlkData["size"]>0 and BlkData["indirect"] > 0): 
            print "Since size as mentioned in fusedata.%d is less than Block Size and has indirect not equal to 0," %location
            print "the size must be incorrect and hence, has been re-calculated and changed"
            BlkData["size"]=4096
            fuse.seek(0)
            fuse.truncate()
            fuse.write(json.dumps(BlkData));
    
    
          
    fuse.close()

## find the blocks which contains file information, and then perform the above checks 
def findFileInode(location):
    fuse = open(PATH + "fusedata."+str(location), "r+")
    Blk = fuse.read();
    BlkData = json.loads(Blk)

    dictLength = len(BlkData["filename_to_inode_dict"])
    for j in range(0, dictLength):
        if ( BlkData["filename_to_inode_dict"][j]["type"] == 'f' ):
            locPointerArrayChkAndFileSizeCheck(BlkData["filename_to_inode_dict"][j]["location"]);
        elif ( BlkData["filename_to_inode_dict"][j]["type"] == 'd' and BlkData["filename_to_inode_dict"][j]["name"] != '.' and BlkData["filename_to_inode_dict"][j]["name"] != '..'):
            findFileInode(BlkData["filename_to_inode_dict"][j]["location"]);
    fuse.close();
    
## Get the no of used blocks which contain files and directories
def getUsedBlockList(location,type):
    fuse = open(PATH+"fusedata."+str(location), "r+")
    blockData = fuse.read();
    
    blockDataJson = json.loads(blockData)
    fuse.close()

    
    if(type == 'f'):
        UsedBlockList.append(blockDataJson["location"])
        if(blockDataJson["indirect"] == 1):
            LocationPointers = []
            fuse = open(PATH+"fusedata."+str(blockDataJson["location"]), "r+")
            blockData = fuse.read();
            blockData = blockData[1:-1]
            
            LocationPointers = blockData.split(',')
            lengthOfArray= len(LocationPointers)
            for j in range(0,lengthOfArray):
                UsedBlockList.append(int(LocationPointers[j]))
            fuse.close()

    elif(type == 'd'):
        dictLength = len(blockDataJson["filename_to_inode_dict"])
        for j in range(0, dictLength):
            if ( blockDataJson["filename_to_inode_dict"][j]["type"] == 'd' and blockDataJson["filename_to_inode_dict"][j]["name"] != '.' and blockDataJson["filename_to_inode_dict"][j]["name"] != '..' ):
                UsedBlockList.append(blockDataJson["filename_to_inode_dict"][j]["location"])
                getUsedBlockList(blockDataJson["filename_to_inode_dict"][j]["location"],'d')
            if( blockDataJson["filename_to_inode_dict"][j]["type"] == 'f' ):
                UsedBlockList.append(blockDataJson["filename_to_inode_dict"][j]["location"])
                getUsedBlockList(blockDataJson["filename_to_inode_dict"][j]["location"],'f')
    
    return UsedBlockList   
    
## Validate and correct the free block list
def ValidateAndUpdateFreeBlockList():
    fuse = open(PATH + "fusedata.0", "r+")
    superBlk = fuse.read();
    superBlkData = json.loads(superBlk)
    fuse.close()

    fuse = open(PATH + "fusedata."+str(superBlkData["root"]), "r+")
    rootBlk = fuse.read();
    rootBlkData = json.loads(rootBlk)
    fuse.close()

    ## To store the free block numbers as mentioned in the list of files which maintain this info
    TotalGivenFreeBlockList = []
    ## To store free block numbers that are actually free
    TotalActualFreeBlocks = []
    ## To store the free block numbers that are actually free but missing in the list of files which maintain this info
    MissingFreeBlockList = []
    ## Used Blocks in Free List
    UsedBlockInFreeLst = []

    ## Store the free block numbers in an array as mentioned in the list of files which maintain this info
    for i in range(superBlkData["freeStart"], superBlkData["freeEnd"]+1):
        fuse = open(PATH+"fusedata."+ str(i), "r+")
        blockData = fuse.read();
        blockData = blockData[1:-1]
        
        LocationPointers = blockData.split(',')
        lengthOfArray= len(LocationPointers)
        for j in range(0,lengthOfArray):
            TotalGivenFreeBlockList.append(int(LocationPointers[j]))
        fuse.close()
        
    ##print "Given:", TotalGivenFreeBlockList
  
    ## Get the blocks being used for files and directories
    TotalUsedBlockList = getUsedBlockList(superBlkData["root"],'d');
    print "Used Blocks for files and directories:" ,TotalUsedBlockList

    flagUsedinFree=0
    ## Finding Used Blocks from the Given list of free blocks and storing them in an array
    for i in range(0,len(TotalUsedBlockList)):
        if(TotalGivenFreeBlockList.count(TotalUsedBlockList[i])>0):
           UsedBlockInFreeLst.append(int(TotalUsedBlockList[i]))
           flagUsedinFree=flagUsedinFree+1

    print "Used Blocks Containing files and directories in FreeList:", UsedBlockInFreeLst   

    lengthOfUsedInFree=len(UsedBlockInFreeLst)
    if(flagUsedinFree > 0):
        for i in range(superBlkData["freeStart"], superBlkData["freeEnd"]+1):
            LocationPointers=[]
            fuse = open(PATH+"fusedata."+ str(i), "r+")
            blockData = fuse.read();
            blockData = blockData[1:-1]
            LocationPointers = blockData.split(',')
            lengthOfArray= len(LocationPointers)
            for j in range(0,lengthOfUsedInFree):
                if(LocationPointers.count(UsedBlockInFreeLst[j]) > 0):
                    print 3
                    LocationPointers.remove(UsedBlockInFreeLst[i])
                    LocationPointersStr = str(LocationPointers[0]) +',' +str(LocationPointers[1])
                    for f in range(2, len(LocationPointers)):
                        LocationPointersStr+= ',' + str(LocationPointers[f])
                    LocationPointersStr = '['+LocationPointersStr+']'
                    print LocationPointersStr
                    fuse.seek(0)
                    fuse.truncate()
                    fuse.write(LocationPointersStr);       
            fuse.close()
        print "The Used blocks present in the free block list has been removed"
    else:
        print "None of the used blocks are present in the free block list"
                 

    print "Checking if there's any free block missing in Free Block List"
    
    ## Store free block numbers in an array that are actually free and, do not have blocks which contain files or directories 
    count=0
    lengthOfUsedBlock = len(TotalUsedBlockList)
    for i in range(superBlkData["root"]+1, superBlkData["maxBlocks"]):
        for j in range(0,lengthOfUsedBlock):
            if(i == int(TotalUsedBlockList[j])):
                count=count + 1
        if(count == 0):
            TotalActualFreeBlocks.append(i)
        count=0
        
    ##print "Actual:", TotalActualFreeBlocks
    
    lengthOfActualFree = len(TotalActualFreeBlocks)
    lengthOfGivenFree = len(TotalGivenFreeBlockList)

    Checkflag = 0
    count = 0

    ## If the free block list mentiond in the blocks contain all the free block numbers that are actually free    
    for i in range(0,lengthOfActualFree):
        if(TotalGivenFreeBlockList.count(TotalActualFreeBlocks[i]) == 0):
            Checkflag = 1
            count=count+1
            MissingFreeBlockList.append(TotalActualFreeBlocks[i])
        count=0
        

    lengthOfMissingList = len(MissingFreeBlockList)
    if(Checkflag == 1):
        print "The following blocks are free but missing from the free block list:", MissingFreeBlockList
        for k in range(0,lengthOfMissingList):
            for i in range(superBlkData["freeStart"], superBlkData["freeEnd"]+1):
                LocationPointers=[]
                fuse = open(PATH+"fusedata."+ str(i), "r+")
                blockData = fuse.read();
                blockData = blockData[1:-1]
                LocationPointers = blockData.split(',')
                #print "LocationPointers:", LocationPointers  
                lengthOfArray= len(LocationPointers)
                               
                if(lengthOfArray<400):
                    LocationPointers.append(int(MissingFreeBlockList[k]))
                    length = len(LocationPointers)
                    freeblocks = str(LocationPointers[0]) +',' +str(LocationPointers[1])
                    for f in range(2, len(LocationPointers)):
                        freeblocks+= ',' + str(LocationPointers[f])

                    freeblocks = '['+freeblocks+']'
                    fuse.seek(0)
                    fuse.truncate()
                    fuse.write(freeblocks);
                    fuse.close()
                    break
                
        print "The free blocks missing from the free block list has been added"
    else:
        print "The free block list already has all the free blocks required, and hence further additions are not required"
            
            
     
    

##Main##
print"                                              ---------Dev Id Check--------"
##Check if the Device Id is correct
checkDevId()
print"------------------------------------------------------------------------------------------------------------------------"
print"                                      ---------Check if all times are in the past--------"
## Check if all times are in the past. If they are in the future, its changed to the present
checkAllTimes()
print"------------------------------------------------------------------------------------------------------------------------"
print"                  ---------Check if all directories have . and .., and their block numbers are correct--------"
## Check if each directory contains . and .. , and if their corresponding block numbers are correct. Also, modify their block numbers if incorrect.
checkCorrectBlkNos()
print"------------------------------------------------------------------------------------------------------------------------"
print"                        ---------Check and validate the size, indirect values and data----------------"
## Check if indirect is 1, then the data in the block pointed to by location pointer is an array
## Check that the size is valid for the number of block pointers in the location array. The three possibilities are:
## a. size<blocksize  should have indirect=0 and size>0
## b. if indirect!=0, size should be less than (blocksize*length of location array)
## c. if indirect!=0, size should be greater than (blocksize*length of location array-1)
AllLocPointArrayAndSizeChk()
print"------------------------------------------------------------------------------------------------------------------------"
print"                                      ---------Validate the Free Block List--------"
## Validate and correct the free block list
ValidateAndUpdateFreeBlockList()
print"------------------------------------------------------------------------------------------------------------------------"





