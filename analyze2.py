'''
Code for analyzing retail_25k.dat to extract the most frequent items bought together. 
"Most" defined by a threshold sigma. 
We only consider sets where number of items in set is more than N (default 3)

@author: Arijit Ray 
January 2017
'''
import argparse
import sys
import itertools
from random import shuffle
from threading import Thread
from operator import itemgetter


class AnalyzeDatabase:

    def __init__(self, currState, filename='', data=[], verbose=False):
		#First let's read and make a properly formatted data list
		"Input: filename path"

		self.verbose=verbose
		try:
			allData=[]		
			vocab=[]
			
			with open(filename, 'r') as f:
				for line in f:
					linedata=(line.rstrip()).split(' ')
					vocab.extend(linedata)	
					allData.append(linedata)
			self.allData=allData
			self.vocab=list(set(vocab))
			print("File Successfully loaded")
		except:
			print("Wrong/Empty File Path, assuming custom data was supplied during initialization")

			if data !=[]:
				self.allData=data
				vocab=[]
				for item in data:
				    vocab.extend(item)
				self.vocab=list(set(vocab))
				print("Successfully loaded custom data...")
			else:
				print("Please supply data filepath or list data")
				return False
		'''		
		adjacencyDict=dict()
		for states in self.vocab:
		    adjacencyDict[state]=dict()
		    for ind,item in enumerate(self.allData):
		        if states in item:
		            copy=item
		            for otherStates in copy.remove(state):
		                if otherStates in adjacencyDict[state]:
		                    adjacencyDict[state][otherStates].append(ind)
		                else:
		                    adjacencyDict[state][otherStates]=[ind]
		
		currState['adjacencyDict']=adjacencyDict
		
		self.adjacencyDict=adjacencyDict
		'''                
		    
class naiveAgent(AnalyzeDatabase):
    				
    def analyzeFrequentPairsNaive(self, currState, sigma, N=3):
        #Function to return frequent sets with frequency>=sigma and set size>=N
        "INPUTS: LIST self.allData, INT sigma, INT N"
        
        #one naive way to do this is to keep a dictionary for all possible combinations above N that occurred in the list and ther frequencies. 
        #problem: high time complexiy, but doesn't eat up the whole RAM. 
        
        allData=self.allData
        shuffle(allData)  
        allCombinationsHistogram=dict()
        
        for ind,item in enumerate(allData):
            if len(item)>=N:
                print item
                for i in range(N,len(item)+1):
                    N_combinations=itertools.combinations(item,i)
                    for subset in N_combinations:
                        #print subset
                        if subset not in allCombinationsHistogram:
                            count=1
                            
                            for otherItem in allData[ind+1:len(allData)]:
                                present=True
                                for num in subset:
                                    if num not in otherItem:
                                        present=False
                                        break
                                if present==True:
                                    count+=1
                            if count>=sigma:
                                allCombinationsHistogram[subset]=count
        
        currState['combinationsHist']=allCombinationsHistogram
        
        formattedOutput=[]
        for itemset in allCombinationsHistogram:
            freq=allCombinationsHistogram[itemset]
            data_entry=[]
            data_entry.append(len(itemset))
            data_entry.append(freq)
            data_entry.extend(itemset)
            formattedOutput.append(data_entry)

        return formattedOutput


    def analyzeFrequentPairsMultiThread(self, currState, numThreads, sigma, N=3):
        
        allThreads=[]
        currState['formattedOutput']=[]
        for i in range(numThreads):
            thread=Thread(target=self.threadAnalyze, args=(currState, i, numThreads, sigma, N))
            thread.start()
            allThreads.append(thread)
            
            
        for thread in allThreads:
            thread.join()
        
        return currState


   
    def threadAnalyze(self, currState, threadID, numThreads, sigma, N=3):
        allData=self.allData
        shuffle(allData)  
        allCombinationsHistogram=dict()
        
        for ind,item in enumerate(allData):
            if len(item)>=N:
                #print item
                diff=len(item)-N
                
                for i in range(N+(threadID*diff/numThreads),N+((threadID+1)*diff/numThreads)):
                    N_combinations=itertools.combinations(item,i)
                    for subset in N_combinations:
                        #print subset
                        if subset not in allCombinationsHistogram:
                            count=1
                            
                            for otherItem in allData[ind+1:len(allData)]:
                                present=True
                                for num in subset:
                                    if num not in otherItem:
                                        present=False
                                        break
                                if present==True:
                                    count+=1
                            if count>=sigma:
                                allCombinationsHistogram[subset]=count
        
        #currState['combinationsHist']=allCombinationsHistogram
        
        #formattedOutput=[]
        for itemset in allCombinationsHistogram:
            freq=allCombinationsHistogram[itemset]
            data_entry=[]
            data_entry.append(len(itemset))
            data_entry.append(freq)
            data_entry.extend(itemset)
            currState['formattedOutput'].append(data_entry) #we can do this because append is thread safe in Python, yay!

        
        #return formattedOutput


