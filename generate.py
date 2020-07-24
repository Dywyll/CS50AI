import sys

from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """

        self.crossword = crossword

        self.domains = {var: self.crossword.words.copy() for var in self.crossword.variables}

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """

        letters = [
            [None for _ in range(self.crossword.width)] for _ in range(self.crossword.height)
        ]

        for variable, word in assignment.items():
            direction = variable.direction

            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)

                letters[i][j] = word[k]

        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """

        letters = self.letter_grid(assignment)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")

            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """

        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100

        cell_border = 2

        interior_size = cell_size - 2 * cell_border

        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black"
        )

        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)

        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                ]

                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, "white")

                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font)

                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2), rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], "black", font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """

        self.enforce_node_consistency()

        self.ac3()

        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        """

        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        """

        words = list()

        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        a, b = overlap

        for i in self.domains[x]:
            flag = False

            for j in self.domains[y]:
                if i != j and i[a] == j[b]:
                    flag = True
                    break

            if not flag:
                words.append(i)

        for word in words:
            self.domains[x].remove(word)

        return len(words) > 0

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        """

        if arcs is None:
            arcs = list()

            for i in self.crossword.variables:
                for j in self.crossword.neighbors(i):
                    arcs.append((i, j))

        for x, y in arcs:
            if self.revise(x, y):
                if self.domains[x] == 0:
                    return False

                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete.
        """

        for i in self.crossword.variables:
            if i not in assignment.keys() or assignment[i] not in self.crossword.words:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent.
        """

        for i in assignment:
            x = assignment[i]

            if i.length != len(x):
                return False

            for j in assignment:
                y = assignment[j]

                if i != j:
                    if x == y:
                        return False

                    overlap = self.crossword.overlaps[i, j]

                    if overlap is not None:
                        a, b = overlap

                        if x[a] != y[b]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`,
        in order by the number of values they rule out for neighboring variables.
        """

        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        """

        for var in self.crossword.variables:
            if var not in assignment.keys():
                return var

    def backtrack(self, assignment):
        """
        Using backtracking search,
        take as input a partial assignment for the crossword and return a complete assignment if possible to do so.
        """

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)

                if result is not None:
                    return result
                else:
                    assignment[var] = None

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]

    words = sys.argv[2]

    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)

    creator = CrosswordCreator(crossword)

    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)

        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
