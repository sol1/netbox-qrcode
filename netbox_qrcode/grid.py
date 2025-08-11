import math

class GridMaker:
    """
    A utility class to calculate grid dimensions and retrieve row/column
    positions based on a given index.

    You must provide exactly two of the three parameters (`rows`, `columns`,
    or `elements`) on initialization. The missing parameter is automatically
    calculated.

    Attributes:
        rows (int | float): Number of rows in the grid.
        columns (int | float): Number of columns in the grid.
        elements (int | float): Total number of elements in the grid.
    """

    def __init__(self, rows=None, columns=None, elements=None):
        """
        Initialize a GridMaker instance.

        Args:
            rows (int | float, optional): Number of rows.
            columns (int | float, optional): Number of columns.
            elements (int | float, optional): Total number of elements.

        Raises:
            TypeError: If fewer than two of the three parameters are provided.
        """
        self.rows = rows
        self.columns = columns
        self.elements = elements

        if [self.rows, self.columns, self.elements].count(None) > 1:
            raise TypeError(
                "GridMaker requires at least 2 values from rows, columns, or elements to calculate grid size"
            )
        self.__calculateGrid()

    @property
    def cells(self):
        """
        float: Total number of cells in the grid (rows × columns).
        """
        return float(self.rows * self.columns)

    def getIndexByColumn(self, index):
        """
        Get the (row, column) position for a 1-based index when filling the
        grid by columns.

        Args:
            index (int): The 1-based index of the element.

        Returns:
            tuple[int, int]: (row_index, col_index)
        """
        col_index = math.ceil(index / self.rows)
        row_index = index - ((col_index - 1) * self.rows)
        return (row_index, col_index)

    def getIndexByRow(self, index):
        """
        Get the (row, column) position for a 1-based index when filling the
        grid by rows.

        Args:
            index (int): The 1-based index of the element.

        Returns:
            tuple[int, int]: (row_index, col_index)
        """
        row_index = math.ceil(index / self.columns)
        col_index = index - ((row_index - 1) * self.columns)
        return (row_index, col_index)

    def __calculateGrid(self):
        """
        Calculate the missing grid dimension (rows or columns) based on the
        provided values.
        """
        if self.rows is None:
            self.rows = float(math.ceil(self.elements / self.columns))
        elif self.columns is None:
            self.columns = float(math.ceil(self.elements / self.rows))


class GridPosition(GridMaker):
    """
    Extends GridMaker to calculate the physical positions of elements in a
    2D grid based on grid size, element size, and offsets.

    This class can determine exact element coordinates within a grid,
    including offsets from grid edges and spacing between elements.

    Attributes:
        element_height (float): Height of each element (optional if offsets are provided).
        element_width (float): Width of each element (optional if offsets are provided).
        grid_width_start (float): X-coordinate where the grid starts.
        grid_height_start (float): Y-coordinate where the grid starts.
        grid_width (float): Total width of the grid.
        grid_height (float): Total height of the grid.
    """

    def __init__(self,
                 rows=None,
                 columns=None,
                 elements=None,
                 element_height=None,
                 element_width=None,
                 element_height_offset=None,
                 element_width_offset=None,
                 grid_start=(0, 0),
                 grid_width=None,
                 grid_height=None):
        """
        Initialize a GridPosition instance.

        Args:
            rows (int | float, optional): Number of rows.
            columns (int | float, optional): Number of columns.
            elements (int | float, optional): Total number of elements.
            element_height (float, optional): Height of each element.
            element_width (float, optional): Width of each element.
            element_height_offset (float, optional): Vertical spacing between elements.
            element_width_offset (float, optional): Horizontal spacing between elements.
            grid_start (tuple[float, float], optional): (x, y) coordinates where the grid starts.
            grid_width (float, optional): Total width of the grid.
            grid_height (float, optional): Total height of the grid.

        Notes:
            - If `element_height` is not provided but `element_height_offset` is,
              the element height is derived from row height minus the offset.
            - If `element_width` is not provided but `element_width_offset` is,
              the element width is derived from column width minus the offset.
        """
        self.element_height = element_height
        self.element_width = element_width
        self.grid_width_start = float(grid_start[0])
        self.grid_height_start = float(grid_start[1])
        self.grid_width = grid_width
        self.grid_height = grid_height
        super().__init__(rows, columns, elements)

        # Allow grid creation from the spaces between elements
        if self.element_height is None and element_height_offset is not None:
            self.element_height = self.row_height - element_height_offset

        if self.element_width is None and element_width_offset is not None:
            self.element_width = self.column_width - element_width_offset

    @property
    def column_width(self):
        """float: Width of a single column in the grid."""
        return self.grid_width / self.columns

    @property
    def row_height(self):
        """float: Height of a single row in the grid."""
        return self.grid_height / self.rows

    @property
    def column_element_offset(self):
        """float: Horizontal spacing between an element and its column boundary."""
        return self.column_width - self.element_width

    @property
    def row_element_offset(self):
        """float: Vertical spacing between an element and its row boundary."""
        return self.row_height - self.element_height

    @property
    def column_edge_offset(self):
        """float: Horizontal offset from the column edge to the nearest element edge."""
        return self.column_element_offset / 2

    @property
    def row_edge_offset(self):
        """float: Vertical offset from the row edge to the nearest element edge."""
        return self.row_element_offset / 2

    def elementCoordinates(self, index, by_row=False):
        """
        Calculate the coordinates of an element in the grid based on the elements index.

        Args:
            index (int): The 1-based index of the element.
            by_row (bool, optional): If True, calculate position assuming elements
                are filled by row first; if False, by column first. Defaults to False.

        Returns:
            tuple[tuple[float, float], tuple[int, int]]:
                - First tuple: (x, y) coordinates of the element's starting point.
                - Second tuple: (row_index, col_index) position in the grid.
        """
        if by_row:
            row_index, col_index = self.getIndexByRow(index)
        else:
            row_index, col_index = self.getIndexByColumn(index)

        col_start = self.grid_width_start + self.column_edge_offset + (self.column_width * (col_index - 1))
        row_start = self.grid_height_start + self.row_element_offset + (self.row_height * (row_index - 1))
        return ((col_start, row_start), (row_index, col_index))
