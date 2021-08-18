import json
import time
f = open("data.json", "r")
jsonData = json.loads(f.read())

allData = jsonData['Sheet1']
pincodes = set()
states = list()
cities = set()


def replaceFromLast(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def getUniqueList(key, allData):
    uniqueList = list()
    for data in allData:
        item = data[key]
        if item not in uniqueList:
            uniqueList.append(item)
    return uniqueList


def mapWithID(uniqueList):

    data = list()
    for item in (uniqueList):
        i = uniqueList.index(item) + 1
        tupledData = (i, item)
        if tupledData not in data:
            data.append(tupledData)

    return data


def findId(string, data):
    if data == None:
        return 1
    for item in data:
        if(item[1] == string):
            return item[0]
    return None


def mapWithParent(matchKey, findKey, data, parentData, allData):
    listData = []
    childFound = []
    for childData in data:
        for globalData in allData:
            if childData[1] == globalData[matchKey] and (childData[1] not in childFound):
                childFound.append(childData[1])
                tupledData = list(childData)
                tupledData.append(findId(
                    globalData[findKey], parentData))
                tupledData = tuple(tupledData)
                if tupledData not in listData:
                    listData.append(tupledData)
    return listData


def getSql(query, data, valuePairs):
    sql = ''
    queryBackup = query
    for item in data:
        keys = valuePairs.keys()
        for key in keys:
            if(0 <= valuePairs[key][0] < len(item)):
                stringValue = str(item[valuePairs[key][0]])
            else:
                stringValue = 1
            if(valuePairs[key][1] == 'int'):
                value = str(stringValue)
            if(valuePairs[key][1] == 'str'):
                value = str("'"+stringValue+"'")
            if(valuePairs[key][1] == 'null'):
                value = 'NULL'
            query = query.replace(key, value)
        sql += query
        query = queryBackup
    return sql


def main():
    cityUniqueList = getUniqueList('City', allData)
    cities_data = mapWithID(cityUniqueList)

    stateUniqueList = getUniqueList('State', allData)
    states_data = mapWithID(stateUniqueList)

    pincodeUniqueList = getUniqueList('Pincode', allData)
    pincodes_data = mapWithID(pincodeUniqueList)

    pre = "INSERT INTO `states`(`id`, `name`, `country_id`, `status`) VALUES "
    query = "(:id,:name,:cid,1),\n"
    post = "; "
    valuePairs = {
        ':id': [0, 'int'],
        ':name': [1, 'str'],
        ':cid': [2, 'int']
    }
    stateSQL = getSql(query, states_data, valuePairs)
    stateSQL = pre+stateSQL+post
    stateSQL = replaceFromLast(stateSQL, ',', '', 1)
    f = open("state.sql", "w")
    f.write(stateSQL)
    f.close()

    cityMappedWithState = mapWithParent(
        'City', 'State', cities_data, states_data, allData)

    pre = "INSERT INTO `cities`(`id`, `state_id`, `name`, `status`) VALUES "
    post = ";"
    query = "(:id,:sid,:name,1),\n"
    valuePairs = {
        ':id': [0, 'int'], ':name': [1, 'str'], ':sid': [2, 'int']
    }
    citySQL = getSql(query, cityMappedWithState, valuePairs)
    citySQL = pre+citySQL+post
    citySQL = replaceFromLast(citySQL, ',', '', 1)
    f = open("city.sql", "w")
    f.write(citySQL)
    f.close()

    pincodeMappedWithCity = mapWithParent(
        'Pincode', 'City', pincodes_data, cities_data, allData)

    pre = "INSERT INTO `pincodes`(`id`, `city_id`, `pincode`, `status`) VALUES "
    query = "(:id,:sid,:name,1),\n"
    post = ";"
    valuePairs = {
        ':id': [0, 'int'], ':name': [1, 'str'], ':sid': [2, 'int']
    }
    pincodeSQL = getSql(query, pincodeMappedWithCity, valuePairs)
    pincodeSQL = pre+pincodeSQL+post
    pincodeSQL = replaceFromLast(pincodeSQL, ',', '', 1)
    f = open("pincode.sql", "w")
    f.write(pincodeSQL)
    f.close()


if __name__ == '__main__':
    start = int(time.time)
    main()
    end = int(time.time())
    print(f"Time Taken: {end-start}")
