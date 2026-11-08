import random
import json

def reset_cards():
    score_cards = {
        "player": {"ones":"",
                "twos":"",
                "threes":"",
                "fours":"",
                "fives":"",
                "sixes":"",
                "three of a kind":"",
                "four of a kind":"",
                "full house":"",
                "small straight":"",
                "large straight":"",
                "yahtzee":"",
                "chance":"",},
        "opponent": {"ones":"",
                "twos":"",
                "threes":"",
                "fours":"",
                "fives":"",
                "sixes":"",
                "three of a kind":"",
                "four of a kind":"",
                "full house":"",
                "small straight":"",
                "large straight":"",
                "yahtzee":"",
                "chance":"",}
    }
    return score_cards

dice = [0,0,0,0,0]
numbers = ["ones","twos","threes","fours", "fives", "sixes"]

def update_running_totals(score_cards):
    player_card = score_cards["player"]
    player_total = 0
    for category, score in player_card.items():
        if category != "total" and score != "":
            player_total += score
    player_card["total"] = player_total

    computer_card = score_cards["opponent"]
    computer_total = 0
    for category, score in computer_card.items():
        if category != "total" and score != "":
            computer_total += score
    computer_card["total"] = computer_total

    return score_cards

def score_numbers(num,list):
    return list.count(num)*num

def roll_dice(num):
    dice[num] = random.randint(1,6)

def player_turn(player):
    rounds = 3
    for die in range(5):
        roll_dice(die)  
    while rounds > 0:
        print(dice, "\n",rounds ,"rerolls left")
        reroll = input("Would you like to reroll? (yes/no): \n").strip().lower()
        if reroll != "yes":
            break     
        redo_dice = input("Which dice would you like to reroll? (e.g., 1 3 5): \n")
        for char in redo_dice:
            if char.isdigit():
                die_index = int(char) - 1
                if 0 <= die_index < 5: 
                    roll_dice(die_index)   
        rounds -= 1   
    print("Your final dice:", dice)
    scoring = input("what would you like to put this roll under? \n(type [score sheet] to see your score sheet)\n")
    if scoring == "score sheet":
        print(json.dumps(score_cards[player], indent=4))
        scoring = input("what would you like to put this roll under?\n")
    if scoring == "chance":
        score_cards[player][scoring] = sum(dice)
    elif scoring in numbers:
        score_cards[player][scoring] = score_numbers(numbers.index(scoring)+1, dice)
    elif scoring == "small straight":
        score_cards[player][scoring] = check_small_straight(dice)
    elif scoring == "large straight":
        score_cards[player][scoring] = check_large_straight(dice)
    elif scoring == "three of a kind":
        score_cards[player][scoring] = check_three_of_a_kind(dice)
    elif scoring == "four of a kind":
        score_cards[player][scoring] = check_four_of_a_kind(dice)
    elif scoring == "full house":
        score_cards[player][scoring] = check_full_house(dice)
    elif scoring == "yahtzee":
        score_cards[player][scoring] = check_yahtzee(dice)
    else:
        print("not an option, round now forfeit")
    update_running_totals(score_cards)
    print("your card:\n",json.dumps(score_cards[player], indent=4))
    print("opponent's turn now")

def computer_reroll_strategy(dice, score_cards):
    comp_card = score_cards["opponent"]
    counts = get_counts(dice)
    if check_yahtzee(dice) > 0 and comp_card["yahtzee"] == "": return []
    if check_large_straight(dice) > 0 and comp_card["large straight"] == "": return []
    if check_full_house(dice) > 0 and comp_card["full house"] == "": return []
    most_common_die, highest_count = counts.most_common(1)[0]
    if highest_count >= 2:
        keep_value = most_common_die
    else:
        keep_value = max(dice)
    reroll_indices = [i for i, val in enumerate(dice) if val != keep_value]
    return reroll_indices

def computer_turn():
    for die in range(5):
        roll_dice(die)
    rerolls_left = 3
    while rerolls_left > 0:
        print("computer's current dice:",dice, "\n",rerolls_left ,"rerolls left")
        to_reroll = computer_reroll_strategy(dice, score_cards)
        if not to_reroll:
            print("computer decides to keep dice.")
            break
        print("computer rerolls dice")
        for idx in to_reroll:
            roll_dice(idx)
        rerolls_left -= 1
    print("computer's final dice:", dice)
    score_and_assign_best_computer(dice, score_cards)
    update_running_totals(score_cards)
    print("computer's card:\n", json.dumps(score_cards["opponent"], indent=4))
    print("your turn now\n")



