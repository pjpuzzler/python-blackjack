from __future__ import annotations
from typing import Union

from _symbols import RANK_SYMBOLS, SUIT_SYMBOLS
from _types import Rank, Suit


class Card:
    """
    The Card class, which represents a single playing card
    """

    def __init__(self, rank: Rank, suit: Suit = 0, is_flipped: bool = False) -> None:
        """
        :param rank: The rank of the card (1=A, 2=2, ..., 13=K)
        :param suit: The suit of the card (1=♠, 2=♥, 3=♦, 4=♣)
        :param is_flipped: Whether or not the card is visible to the user
        """

        if not (0 <= rank <= 13):
            raise ValueError(f'rank must be 0-13, got {rank}')

        if not (0 <= suit <= 4):
            raise ValueError(f'suit must be 0-4, got {suit}')

        self._rank: Rank = rank
        self._suit: Suit = suit
        self._is_flipped: bool = is_flipped

        if self == 1:  # A
            self._value: int = 11  # aces are worth 11 to start

        elif 11 <= self <= 13:  # J-K
            self._value: int = 10  # face cards are worth 10

        else:  # 0, 2-10
            self._value: int = self.rank  # numeric and stop cards are worth their rank

    def __repr__(self) -> str:
        if self.is_flipped:
            return '🂠'  # flipped cards are not displayed to the player

        # show card's rank and suit, i.e. '4♥'
        return self.rank_symbol + self.suit_symbol

    def __eq__(self, other: Union[Card, Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank == other  # compare card's rank to a rank number

        return self.rank == other.rank  # compare card's rank to another card's rank

    def __gt__(self, other: Union[Card, Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank > other  # compare card's rank to a rank number

        return self.rank > other.rank  # compare card's rank to another card's rank

    def __lt__(self, other: Union[Card, Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank < other  # compare card's rank to a rank number

        return self.rank < other.rank  # compare card's rank to another card's rank

    def __ge__(self, other: Union[Card, Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank >= other  # compare card's rank to a rank number

        return self.rank >= other.rank  # compare card's rank to another card's rank

    def __le__(self, other: Union[Card, Rank]) -> bool:
        if isinstance(other, Rank):
            return self.rank <= other  # compare card's rank to a rank number

        return self.rank <= other.rank  # compare card's rank to another card's rank

    def flip(self) -> None:
        """
        Flips a card, making it either visible or not visible
        """

        self._is_flipped: bool = not self.is_flipped  # change the card's flipped value

    @property
    def rank(self) -> Rank:
        return self._rank

    @property
    def suit(self) -> Suit:
        return self._suit

    @property
    def is_flipped(self) -> bool:
        # if card isn't a stop card, it could be flipped, otherwise it couldn't be
        return self._is_flipped if self != 0 else False

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """
        Can change the value of an ace

        :param value: The new value of the ace (must be either 11 or 1)
        """

        if self != 1:
            raise ValueError(
                f'card must be an ace to change value, is {self.rank_symbol!r}')

        if value not in (11, 1):
            raise ValueError(
                f'new value must be one of (11, 1), got {value}')

        self._value: int = value  # change the value of an ace to 11 or 1

    @property
    def rank_symbol(self) -> str:
        # stop cards are shown as a blank rectangle
        return RANK_SYMBOLS[self.rank - 1] if self.rank != 0 else '■'

    @property
    def suit_symbol(self) -> str:
        return SUIT_SYMBOLS[self.suit - 1] if self.suit != 0 else ''

    @classmethod
    def stop_card(cls) -> Card:
        """
        Returns the card that signifies the deck should be reshuffled

        :return: The stop card
        """

        return Card(0)  # stop cards have a rank of 0 and no suit
