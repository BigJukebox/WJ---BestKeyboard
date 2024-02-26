import numpy as np
import time
import random
import math
import bisect
from datetime import datetime
import colorama
import concurrent.futures
import threading
import keyboard
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent


# - nur für show() Funktion
#import sys
#sys.path.append(r"C:\Users\max.stephan\Desktop\Projects\KeyboardRundown")
#import imagegen as KeyboardGenerator



#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-------------------------|-----------------------------------------------------------------|---------------------------
#-------------------------|----------------------------VARIABLES----------------------------|---------------------------
#-------------------------V-----------------------------------------------------------------V---------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


fingerindecies = { # storing which finger is responsible for which key positions (modulo 12)
    0: -4,
    1: -3,
    2: -2,
    3: -1,
    4: -1,

    5: 1,
    6: 1,
    7: 2,
    8: 3,
    9: 4,
    10: 4,
    11: 4,
}


standardposition = {    # sets starting position
            -4: 12,
            -3: 13,
            -2: 14,
            -1: 15,

            1: 18,
            2: 19,
            3: 20,
            4: 21

        }


availablekeys   = ["q@","w","e€","r","t","z","u","i","o","p","ü","+*~",
                       "a", "s", "d","f","g","h","j","k","l","ö","ä","#'",
                  "<>|","y", "x", "c","v","b","n","m",",;",".:","-_"] # all the available keys on a standard qwertz - Keyboard (German Layout)


v1 = np.array([0.25, 1])
v2 = np.array([0.5, 1])

stop = threading.Event()

fitnessfactors = [1, 10] # 0: basic wordlist, 1: harry potter
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------CLASS----------------------------------------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



