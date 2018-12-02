#! /usr/bin/env python

#Import Necessary Packages
import os
import os.path
import sys
import yaml
import heapq
import operator

#####################NGRAM ITERATOR###################################################
class LanguageFile:
    #Class That Loops Through Characters In Each Language File
    #Where Each Iteration Corresponds To A Different N-Gram Size.

    #Initialize Object
    def __init__(self, ngramFile, nGms):
        #Initialize Class Attributes
        self.line = None
        self.fPos = -1
        self.file = ngramFile
        #Iterator To Get Each Character In Each Line, N-Gram Count, Blank Symbol, Current Gram
        self.numGrams = nGms
        self.switchBlank = '_'
        self.gram = self.switchBlank * self.numGrams
        self.include = '\''

    #Iter Method To Return Current N-Gram Iterator
    def __iter__(self):
        return self

    #Method To Get The Next Character In The File
    def next(self):
        try:
            #Get The Next Set Of Characters
            charArray = self.extractLine().lower()
        except:
        #If Nothing Is In Character Array    
            charArray = None
        if charArray is None:
            #Stop Iteration
            if self.gram[1:] == self.switchBlank * (self.numGrams - 1):
                raise StopIteration
            else:
                self.gram = self.gram[1:] + self.switchBlank
        #If Character Is A  Space, Letter, Replace With Underscore or Add to Character Array
        elif charArray.isspace():
            self.gram = self.gram[1:] + self.switchBlank
        elif charArray.isalpha() or charArray in self.include:
            self.gram = self.gram[1:] + charArray
        else:
            return self.next()
        #Return Gram
        return self.gram

    #Method To Loop Through File and Extract Each Line
    def extractLine(self):
        #If Line Is None, Read In Next Line, Set File Position To 0
        if self.line is None:
            self.line = self.file.readline()
            self.fPos = 0
            #Stop Looping If Hit End Of FIle
            if self.line is None:
                raise StopIteration
        #Add Current Character To 'Array'
        charArray = self.line[self.fPos]
        #Increment Position In File
        self.fPos += 1
        #If Postition In File Equal To Length Of Line
        if self.fPos == len(self.line):
            #Reset Line To None For Next Line Reading
            self.line = None
        #Return Line Of Characters
        return charArray

##############NGRAM PROFILE CLASS######################

#NGram Profile Class
class ngProfile:

    #NGram Profile Constructor
    def __init__(self, gramList, name=None):
        #Create An NGram Profile Dictionary
        self.profile = dict()
        #Set The Grams For The Profile
        for k in xrange(len(gramList)):
            self.profile[gramList[k]] = k
        #Set The Current Language
        self.language = name

    #Method To Compute Distance Using Out-Of-Place Measure
    def compare(self, udLang):
        
        #Initialize Score To 0
        distTotal = 0
        #Set The Max Score To The Max Of The Two Profiles Being Compared
        max_score = max(len(self.profile), len(udLang.profile))
        print("\n---------------------------------COMPARING----------------------------------------")
        print 'Testing Profile: ', udLang.language
        print 'Defined Profile: ', self.language
        #For Each Word And Its Position In The Read In Profile
        for gram, position in udLang.profile.iteritems():
            #Set The Score To The Max Score
            score = max_score
            #If The Word Is In The Profile
            if gram in self.profile:
                #Set The Score As Difference
                score = abs(position - self.profile[gram])
                #Add Score To Total Score
            distTotal += score
        #Return Total Score
        print 'Out-of-Place Distance Score: ', distTotal
        return distTotal

#Method To Build N-Gram Character Profile, Default Values Of 5 N-Grams and A Profile Size Of 300
def ngramProfile(ngramFile, ngramSize=5, maxCount=300):

    #Make Count Dictionary and Gram List
    gramCount = dict()
    nGramList = list()
    #For Each N-Gram In The N-Gram Range
    for ngram in xrange(1, ngramSize + 1):
        #Go To Beginning Of File
        ngramFile.seek(0)
        #Set The N-Gram Iterator
        gramList = LanguageFile(ngramFile, ngram)
        #For Each Gram In The Iterator
        for gram in gramList:
            #Set The Gram To The Count
            gramCount[gram] = gramCount.get(gram, 0) + 1
    #Set Counts Dictionary To The Largest 300 Items
    gramCount = heapq.nlargest(maxCount, gramCount.iteritems(), key=lambda item: item[1])

    #For Each Element In Gram Count, Append Them To Gram List
    for count in gramCount:
        nGramList.append(count[0])
    #Return The Grams For The Profile
    return ngProfile(nGramList)

#Method To Print To Output File
def writeProfile(profile, path):
    with open(path, 'w') as ngramFile:
        print 'Profile: ', yaml.dump(profile.profile)
        ngramFile.write(yaml.dump(profile))

