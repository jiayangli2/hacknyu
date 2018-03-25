import io
import os
import copy


from google.cloud import vision
from google.cloud.vision import types


# restaurant dic that contains res restaurant name and it recipe.
restaurant = {"shakeshack" : {"shackburger": ['Shack Burger',490],
                              "doubleshackburger":770,
                              "shacksmoke": ['Smoke Shack Burger', 630],
                              "doublesmokeshack":910,
                              "shroomshack" :['Shroom Shack Burger',630],
                              "shackstack":770,
                              "hamburger":360,
                              "doublehamburger":570,
                              "shackcagodog":335,
                              "cheesefries":['Cheese Fries',685],
                              "regsoda":['Small Fountain Soda',180],
                              "regrootbeer":180,
                              'icedregtea': ['Small Iced Tea',0]}, }

def appex_same_number(n1,n2):
    if n1-n2 <= 15 and n1-n2 > -15:
        return True
    else:
        return False

def is_in_same_line(cordy1, cordy2):
    if appex_same_number(cordy1[0].y,cordy2[0].y) == True and \
                    appex_same_number(cordy1[1].y,cordy2[1].y) == True and \
                    appex_same_number(cordy1[2].y,cordy2[2].y) == True and \
                    appex_same_number(cordy1[3].y,cordy2[3].y) == True:
        return True
    else:
        return False

def reorder(d):
    dd = sorted(d,key=lambda d : d[1][0].x)
    new_d = sorted(dd,key=lambda d : d[1][0].y)
    return new_d

def deleteDuplicatedElementFromList(list):
    resultList = []
    for item in list:
        if not item in resultList:
            resultList.append(item)
    return resultList


# Imports the Google Cloud client library
# function return a list contant text and location in the pic. The list item is like [name,[x:,y:]*4]
def detect_text(img):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    content=img

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    d = []
    for text in texts:
        d.append([text.description, text.bounding_poly.vertices])

    d.pop(0)
    return d
def isnumber(string):
    try:
        float(string)
        return True
    except:
        return False

def convertNumber(string):
    return float(string)
def filtrate_useful_information(d):
    all_line = []#cotain all text in the paper, separate into different lines
    each_line = []#contain each line context
    restaurantName = ''
    for i in range(1,len(d)):
        if is_in_same_line(d[i][1],d[i-1][1]) == True:
            each_line.append(d[i-1][0])
            each_line.append(d[i][0])
        elif is_in_same_line(d[i][1],d[i-1][1]) == False:
            copy_each_line = copy.deepcopy(each_line)
            all_line.append(copy_each_line)
            each_line[:] = []


    for i in range(len(all_line)):
        all_line[i] = deleteDuplicatedElementFromList(all_line[i])

    final_out_list=[]
    each_item = []
    for i in range(len(all_line)):
        oneLineText = "".join(all_line[i]).lower()
        if oneLineText.isalpha():
            if oneLineText in restaurant:
                restaurantName = oneLineText
        else:
            alphaList = []
            price = 0
            for item in all_line[i]:
                if ")" in item:
                    item =item.replace(')','')
                if item.isalpha():
                    alphaList.append(item)
                elif item.isalpha()==False and isnumber(item) == True:
                    price = convertNumber(item)
            food_name_detect = ''.join(sorted(alphaList)).lower()
            if food_name_detect in restaurant[restaurantName]:
                each_item.append(restaurant[restaurantName][food_name_detect][0])
                each_item.append(restaurant[restaurantName][food_name_detect][1])
                each_item.append(price)
        copy_each_item = copy.deepcopy(each_item)
        final_out_list.append(copy_each_item)
        each_item[:] = []

    FINAL_OUT_LIST = []
    for i in final_out_list:
        if i != []:
            FINAL_OUT_LIST.append(i)
    return FINAL_OUT_LIST

def filter(img):
    test_text = detect_text(img)
    new_test_text = reorder(test_text)
    return filtrate_useful_information(new_test_text)



