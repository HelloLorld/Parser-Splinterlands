import os
import requests
import json
import collections


# Обращение к api, получение боев
def getListBattles(user="haoge"):
    req = requests.get(
        url="https://api.splinterlands.io/battle/history?player=" + user)
    jsonreq = json.loads(req.text)
    jsonbattles = jsonreq["battles"]
    return jsonbattles

# Проверка полученных боев


def checkBattles(list=[], needRules=[], needMana=[], user="", summoners=[]):
    jsonBattles = getListBattles(user=user)
    flagOfMana = False
    if (len(needMana) != 0):
        flagOfMana = True
    flagOfRules = False
    if (len(needRules) != 0):
        flagOfRules = True
    for battle in jsonBattles:
        rules = battle["ruleset"].lower()
        if flagOfRules:
            if (rulesInNeedRules(rules=rules, needRules=needRules)):
                descr = checkingMana(
                    battle=battle, flagOfMana=flagOfMana, needMana=needMana, user=user, summoners=summoners)
                if (descr != ""):
                    if (descr == "All mana found"):
                        return list
                    writeIntoList(list=list, decribeBattle=descr, rule=rules)
            else:
                continue
        else:
            descr = checkingMana(
                battle=battle, flagOfMana=flagOfMana, needMana=needMana, user=user, summoners=summoners)
            if (descr != ""):
                if (descr == "All mana found"):
                    return list
                writeIntoList(list=list, decribeBattle=descr, rule=rules)
    return list


def writeIntoList(list=[], decribeBattle="", rule=""):
    dictBattles = {}
    for i in range(len(list)):
        if (list[i].get("rule").find(rule) != -1):
            dictBattles = list[i]
            dictBattles[decribeBattle[:4].replace('"', "")] = decribeBattle[5:]
            list[i] = dictBattles
            return list
    dictBattles["rule"] = rule
    dictBattles[decribeBattle[:4].replace('"', "")] = decribeBattle[5:]
    list.append(dictBattles)
    return list


# Проверка входит ли правило в нужные


def rulesInNeedRules(rules, needRules=[]):
    for rule in needRules:
        if (rules.find(rule) != -1):
            # print("Find rule")
            return True
    return False

# Провека входит ли мана в диапазон


def checkingMana(battle, flagOfMana, needMana=[], user="", summoners=[]):
    mana = battle["mana_cap"]
    if (flagOfMana):
        if (mana in needMana):
            if (len(needMana) == 0):
                return "All mana found"
            needMana.remove(mana)
            return getDescrabingOfBattle(battle, user=user,summoners=summoners)
        else:
            return ""
    else:
        return getDescrabingOfBattle(battle, user, summoners=summoners)

# Получение описания битвы


def getDescrabingOfBattle(battle, user="", summoners=[]):
    mana = battle["mana_cap"]
    describeBattle = str(
        getInfoAboutBattle(battle["details"], user=user, summoners=summoners))
    # print(describeBattle)
    if (describeBattle == ""):
        return ""
    else:
        return '"' + \
            str(mana) + '":' + describeBattle

# Получение информации о конкретном бое


def getInfoAboutBattle(battle, user="", summoners=[]):
    jsonBattle = json.loads(battle.replace("\\", ""))
    isSurrender = False
    try:
        jsonBattle["type"]
        isSurrender = True
    except Exception as ex:
        isSurrender = False
    teams = []
    if (not isSurrender):
        teams.append((jsonBattle["team1"]))
        teams.append((jsonBattle["team2"]))
    else:
        return ""
    for team in teams:
        if (team.get("player").lower() == user.lower()):
            summonerId = team.get("summoner").get("card_detail_id")
            if (summonerId in summoners):
                monstersDict = team.get("monsters")
                monstersId = []
                for monster in monstersDict:
                    monstersId.append(monster.get("card_detail_id"))
                describeBattle = '"' + str(summonerId) + ','
                for id in monstersId:
                    describeBattle += str(id) + ','
                return describeBattle[:-2]+'"'
            else:
                return ""

# Запись всех результатов в файл


def writeResultInFile(foundBattles: list):
    for dictBattle in foundBattles:
        dictBattle = collections.OrderedDict(sorted(dictBattle.items()))
        completeName = os.path.join("rules", dictBattle.get("rule")+".txt")
        with open(completeName, 'w') as f:
            if (len(dictBattle) == 0):
                f.write("Battles not found")
            else:
                for (key, value) in dictBattle.items():
                    if key == "rule":
                        continue
                    f.write('"%s":%s\n' % (key, value))
        f.close()


def main():
    needMana = False
    mana = []
    print("You need mana?")
    if (input().lower().find("y") != -1):
        needMana = True
    if (needMana):
        number = int(input("Enter mana: "))
        while (number != 0):
            mana.append(number)
            number = int(input())
    rules = []
    rule = input("Enter rule: ").lower()
    while (rule != "end"):
        rules.append(rule)
        rule = input("Enter rule: ").lower()
    user = input("Enter nickname: ")
    bottom = int(input("Enter bottom: "))
    top = int(input("Enter top: "))
    allBattles = []
    summoners = []
    for i in range(2):
        summoners.append(int(input("Enter Id of summoner: ")))
    for i in range(bottom, top+1):
        print(user+str(i))
        allBattles = checkBattles(
            list=allBattles, needRules=rules, needMana=mana, user=user+str(i), summoners=summoners)
        if (needMana and len(mana) == 0):
            break
        print("##############")
    writeResultInFile(allBattles)


if __name__ == "__main__":
    main()
