import fridge_recipe as fr
#import nose.tools as nose


def test_load_file(filename):
    print("\nTesting fridge file load...")
    returnData = fr.loadFridgeFile(filename)
    return returnData


def test_data_validation(dataList):
    print("\nTesting fridge data validation...")
    returnData = fr.validateFridgeContent(returnData1)
    return returnData


def test_frdige_display(ingredientDF):
    print("\nTesting fridge display...")
    returnData = fr.checkFridge(ingredientDF)
    return returnData

def test_recipe_check(inputRecipe,ingredientDF):
    print("\nTesting recipe check...")
    returnData = fr.handleRecipe(inputRecipe,ingredientDF)
    return returnData

## test load file
returnData1 = test_load_file('my-fridge.csv')
print("\nData read from the fridge file:\n{}".format(returnData1))

## test data validation
returnData2 = test_data_validation(returnData1)
print("\nData post validation:\n{}".format(returnData2))

## test fridge display
returnData3 = test_frdige_display(returnData2)
print("\nFridge display:\n{}".format(returnData3))

## test recipe check
recipeList = [{"name": "Toasted Cheese","ingredients": [{ "item":"bread", "quantity":"2", "unit-of-measure":"slices"},{ "item":"cheese", "quantity":"3", "unit-of-measure":"slices"}]},{"name": "Vegemite Sandwich","ingredients": [{ "item":"bread", "quantity":"2", "unit-of-measure":"slices"},{ "item":"vegemite", "quantity":"100", "unit-of-measure":"grams"}]}]
returnData4 = test_recipe_check(recipeList,returnData2)
print("\nRecipe check result:\n{}".format(returnData4))