#Method To Open File For Result Writing
def sortProfile(path):
    with open(path, 'r') as ngramFile:
        return yaml.load(ngramFile)



#########################################################TRAINING#############################################################

#Method To Begin Training The Model
def trainModel(inputDir, outputDir=None):
    
    # Read All Files To Be Used For Training
    #Create A List Object To Hold The Training Path, Model Path, And Languages
    tModelPath = list()
    modList = list()
    languages = list()

    #For Each File In The Input Foler
    for name in os.listdir(inputDir):
        #Set The Path Variable For The Training File
        training_path = os.path.join(inputDir, name)
        #print("TRAINING PATH: ", training_path)
        #If Training File Is Valid File
        if os.path.isfile(training_path):
        
    #Pick Off The Filename From The Training Path
            language = os.path.splitext(name)[0]
            #print("LANGUAGE: ", language)
            #Add Filename To Languages List
            languages.append(language)
            #Add Training Path To Training Paths List
            tModelPath.append(training_path)
            #Add Model Path To Model Path List
            modList.append(os.path.join(outputDir, language + '.yaml'))

    #Build The Language Models
    #Create Zip Object To Associate Training Path, Model Path, And Languages
    #For Each Zip Object
    for data, model, language in zip(tModelPath, modList, languages):
        #Open Training File For Reading
        with open(data, 'r') as f:
            #Print File We Are Training With
            print 'Training File:', data.split('/')[1]
            print 'Training Language: ', data.split('/')[1].split('.')[0]
            #Add Training Data To N-Gram Profile
            print 'Building Profile For: ', data.split('/')[1].split('.')[0]
            profile = ngramProfile(f)
            #Set The Profile Language
            profile.language = language
            #Write Profile 
            writeProfile(profile, model)



######################TESTING###################################
#Read The Models Of The Folder
def getProfile(proDir):
    #Set The Model Paths
    #modList = ioutils.list_files_only(proDir)
    modList = filter(os.path.isfile, [os.path.join(proDir, name) for name in os.listdir(proDir)])
    #Create A List For The Models
    profiles = list()
    #For Each Model In The Model Paths List
    for model in modList:
        #Append The Model Profile To The Models List
        profiles.append(sortProfile(model))
    #Return The Models List
    return profiles

#Method To Identify The Language Under Consideration
def predictLanguage(langPros, unknownLang):
    
    #Set The Minimum Distance, Initialize Best Model
    minDist = sys.maxint
    bestPredict = None

    #For Each Model In The Models List
    for profile in langPros:
        #Find The Distance Between Models
        distance = profile.compare(unknownLang)

        #If The Calculated Distance Is Less Than The Minimum Distance
        if distance < minDist:
            #Set The Minimum Distance To Current Distance
            minDist = distance
            #Update The Best Model To The Current Model
            bestPredict = profile

    #Return The Best Model Language
    return bestPredict.language


#Method To Test The Profiles
def testModel(langPros, proDir):
    
    #Initialize The Total Correct, Not Correct, And Create Confusion Matrix
    langTotal = 0
    matchedLangs = 0

    #Set The Paths Variable
    langFiles = filter(os.path.isfile, [os.path.join(proDir, name) for name in os.listdir(proDir)])
    
    #For Each Path In Paths
    for lang in langFiles:
        #Increment The Total Number Of Languages
        langTotal += 1
        #With The File Open
        with open(lang, 'r') as unknown:
            #Print The File Being Processed
            print 'Currently Testing: ', lang.split('/')[1]
            #Build The Profile
            unknownLang = ngramProfile(unknown)
            unknownLang.language = os.path.splitext(os.path.basename(lang))[0].split('-')[0]
    
        #Predict The Language Being Used
        print("\n++++++++++++++++++++++++++++++++++++++++++++++++++IDENTIFYING LANGUAGE+++++++++++++++++++++++++++++++++++++++++++++++++++")
        langPrediction = predictLanguage(langPros, unknownLang)
        #Print The Predicted And Expected Languages
        print("\n====================================================================================")
        print 'Expected Language: ', unknownLang.language
        print 'Language Prediction: ', langPrediction
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        
        #If Language Is Correct, Increment Correct Counter
        if langPrediction == unknownLang.language:
            matchedLangs += 1
            
    #Print Accuracy Of Model
    print 'Correct / Total = ', matchedLangs / langTotal
    print '%ACCURATE: ', matchedLangs * 1.0 / langTotal


#Begin Program Execution

print("*****************************************PROGRAM START*********************************************************************\n")
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Training Model^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
trainModel('training', 'profiles')
print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Testing Model^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n")
profiles = getProfile('profiles')
testModel(profiles, 'testing')

