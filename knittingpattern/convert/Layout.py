"""Map ``(x, y)`` coordinates to instructions

"""
from itertools import chain
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
INSTRUCTION_HEIGHT = 1


class InGrid(object):

    """Base class for things in a grid"""

    def __init__(self, position):
        """Create a new InGrid object."""
        self._position = position

    @property
    def x(self):
        """:return: x coordinate in the grid
        :rtype: float
        """
        return self._position.x

    @property
    def y(self):
        """:return: y coordinate in the grid
        :rtype: float
        """
        return self._position.y

    @property
    def xy(self):
        """:return: ``(x, y)`` coordinate in the grid
        :rtype: float
        """
        return self._position

    @property
    def width(self):
        """:return: width of the instruction on the grid
        :rtype: float
        """
        return self._number_of_consumed_meshes

    @property
    def height(self):
        """:return: height of the instruction on the grid
        :rtype: float
        """
        return INSTRUCTION_HEIGHT


class InstructionInGrid(InGrid):

    """Holder of an instruction in the GridLayout."""

    def __init__(self, instruction, position):
        """
        :param instruction: an :class:`instruction
          <knittingpattern.Instruction.InstructionInRow>`
        :param Point position: the position of the :paramref:`instruction`

        """
        self._instruction = instruction
        super().__init__(position)

    @property
    def _number_of_consumed_meshes(self):
        """:return: the number of consumed meshes"""
        return self._instruction.number_of_consumed_meshes

    @property
    def instruction(self):
        """:return: instruction that is placed on the grid
        :rtype: knittingpattern.Instruction.InstructionInRow
        """
        return self._instruction

    @property
    def color(self):
        """:return: the color of the :attr:`instruction`"""
        return self._instruction.color


class RowInGrid(InGrid):
    """Assign x and y coordinates to rows."""

    def __init__(self, row, position):
        """Create a new row in the grid."""
        super().__init__(position)
        self._row = row

    @property
    def _number_of_consumed_meshes(self):
        """:return: the number of consumed meshes"""
        return self._row.number_of_consumed_meshes

    @property
    def instructions(self):
        """:return: the instructions in a grid"""
        x = self.x
        y = self.y
        for instruction in self._row.instructions:
            instruction_in_grid = InstructionInGrid(instruction, Point(x, y))
            x += instruction_in_grid.width
            yield instruction_in_grid


def identity(object_):
    """:return: the argument"""
    return object_


class _RecursiveWalk(object):
    """This class starts walking the knitting pattern and maps instructions to
    positions in the grid that is created."""

    def __init__(self, first_instruction):
        """Start walking the knitting pattern starting from first_instruction.
        """
        self._rows_in_grid = {}
        self._todo = []
        self._expand(first_instruction.row, Point(0, 0), [])
        self._walk()

    def _expand(self, row, consumed_position, passed):
        """Add the arguments `(args, kw)` to `_walk` to the todo list."""
        self._todo.append((row, consumed_position, passed))

    def _step(self, row, position, passed):
        """Walk through the knitting pattern by expanding an row."""
        if row in passed or not self._row_should_be_placed(row, position):
            return
        self._place_row(row, position)
        passed = [row] + passed
        print("{}{} at\t{} {}".format("  " * len(passed), row, position,
                                      passed))
        for i, produced_mesh in enumerate(row.produced_meshes):
            self._expand_produced_mesh(produced_mesh, i, position, passed)

    def _expand_produced_mesh(self, mesh, mesh_index, row_position, passed):
        """expand the produced meshes"""
        if not mesh.is_consumed():
            return
        row = mesh.consuming_row
        position = Point(
                row_position.x - mesh.index_in_consuming_row + mesh_index,
                row_position.y + INSTRUCTION_HEIGHT
            )
        self._expand(row, position, passed)

    def _row_should_be_placed(self, row, position):
        """:return: whether to place this instruction"""
        placed_row = self._rows_in_grid.get(row)
        return placed_row is None or placed_row.y < position.y

    def _place_row(self, row, position):
        """place the instruction on a grid"""
        self._rows_in_grid[row] = RowInGrid(row, position)

    def _walk(self):
        """Loop through all the instructions that are `_todo`."""
        while self._todo:
            args = self._todo.pop(0)
            self._step(*args)

    def instruction_in_grid(self, instruction):
        """Returns an `InstructionInGrid` object for the `instruction`"""
        row_position = self._rows_in_grid[instruction.row].xy
        x = instruction.index_of_first_consumed_mesh_in_row
        position = Point(row_position.x + x, row_position.y)
        return InstructionInGrid(instruction, position)

    def row_in_grid(self, row):
        """Returns an `RowInGrid` object for the `row`"""
        return self._rows_in_grid[row]


class Connection(object):
    """a connection between two :class:`InstructionInGrid` objects"""

    def __init__(self, start, stop):
        """
        :param InstructionInGrid start: the start of the connection
        :param InstructionInGrid stop: the end of the connection
        """
        self._start = start
        self._stop = stop

    @property
    def start(self):
        """:return: the start of the connection
        :rtype: InstructionInGrid
        """
        return self._start

    @property
    def stop(self):
        """:return: the end of the connection
        :rtype: InstructionInGrid
        """
        return self._stop

    def is_visible(self):
        """:return: is this connection is visible
        :rtype: bool

        A connection is visible if it is longer that 0."""
        if self._start.y + 1 < self._stop.y:
            return True
        return False


class GridLayout(object):
    """This class places the instructions at ``(x, y)`` positions."""

    def __init__(self, pattern):
        """
        :param knittingpattern.KnittingPattern.KnittingPattern pattern: the
          pattern to layout

        """
        self._pattern = pattern
        self._rows = list(sorted(self._pattern.rows))
        self._walk = _RecursiveWalk(self._rows[0].instructions[0])

    def walk_instructions(self, mapping=identity):
        """
        :return: an iterator over :class:`instructions in grid
          <InstructionInGrid>`
        :param mapping: funcion to map the result

        .. code:: python

            for pos, c in layout.walk_instructions(lambda i: (i.xy, i.color)):
                print("color {} at {}".format(c, pos))

        """
        instructions = chain(*self.walk_rows(lambda row: row.instructions))
        grid = map(self._walk.instruction_in_grid, instructions)
        return map(mapping, grid)

    def walk_rows(self, mapping=identity):
        """
        :return: an iterator over :class:`rows <knittingpattern.Row.Row>`
        :param mapping: funcion to map the result, see
          :meth:`walk_instructions` for an example usage
        """
        return map(mapping, self._rows)

    def walk_connections(self, mapping=identity):
        """
        :return: an iterator over :class:`connections <Connection>` between
          :class:`instructions in grid <InstructionInGrid>`
        :param mapping: funcion to map the result, see
          :meth:`walk_instructions` for an example usage
        """
        for start in self.walk_instructions():
            for stop_instruction in start.instruction.consuming_instructions:
                if stop_instruction is None:
                    continue
                stop = self._walk.instruction_in_grid(stop_instruction)
                connection = Connection(start, stop)
                if connection.is_visible():
                    # print("connection:",
                    #      connection.start.instruction,
                    #      connection.stop.instruction)
                    yield mapping(connection)

    @property
    def bounding_box(self):
        """
        :return: ``(min_x, min_y, max_x + 1, max_y + 1)`` the bounding box
          of this layout
        :rtype: tuple
        """
        x, y = zip(*self.walk_instructions(
                lambda instruction: (instruction.x, instruction.y)
            ))
        return min(x), min(y), max(x) + 1, max(y) + 1

__all__ = ["GridLayout", "InstructionInGrid", "Connection", "identity"
           "Point"]