class Keyboard:

    keys = []
    score = 0

    def __init__(self, keys: list, score: float = 0):
        self.keys = keys
        self.score = score

    def distance(self, word: str): # computes the distance of a word
        accordingkey = standardposition.copy()



        left = []
        right = []

        hand = {}




        # --computing distance for both hands--
        before = -1
        for key in word:
            modifier = 0
            if key != key.lower(): modifier = 1
            key = key.lower()
            position, m = self.fullindex(key) #where is the according key?
            if m != 0: modifier = m


            if position == -1: continue

            finger = self.finger(position) #what is the responsible finger?





            reset = True
            if position == accordingkey[finger]: reset = False


            #checks for roll movement --> if so, entire hand moved and distance is zero
            if before != -1 and (before == position + 1 or before == position -1) and before%12 <= 9 and before != 4 and before%12 != 5 and position%12 <= 9 and position%12 != 4 and position%12 != 5: # is it a rolling movement? --> no keyreset, hand moves up
                keydistance = 0
                accordingkey[finger] = position
                reset = False



            #some movements like  qg wg eg   ih oh ph   (on QWERTY) can be done simultaneously --> overlaps these movements
            elif (not len(left) == 0) and position == 16 and 0 <= left[len(left)-1]["index"] <= 2:
                    keydistance = 0
                    accordingkey[finger] = position
                    reset = False
            elif (not len(left) == 0) and left[len(left)-1]["index"] == 16 and 0 <= position <= 2:
                    keydistance = self.keydistance(accordingkey[finger], position) - 1
                    if keydistance < 0: keydistance = 0
                    accordingkey[finger] = position
                    reset = False

            elif (not len(right) == 0) and position == 17 and 7 <= right[len(right)-1]["index"] <= 9:
                keydistance = 0
                accordingkey[finger] = position
                reset = False
            elif (not len(right) == 0) and right[len(right)-1]["index"] == 17 and 7 <= position <= 9:
                keydistance = self.keydistance(accordingkey[finger], position) - 1
                if keydistance < 0: keydistance = 0
                accordingkey[finger] = position
                reset = False



            #default distance
            else:
                keydistance = self.keydistance(accordingkey[finger], position)
                accordingkey[finger] = position
            if reset: Keyboard.resetfingers(accordingkey, finger)

            moddistance = 0



            # shift punishement
            if modifier == 1: # SHIFT
                if finger < 0: #rightshift
                    moddistance = self.keydistance(accordingkey[4], 36)
                    accordingkey[4] = 36
                    Keyboard.resetfingers(accordingkey, 4)

                else: #leftshift
                    moddistance = self.keydistance(accordingkey[-4], 35)
                    accordingkey[-4] = 35
                    Keyboard.resetfingers(accordingkey, -4)

            elif modifier == 2:  # ALT
                moddistance = 2
                Keyboard.resetfingers(accordingkey, 5)



            if finger > 0: # splits keys between hands
                right.append({"key": key, "distance": keydistance, "index": position, "modifier": moddistance})
                hand[key] = 0 # 0 --> right
            else:
                left.append({"key": key, "distance": keydistance, "index": position, "modifier": moddistance})
                hand[key] = 1 # 1 --> left

            before = position


        #/////////////////////////////
        #--assembling hand movements--
        left_distance = 0
        right_distance = 0


        for key in word:
            key = key.lower()
            if not key in hand.keys(): continue #throwing out key if not on the keyboard
            if hand[key]:
                popper = left.pop(0)

                left_distance += popper["distance"]

                right_distance += popper["modifier"] #modifier
                if popper["modifier"] != 0:
                    if right_distance < left_distance: right_distance = left_distance



                if left_distance < right_distance: left_distance = right_distance # waits on the other hand

            else:
                popper = right.pop(0)

                right_distance += popper["distance"]

                left_distance += popper["modifier"] #modifier
                if popper["modifier"] != 0:
                    if left_distance < right_distance: left_distance = right_distance


                if right_distance < left_distance: right_distance = left_distance # waits on the other hand



        if left_distance > right_distance: return left_distance
        else: return right_distance





    def index(self, key: str) -> int: # returns, which index a given key has
        if key == "ß" or key == "?": return -2

        for j in range(len(self.keys)):
            if key in self.keys[j]: return j
        #C raise NotImplementedError(f"{key} seems to not be on the keyboard.")

        #default:
        return -1 # returns -1 if character not found


    def fullindex(self, key: str) -> tuple: #returns, which index a given key has, with it's modifiers (shift, alt, ...)
        if key == "ß": return -2, 0 #T PLACEHOLDER
        if key == "?": return -2, 1

        for j in range(len(self.keys)):
            modifier = self.keys[j].find(key)
            if self.keys[j] != self.keys[j].upper() and modifier > 0: modifier += 1
            if modifier != -1: return j, modifier
        #C raise NotImplementedError(f"{key} seems to not be on the keyboard.")

        #default:
        return -1, 0 # returns -1 if character not found



    def scorestring(self): # returns formatted score string (2789125.1482213293 --> 2,789,125.1482213293)
        return "{:,}".format(self.score)




    def show(self, mark=None, markcolor=None, colormap=None, heatmaptype=None):
        KeyboardGenerator.showkeyboard(self.keys, mark=mark, markcolor=markcolor, colormap=colormap, heatmaptype=heatmaptype)








    def __str__(self):
        string = "--------------------------------------------------------\n |"
        for el in range(len(self.keys)-1):
            if el == 12: string += "\n  |"
            if el == 24: string += "\n| " + self.keys[34] + " |"
            string += " " + self.keys[el] + " |"
        string += "\n-------------------------------------------------"

        return string


    def print_keys (self):
        string = "["
        for i in range(len(self.keys)-1):
            el = self.keys[i]

            string += "\"" + el + "\","

        string += "\"" + self.keys[len(self.keys)-1] + "\"]"

        return string



    @staticmethod#      resets all fingers of one hand but the one specified (the resetted hand is the one of the finger)
    def resetfingers(dictionary, finger):
        fingers = [1, 2, 3, 4]
        if finger < 0: fingers = [-f for f in fingers]
        if not (finger == -5 or finger == 5): fingers.remove(finger)

        for f in fingers:
            dictionary[f] = standardposition[f]

    @staticmethod #     returns responsible finger for a given key
    def finger(index: int):
        if index == -2: return 4 # ß/? - special case
        return fingerindecies[index%12]

    @staticmethod #     computes distance between two key positions
    def keydistance(a: int, b: int):
        vec_a = Keyboard.index_to_vector(a) #converts indecies to vectors
        vec_b = Keyboard.index_to_vector(b)


        result = vec_a - vec_b

        return np.sqrt(result[0]**2 + result[1]**2) # returns distance between vectors

    @staticmethod #     computes distance between two key positions but in vector form
    def vectorkeydistance(a: np.array, b: np.array):
        result = a - b
        return np.sqrt(result[0]**2 + result[1]**2)

    @staticmethod #     converts an index to a vector
    def index_to_vector(index: int):
        """
        :param index: index of a key on the keyboard
        :return: vector

        vectorspace has 0|0 in the upperleftmost key (Q on standard QWERTY)\n
        the X-axis is horizontal and goes to the right\n
        the Y-axis is vertical and goes down

        the size of a key and therefore the horizontal distance between two adjacent keys is defined to 1

        (0|0)
        -+------------------->
         | .
         |   .
         |     .
         V

        """
        if index == 34: return v1 + v2 + np.array([-1, 0])
        if index == -2: return np.array([9.5, -1])  # ß/? - special case
        if index == 35: return np.array([-1.25, 2]) #leftshift
        if index == 36: return np.array([10.75, 2])  #rightshift

        vec = np.array([float(index % 12), 0])  # converting index a to vector
        if index >= 12: vec += v1
        if index >= 24: vec += v2


        return vec

    @staticmethod #     converts an index to the coordinates
    def index_to_coordinates(index: int):
        if index == 34: return [0, 3]       #<>
        if index == -2: return [11, 0]      #ß?
        if index == 35: return [-1, 3]   #LEFTSHIFT
        if index == 36: return [11, 3]   #RIGHTSHIFT
        cord = [1, 1]

        cord[0] = (index % 12) + 1
        if index >= 12: cord[1] = 2
        if index >= 24: cord[1] = 3

        return cord

    @staticmethod #     converts coordinates into an index
    def coordinates_to_index(coordinates):
        if coordinates == [0, 3]: return 34     #<>
        if coordinates == [11, 0]: return -2    #ß?
        if coordinates == [-1, 3]: return 35 #LEFTSHIFT
        if coordinates == [11, 3]: return 36 #RIGHTSHIFT

        if coordinates[0] < 1 or coordinates[0] > 12: return -1 # returns -1 when coordinate is invalid
        if coordinates[1] < 1 or coordinates[1] > 3: return -1


        index = (12*(coordinates[1]-1)) + coordinates[0] - 1
        if index > 33: return -1
        return index








