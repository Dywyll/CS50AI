import random


class Minesweeper:
    """
    Minesweeper game representation.
    """

    def __init__(self, height=8, width=8, mines=8):
        # Set initial width, height, and number of mines
        self.height = height
        self.width = width

        self.mines = set()

        # At first, player has found no mines
        self.mines_found = set()

        # Initialize an empty field with no mines
        self.board = list()

        for i in range(self.height):
            row = list()

            for j in range(self.width):
                row.append(False)

            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)

            if not self.board[i][j]:
                self.mines.add((i, j))

                self.board[i][j] = True

    def print(self):
        """
        Prints a text-based representation of where mines are located.
        """

        for i in range(self.height):
            print("--" * self.width + "-")

            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")

            print("|")

        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell

        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """

        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of board cells, and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)

        self.count = count

        self.mines = set()
        self.safes = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __hash__(self):
        return hash((tuple(self.cells), self.count))

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.mines.add(cell)

            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that a cell is known to be safe.
        """

        if cell in self.cells:
            self.cells.remove(cell)
            self.safes.add(cell)


class MinesweeperAI:
    """
    Minesweeper game player.
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # Set of sentences about the game known to be true
        self.knowledge = set()

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge to mark that cell as a mine as well.
        """

        self.mines.add(cell)

        self.moves_made.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge to mark that cell as safe as well.
        """

        self.safes.add(cell)

        self.moves_made.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given safe cell,
        how many neighboring cells have mines in them.
        """

        # Add cell to safe cells
        self.safes.add(cell)

        # Mark cell as a move that's been made
        self.moves_made.add(cell)

        # Add new sentence to AI knowledge base
        cells = list()

        x, y = cell

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) != cell:
                    cells.append((i, j))

        self.knowledge.add(Sentence(cells, count))

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # Mark additional cells as safe or mines
        for sentence in self.knowledge:
            if sentence.count == len(sentence.cells):
                for cell in sentence.cells:
                    self.mines.add(cell)
            if sentence.count == 0:
                for cell in sentence.cells:
                    self.safes.add(cell)

        for mine in self.mines:
            for sentence in self.knowledge:
                sentence.mark_mine(mine)

        for safe in self.safes:
            for sentence in self.knowledge:
                sentence.mark_safe(safe)

        # Adding knowledge to base based on other knowledge
        sentences = list()

        for x in self.knowledge:
            for y in self.knowledge:
                if x != y and y.cells.issubset(x.cells):
                    sentences.append(Sentence(x.cells.difference(y.cells), x.count - y.count))

        for sentence in sentences:
            self.knowledge.add(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move that has been made.
        This function may use the knowledge in self.mines, self.safes and self.moves_made,
        but should not modify any of those values.
        """

        for i, j in self.safes:
            if (i, j) not in self.moves_made:
                return i, j

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """

        forbidden = self.mines.union(self.moves_made)

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in forbidden:
                    return i, j

        return None
