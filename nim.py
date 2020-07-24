import random
import time


class Nim:
    def __init__(self, initial=None):
        """
        Initialize game board.
        """

        if initial is None:
            initial = [1, 3, 5, 7]

        self.piles = initial.copy()

        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Takes a piles list as input and returns all of the available actions in that state.
        """

        actions = set()

        for i, pile in enumerate(piles):
            for j in range(1, piles[i] + 1):
                actions.add((i, j))

        return actions

    @classmethod
    def other_player(cls, player):
        """
        Returns the player that is not `player`.
        """

        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch the current player to the other player.
        """

        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Make the move for the current player.
        """

        pile, count = action

        # Check for errors
        if self.winner is not None:
            raise Exception("Game already won.")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile.")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects.")

        # Update pile
        self.piles[pile] -= count

        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI:
    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary, an alpha (learning) rate, and an epsilon rate.
        """

        self.q = dict()

        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken in that state, a new resulting state,
        and the reward received from taking that action.
        """

        old = self.get_q_value(old_state, action)

        best_future = self.best_future_reward(new_state)

        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state and the action.
        """

        return self.q.get((tuple(state), action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state and the action given the previous Q-value, a current reward,
        and an estimate of future rewards.
        """

        self.q[tuple(state), action] = old_q + self.alpha * ((reward + future_rewards) - old_q)

    def best_future_reward(self, state):
        """
        Given a state, consider all possible pairs available and return the maximum of all of their Q-values.
        """

        state = tuple(state)

        result = 0

        # Iterating through Q dictionary to find the highest reward value
        for (i, j), reward in self.q.items():
            if i == state:
                result = max(result, reward)

        return result

    def choose_action(self, state, epsilon=True):
        """
        Given a state, return an action to take.
        """

        actions = Nim.available_actions(state)

        if epsilon:
            # Probability of True is `self.epsilon` and False is `1 - self.epsilon`
            random_ = random.choices([True, False], [self.epsilon, 1 - self.epsilon])[0]

            # If using epsilon, choose random action, otherwise choose best action
            return random.choice(list(actions)) if random_ else self.best_action(state, actions)
        else:
            # If not using epsilon, choose best action
            return self.best_action(state, actions)

    def best_action(self, state, actions):
        # Starting with empty action and max value
        action, maximum = tuple(), 0

        # Converting state list to tuple
        state = tuple(state)

        # Iterating through actions
        for move in actions:
            # Checking for key existence
            try:
                reward = self.q[state, move]
            except KeyError:
                continue
            
            # If reward found is higher than current max value or action is empty (first time), update
            if reward > maximum or not action:
                action = move
                maximum = reward

        # Result is an action if it was found, otherwise a random choice
        return action if action else random.choice(list(actions))


def train(n):
    """
    Train an AI by playing games against itself.
    """

    player = NimAI()

    # Play games
    for i in range(n):
        print(f"Playing training game {i + 1}...")

        game = Nim()

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:
            # Keep track of current state and action
            state = game.piles.copy()

            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)

            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)

                player.update(last[game.player]["state"], last[game.player]["action"], new_state, 1)

                break
            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(last[game.player]["state"], last[game.player]["action"], new_state, 0)

    print("Done training.")

    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:
        # Print contents of piles
        print("\nPiles:")

        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")

        # Compute available actions
        available_actions = Nim.available_actions(game.piles)

        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("\nYour turn!")

            while True:
                pile = int(input("Choose pile: "))
                count = int(input("Choose count: "))

                if (pile, count) in available_actions:
                    break

                print("Invalid move, try again.")
        # Have AI make a move
        else:
            print("\nAI's turn!")

            pile, count = ai.choose_action(game.piles, epsilon=False)

            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print("\nGAME OVER!")

            winner = "Human" if game.winner == human_player else "AI"

            print(f"{winner} won!")

            return None