class DynamicAnalyzeAgent(AnalyzeDatabase):

    def analyzeDynamically(self, currState, sigma, N=3):
        #Function to return frequent sets with frequency>=sigma and set size>=N
        "INPUTS: LIST self.allData, INT sigma, INT N"
        
        #dynamically prune the possible states based on the sigma. 
        
        
        self.sigma=sigma
        tempIndices=dict()
        vocabIndices=dict()
        
        finalPairs=[]
        frontier=[]
        
	    #some stuff to optimise counting
        for ind, items in enumerate(self.allData):
            for item in items:
                if item in tempIndices:
                    tempIndices[item].append(ind)
                else:
                    tempIndices[item]=[ind]
        #TempIndices will end up taking too much RAM, so lets just keep what's necessary
        for key in tempIndices:
            if len(tempIndices[key])>=sigma:
                temp=tempIndices[key]
                vocabIndices[key]=temp
                frontier.append(key)
        tempIndices=None #free up some RAM
        #print vocabIndices
        self.vocabIndices=vocabIndices
        '''
        #print self.vocab
        for item in self.vocab:
            print item
            count=self.countItem(item)
            if count>=sigma:
                frontier.append(item)
                
        #self.vocabIndices=vocabIndices        
        '''
        while frontier!=[]:
            currItem=frontier.pop()
            nextItems=self.getNextStates(currItem)
            
            if len(frontier)%100==0:
                print len(frontier) 
                #print "VocabIndices "+str(len(self.vocabIndices))
            #if (len(finalPairs)+1)%10==0:
             #   print len(finalPairs)
              #  print finalPairs[-5:]
            
            for nextItem in nextItems:
                potentialNextItem=currItem + "_" + nextItem
                #print potentialNextItem
                newItemCount=self.countItem(potentialNextItem)
                
                if newItemCount>=sigma:
                    frontier.append(potentialNextItem)
                    #if len(potentialNextItem.split("_"))>=N:
                     #   finalPairs.append((potentialNextItem,newItemCount))
                        
        finalpairs=[]
        for key in self.vocabIndices:
            l_n=len(key.split("_"))
            l_s=len(self.vocabIndices[key])
            if l_s>=sigma and l_n>=N:
                temp=[]
                temp.append(l_n)
                temp.append(l_s)
                temp.extend(key.split("_"))
                finalpairs.append(temp)
	
        return finalpairs        
                            
    def countItem(self, item):
        #count the occurences of the item in the data
        if item in self.vocabIndices:
            return len(self.vocabIndices[item])
        else:
            tempindices=[]
            tempItems=item.split("_")
            prevItem=tempItems[0:-1]
            searchItem="_".join(prevItem)
            indices=self.vocabIndices[searchItem]
            
            for ind in indices:
                if tempItems[-1] in self.allData[ind]:
                    tempindices.append(ind)
            if len(tempindices)>=self.sigma:
                self.vocabIndices[item]=tempindices        
            return len(tempindices)
    
    def getNextStates(self, currItem):
        #get the next plausible items by which we can extend the current Item
        tempItem=currItem.split("_")
        latestItem=tempItem[-1]
        index=self.vocab.index(latestItem)
        nextStates=self.vocab[index+1:]
        return nextStates


