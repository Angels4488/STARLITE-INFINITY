import random
import time

class SimonSaysGame:
    """Simple Simon Says game for reinforcement learning."""
    def __init__(self):
        self.sequence = []
        self.score = 0
        self.actions = ['red', 'blue', 'green', 'yellow']

    def next_round(self):
        self.sequence.append(random.choice(self.actions))
        return self.sequence.copy()

    def check_response(self, user_sequence):
        if user_sequence == self.sequence:
            self.score += 1
            return True, self.score
        else:
            self.score = 0
            self.sequence = []
            return False, self.score

class UnoGame:
    """Simple UNO game for agent play and RL."""
    def __init__(self):
        self.colors = ['red', 'yellow', 'green', 'blue']
        self.values = [str(n) for n in range(0, 10)] + ['skip', 'reverse', 'draw2']
        self.deck = [(c, v) for c in self.colors for v in self.values]
        self.hand = []
        self.discard = []
        self.reset()

    def reset(self):
        self.hand = random.sample(self.deck, 7)
        self.discard = [random.choice(self.deck)]

    def play_card(self, card):
        if card in self.hand and (card[0] == self.discard[-1][0] or card[1] == self.discard[-1][1]):
            self.hand.remove(card)
            self.discard.append(card)
            return True, f"Played {card}. Cards left: {len(self.hand)}"
        return False, "Invalid card. Try again."

    def draw_card(self):
        card = random.choice(self.deck)
        self.hand.append(card)
        return card

    def get_state(self):
        return {
            'hand': self.hand,
            'discard': self.discard[-1]
        }

class AptitudeTest:
    """Army/Navy style aptitude test for agents."""
    def __init__(self):
        self.questions = [
            ("What is 7 x 8?", "56"),
            ("Which is heavier: 1kg of steel or 1kg of feathers?", "same"),
            ("What is the capital of France?", "paris"),
            ("If a train leaves at 3pm and travels 60 miles in 1 hour, what time does it arrive?", "4pm"),
            ("Spell 'aptitude' backwards.", "edutpA")
        ]
        self.index = 0
        self.score = 0

    def next_question(self):
        if self.index < len(self.questions):
            q = self.questions[self.index][0]
            return q
        return None

    def check_answer(self, answer):
        correct = self.questions[self.index][1].lower()
        if answer.lower() == correct:
            self.score += 1
            result = True
        else:
            result = False
        self.index += 1
        return result, self.score

    def reset(self):
        self.index = 0
        self.score = 0

class Gauntlet:
    """Army/Navy mental conditioning gauntlet."""
    def __init__(self):
        self.challenges = [
            ("Solve: 12 + 15", "27"),
            ("Memory: Repeat 'red blue green yellow'", "red blue green yellow"),
            ("Logic: If all cats are mammals and Tom is a cat, is Tom a mammal?", "yes"),
            ("Speed: Type 'Bravo Zulu' in 3 seconds!", "bravo zulu"),
            ("Spatial: Which direction is north if the sun rises in the east?", "left")
        ]
        self.index = 0
        self.score = 0
        self.start_time = None

    def next_challenge(self):
        if self.index < len(self.challenges):
            self.start_time = time.time()
            return self.challenges[self.index][0]
        return None

    def check_response(self, response):
        correct = self.challenges[self.index][1].lower()
        elapsed = time.time() - self.start_time if self.start_time else 0
        if response.lower() == correct and elapsed < 10:
            self.score += 1
            result = True
        else:
            result = False
        self.index += 1
        return result, self.score, elapsed

    def reset(self):
        self.index = 0
        self.score = 0
        self.start_time = None
