import csv
import sqlite3
import sys
import io
from urllib.request import urlopen
import datetime
#from tabulate import tabulate

day = datetime.datetime.now()
day = day.strftime("%x")

SkillNames = ['Overall', 'Attack', 'Defence', 'Strength', 'Constitution',
                'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting', 
                'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 
                'Herblore', 'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecrafting',
                'Hunter', 'Construction']

def update_member_name(player,new_name):
    try:

        real_player = player
        player = player_to_table(player)
        to_db = [new_name, real_player]
        #update Players_Table
        c.execute(''''UPDATE %s Set 'Name'=? WHERE Name=?''' % player, to_db)
        #update Members_List
        c.execute(''''UPDATE Members_List Set 'Name'=? WHERE Name=?''', to_db)
    except Exception as e:
        print(e)
        print("Possibly could not find player")

def delete_player(New_List):
    for i in New_List:
        real_player = i
        i = player_to_table(i)

        to_db = [real_player]
        c.execute('''DELETE from Members_List where Name=?''', to_db)
        c.execute('''DROP TABLE %s''' % i)
        print(i, "deleted")


def search_duplicates(New_list):
    clan_list = create_clan_list()
    duplicates = []
    for i in clan_list:
        for x in New_list:
            x = x.lower()
            if x == i:
                duplicates.append(x)
                print(x, "seems to be tracking already")
                New_list.remove(x)                
    if len(duplicates) > 1:
        print("These are the duplicates:", duplicates)
    elif len(duplicates) == 1:
        print("There was one duplicate:", duplicates)
    return New_list


def add_new_member(New_List):
    new_members = True
    New_List = search_duplicates(New_List)
    if len(New_List) == 0:
        print("There are no names to add")
    else:
        highscore_search(New_List, new_members)
        for i in New_List:
            update_member_list(i,new_members)


def check_if_new():
    try:
        c.execute('''CREATE TABLE Check_Table
        (Value)''')
        return True
    except Exception as e:
        print(e)
        #in theory this should raise an expection if the clan already has
        #a check_table which would mean it has already been "created"


def initialize_clan(clan):
    new_members = True
    create_member_list(clan)
    clan_list = []
    cont = 1
    counter = 1
    while True:
        try:
            number_names = int(input("Please enter the amount of names you'd like to add: "))
            break
        except:
            print("Please only enter in a number")
    while True:
        if number_names > 1:
            number_names += 1
            while counter != number_names:
                print(counter)
                print(number_names)
                player_string = input("Please enter in a players name: ")
                clan_list.append(player_string)
                counter += 1
                print(clan_list)
            for i in clan_list:
                i = i.lower()
            print(clan_list)
            
  
            break
        else:
            player = input("Please enter the players name: ")
            player = player.lower()
            clan_list.append(player)
            break
    highscore_search(clan_list,new_members)
    for i in clan_list:
        update_member_list(i,new_members)
    print()
    print("end of initialize clan")


def highscore_search(clan_list,new_members):
    for i in clan_list:
        reject_list = []
        counter = 0
        print()
        print("Searching hiscores for", i)
        #print(i)
        api_link = 'https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={0}'.format(i)
        try:
            api_contents = urlopen(api_link)
            data = csv.reader(io.TextIOWrapper(api_contents))
            player = player_to_table(i)
            if new_members is True:
                create_player_table(player)
                for x, skill in zip(data, SkillNames):
                    if counter == 24:
                        break
                    if counter > 0:
                        to_db = [None, SkillNames[counter], x[0], x[1], x[2]]
                        c.execute("INSERT INTO %s VALUES (?,?,?,?,?)" % player, to_db)
                    else:
                        to_db = [i, SkillNames[counter], x[0], x[1], x[2]]
                        c.execute("INSERT INTO %s VALUES (?,?,?,?,?)" % player, to_db)
                    conn.commit()        
                    #print(skill, x)
                    counter += 1
            else:
                value_list = ('Rank', 'Level', 'Experience')
                for x, skill in zip(data, SkillNames):
                    if counter == 24:
                        break
                    to_db = [x[0], SkillNames[counter]]
                    c.execute('''UPDATE %s Set 'Rank'=? WHERE Skill=?''' % player, to_db)
                    to_db = [x[1], SkillNames[counter]]
                    c.execute('''UPDATE %s Set 'Level'=? WHERE Skill=?''' % player, to_db)
                    to_db = [x[2], SkillNames[counter]]
                    c.execute('''UPDATE %s Set 'Experience'=? WHERE Skill=?''' % player, to_db)
                    #print(skill, x)
                    counter += 1
                conn.commit()
        except Exception as e:
            print(e)
            cont = 1
            while cont == 1:
                print(i, "was not found in the highscores")
                print("Was", i, "spelt correctly? ")
                check_again = input("1 for yes, 2 for no: ")
                if check_again == '1':
                    print("This name might not be in the highscores, do you want to add it to not_tracked table?")
                    user_input = input("Please enter a 1 to add to the table, or 2 to remove from clan list: ")
                    if user_input == '1':
                        print("Sorry, this doesn't do anything yet")
                        #add to not_tracked table
                if check_again == '2':
                    clan_list.remove(i)
                    cont = 'end'
            reject_list.append(i)
            cont = 2
            return cont
