import random


class GameSession:

    def __init__(self, time_limit, topic):
        self.time_limit = time_limit
        self.topic = topic
        digit_one = random.randint(0, 9)
        digit_two = random.randint(0, 9)
        digit_three = random.randint(0, 9)
        digit_four = random.randint(0, 9)
        self.session_id = str(digit_one) + str(digit_two) + str(digit_three) + str(digit_four)