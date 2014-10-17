# Mini-project: Rock-paper-scissors-lizard-Spock
# 0 — rock
# 1 — Spock
# 2 — paper
# 3 — lizard
# 4 — scissors

import random

def name_to_number(name):
    if   name == "rock":   number = 0
    elif name == "Spock":  number = 1
    elif name == "paper":  number = 2
    elif name == "lizard": number = 3
    elif name == "scissors": number = 4  
    else:
         print "Error - illegal name entered: %s \n" % (name)
         raise Exception
    return number

def number_to_name(number):
    if   number == 0: name = "rock"
    elif number == 1: name = "Spock"    
    elif number == 2: name = "paper"
    elif number == 3: name = "lizard"
    elif number == 4: name = "scissors"
    else:
        print "Error - %s number entered outside legal range \n" % (number)
        raise Exception
    return name

def rpsls(player_choice):
    print "\n"
    print "Player chooses %s" % (player_choice)
    player_number = name_to_number(player_choice)
    
    comp_number = random.randrange(0,5,1)
    comp_name = number_to_name(comp_number)
    print "Computer chooses %s" % (comp_name)
    
    result = (comp_number - player_number) % 5
    
    if   (result == 0): print "Player and computer tie!\n"
    elif (result == 1): print "Computer wins!\n"
    elif (result == 2): print "Computer wins!\n"        
    elif (result == 3): print "Player wins!\n"
    elif (result == 4): print "Player wins!\n"
    else:
        print "Error - illegal result number %s \n" % (result)
        raise Exception

rpsls("rock")
rpsls("Spock")
rpsls("paper")
rpsls("lizard")
rpsls("scissors")
rpsls("error")


                 