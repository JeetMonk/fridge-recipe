import os
import csv
from datetime import datetime, timedelta
import pandas
import json
import numpy as np
import sys
import requests
from starlette.applications import Starlette
from starlette.responses import UJSONResponse
import uvicorn


cwd = os.getcwd()
fridgeFileName = 'my-fridge.csv'
#fridgeFileName = ''
#fridgeFileName = sys.argv[1]
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
            #print("Invalid quantity for this content, throw to exception")
            invalidContent = content.copy()
            invalidContent.append('invalid quantity')
            fridgeContentExceptionList.append(invalidContent)
            continue
        try:
            expireDate = datetime.strptime(expireDate, "%d/%m/%Y")
        except:
            try:
                expireDate = datetime.strptime(expireDate, "%Y-%m-%d")
            except:
                #print("Invalid used-by-date for this content, throw to exception")
                invalidContent = content.copy()
                invalidContent.append('invalid used-by-date')
                fridgeContentExceptionList.append(invalidContent)
                continue

        ## passed validation
        ingredient = {'item': item.lower(), 'quantity': quantity, 'unit': unit.lower(), 'expireDate':expireDate}
        contentDF = contentDF.append(ingredient, ignore_index=True)

    ## diplay exception ingredient
    if not fridgeContentExceptionList:
        print("\nAll ingredients in fridge file {} are valid\n".format(fridgeFileName))
    else:
        print("\nFollowing ingredients in fridge file {} are invalid:".format(fridgeFileName))
        print(fridgeContentExceptionList)
        print("\n")

    return contentDF



def checkFridge(ingredientDF):
    ingredientDisplayDF = ingredientDF.copy()
    #print(ingredientDisplayDF)
    currentDT = datetime.now()
    currentDate = currentDT.strftime("%Y-%m-%d")
    ingredientDisplayDF['status'] = np.where(ingredientDisplayDF['expireDate']>=currentDate, 'good', 'expired')
    ingredientDisplayDF['expireDate']=ingredientDisplayDF['expireDate'].astype(str)
    ingredientList = ingredientDisplayDF[['item','quantity','unit','expireDate','status']].to_dict(orient='records')
    return ingredientList



def updateFridgeContentFile():
    ingredientDF.to_csv(cwd+'/'+fridgeFileName, header=False, columns=["item","quantity","unit","expireDate"], index = False)
    return



def addToFridgeContent(addToFridgeContentList):
    global ingredientDF
    
    for content in addToFridgeContentList:
        item = content['item'].lower()
        quantity = float(content['quantity'])
        unit = content['unit'].lower()
        expireDate = datetime.strptime(content['expireDate'], "%Y-%m-%d")
        ingredient = {'item': item, 'quantity': quantity, 'unit': unit, 'expireDate':expireDate}
        ## append to the master DF
        ## the ingredient is new
        if ingredientDF.loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)].empty:
            ingredientDF = ingredientDF.append(ingredient, ignore_index=True)
        ## the ingredient is same the existing
        else:
            currentQuantity = ingredientDF['quantity'].loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)].min()
            newQuantity = currentQuantity + quantity
            ingredientDF['quantity'].loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)] = newQuantity
    ## update fridge file
    updateFridgeContentFile()
    returningredientList = checkFridge(ingredientDF)
    return returningredientList



def takeoutFridgeContent(deleteFromFridgeContentList):
    global ingredientDF
    
    for content in deleteFromFridgeContentList:
        item = content['item'].lower()
        quantity = float(content['quantity'])
        unit = content['unit'].lower()
        expireDate = datetime.strptime(content['expireDate'], "%Y-%m-%d")

        ## not found the ingredient
        if ingredientDF.loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)].empty:
            None
        ## found the ingredient
        else:
            currentQuantity = ingredientDF['quantity'].loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)].min()
            ## have more quantity
            if currentQuantity > quantity:
                newQuantity = currentQuantity - quantity
                ingredientDF['quantity'].loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)] = newQuantity
            ## take all the quantity    
            else:
                ingredientDF.drop(ingredientDF.loc[(ingredientDF['item'] == item) & (ingredientDF['unit'] == unit) & (ingredientDF['expireDate'] == expireDate)].index, inplace=True)
        
    ## update fridge file
    updateFridgeContentFile()
    returningredientList = checkFridge(ingredientDF)
    return returningredientList