class FPGrowthAgent(AnalyzeDatabase):

    def FPGrowthAnalyze(self, currState, sigma, N=3):
        #There are implemented FP trees out there in python, but I am going to go ahead and implement my own. 
        self.sigma=sigma
        self.N=N                
        elementCount=dict()
        for items in self.allData:
            for item in items:
                if item in elementCount:
                    elementCount[item]+=1     
                else:
                    elementCount[item]=1
        
        formattedTransactions=[]
        for transactions in self.allData:
            tempTransaction=[]
            for item in transactions:
                tempTransaction.append((item, elementCount[item]))
            tempTransaction.sort(key=lambda x:-x[1])
            formattedTransactions.append(tempTransaction)

        #Now, let's make the fp tree.
        fpTree=dict()
        #currState['formatTrans']=formattedTransactions
        for transaction in formattedTransactions:
            currItem=''
            newItem=''
            for item in transaction:
                newItem+=item[0]+'_'
                if currItem in fpTree:
                    fpTree[currItem]['count']+=1
                    if newItem not in fpTree[currItem]['nextItems']:
                        fpTree[currItem]['nextItems'].append(newItem)
                else:
                    fpTree[currItem]=dict()
                    fpTree[currItem]['count']=1
                    fpTree[currItem]['nextItems']=[newItem]
                currItem=newItem
            if newItem in fpTree:
                fpTree[newItem]['count']+=1
                fpTree[newItem]['nextItems']=[]
            else:
                fpTree[newItem]=dict()
                fpTree[newItem]['count']=1
                fpTree[newItem]['nextItems']=[]

        currState['fptree']=fpTree

        #Now, scan the fpTree for the frequent pairs above sigma. 
        finalPairs=dict()
        self.finalPairs=finalPairs
        sortedItems=[]
        for item in self.vocab:
            if elementCount[item]>=sigma:
                sortedItems.append((item, elementCount[item]))
        sortedItems.sort(key=lambda x:x[1])
        self.sortedItems=sortedItems
        for ind,item in enumerate(sortedItems):
            tempTree=self.pruneTree(fpTree, item)
            #print tempTree
            print "=========INDEX============"+str(ind)
            frontier=[]
            frontier.append([item[0]])
            while frontier!=[]:
                print len(frontier)
                #print frontier
                currItem=frontier.pop()
                nextItems=self.getEligibleNextItems(currItem, tempTree) #this fills in self.finalPairs
                #print nextItems
                frontier.extend(nextItems)
        
        

        return self.finalPairs


    def pruneTree(self,fpTree, item):
        tempTree=dict()
        for transactions in fpTree:
            if transactions!='':
                #print transactions
                #print item
                #print transactions.split("_")[-2]
                if transactions.split("_")[-2]==item[0]:
                    tempTree[transactions]=fpTree[transactions]

        return tempTree


    def getEligibleNextItems(self, currItem, tempTree):
        #print "currItem"
        #print currItem
        items=currItem
        nextItemCounts=dict()
        for transaction in tempTree:
            tempTrans=transaction.split("_")[0:-1]
            present=True
            for item in items:
                if item not in tempTrans:
                    present=False
            if present==True: 
               # tempTrans.reverse()
                for item in tempTrans:
                    if item not in items:
                        if item not in nextItemCounts:
                            nextItemCounts[item]=tempTree[transaction]['count']
                        else:
                            nextItemCounts[item]+=tempTree[transaction]['count']
        finalnextItems=[]
        finalpairs=[]
        for key in nextItemCounts:
            if nextItemCounts[key]>=self.sigma:
                tempnextItem=currItem+[key]
                finalnextItems.append(tempnextItem)
                if len(tempnextItem)>=self.N:
                    tempnextItem.sort(key=int)
                    self.finalPairs["_".join(tempnextItem)]=nextItemCounts[key]


        return finalnextItems
        

                        
