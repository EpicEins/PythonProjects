import json
import io
import csv
from urllib.request import urlopen


api_link = 'http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName=pro crasta nation'
api_contents = urlopen(api_link)
txt = csv.reader(io.TextIOWrapper(api_contents))
player_dict = []
clan_dict = {'clan': ""}
for clan_member in txt:
    if clan_member[0] == "Clanmate" or clan_member[1] == " Clan Rank" or clan_member[2] == " Total XP" or clan_member[3] == " Kills":
        continue
    value = {
            "Clanmate": str(clan_member[0]),
            "Clan Rank": str(clan_member[1]),
            "Total XP": str(clan_member[2]),
            "Kills": str(clan_member[3])
        }
    player_dict.append(value)
clan_dict['clan'] = player_dict
#print(player_dict)
    
with open('data.json', 'a') as outfile:  
    json.dump(clan_dict, outfile)
clan_list = []
with open('data.json') as data_file:
    data = json.load(data_file)
    #print(data['clan'])
    for i in data['clan']:
        #print(i['Clanmate'])
        clan_list.append(i['Clanmate'])
new_list = []
for i in clan_list:
    i = i.replace('\xa0', ' ')
    new_list.append(i)
print(clan_list)
print(new_list)
