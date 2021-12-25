from __future__ import annotations
from typing import Iterable, List, Union

from _card import Card
from _cards import ACE, SIX


class Hand:
    """
    The Hand class, which represents one or more cards that a player is holding
    """

    def __init__(self, *args: Card, times_split: int = 0) -> None:
        """
        :param cards: The cards of the hand, or None for an empty hand
        :param times_split: The number of times the hand has previously been split
        """

        if not (times_split >= 0):
            raise ValueError(
                f'times split must be at least 0, got {times_split}')

        self._cards: List[Card] = list(args)
        # keep track of the times a player split a hand, house rules can limit this
        self._times_split: int = times_split

    def __repr__(self) -> str:
        return repr(self.cards)

    def __iter__(self) -> Iterable[Card]:
        return iter(self.cards)

    def __getitem__(self, i) -> Card:
        return self.cards[i]

    def __eq__(self, other: Union[Hand, List[Card]]) -> bool:
        # order doesn't matter when comparing hands, must have same length and card ranks
        return sorted(self) == sorted(other)

    def __len__(self) -> int:
        return len(self.cards)

    def _orient_hand(self) -> None:
        """
        If the hand is busted, changes 11-aces to 1-aces where possible
        """

        while self.is_busted:  # check if the hand is still busted
            for card in self:  # look for 11-aces
                if card.value == 11:  # 11-ace
                    card.value = 1  # 11 -> 1

                    break  # check if hand is no longer busted

            else:
                break  # no 11-aces found

    def add(self, card: Card, front: bool = False) -> None:
        """
        Adds a card to the hand

        :param card: The card to add
        :param front: Whether to put the card at the front of the hand
        """

        if not front:
            self.cards.append(card)  # add card to back of hand
        else:
            self._cards: List[Card] = [card] + \
                self.cards  # add card to front of hand

        self._orient_hand()  # card might have busted hand, try to reduce 11-aces

    def split(self) -> Hand:
        """
        Splits the hand into two hands, one with the first card and one with the second card

        :return: The hand with the second card
        """

        self._times_split += 1  # increase the first hand's times_split

        if self[0].value == 1:  # 1-ace
            self[0].value = 11  # 1 -> 11

        # take second card out of hand
        card: Card = self.cards.pop()

        # return second card as a new hand along with times the hand has been split
        return Hand(card, times_split=self.times_split)

    @property
    def cards(self) -> List[Card]:
        return self._cards

    @property
    def times_split(self) -> bool:
        return self._times_split

    @property
    def display_score(self) -> str:
        if not [card for card in self if not card.is_flipped]:  # no cards are visible yet
            return ''  # no score is shown

        # visible score is the sum of the values for all visible cards
        score: int = sum(card.value for card in self if not card.is_flipped)

        if score >= 21:  # hand is busted
            return str(score)  # only possible score

        score: int = f'{score}/{score-10}' if any(
            card.value == 11 for card in self if not card.is_flipped) else str(score)  # hands with aces are shown with 2 possible scores

        if self.has_flipped_cards:
            score += '+'  # hands with flipped cards are signified as actually having a higher score

        return score

    @property
    def score(self) -> int:
        # true score is sum of all card values
        return sum(card.value for card in self)

    @property
    def is_busted(self) -> bool:
        return self.score > 21  # busted hands are hands over 21

    @property
    def is_21(self) -> bool:
        return self.score == 21  # hands with 21 are completed

    @property
    def has_flipped_cards(self) -> bool:
        # hands with flipped cards still have to be played
        return any(card.is_flipped for card in self)

    @property
    def can_split(self) -> bool:
        if len(self) != 2:
            return False  # can only split hands that have exactly 2 cards

        if self[0] > 10:
            # face cards don't need to have the same rank to split
            return self[0].value == self[1].value

        return self.can_split_same  # otherwise the ranks have to match to split

    @property
    def can_split_same(self) -> bool:
        # can split hands with 2 cards and matching ranks
        return len(self) == 2 and self[0] == self[1]

    @property
    def is_s17(self) -> bool:
        # soft 17 (A and 6), where the house either hits or stands, depending on house rules
        return self == (ACE, SIX)