if __name__=="__main__":

    currState=dict()  #this state variable will be useful in debugging local function variables. 

    parser=argparse.ArgumentParser(description='input sigma to frequent itemset mining')
    parser.add_argument('--sigma', dest='sigma', help='sigma parameter')
    parser.add_argument("--N", dest="N", help='N')

    if len(sys.argv) <=1:
        print "No arguments specified, running with default N=3 and sigma=4"
        if False: #set True to run a custom data through a naive implementation
            testAnalysis1=naiveAgent(currState, data=[[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4,5],[2,3,4,5],[2,3,4,7],[3,4,7,10],[3,4,7,14,15],[1,3,4,7,8]])
            testAnalysis1.analyzeFrequentPairsNaive(currState, 2)

        if False: #set True to run given data file through a naive implmentation. warning: will take forever and ever and ever....
        	testAnalysis2=naiveAgent(state, filename='retail_25k.dat')
        	output=testAnalysis2.analyzeFrequentPairsNaive(currState, 4)
                          
        if False: # set True to run given data file through naive implementation but multi-threaded. Still might take ages unless you have a supercomputer lying around
        	#testAnalysis3=AnalyzeDatabase(currState, data=[[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4,5],[2,3,4,5],[2,3,4,7],[3,4,7,10],[3,4,7,14,15],[1,3,4,7,8]])
        	testAnalysis3=naiveAgent(currState, filename='retail_25k.dat')
        	output=testAnalysis3.analyzeFrequentPairsMultiThread(currState, 8, 4)

        if True: # set True to run an optimised pruned search type algorithm which "should" work faster. This is similar to a apriori approach with some optimizations for counting
        	#testAnalysis4=AnalyzeDatabase(currState, data=[['1','2','3','4'],['1','2','3','4'],['1','2','3','4'],['1','2','3','4','5'],['2','3','4','5'],['2','3','4','7'],['3','4','7','10'],['3','4','7','14','15'],['1','3','4','7','8']])
        	testAnalysis4=DynamicAnalyzeAgent(currState, filename='retail_25k.dat')
        	output=testAnalysis4.analyzeDynamically(currState, 4)

        if False: #set to True to run FP Growth method for mining frequent pairs. Turns out FP growth takes longer than my dynamic method. There are ways to optimise the FP growth, but I will just use the dynamic agent and submit. 
            #testAnalysis5=FPGrowthAgent(currState, data=[['1','2','3','4'],['1','2','3','4'],['1','2','3','4'],['1','2','3','4','5'],['2','3','4','5'],['2','3','4','7'],['3','4','7','10'],['3','4','7','14','15'],['1','3','4','7','8']])

            testAnalysis5=FPGrowthAgent(currState, filename='retail_25k.dat')
            output=testAnalysis5.FPGrowthAnalyze(currState, 4)
            
    else:
        args=parser.parse_args()
        testAnalysis4=DynamicAnalyzeAgent(currState, filename='retail_25k.dat')
        try:
        	sig=int(args.sigma)
        	N=int(args.N)
        except:
        	print "please enter integer sigma and N"
        	sys.exit()
        output=testAnalysis4.analyzeDynamically(currState, sig, N)

    #output must be the final formatted list that we want to store at this point. 
    try:
    	with open("output_25k.dat","w") as f:
        	for item in output:
        		print>>f, item
        print "Output file: output_25k.dat successfully saved"
    except:	
        print "File saving failed. Make sure you have proper permissions to write output file"
