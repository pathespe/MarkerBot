# -*- coding: utf-8 -*-

# calculate length of list
def list_length(somelist):
    return(len(somelist))
    
#calculate sum of all numbers
def list_sum(somelist):
    return(sum(somelist))

# maximum
def list_max(somelist):
    return(max(somelist))

# minimum
def list_min(somelist):
    return(min(somelist))
    
# mean
def list_mean(somelist):
    return(sum(somelist)/len(somelist))

# square map
def square_map(itemList):
    squares = []
    for item in itemList:
        squares.append(item**2)
    return(squares)
  
# apppend check
def my_append(somelist, animal):
    if not animal in somelist:
        somelist.append(animal)
        return(somelist)
    else:
        return(somelist)
  
# pretty print
def pprint(dictionary):
    print('{')
    for key, value in dictionary.items():
        print('\t{0}: {1}'.format(key, value))
    print('}')

# into the wild
def fill_backpack(itemDictionary):
    # set up an empty bag
    backpack = {
        u'items': [],
        u'weight': 0
        }

    weight_limit = 6

    for item in itemDictionary:
        # check if the item fits in the backpack
        if item[u'weight'] + backpack[u'weight'] < weight_limit:
            backpack[u'items'].append(item[u'name']) # add item to backpack
            backpack[u'weight'] += item[u'weight'] # update the weight of the backpack
    backpack[u'weight'] = round(backpack[u'weight'], 2)
    return backpack

# def fill_backpack(itemDictionary):
#     # set up an empty bag
#     backpack = {
#         u'items': [],
#         u'weight': 0
#         }

#     weight_limit = 6

#     itemDictionary = sorted(itemDictionary, key=lambda k: k[u'weight'])
#     print(itemDictionary)
#     for item in itemDictionary:
#         # check if the item fits in the backpack
#         if item[u'weight'] + backpack[u'weight'] < weight_limit:
#             backpack[u'items'].append(item[u'name']) # add item to backpack
#             backpack[u'weight'] += item[u'weight'] # update the weight of the backpack
    
#     backpack[u'items'].sort()
#     return backpack

# print list_length(*[[1,2,3]])