def calc_clan_XP(i):
    player = player_to_table(i)
    try:
        to_db = [i]
        #Get Initial Experience
        c.execute('SELECT Initial_XP FROM Members_List WHERE Name=?', to_db)
        val = c.fetchone()
        for initial in val:
            initial = int(initial)
        c.execute('SELECT Current_XP FROM Members_List WHERE Name=?', to_db)
        val = c.fetchone()
        for current_xp in val:
            current_xp = int(current_xp)
        
        calc = current_xp - initial
        calc_db = [str(calc), i]
        c.execute('''UPDATE Members_List Set 'Clan_XP'=? WHERE Name=?''', calc_db)
        conn.commit()
    except Exception as e:
        print(e)


        
def create_member_list(clan):
    c.execute('''CREATE TABLE IF NOT EXISTS Members_List
    (Name,Join_Date,Initial_XP,Current_XP,Clan_XP)''')
    conn.commit()

def update_member_list(i, new_members):
    #checks if new_members are being added so that their total xp is added to both
    #Current and Initial XP in the Members_list
    if new_members is True:
        try:
            player = player_to_table(i)
            c.execute('SELECT Experience FROM %s WHERE _rowid_=1' % player)
            val = c.fetchone()
            for y in val:
                #y = total experience from the player's table
                y = int(y)
                to_db = [i, str(day), str(y), str(y), None]
                c.execute("INSERT INTO Members_list VALUES (?,?,?,?,?)", to_db)
                conn.commit()
                #scalc_clan_XP(i)
        except Exception as e:
            print(e)
            print("Player cell not found")

    else:
        try:
            player = player_to_table(i)
            c.execute('SELECT Experience FROM %s WHERE _rowid_=1' % player)
            val = c.fetchone()
            for y in val:
                #y = total experience from the player's table
                y = int(y)
        except:
            print("Player cell not found")
        to_db = [str(y), i]
        c.execute('''UPDATE Members_List Set 'Current_XP'=? WHERE Name=?''', to_db)
        conn.commit()
        #calc_clan_XP(i,new_members)


def create_player_table(player):
    c.execute('''CREATE TABLE IF NOT EXISTS %s
        (Name,Skill,Rank,Level,Experience)''' % player)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def player_to_table(player):
    CI_Table = ''
    
    if hasNumbers(player) is True:
        result = ''
        for i in player:
            if i.isalpha() is True:
                result = result + i
        player = result
    #not sure if I should keep player_number to search
    #player_number = clan_member[0]
    else:
        player = player.replace(" ", "")
        
        #Current Highscore Search
    CI_Table = player + "_CI"
    return CI_Table

def create_clan_list():
    clan_list = []
    while True:
        try:
            c.execute('SELECT Name FROM Members_List')
            val = c.fetchall()
            for i in val:
                for unit in i:
                    clan_list.append(unit)
            break
        except Exception as e:
            print("Error")
            print(e)
            print("Error")
            break
    return clan_list

def display_clan():
    value_list = ('Name', 'Date_Joined', 'Initial_XP', 'Current_XP', 'Clan_XP')
    c.execute('''SELECT * FROM Members_List''')
    rows = c.fetchall()
    for row in rows:
        print()
        print(value_list)
        print(row)
        #for item in row:
            #print(item)