def handleRecipe(inputRecipe,ingredientDF):
    ## read the input recipe
    #recipeList = json.loads(inputRecipe)
    recipeList = inputRecipe
    currentDT = datetime.now()
    currentDate = currentDT.strftime("%Y-%m-%d")
    recipeostCheckList = []
    
    ## validate each recipe
    for recipe in recipeList:
        recipeName = recipe['name']
        expireDateList = []
        recipeFlage = 'Y'
        recipePostCheckDict = {}

        ## check each ingredient of the recipe
        for ingredient in recipe['ingredients']:
            item = ingredient['item']
            quantity = ingredient['quantity']
            unit = ingredient['unit-of-measure']

            ## found eligible ingredient
            if ingredientDF['item'].loc[(ingredientDF['expireDate'] >= currentDate) & (ingredientDF['unit'] == unit) & (ingredientDF['quantity'] >= float(quantity))].isin([item]).any():
                expireDate = ingredientDF['expireDate'].loc[(ingredientDF['item'] == item) & (ingredientDF['expireDate'] >= currentDate) & (ingredientDF['unit'] == unit) & (ingredientDF['quantity'] >= float(quantity))].min()
                expireDateList.append(expireDate)
            ## no eligible ingredient
            else:
                recipeFlage = 'N'
                expireDateList.append(None)

        try:
            ClosestUseByDate = min(expireDate for expireDate in expireDateList if expireDate is not None)
        except:
            ClosestUseByDate = None

        recipePostCheckDict = {'recipe': recipeName, 'available': recipeFlage, 'closestUseByDate':str(ClosestUseByDate)}
        recipeostCheckList.append(recipePostCheckDict)

    ## populate API return dict
    ## get all the available recipes
    recipeAvailableList = []
    for recipeItem in recipeostCheckList:
        recipeAvailableList.append(recipeItem) if recipeItem['available'] == 'Y' else None
    ## populate the preferred recipe
    try:
        preferRecipe = min(recipeAvailableList, key=lambda x:x['closestUseByDate']).copy()
        del preferRecipe['available']
    except:
        preferRecipe = None

    feedbackRecipeDict = {'preferredRecipe': preferRecipe, 'allReceivedRecipe': recipeostCheckList}
    return feedbackRecipeDict
    

async def lookIntoFridge(request):
    returnDict = checkFridge(ingredientDF)
    return UJSONResponse(returnDict)


async def checkRecipe(request):
    body = await request.json()
    print("body:",body)
    returnDict = handleRecipe(body,ingredientDF)
    return UJSONResponse(returnDict)


async def addIngredient(request):
    body = await request.json()
    print("body:",body)
    returnDict = addToFridgeContent(body)
    return UJSONResponse(returnDict)


async def deleteIngredient(request):
    body = await request.json()
    print("body:",body)
    returnDict = takeoutFridgeContent(body)
    return UJSONResponse(returnDict)

#################################### MAIN ####################################

app = Starlette()
app.add_route("/check-fridge", lookIntoFridge, methods=["GET"])
app.add_route("/check-recipe", checkRecipe, methods=["POST"])
app.add_route("/add-ingredient", addIngredient, methods=["POST"])
app.add_route("/take-ingredient", deleteIngredient, methods=["POST"])

if __name__ == '__main__':
    ## read the fridge file as the initial load
    try:
        fridgeContentRawList = loadFridgeFile(cwd+'/'+fridgeFileName)
    except:
        print("File not found! Terminates the program.")
        exit()

    #print("fridgeContentRawList:\n",fridgeContentRawList)
    ## validate the fridge file and generate the ingredient dictionary
    ingredientDF = validateFridgeContent(fridgeContentRawList)
    #print("\nThe current ingredient: \n{}".format(ingredientDF))

    ## set API
    uvicorn.run(app, host='localhost', port=5000)
