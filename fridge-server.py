import os
import csv
from datetime import datetime, timedelta
import pandas
import json
import numpy as np


cwd = os.getcwd()
fridgeFileName = 'my-fridge.csv'
fridgeContentRawList = []
fridgeContentExceptionList = []
ingredientDF = pandas.DataFrame()


#################################### FUNCTION ####################################
## initially read the fridge file
def loadFridgeFile(fileNameFullPath):
    with open(fileNameFullPath, 'r') as fridgeFile:
        fridgeContent = csv.reader(fridgeFile, delimiter=',')
        for content in fridgeContent:
            fridgeContentRawList.append(content)
    return fridgeContentRawList


## validate fridge content
def validateFridgeContent(fridgeContentRawList):
    contentDF = pandas.DataFrame()
    
    ## check for each content
    for content in fridgeContentRawList:
        ## check number of information in each content
        if len(content) != 4:
            print("No enought information for this content,throw to exception")
            fridgeContentExceptionList.append(content.append('No enought information'))
            continue

        ## check for each information type
        (item,quantity,unit,expireDate) = content
        try:
            quantity = float(quantity)
        except:
            print("Invalid quantity for this content, throw to exception")
            fridgeContentExceptionList.append(content.append('Invalid quantity'))
            continue
        try:
            expireDate = datetime.strptime(expireDate, "%d/%m/%Y")
        except:
            print("Invalid used-by-date for this content, throw to exception")
            fridgeContentExceptionList.append(content.append('Invalid used-by-date'))
            continue
            
        ## passed validation
        ingredient = {'item': item, 'quantity': quantity, 'unit': unit, 'expireDate':expireDate}
        contentDF = contentDF.append(ingredient, ignore_index=True)
    return contentDF


def updateFridgeContentFile():
    print("This will update fridge content file")



def addToFridgeContent(addToFridgeContent):
    global ingredientDF
    
    ## read add content
    
    ## validate add content
    
    ## add to df
    
    ## update fridge file -> call updateFridgeContentFile()
    
    print("This will add content to fridge.")
    


def takeoutFridgeContent():
    global ingredientDF
    
    ## read delete content
    
    ## validate delete content
    
    ## delete content
    
    ## update fridge file -> call updateFridgeContentFile()
    
    print("This will take content out of fridge")
        

def checkFridge():
    ingredientDisplayDF = ingredientDF.copy()
    currentDT = datetime.now()
    currentDate = currentDT.strftime("%Y-%m-%d")
    ingredientDisplayDF['status'] = np.where(ingredientDisplayDF['expireDate']>=currentDate, 'Good', 'Expired')
    ingredientList = ingredientDisplayDF[['item','quantity','unit','expireDate','status']].to_dict(orient='records')
    return ingredientList
    
    

    
def handleRecipe(inputRecipe):
    ## read the input recipe
    recipeList = json.loads(inputRecipe)
    currentDT = datetime.now()
    currentDate = currentDT.strftime("%Y-%m-%d")
    availableRecipeList = []
    
    ## validate each recipe
    for recipe in recipeList:
        recipeName = recipe['name']
        expireDateList = []
        recipeFlage = 'Y'
        availableRecipeDict = {}

        for ingredient in recipe['ingredients']:
            item = ingredient['item']
            quantity = ingredient['quantity']
            unit = ingredient['unit-of-measure']
            if ingredientDF['item'].loc[(ingredientDF['expireDate'] >= currentDate) & (ingredientDF['unit'] == unit) & (ingredientDF['quantity'] >= float(quantity))].isin([item]).any():
                expireDate = ingredientDF['expireDate'].loc[(ingredientDF['item'] == item) & (ingredientDF['expireDate'] >= currentDate) & (ingredientDF['unit'] == unit) & (ingredientDF['quantity'] >= float(quantity))].min()
                expireDateList.append(expireDate)
            else:
                recipeFlage = 'N'
        availableRecipeDict = {'recipe': recipeName, 'available': recipeFlage, 'closestUseByDate':str(min(expireDateList))}
        availableRecipeList.append(availableRecipeDict)

    ## populate the preferred recipe
    preferRecipe = min(availableRecipeList, key=lambda x:x['closestUseByDate']).copy()
    del preferRecipe['available']
    feedbackRecipeDict = {'preferredRecipe': preferRecipe, 'allReceivedRecipe': availableRecipeList}
    return feedbackRecipeDict
    

#################################### MAIN ####################################

# if __name__ == '__main__':
#     ## read the fridge file as the initial load

try:
    fridgeContentRawList = loadFridgeFile(cwd+'/'+fridgeFileName)
except:
    print("File not found! Terminates the program.")

## validate the fridge file and generate the ingredient dictionary
ingredientDF = validateFridgeContent(fridgeContentRawList)
print("\nThe current ingredient: \n{}".format(ingredientDF))