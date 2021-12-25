from random import randint, shuffle
from time import sleep
from typing import List

from _card import Card
from _cards import STOP_CARD


class Deck:
    """
    The Deck class, which represents a deck of cards
    """

    def __init__(self, num_decks: int = 1, use_stop_card: bool = False) -> None:
        """
        :param num_decks: The number of decks to use
        :param use_stop_card: Whether the deck should have a card placed near the bottom to prevent card counting
        """

        self._num_decks: int = num_decks
        self._use_stop_card: bool = use_stop_card

        # keep track of when a deck needs to be reshuffled after the round
        self._insert_reached: bool = False
        self._num_cards: int = 52 * self._num_decks  # 52 cards per deck

        self._reset_cards()  # intialize the deck's cards

    def _reset_cards(self) -> None:
        """
        Resets the deck with its original number of cards in a random order
        """

        self._cards: List[Card] = [Card(i, j, is_flipped=True) for i in range(1, 14)
                                   for j in range(1, 5) for _ in range(self._num_decks)]  # makes the necessary amount of 52-card decks

        shuffle(self.cards)

        if self.use_stop_card:
            # stop card is inserted near the end of the deck randomly
            self.cards.insert(randint(60, 75), Card.stop_card())

    def shuffle(self) -> None:
        """
        Shuffles the cards of the deck
        """

        # display shuffling animation
        print('Shuffling', end='')
        sleep(0.5)

        for _ in range(3):
            print('.', end='')
            sleep(0.5)

        print('.', end='\n\n')
        sleep(0.5)

        self._reset_cards()  # remake the deck and shuffle it

    def draw_card(self, face_down: bool = False) -> Card:
        """
        Removes the top card from the deck and returns it
        If the deck is empty, it will reshuffle the cards

        :return: The top card of the deck
        """

        if not self.cards:  # deck is empty
            print('Out of cards...')

            self.shuffle()  # reset the deck

        card: Card = self.cards.pop()  # draw a card

        if card == STOP_CARD:  # drawn card was stop card
            self._insert_reached: bool = True  # remember to shuffle deck after round

            print('Insert Reached...')

            card: Card = self.cards.pop()  # draw a replacement card

        if not face_down:
            card.flip()  # give it to player face up if not specified

        return card

    @property
    def num_decks(self) -> int:
        return self._num_decks

    @property
    def use_stop_card(self) -> bool:
        return self._use_stop_card

    @property
    def num_cards(self) -> int:
        return self._num_cards

    @property
    def cards(self) -> List[Card]:
        return self._cards

    @property
    def insert_reached(self) -> bool:
        return self._insert_reached

    @insert_reached.setter
    def insert_reached(self, insert_reached: bool) -> None:
        """
        :param insert_reached: Whether the stop card has been reached
        """

        # changed when deck should be shuffled after round
        self._insert_reached: bool = insert_reached

    @property
    def cards_left(self) -> int:
        if not self.use_stop_card:
            # deck without stop card has all of its cards left
            return len(self.cards)

        # cards left until stop card
        return len(self.cards) - self.cards.index(Card.stop_card()) - 1