#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-------------------------|-----------------------------------------------------------------|---------------------------
#-------------------------|----------------------------FUNCTIONS----------------------------|---------------------------
#-------------------------V-----------------------------------------------------------------V---------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def sort_into (keyboardlist, keyboard):
    bisect.insort_left(keyboardlist, keyboard, key= lambda k: k.score)






def fitness_harry_potter_pt1(keyboard): #i: 1
    with open("HarryPotter_German_Pt1.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

        totaldistance = 0
        for line in lines:
            line = line.replace("\n", "")
            totaldistance += keyboard.distance(line)

        keyboard.score += totaldistance * fitnessfactors[1]
        return keyboard




def fitness_basic_wordlist(keyboard, verbose=0): #i: 0
    with open("GermanWordList_25k.txt", "r", encoding="utf-8") as file:
        totaldistance = 0
        totalscore = 0
        count = 0
        m = 0
        points = 0
        lines = file.readlines()
        n = len(lines)

        if verbose == 1: print(keyboard)
        if verbose == 1: print(f"computing fitness", end="")


        for line in lines:

            m += 1 #" computing fitness...
            if verbose == 1:
                if m % (math.floor(n/4)) == 0 & points < 3:
                    print(f".", end="")
                    points += 1




            line = line.replace("\n", "")
            data = line.split(" ")
            frequency = float(data[1])
            text = data[2]
            if len(text) <= 1: continue  # throws out all lone characters
            count += frequency


            distance = keyboard.distance(text) #updating stats
            totaldistance += distance
            score = frequency * distance
            totalscore += score







            if verbose >=3: print(f"{line}      distance: {distance}        score: {score}")


        if verbose == 1: print(f"\n\n")
        if verbose >= 2: print(f"------------------------------------------------------\n\nTotal Distance: {totaldistance}           Total Score: {totalscore}\nAverage Word Distance: {totalscore / count}")

        keyboard.score += totalscore * fitnessfactors[0]
        return keyboard







def fitness_combined(keyboard):
    fitness_basic_wordlist(keyboard)
    fitness_harry_potter_pt1(keyboard)
    return keyboard



def generate_sex (keyboard1, keyboard2, deterministic:bool=False):

    keys = keyboard1.keys.copy()
    if not deterministic: random.shuffle(keys)
    keyorder = []
    for key in keys: # computes order in which keys should be merged (smallest distance to largest)
        i1 = keyboard1.index(key)
        i2 = keyboard2.index(key)

        bisect.insort_left(keyorder, {"key": key, "i1": i1, "i2": i2, "distance": Keyboard.keydistance(i1, i2)}, key= lambda el: el["distance"])


    newkeyboard = {}

    for element in keyorder:
        middle = (Keyboard.index_to_vector(element["i1"]) + Keyboard.index_to_vector(element["i2"]))/2 # arithmetic mean


        if (element["i1"] == 33 and element["i2"] == 23) or (element["i1"] == 23 and element["i2"] == 33): middle = Keyboard.index_to_vector(22) # special case: eliminating possible out-of-bounds result

        y = int(middle[1] + 0.5) +1
        if y - middle[1] - 1 == 0.5 and not deterministic: y += random.choice([0, -1]) # compensates for rounding bias (~.5 --> exactly in the middle, but is always rounded up)

        x = middle[0]
        if y >= 2: x -= v1[0]
        if y >= 3: x -= v2[0]

        x_save = x
        x = int(x + 0.5) +1
        if x - x_save - 1 == 0.5 and not deterministic: x += random.choice([0, -1])  # compensates for rounding bias (~.5 --> exactly in the middle, but is always rounded up)

        nearest = [x, y]
        nearestindex = Keyboard.coordinates_to_index(nearest)


        if not nearestindex in newkeyboard.keys(): newkeyboard[nearestindex] = element["key"]; continue
        else:
            search = 1 # x-coordinate
            possiblepositions = []
            done = False
            while search < len(keyboard1.keys): # iterating onion-wise in circles around best fitting key, to save some computation time and find 2nd best fit (the while condition is just an upper limit to stop an infinite loop)

                range_ = [1, 2, 3]
                if not deterministic: random.shuffle(range_)
                for i in range_: # y-coordinate

                    # ordering coordinates according to their fitting
                    if x-search >= 1 or [x-search, i] == [0, 3]:
                        bisect.insort_left(possiblepositions, [x-search, i], key= lambda keyy: Keyboard.vectorkeydistance(middle, Keyboard.index_to_vector(Keyboard.coordinates_to_index(keyy))))
                    if x+search <= 12:
                        bisect.insort_left(possiblepositions, [x+search, i], key= lambda keyy: Keyboard.vectorkeydistance(middle, Keyboard.index_to_vector(Keyboard.coordinates_to_index(keyy))))
                    if search == 1 and y != i:
                        bisect.insort_left(possiblepositions, [x,        i], key= lambda keyy: Keyboard.vectorkeydistance(middle, Keyboard.index_to_vector(Keyboard.coordinates_to_index(keyy))))


                for pos in possiblepositions: # checks whether key can be placed there
                    indexx = Keyboard.coordinates_to_index(pos)
                    if indexx == -1: continue # invalid position
                    if indexx == 35 or indexx == 36: continue # shift keys not available for key assignment

                    if not Keyboard.coordinates_to_index(pos) in newkeyboard.keys(): newkeyboard[indexx] = element["key"]; done = True; break
                if done: break

                possiblepositions = [] # no valid placement found, all keys already full --> reset and next iteration
                search += 1
                continue


            if not done: raise Exception("something is wrong here, the keyboard seems to already be full (terminated infinite loop)")



    # now every key has found it's place, time for assembly
    assembledkeyboard = Keyboard([newkeyboard[index] for index in range(len(keyboard1.keys))])

    return assembledkeyboard # finished :)


def generate_swap (keyboard, number, function=lambda x: ((2/3)**(math.log2(x)))/x, multiples:bool=True):
    newkeyboard = Keyboard(keyboard.keys.copy())
    keys = newkeyboard.keys.copy()

    if not multiples: # swapping more than available is not possible: setting upper bound
        if number > int(len(keys)/2): number = int(len(keys)/2)

    for _ in range(number):
        key1 = random.choice(keys) # choosing random key
        keys_ = keys.copy()
        keys_.remove(key1)

        times = 0 # counter to avoid infinite loop
        while times <= len(keyboard.keys):
            times += 1
            key2 = random.choice(keys_) # choosing random second key
            distance = Keyboard.keydistance(keyboard.index(key1), keyboard.index(key2))

            prob = function(distance)
            # swaps keys with certain probability
            if random.random() <= prob or times == len(keyboard.keys):
                i1 = newkeyboard.index(key1)
                i2 = newkeyboard.index(key2)
                newkeyboard.keys[i1], newkeyboard.keys[i2] = newkeyboard.keys[i2], newkeyboard.keys[i1]
                break

        if not multiples: keys.remove(key1); keys.remove(key2) # excludes just swapped keys from getting drawn again

    return newkeyboard


def generate_random (keyboard, probability):
    keepindecies = []
    keep = []
    for n in range(len(keyboard.keys)): # decide, which keys should be kept
        if random.random() <= probability:
            keep.append(keyboard.keys[n])
            keepindecies.append(n)





    randorder = keyboard.keys.copy() # shuffle rest of the keys
    for el in keep:
        randorder.remove(el)
    random.shuffle(randorder)



    newkeyboard = Keyboard([])
    for n in range(len(keyboard.keys)): # assembling to a new keyboard
        if n in keepindecies: newkeyboard.keys.append(keyboard.keys[n])
        else: newkeyboard.keys.append(randorder.pop())



    return newkeyboard


def generate_random_new ():
    shuffledkeys = availablekeys.copy()
    random.shuffle(shuffledkeys)
    return Keyboard(shuffledkeys)







def process_compute_multiple(keyboardlist):
    newlist = keyboardlist.copy()
    for kb in newlist:
        kb.score = fitness_basic_wordlist(kb)

    return newlist



def await_input():
    while True:
        if keyboard.is_pressed("c"): stop.set(); break





#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-------------------------|-----------------------------------------------------------------|---------------------------
#-------------------------|----------------------------VARIABLES----------------------------|---------------------------
#-------------------------V-----------------------------------------------------------------V---------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



QWERTZ   = Keyboard(["q@","w","e€","r","t","z","u","i","o","p","ü","+*~",
                       "a", "s", "d","f","g","h","j","k","l","ö","ä","#'",
                        "y", "x", "c","v","b","n","m",",;",".:","-_","<>|"]) # standard qwertz - Keyboard (German Layout)


RANDOMFUNCTION1 = lambda x: 0.95 - ((0.25/9)*x)

RANDOMFUNCTION2 = lambda x: RANDOMFUNCTION1(x) - 0.5

SWAPPINGNUMBER1 = lambda x: int(((4/81)*(x**2)) + 2.5)

SWAPPINGNUMBER2 = lambda x : int(((-4/81)*((x-9)**2))+6.5)

FITNESSFUNCTION = fitness_combined

LOGS = "log2_V2.0_(long)2.txt"

VERBOSE = 1

GENERATIONSIZE = 60

BESTWINDOWSIZE = 10

STARTINGCONFIG = [Keyboard([",;","g","w","p","ü","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","c","h","x","y","k","ö","ä","v","#'"], 3134574.1032914915),
Keyboard([",;","g","w","x","p","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","c","h","ü","y","k","ö","ä","v","#'"], 3136201.1369537795),
Keyboard([",;","g","w","x","p","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","#'","o","c","h","ü","y","k","ö","ä","v","<>|"], 3136234.7022395935),
Keyboard([",;","g","w","x","p","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","c","h","ü","ä","k","ö","v","y","#'"], 3136881.245259069),
Keyboard([",;","g","w","x","p","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","#'","o","c","h","ü","ä","k","ö","v","y","<>|"], 3136914.810544883),
Keyboard([",;","g","w","x","p","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","y","h","ü","c","k","ö","ä","v","#'"], 3137110.686088266),
Keyboard([",;","g","w","p","ü","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","c","h","x","y","k","ö","v","ä","#'"], 3140539.885698707),
Keyboard([",;","g","w","p","ü","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","#'","o","c","h","x","y","k","ö","v","ä","<>|"], 3140573.450984521),
Keyboard([",;","g","w","p","x","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","<>|","o","c","h","ü","y","k","ö","ä","v","#'"], 3141114.651392505),
Keyboard([",;","g","w","p","x","j","b",".:","m","z","q@","-_","r","i","t","u","a","f","s","e€","n","d","l","+*~","#'","o","c","h","ü","y","k","ö","ä","v","<>|"], 3141148.216678319)]

STARTINGTIME = 14660.429968833923

#--------------------------------------------------------MAIN-----------------------------------------------------------

logspath = root_dir / "BestKeyboardLayout" / "logs" / LOGS


if __name__ == "__main__":
    colorama.init()
    #Generate First Generation
    #Compute Fitness - Multiprocessing
    #Generate Next Generation

    time1 = time.time()

    with open(logspath, mode="w") as logs:
        threading.Thread(target=await_input, args=()).start() # initiating clean exit key (c)


        generation = [generate_random_new() for _ in range(60)]

        first = True
        while not stop.is_set():
            best = []
            if len(STARTINGCONFIG) == BESTWINDOWSIZE: best = STARTINGCONFIG.copy(); alltimebest = STARTINGCONFIG.copy(); first = False


            if VERBOSE: print(f"\rcomputing fitness...         ", end="\n")
            #Computing Fitness
            number = 1

            '''First Multi-Processing solution, every keyboard as own process'''
            with concurrent.futures.ProcessPoolExecutor() as executor:
                #starting computations as processes
                results = [executor.submit(FITNESSFUNCTION, keyboard) for keyboard in generation]


                #collecting results
                for result in concurrent.futures.as_completed(results):
                    k = result.result()


                    if VERBOSE: print(f"\r{number}/{len(generation)}", end=""); number += 1  # counter

                    if len(best) < 10: bisect.insort_left(best, k, key=lambda kk: kk.score); continue
                    if best[9].score > k.score: bisect.insort_left(best, k, key=lambda kk: kk.score); best.pop(10); continue

            '''For some reason this breaks everything and i have absolutely no idea why ¯\_(ツ)_/¯ (attempt of making it a bit more efficient by assigning each process 5 keyboards to compute)'''
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     #starting computations as processes
            #
            #     results = []
            #     while len(generation) > 0: #breaking up computation in chunks of length 5
            #         l = []
            #         for _ in range(5):
            #             if len(generation) == 0: break
            #             l.append(generation.pop())
            #
            #         results.append(executor.submit(process_compute_multiple, l))
            #
            #
            #     #collecting results
            #     for result in concurrent.futures.as_completed(results):
            #         for k in result.result():
            #
            #             if VERBOSE: print(f"\r{number}/{GENERATIONSIZE}", end=""); number += 1  # counter
            #
            #             if len(best) < 10: bisect.insort_left(best, k, key=lambda kk: kk.score); continue
            #             if best[9].score > k.score: bisect.insort_left(best, k, key=lambda kk: kk.score); best.pop(
            #                 10); continue

            #earlier non-multithreading solution:
            #for k in generation:
            #    if VERBOSE: print(f"\r{number}/{len(generation)}", end=""); number += 1 # counter


            #    k.score = FITNESSFUNCTION(k) # main computation

            #    if len(best) < 10: bisect.insort_left(best, k, key= lambda kk: kk.score); continue
            #    if best[9].score > k.score: bisect.insort_left(best, k, key= lambda kk: kk.score); best.pop(10); continue

            if VERBOSE: print("\033[A", end="")
            if first: alltimebest = best.copy(); first = False
            if best[0].score <= alltimebest[0].score:
                date = datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
                log = f"{date}; {time.time() + STARTINGTIME - time1}; {best[0].score}; {best[0].print_keys()}\n"
                logs.write(log)
                logs.flush()
                if VERBOSE and best[0].keys != alltimebest[0].keys: print(f"\r{log}", end="")

            for k in best:
                if k.score < alltimebest[9].score:
                    if k.keys in [kb.keys for kb in alltimebest]: continue

                    bisect.insort_left(alltimebest, k, key= lambda kk: kk.score)
                    alltimebest.pop(10)




            if VERBOSE: print(f"\rgenerating next generation...", end="")
            #--Generating Next Generation--

            generation = [generate_random_new() for _ in range(30)]
            sex = 1
            for keybi in range(len(best)):
                generation.append(generate_random(best[keybi], RANDOMFUNCTION1(keybi)))
                #newlygenerated.append(generate_random(best[keybi], RANDOMFUNCTION2(keybi)))

                generation.append(generate_swap(best[keybi], SWAPPINGNUMBER1(keybi)))
                #.append(generate_swap(best[keybi], SWAPPINGNUMBER2(keybi)))


                if sex <= 10: generation.append(generate_sex(best[keybi], best[keybi+1])); sex += 1
                if keybi <= 2: generation.append(generate_sex(best[keybi], best[keybi + 2])); sex += 1
                #T Sex Generation
                #--> logs
                #--> Then finished :)

        if stop:
            logs.write("--------------------------------------------\n")
            logs.flush()
            if VERBOSE: print("\n\n-----------------------------------------------")
            for k in alltimebest:
                log = f"{k.print_keys()}, {k.score}\n"
                logs.write(log)
                logs.flush()
                if VERBOSE: print(log, end="")

        input() # keeping window open before terminating



#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#-------------------------|-----------------------------------------------------------------|---------------------------
#-------------------------|----------------------------TESTRANGE----------------------------|---------------------------
#-------------------------V-----------------------------------------------------------------V---------------------------
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



if __name__ == "__main_": #T Test Swap-Generation!!!
    # l = [
    #     "rg",
    #     "eggers",
    #     "Mark",
    #     "mr"
    # ]
    # for k in l: print(QWERTZ.distance(k))

    while True:
        i = input()
        print(QWERTZ.distance(i))
#T! ölkj,.jklö - switches to ,. and rolls, but after that hand returns -> because j never left the place, distance remains zero - do we want that?
#T! No pressing time involved --> pressing happens instantaniously
#G is rolling to lower line allowed?


if __name__ == "__main_":
    while True:
        t0 = time.time()
        word = input()
        t1 = time.time()
        print(f"{t1-t0}s  -  {QWERTZ.distance(word)/3.1120315917163413}s")





if __name__ == "__main_":
    k1 = Keyboard(["ä","c","l","g","v","p","m","o","t","w","ö","+*~","d","a","r","u","h","z","n","e€","i","s",".:","#'","x","q@",",;","k","-_","b","j","ü","y","f","<>|"])
    k1.show()
    # k1 = generate_random_new()
    # k1.show()

    # k1, k2 = (generate_random_new() for i in range(2))
    # k1.show()
    # k2.show()
    # time.sleep(1)
    # k3 = generate_sex(k1, k2)
    # k3.show()

if __name__ == "_main_": # testing range
    t0 = time.time()

    n = 1000
    keyboards = []
    QWERTZ.score = fitness_basic_wordlist(QWERTZ, verbose=1)


    for _ in range(n):
        new = generate_random_new()
        new.score = fitness_basic_wordlist(new, verbose=1)
        sort_into(keyboards, new)

    for s in [f"{str(x.scorestring())}\n" for x in keyboards]: print(s)

    print(f"\n\n\n-------------------------------------------------------------------------------\n\nQWERTZ:\n{QWERTZ}\nScore: {QWERTZ.scorestring()}\n\n\nBest:\n{keyboards[0]}\nScore: {keyboards[0].scorestring()}\n\n\n")







    t1 = time.time()

    print(f"\ncode finished in {t1-t0}s\n{(t1-t0)/(25000*(n+1))}s per word")

    input()




    #T - run and make different models
    #(Also : Average word distance
    #Correlate to word speed (wpm) --> how well does it match? (from website and calculated over distance and average worddistance))
