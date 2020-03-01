# Fridge and Recipe
Fridge server with API functionalities to verify recipe, in addtion add or remove ingredients from fridge by API calls.


## manual guide

### Running Project.
This project contains mainly one program. <br>
1. fridge server (fridge_recipe.py) <br>

#### Start up HTTP server (runs at backend)
Start the main program by giving the initial fridge ingredients file (the file should be in the same dictory as the program).
> python3 fridge_recipe.py  my-fridge.csv <br>

This will start the fridge server that allows user to interact with it by API calls.. <br>


### Interact with Elevators
Once the main program starts, there are 4 API's will be available to interact with the elevators. <br>
There are 1 main API  and 3 additional API's. <br>

#### main recipe API
recipe API to POST recipe(s) and receive feedback with all recipe availabilites and preferred recipe. <br>


#### additional APIs
1. fridge display API to display all the ingredients that are currently in fridge. <br>
2. add ingredients API to simulate adding ingredients to the fridge and display all the ingredients in the fridge after added. <br>
3. remove ingredients API to simulate taking ingredients out of the fridge and display all the ingredients in the fridge after taken. <br>



## API Manual

*All above 4 APIs can be called by using Postman.

### recipe API
POST http://localhost:5000/check-recipe
Body (raw json): <br>
[
  {
    "name": "Toasted Cheese",
    "ingredients": [
      {
        "item": "bread",
        "quantity": "2",
        "unit-of-measure": "slices"
      },
      {
        "item": "cheese",
        "quantity": "3",
        "unit-of-measure": "slices"
      }
    ]
  },
  {
    "name": "Vegemite Sandwich",
    "ingredients": [
      {
        "item": "bread",
        "quantity": "2",
        "unit-of-measure": "slices"
      },
      {
        "item": "vegemite",
        "quantity": "100",
        "unit-of-measure": "grams"
      }
    ]
  }
]

### fridge display API
GET http://localhost:5000/check-fridge 

### add ingredients to fridge API
POST http://localhost:5000/add-ingredient
Body (raw json): <br>
[
    {
        "item": "apple",
        "quantity": 500.0,
        "unit": "grams",
        "expireDate": "2020-06-25"
    },
    {
        "item": "egg",
        "quantity": 100.0,
        "unit": "each",
        "expireDate": "2020-06-25"
    }
]

### take out ingredients from fridge API
POST http://localhost:5000/take-ingredient
Body (raw json): <br>
[
    {
        "item": "cheese",
        "quantity": 1.0,
        "unit": "slices",
        "expireDate": "2016-06-02"
    },
    {
        "item": "apple",
        "quantity": 30.0,
        "unit": "grams",
        "expireDate": "2020-06-25"
    }
]
<br><br>

> Any above API which will change the ingredients of the fridge will also update the fridge ingredients file (my-fridge.csv).