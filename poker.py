"""
Implement functions to identify poker hands:
- is_pair(hand) -> bool
- is_two_pair(hand) -> bool
- is_three_of_kind(hand) -> bool
- is_straight(hand) -> bool
- is_flush(hand) -> bool
- is_full_house(hand) -> bool

Hand is a list of card tuples: [('A', 'Hearts'), ('K', 'Spades'), ...]
"""

def is_pair(hand):
  ranks = [card[0] for card in hand]
  rank_counts = {rank: ranks.count(rank) for rank in ranks}
  return 2 in rank_counts.values() and max(rank_counts.values()) == 2

def is_two_pair(hand):
  # two pair implies we have >= 2 pairs of cards
  # if we have ranks
  ranks = [card[0] for card in hand]
  rank_counts = {rank: ranks.count(rank) for rank in ranks}
  pairs = [count for count in rank_counts.values() if count == 2]
  return len(pairs) >= 2

def is_three_of_kind(hand):
  ranks = [card[0] for card in hand]
  rank_counts = {rank: ranks.count(rank) for rank in ranks}
  return 3 in rank_counts.values() and max(rank_counts.values()) == 3

def is_straight(hand):
    ranks = [card[0] for card in hand]
    # Define rank values including both Ace cases
    rank_to_value = {'A': 14, 'J': 11, 'Q': 12, 'K': 13}
    
    # Convert ranks to numeric values
    ranks_values = []
    for rank in ranks:
        if rank in rank_to_value:
            ranks_values.append(rank_to_value[rank])
        else:
            ranks_values.append(int(rank))
    
    # Sort the values
    ranks_values.sort()
    
    # Check regular straight
    diffs = [ranks_values[i] - ranks_values[i - 1] for i in range(1, len(ranks_values))]
    if all(diff == 1 for diff in diffs):
        return True
        
    # Check special case: Ace-low straight (A-2-3-4-5)
    if 14 in ranks_values:  # If we have an Ace
        # Replace 14 with 1 and sort again
        ranks_values.remove(14)
        ranks_values.append(1)
        ranks_values.sort()
        diffs = [ranks_values[i] - ranks_values[i - 1] for i in range(1, len(ranks_values))]
        return all(diff == 1 for diff in diffs)
        
    return False

def is_flush(hand):
  suits = [card[1] for card in hand]
  suit_counts = {suit: suits.count(suit) for suit in suits}
  return 5 in suit_counts.values()

def is_full_house(hand):
  ranks = [card[0] for card in hand]
  rank_counts = {rank: ranks.count(rank) for rank in ranks}
  return 3 in rank_counts.values() and 2 in rank_counts.values()

def evaluate_hand(hand):
  """
  Return 1 for pair,
    2 for two pair,
    3 for three of a kind,
    4 for straight,
    5 for flush,
    6 for full house
  """
  if is_pair(hand):
    return 1
  elif is_two_pair(hand):
    return 2
  elif is_three_of_kind(hand):
    return 3
  elif is_straight(hand):
    return 4
  elif is_flush(hand):
    return 5
  elif is_full_house(hand):
    return 6
  
def evaluate_hand_with_jokers(hand):
    """
    Evaluate a poker hand that may contain 1-2 jokers.
    Jokers can be any card to make the best possible hand.
    Returns the highest possible hand value.
    """
    # Count jokers
    jokers = len([card for card in hand if card[0] == 'Joker'])
    if jokers == 0:
        return evaluate_hand(hand)
    
    # Remove jokers from hand
    regular_cards = [card for card in hand if card[0] != 'Joker']
    
    # All possible ranks and suits
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    
    # Try all possible combinations for the jokers
    best_score = 0
    
    if jokers == 1:
        # Try each possible card for the single joker
        for rank in ranks:
            for suit in suits:
                test_hand = regular_cards + [(rank, suit)]
                score = evaluate_hand(test_hand)
                best_score = max(best_score, score)
    
    elif jokers == 2:
        # Try each possible card combination for both jokers
        for rank1 in ranks:
            for suit1 in suits:
                for rank2 in ranks:
                    for suit2 in suits:
                        test_hand = regular_cards + [(rank1, suit1), (rank2, suit2)]
                        score = evaluate_hand(test_hand)
                        best_score = max(best_score, score)
    
    return best_score

def get_high_card(hand):
    rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11}
    ranks = [rank_values.get(card[0], int(card[0])) for card in hand]
    return max(ranks)

def compare_hands(hand1, hand2):
    """
    Return 1 if hand1 is better, 2 if hand2 is better, 0 if they are the same
    """
    score1 = evaluate_hand_with_jokers(hand1)
    score2 = evaluate_hand_with_jokers(hand2)
    
    if score1 != score2:
        return 1 if score1 > score2 else 2
        
    # Same type of hand, compare high cards
    return 1 if get_high_card(hand1) > get_high_card(hand2) else 2

from itertools import combinations

def best_hand(cards):
    """
    Given 7 cards, find the best possible 5-card poker hand:
    find_best_hand(cards) -> list[tuple]

    Example: [('A','Hearts'), ('A','Spades'), ('A','Clubs'), ('K','Hearts'), 
            ('K','Spades'), ('2','Hearts'), ('3','Hearts')]
    """
    best_score = 0
    best_hand = None
    
    # Generate all possible 5-card combinations
    for five_cards in combinations(cards, 5):
        score = evaluate_hand_with_jokers(list(five_cards))
        if score > best_score:
            best_score = score
            best_hand = list(five_cards)
    
    return best_hand

def main():
  test_hand = (
    ('A', 'Hearts'),
    ('K', 'Spades'),
    ('Q', 'Clubs'),
    ('J', 'Diamonds'),
    ('10', 'Hearts'),
  )  
  
  print(evaluate_hand(test_hand))

if __name__ == "__main__":
  main()