from collections import Counter

def get_counts(dice):
    return Counter(dice)

def check_small_straight(dice):
    unique = set(dice)
    if any(all(num in unique for num in range(i, i + 4)) for i in (1, 2, 3)):
        return 30
    return 0

def check_large_straight(dice):
    unique = set(dice)
    if any(all(num in unique for num in range(i, i + 5)) for i in (1, 2)):
        return 40
    return 0

def check_three_of_a_kind(dice):
    counts = get_counts(dice)
    if any(count >= 3 for count in counts.values()):
        return sum(dice)
    return 0

def check_four_of_a_kind(dice):
    counts = get_counts(dice)
    if any(count >= 4 for count in counts.values()):
        return sum(dice)
    return 0

def check_full_house(dice):
    counts = get_counts(dice)
    if 3 in counts.values() and 2 in counts.values():
        return 25
    return 0

def check_yahtzee(dice):
    counts = get_counts(dice)
    if 5 in counts.values():
        return 50
    return 0

def score_and_assign_best_computer(dice, score_cards):
    counts = get_counts(dice)
    
    potential_scores = {
        "yahtzee": check_yahtzee(dice),
        "large straight": check_large_straight(dice),
        "small straight": check_small_straight(dice),
        "full house": check_full_house(dice),
        "four of a kind": check_four_of_a_kind(dice),
        "three of a kind": check_three_of_a_kind(dice),
        "sixes": counts[6] * 6,
        "fives": counts[5] * 5,
        "fours": counts[4] * 4,
        "threes": counts[3] * 3,
        "twos": counts[2] * 2,
        "ones": counts[1] * 1,
        "chance": sum(dice)
    }

    best_category = None
    max_score = -1

    for category, score in potential_scores.items():
        if score_cards["opponent"][category] == "":
            if score > max_score:
                max_score = score
                best_category = category

    if best_category is not None:
        score_cards["opponent"][best_category] = max_score
    return score_cards

def check_final_bonuses(score_cards):
    player_upper_sum = sum(score_cards["player"][num] for num in numbers)
    if player_upper_sum >= 63:
        score_cards["player"]["total"] += 35
    computer_upper_sum = sum(score_cards["opponent"][num] for num in numbers)
    if computer_upper_sum >= 63:
        score_cards["opponent"]["total"] += 35

    return score_cards

play = "yes"
opponent = input("vs computer or player2?\n")
while play == "yes":
    score_cards = reset_cards()
    turn = 1
    if opponent == "computer":
        print("yahtzee time!\n(fun fact you can put a roll on a score that already has one! only drawback is it breaks the code!)")
        while turn < 14:
            print("turn:",turn)
            player_turn("player")
            computer_turn()
            turn += 1
        print("no more turns!")
        check_final_bonuses(score_cards)
        print("player score:",score_cards["player"]["total"],"\ncomputer score:",score_cards["opponent"]["total"],)
        if score_cards["player"]["total"] > score_cards["opponent"]["total"]:
            winner = "the player!"
        elif score_cards["player"]["total"] < score_cards["opponent"]["total"]:
            winner = "the computer!"
        else:
            winner = "no-one. it's a tie :/"
        print("and the winner is ",winner,)
    else:
        print("yahtzee time!\n(fun fact you can put a roll on a score that already has one! only drawback is it breaks the code!)")
        while turn < 14:
            print("turn:",turn)
            player_turn("player")
            player_turn("opponent")
            turn += 1
        print("no more turns!")
        check_final_bonuses(score_cards)
        print("player score:",score_cards["player"]["total"],"\ncomputer score:",score_cards["opponent"]["total"],)
        if score_cards["player"]["total"] > score_cards["opponent"]["total"]:
            winner = "the player!"
        elif score_cards["player"]["total"] < score_cards["opponent"]["total"]:
            winner = "the computer!"
        else:
            winner = "no-one. it's a tie :/"
        print("and the winner is ",winner,)
    play = input("play again?\n")
print("byebye")