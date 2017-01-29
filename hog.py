"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    outcome, total, pig_out = 0, 0, False

    while num_rolls > 0:
        outcome = dice()
        if outcome == 1: # Pig out
            pig_out = True    
        total += outcome
        num_rolls -= 1
    return 1 if pig_out else total #This line can be written in 3 lines but this way is more concise


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    
    if num_rolls == 0:
        return 1 + max(opponent_score // 10, opponent_score % 10)
    return roll_dice(num_rolls, dice)

# Playing a game

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).

    >>> select_dice(4, 24) == four_sided
    True
    >>> select_dice(16, 64) == six_sided
    True
    >>> select_dice(0, 0) == four_sided
    True
    """
    return four_sided if (score + opponent_score) % 7 == 0 else six_sided #This line can be written in 3 lines but this way is more concise

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score, opponent_score = 0, 0
    num_dice = 0

    while score < goal and opponent_score < goal:
        num_dice = strategy0(score, opponent_score)
        type_dice = select_dice(score, opponent_score) # Special Rule: Hog Wild
        score  += take_turn(num_dice, opponent_score, type_dice) 

        # Speical rule: Swine swap
        if (opponent_score - score == score) or (score - opponent_score == opponent_score):
            score, opponent_score = opponent_score, score

        # Next players turn, swap
        # These lines can be written in one line but too long
        score, opponent_score = opponent_score, score
        strategy0, strategy1 = strategy1, strategy0
        who = other(who)

    # If Player0 reached 100 and it is player2's turn, reverse score
    if who == 1:
        score, opponent_score = opponent_score, score

    return (score, opponent_score)

#######################
# Phase 2: Strategies #
#######################

# Basic Strategy

BASELINE_NUM_ROLLS = 5
BACON_MARGIN = 8

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def average(*args):
        count, total = 0, 0
        while count < num_samples:
            total += fn(*args)
            count += 1
        return total / count
    return average

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    count, curr, best_avg, best_num = 1, 0, 0, 1
    roll_average = make_averaged(roll_dice)

    while count <= 10:
        curr = roll_average(count, dice)
        print(count,"dice scores", curr, "on average")
        best_avg = max(best_avg, curr)
        best_num = count if curr == best_avg else best_num #This line can be written in 3 lines but this way is more concise
        count += 1
    return best_num
    

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(BASELINE_NUM_ROLLS)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if True: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to False to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to False to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))
    i = 0
    while i < 10: 
        if True: # Change to False to test final_strategy
            print('final_strategy win rate:', average_win_rate(final_strategy))
            i += 1
    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score):
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    if max(opponent_score // 10, opponent_score % 10) + 1 >= BACON_MARGIN: 
        return 0
    return BASELINE_NUM_ROLLS

def swap_strategy(score, opponent_score):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls BASELINE_NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least BACON_MARGIN points and rolls
    BASELINE_NUM_ROLLS otherwise.

    >>> swap_strategy(23, 60) # 23 + (1 + max(6, 0)) = 30: Beneficial swap
    0
    >>> swap_strategy(27, 18) # 27 + (1 + max(1, 8)) = 36: Harmful swap
    5
    >>> swap_strategy(50, 80) # (1 + max(8, 0)) = 9: Lots of free bacon
    0
    >>> swap_strategy(12, 12) # Baseline
    5
    """
    # opponent divde
    swap = score + (1 + max(opponent_score // 10, opponent_score % 10))

    if opponent_score - swap == swap: #beneficial
        return 0
    elif swap - opponent_score == opponent_score: #harmful
        return BASELINE_NUM_ROLLS
    else:
        return bacon_strategy(score, opponent_score)


four_sided_max = max_scoring_num_rolls(four_sided)
six_sided_max = max_scoring_num_rolls(six_sided)
def final_strategy(score, opponent_score):
    """
    This strategy rolls 0 whenever swap occurs. If dice is four_sided, it is better to roll0 unless it cause harmful swap.
    The function repeated_strategy checks if swap can occur even player doesn't roll 0 dice. If opponent_score is sufficient
    to make the players' pass the GOAL_SCORE, roll0. Otherwise, roll the best number of dice.
    """

    type_dice = select_dice(score, opponent_score)
    roll0 = score + (1 + max(opponent_score // 10, opponent_score % 10))
    best_num_dice = four_sided_max if type_dice is four_sided else six_sided_max
    diff = opponent_score - score # If opponent winning, by how much?
    estimate = opponent_score + roll_dice(5) # opponent will roll 5 always

    def repeated_strategy():
        difference = opponent_score // 2 - score
        if type_dice is four_sided:
            if difference <= 1:
                return 10
            elif difference <= 2:
                return 1
            elif difference <= 3:
                return 2
            elif difference <= 4:
                return 3
            elif difference <= 5:
                return 3
        else:
            if difference <= 1:
                return 10
            elif difference < 4:
                return 1
            elif difference <= 8:
                return 2
            elif difference <= 12:
                return 3
            elif difference <= 17:
                return 4
        if score + best_num_dice >= GOAL_SCORE:
            return 2
        else:
            return best_num_dice

    #Best option
    if roll0 < opponent_score and opponent_score // roll0 == 2 and opponent_score % roll0 == 0: #beneficial
        return 0

    #If Dice type is four side and 
    if type_dice is four_sided:
        if roll0 > opponent_score and roll0 == 2 and roll0 % opponent_score == 0: #danger
            return best_num_dice

        elif opponent_score > score and (opponent_score // 2 - score) > 0:
            return repeated_strategy()
        else:
            if max(opponent_score // 10, opponent_score % 10) + 1 >= 4: # Margin should be smaller
                return 0
            else:
                return best_num_dice

    #End of the game
    elif opponent_score > 80 and score > 91:
        return 0

    #If my score is almost goal score and roll0 is enough, roll 0
    elif score + max(opponent_score // 10, opponent_score % 10) >= 100:
        if opponent_score != 0 and roll0 // opponent_score == 2 and roll0 % opponent_score == 0:
            return best_num_dice
        else:
            return 0

    #To make opponent roll 4 sided dice - higher chance
    elif select_dice(roll0, opponent_score) is four_sided:    
        if opponent_score != 0 and roll0 // opponent_score == 2 and roll0 % opponent_score == 0:
            return best_num_dice
        else:
            return 0

    #To make swap without rolling - good chance to swap
    #Only case for six sided
    #Very effective
    elif opponent_score > score and (opponent_score // 2 - score) > 0:
        return repeated_strategy()

    #Winning and opponnent has no chance to swap
    elif opponent_score > 50 and score - opponent_score > 15:
        return 0

    #If score + 5 or 7 is greater than 100
    elif score + best_num_dice >= GOAL_SCORE:
            return 2
    else:
        return best_num_dice
        


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use featuares
#       of Python not yet covered in the course.

def get_int(prompt, min):
    """Return an integer greater than or equal to MIN, given by the user."""
    choice = input(prompt)
    while not choice.isnumeric() or int(choice) < min:
        print('Please enter an integer greater than or equal to', min)
        choice = input(prompt)
    return int(choice)

def interactive_dice():
    """A dice where the outcomes are provided by the user."""
    return get_int('Result of dice roll: ', 1)

def make_interactive_strategy(player):
    """Return a strategy for which the user provides the number of rolls."""
    prompt = 'Number of rolls for Player {0}: '.format(player)
    def interactive_strategy(score, opp_score):
        if player == 1:
            score, opp_score = opp_score, score
        print(score, 'vs.', opp_score)
        choice = get_int(prompt, 0)
        return choice
    return interactive_strategy

def roll_dice_interactive():
    """Interactively call roll_dice."""
    num_rolls = get_int('Number of rolls: ', 1)
    turn_total = roll_dice(num_rolls, interactive_dice)
    print('Turn total:', turn_total)

def take_turn_interactive():
    """Interactively call take_turn."""
    num_rolls = get_int('Number of rolls: ', 0)
    opp_score = get_int('Opponent score: ', 0)
    turn_total = take_turn(num_rolls, opp_score, interactive_dice)
    print('Turn total:', turn_total)

def play_interactive():
    """Interactively call play."""
    strategy0 = make_interactive_strategy(0)
    strategy1 = make_interactive_strategy(1)
    score0, score1 = play(strategy0, strategy1)
    print('Final scores:', score0, 'to', score1)

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--interactive', '-i', type=str,
                        help='Run interactive tests for the specified question')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.interactive:
        test = args.interactive + '_interactive'
        if test not in globals():
            print('To use the -i option, please choose one of these:')
            print('\troll_dice', '\ttake_turn', '\tplay', sep='\n')
            exit(1)
        try:
            globals()[test]()
        except (KeyboardInterrupt, EOFError):
            print('\nQuitting interactive test')
            exit(0)
    elif args.run_experiments:
        run_experiments()