def export_csv(csv_choice):
    if csv_choice == '1':
        ifile = open('Members_List.csv', 'w')
        ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format("Name", 'Join_Date', 'Initial_XP', 'Current_XP', 'Clan_XP'))
        c.execute('''SELECT * FROM Members_List''')
        rows = c.fetchall()
        for row in rows:
            item_list = []
            for item in row:
                item_list.append(item)
            ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format(item_list[0], item_list[1], item_list[2], item_list[3], item_list[4]))
        ifile.close()
    if csv_choice == '2':
        player = input("What player would you like to export: ")
        ifile = open('{0}.csv'.format(player), 'w')
        ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format("Name", 'Skill', 'Rank', 'Level', 'Experience'))
        player = player_to_table(player)
        c.execute('''SELECT * FROM %s''' % player)
        rows = c.fetchall()
        for row in rows:
            item_list = []
            for item in row:
                item_list.append(item)
            ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format(item_list[0], item_list[1], item_list[2], item_list[3], item_list[4]))
        ifile.close()
    if csv_choice == '3':
        clan_list = create_clan_list()
        print(clan_list)
        for player in clan_list:
            ifile = open('{0}.csv'.format(player), 'w')
            ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format("Name", 'Skill', 'Rank', 'Level', 'Experience'))
            player = player_to_table(player)
            c.execute('''SELECT * FROM %s''' % player)
            rows = c.fetchall()
            for row in rows:
                item_list = []
                for item in row:
                    item_list.append(item)
                ifile.write('{0}, {1}, {2}, {3}, {4}\n'.format(item_list[0], item_list[1], item_list[2], item_list[3], item_list[4]))
            ifile.close()
    
def program_features(user_choice):
    if user_choice == '1':
        print('testing')
        clan_list = create_clan_list()
        print(clan_list)
        highscore_search(clan_list,new_members)
    elif user_choice == '2':
        New_List = []
        cont = 1
        counter = 0
        while True:
            try:
                number_names = int(input("Please enter the amount of names you'd like to add: "))
                break
            except:
                print("Please only enter in a number")
        while True:
            if number_names > 1:
                player_string = input("Please enter in a players name: ")
                New_List = player_string.split(", ")
                for i in New_List:
                    i = i.lower()
                break
            else:
                player = input("Please enter the players name: ")
                player = player.lower()
                New_List.append(player)
                break
        add_new_member(New_List)
    elif user_choice == '3':
        New_List = []
        cont = 1
        counter = 0
        while True:
            try:
                number_names = int(input("Please enter the amount of names you'd like to delete: "))
                break
            except:
                print("Please only enter in a number")
        while cont == 1:
            if counter >= number_names:
                break
            print(counter)
            player = input("Please enter in a players name: ")
            player = player.lower()
            New_List.append(player)
            counter += 1
        delete_player(New_List)
        conn.commit()
    elif user_choice == '4':
        display_clan()
    elif user_choice == '5':
        print("What information would you like exported to a csv file?")
        csv_choice = input("1 for Members_List, 2 for a player's table, and 3 for all players: ")
        export_csv(csv_choice)

    elif user_choice != '1' and user_choice != '2' and user_choice != '3' and user_choice != '4' and user_choice != '5':
        print("Please only enter 1-5")



clan = input("Enter a clan name: ")
db_filename = '{0}.db'.format(clan)

conn = sqlite3.connect(db_filename)
c = conn.cursor()
cont = '1'
cont2 = '2'
while True:
    if cont2 != '2':
        break
    if check_if_new() is True:
        while cont == '1':
            print("This seems to be a new clan")
            print("Would you like to add some members?")
            add_memb = input("Please enter a 1 for yes or 2 for no: ")
            if add_memb == '1':
                initialize_clan(clan)
                print("Would you like to do anything else?")
                cont = input("Please enter a 2 to do something else or anything to close the file: ")
            elif add_memb == '2':
                print("This doesn't do anything, sorry")
                pass
            if add_memb != '1' or '2':
                print("Please only enter a 1 or a 2")
    else:
        while True:
            new_members = False
            print()
            print("Current clan selected is:", clan)
            print("What would you like to do?")
            print("Your options are: ")
            print("                  1. Update hiscores of members")
            print("                  2. Add new member(s)")
            print("                  3. Remove current member(s)")
            print("                  4. Display all current members")
            print("                  5. Export various clan data to csv")
            user_choice = input("Please enter a number: ")
            program_features(user_choice)
            print()
            cont = input("Would you like to do anything else? Enter 1 to do something else: ")
            if cont != '1':
                cont2 = 'end'
                break

input("end of program")
