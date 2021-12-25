from IPython.display import clear_output
from time import sleep
from typing import List, Optional

from _card import Card
from _deck import Deck
from _hand import Hand


class Blackjack:
    """
    The Blackjack class, which represents the various aspects of the game
    """

    def __init__(self, starting_money: int = 1000, h17: bool = True, can_dd_after_split: bool = True, max_splits: Optional[int] = 3, natural_after_split: bool = True, can_split_diff_tens: bool = True, one_hit_ace_split: bool = True, num_decks: int = 6, use_stop_card: bool = True, min_bet: int = 2, max_bet: Optional[int] = 500) -> None:
        """
        :param starting_money: The amount of money the player starts with
        :param h17: Whether the house hits on soft 17
        :param can_dd_after_split: Whether the player can double down after splitting
        :param max_splits: The maxmimum number of times the player can split in a round (None for unlimited)
        :param natural_after_split: Whether the player can get a natural after splitting
        :param can_split_diff_tens: Whether the player can split 10-cards when the ranks are different
        :param one_hit_ace_split: Whether the player must hit once after splitting aces
        :param num_decks: The number of decks to use throughout the game
        :param use_stop_card: Whether the deck should have a card placed near the bottom to prevent card counting (Must use at least 2 decks)
        :param min_bet: The minimum bet the player must place on a hand
        :param max_bet: The maximum bet the player can place on a hand (None for unlimited)
        """

        if not (starting_money >= 1):
            raise ValueError(
                f'starting money must be at least 1, got {starting_money}')

        if max_splits is not None and not (max_splits >= 0):
            raise ValueError(
                f'max_splits must be at least 0, got {max_splits}')

        if not (num_decks >= 1):
            raise ValueError(f'must use at least 1 deck, got {num_decks}')

        if use_stop_card and num_decks == 1:
            raise ValueError(
                f'must have at least 2 decks to use stop card, got 1')

        if not (min_bet >= 1):
            raise ValueError(f'minimum bet must be at least 1, got {min_bet}')

        if max_bet is not None and not (max_bet >= min_bet):
            raise ValueError(
                f'maximum bet must be greater than minimum bet, got {max_bet} < {min_bet}')

        self._money_left: int = starting_money
        self._h17: bool = h17
        self._can_dd_after_split: bool = can_dd_after_split
        self._max_splits: Optional[int] = max_splits
        self._natural_after_split: bool = natural_after_split
        self._can_split_diff_tens: bool = can_split_diff_tens
        self._one_hit_ace_split: bool = one_hit_ace_split
        self._deck: Deck = Deck(num_decks=num_decks,
                                use_stop_card=use_stop_card)
        self._min_bet: int = min_bet
        self._max_bet: Optional[int] = max_bet

        self._rounds_played: int = 0  # counter for total number of rounds player has played

    def _refresh_output(self) -> None:
        """
        Clears the output and prints header information
        """

        clear_output(wait=True)  # clear the screen

        # print round and money left
        print(f'Round {self.rounds_played + 1}')
        print(f'${self.money_left} left', end='\n\n')

    def _start_round(self) -> None:
        """
        Sets up the player's hand(s) and the house's hand
        """

        if not (self.money_left >= self.min_bet):
            raise ValueError(
                f'money left must be at least the minimum bet, got {self.money_left} < {self.min_bet}')

        self._refresh_output()  # clear screen and redisplay header info

        if self.money_left >= self.min_bet * 2:  # player has enough money for more than one hand
            # maximum number of hands player can afford
            max_hands: int = min(self.money_left//self.min_bet, 7)
            # number of hands player wants to play this round
            num_starting_hands: int = int(
                input(f'How many hands? (1 -> {max_hands}): '))

            if not (1 <= num_starting_hands <= 7):
                raise ValueError(
                    f'number of player hands must be 1-7, got {num_starting_hands}')

            min_money_needed = self.min_bet * num_starting_hands

            if not (self.money_left >= min_money_needed):
                raise ValueError(
                    f'money left must be at least the minimum bet times number of starting hands, got {self.money_left} < {min_money_needed}')

        else:
            num_starting_hands = 1  # only enough money for one hand

        self._player_hands: List[Hand] = [Hand() for _ in range(
            num_starting_hands)]  # create player's hands
        self._house_hand: List[Hand] = Hand()  # create house hand

    def _collect_bets(self) -> None:
        """
        Gathers bets for each player hand
        """

        self._bets: List[int] = []

        for i in range(self.num_player_hands):  # iterate through player hands
            self._refresh_output()  # clear screen and redisplay header info

            # max possible bet takes into account previous bets
            max_bet: int = min(self.money_left - sum(self._bets),
                               self.max_bet if self.max_bet is not None else float('inf'))
            # how much player bets on current hand
            bet: int = int(
                input(f'<Hand {i + 1}> Bet (${self.min_bet} -> ${max_bet}): '))

            # bet must be at least minimum and at most maximum or the money available
            if not (bet >= self.min_bet):
                raise ValueError(
                    f'bet must be at least the minimum bet, got {self.bet} < {self.min_bet}')

            if not (bet <= max_bet):
                raise ValueError(
                    f'bet must be at at most the least of either the money left or maximum bet, got {bet} > {max_bet}')

            self._bets.append(bet)  # remember bet

        print()

    def _show_hands(self) -> None:
        """
        Shows the face-up cards and scores of the player's hand(s) and house hand
        """

        self._refresh_output()  # clear screen and redisplay header info

        for i in range(len(self._player_hands)):
            print(
                f'<Hand {i + 1}> ({self._player_hands[i].display_score}): {self._player_hands[i]} -> ${self._bets[i]}')  # info for player hand, i.e. <Hand 1> (12): [2♠, 10♠] -> $10

        print()
        print(
            f'<House> ({self._house_hand.display_score}): {self._house_hand}', end='\n\n')  # info for house hand, i.e. <House> (8+): [8♠, 🂠]
        sleep(0.5)

    def _deal(self) -> None:
        """
        Deals two cards to each player hand and the house hand
        """

        self._refresh_output()  # clear screen and redisplay header info

        if self.deck.insert_reached:  # stop card was reached on previous round
            self.deck.shuffle()  # reset the deck

            self.deck.insert_reached = False  # new stop card

        self._show_hands()

        # player's first card(s)
        for i in range(len(self._player_hands)):
            card: Card = self._deck.draw_card()

            self._player_hands[i].add(card)

            self._show_hands()

        # house's first card (face down)
        card: Card = self._deck.draw_card(face_down=True)

        self._house_hand.add(card)

        self._show_hands()

        # player's second card(s)
        for i in range(len(self._player_hands)):
            card: Card = self._deck.draw_card()

            self._player_hands[i].add(card)

            self._show_hands()

        # house's second card
        card: Card = self._deck.draw_card()

        self._house_hand.add(card, front=True)

        self._show_hands()

    def _check_naturals(self) -> None:
        """
        Checks if the player and/or house has a natural (21 with two cards)
        """

        self._results: List[Optional[int]] = [
            None] * self.num_player_hands  # store money results of player's hands

        # house natural
        if self._house_hand.is_21:
            self._house_hand[1].flip()

            self._show_hands()

            print(f'<House> has a natural', end='\n\n')

        for i in range(len(self._player_hands)):
            # player natural and no house natural: 1.5x win
            if self._player_hands[i].is_21 and not self._house_hand.is_21:
                print(f'<Hand {i + 1}> has a natural', end='\n\n')

                self._results[i] = int(
                    round(self._bets[i] * 1.5))

            # house natural and no player natural: lose
            elif self._house_hand.is_21 and not self._player_hands[i].is_21:
                self._results[i] = -self._bets[i]

            # player natural and house natural: win
            elif self._player_hands[i].is_21 and self._house_hand.is_21:
                print(f'<Hand {i + 1}> has a natural', end='\n\n')

                self._results[i] = 0

    def _player_turn(self) -> None:
        """
        Performs actions for player's hand(s) and deals extra cards if necessary
        """

        i: int = 0

        while i < len(self._player_hands):
            # hand is at least 21 and is done being played
            if self._results[i] is not None:
                i += 1

                continue

            while True:
                actions: List[str] = ['Hit', 'Stand']
                choices: List[str] = ['h', 's']

                if self.one_hit_ace_split and self._player_hands[i].times_split == 1 and self._player_hands[i][0] == 1:
                    choice: str = 'h'  # player has to hit after splitting aces

                    one_hit_ace: bool = True  # player cannot play the hand anymore

                else:
                    one_hit_ace: bool = False

                    # player has enough money to redo bet
                    if self.money_left - sum(self._bets) >= self._bets[i] and (self.can_dd_after_split or self._player_hands[i].times_split == 0):
                        actions.append('Double Down')
                        choices.append('dd')

                    # house rules allow player to split cards and player has enough money to redo bet
                    if (self._player_hands[i].can_split if self.can_split_diff_tens else self._player_hands[i].can_split_same) and (self.max_splits is None or self._player_hands[i].times_split < self.max_splits) and self.money_left - sum(self._bets) >= self._bets[i]:
                        actions.append('Split')
                        choices.append('sp')

                    choice: str = input(
                        f'<Hand {i + 1}> ({self._player_hands[i].display_score}): {"? ".join(actions)} ({"/".join(choices)}): ').lower()  # get player action, i.e. <Hand 1> (12): Hit? Stand? Double Down? (h/s/dd):

                    if choice not in choices:
                        raise ValueError(
                            f'choice must be one of ({"/".join(choices)}), got {choice!r}')

                    print()

                if choice == 's':  # stand
                    self._show_hands()

                    break

                elif choice == 'dd':  # double down
                    self._bets[i] *= 2

                elif choice == 'sp':  # split
                    # make another hand from second card
                    hand: Hand = self._player_hands[i].split()

                    # add new hand to player's hands
                    self._player_hands.insert(i + 1, hand)
                    self._bets.insert(i + 1, self._bets[i])
                    self._results.insert(i + 1, None)

                    self._show_hands()

                    continue

                card: Card = self._deck.draw_card()  # draw card for player

                self._player_hands[i].add(card)

                self._show_hands()

                if self._player_hands[i].is_busted:  # hand is busted: loss
                    print(
                        f'<Hand {i + 1}> is busted with {self._player_hands[i].score}', end='\n\n')

                    self._results[i] = -self._bets[i]

                    break

                if self._player_hands[i].is_21:
                    # hand had previously split and house rules allow naturals after splits: 1.5x win
                    if self.natural_after_split and len(self._player_hands[i]) == 2:
                        print(f'<Hand {i + 1}> has a natural', end='\n\n')

                        self._results[i] = int(round(self._bets[i] * 1.5))

                    else:  # non-natural 21
                        print(f'<Hand {i + 1}> has 21', end='\n\n')

                    break

                if choice == 'dd' or one_hit_ace:
                    break  # doubling down or splitting aces allows only one hit

            i += 1

    def _house_turn(self) -> None:
        """
        Reveals the house's card and deals extra cards while under 17
        """

        # at least one player hand is under 21 (round is not over)
        if any(result is None for result in self._results):
            self._house_hand[1].flip()  # reveal house card

            self._show_hands()

            # while dealer score is under 17 (taking into account soft 17 rule)
            while self._house_hand.score < 17 or self._house_hand.is_s17 and self.h17:
                card: Card = self._deck.draw_card()  # draw new card

                self._house_hand.add(card)

                self._show_hands()

            if self._house_hand.is_busted:
                print(
                    f'<House> is busted with {self._house_hand.score}', end='\n\n')

                for i in range(len(self._player_hands)):
                    if self._results[i] is None:
                        # hand is still valid: win
                        self._results[i] = self._bets[i]

    def _show_results(self) -> None:
        """
        Go through player hands and show the results of each bet
        """

        # house finished its hand
        if not self._house_hand.has_flipped_cards and not (self._house_hand.score == 21 and len(self._house_hand) == 2):
            print(f'<House> has {self._house_hand.score}',
                  end='\n\n')  # display house's score

        for i in range(len(self._player_hands)):
            # house was a natural
            if self._house_hand.score == 21 and len(self._house_hand) == 2:
                # player hand was a natural: tie
                if self._player_hands[i].score == 21:
                    print(f'<Hand {i + 1}> ties with a natural -> +$0')

                # player hand was not natural (and house was a natural): loss
                else:
                    print(
                        f'<Hand {i + 1}> loses with no natural -> -${self._bets[i]}')

            # player hand was a natural: 1.5x win
            elif self._player_hands[i].score == 21 and self._results[i] == round(self._bets[i] * 1.5):
                print(
                    f'<Hand {i + 1}> wins with a natural -> +${self._results[i]}')

            # player hand was busted: loss
            elif self._player_hands[i].score > 21:
                print(
                    f'<Hand {i + 1}> loses with a busted {self._player_hands[i].score} -> -${self._bets[i]}')

            elif self._house_hand.is_busted:  # house was busted: win
                print(
                    f'<Hand {i + 1}> wins with a non-busted {self._player_hands[i].score} -> +${self._bets[i]}')

            # house score was greater than player score: loss
            elif self._player_hands[i].score < self._house_hand.score:
                print(
                    f'<Hand {i + 1}> loses with {self._player_hands[i].score} < {self._house_hand.score} -> -${self._bets[i]}')

                self._results[i] = -self._bets[i]

            # player score was greater than house score: win
            elif self._player_hands[i].score > self._house_hand.score:
                print(
                    f'<Hand {i + 1}> wins with {self._player_hands[i].score} > {self._house_hand.score} -> +${self._bets[i]}')

                self._results[i] = self._bets[i]

            else:  # player score was equal to house score: tie
                print(
                    f'<Hand {i + 1}> ties with {self._player_hands[i].score} = {self._house_hand.score} -> +$0')

                self._results[i] = 0

        print()

    def _end_round(self) -> None:
        """
        Shows result of round and asks to play again
        """

        result: int = sum(self._results)  # change in money

        self._money_left += result

        if result < 0:
            neg = True
            result = abs(result)

        else:
            neg = False

        print(
            f'Result: {"-" if neg else "+"}${result} -> ${self.money_left}', end='\n\n')  # display result of round, i.e. Result: +$100 -> $820

        self._rounds_played += 1

        if self.money_left >= self.min_bet:  # player has enough money to play another round
            play_again = input('Play Again? (y/n): ').lower()

            if play_again not in ('y', 'n'):
                raise ValueError(
                    f'answer must be one of (y/n), got {play_again!r}')

            if play_again == 'y':
                self.play()

            else:
                clear_output()

        else:  # player does not have enough money to play another round
            clear_output()

    def play(self) -> None:
        """
        Plays a round of blackjack
        """

        self._start_round()
        self._collect_bets()
        self._deal()
        self._check_naturals()
        self._player_turn()
        self._house_turn()
        self._show_results()
        self._end_round()

    @property
    def deck(self) -> Deck:
        return self._deck

    @property
    def money_left(self) -> int:
        return self._money_left

    @property
    def h17(self) -> bool:
        return self._h17

    @property
    def can_dd_after_split(self) -> bool:
        return self._can_dd_after_split

    @property
    def max_splits(self) -> Optional[int]:
        return self._max_splits

    @property
    def natural_after_split(self) -> bool:
        return self._natural_after_split

    @property
    def can_split_diff_tens(self) -> bool:
        return self._can_split_diff_tens

    @property
    def one_hit_ace_split(self) -> bool:
        return self._one_hit_ace_split

    @property
    def min_bet(self) -> int:
        return self._min_bet

    @property
    def max_bet(self) -> Optional[int]:
        return self._max_bet

    @property
    def rounds_played(self) -> int:
        return self._rounds_played

    @property
    def num_decks(self) -> int:
        return self._deck.num_decks

    @property
    def use_stop_card(self) -> bool:
        return self._deck.use_stop_card

    @property
    def num_cards(self) -> int:
        return self._deck.num_cards

    @property
    def num_player_hands(self) -> int:
        return len(self._player_hands)
