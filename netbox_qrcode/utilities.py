import base64
import math
import qrcode
from io import BytesIO

# ******************************************************************************************
# Includes useful tools to create the content.
# ******************************************************************************************

##################################          
# Creates a QR code as an image.: https://pypi.org/project/qrcode/3.0/
# --------------------------------
# Parameter:
#   text: Text to be included in the QR code.
#   **kwargs: List of parameters which properties the QR code should have. (e.g. version, box_size, error_correction, border etc.)
def get_qr(text, **kwargs):
    qr = qrcode.QRCode(**kwargs)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    img = img.get_image()
    return img

##################################          
# Converts an image to Base64
# --------------------------------
# Parameter:
#   img: Image file
def get_img_b64(img):
    stream = BytesIO()
    img.save(stream, format='png')
    return str(base64.b64encode(stream.getvalue()), encoding='ascii')

##################################
# Creates a grid for the QR code labels.
# --------------------------------
# Parameter:
#   rows: Number of rows in the grid.
#   columns: Number of columns in the grid.
#   elements: Number of elements in the grid.
class GridMaker:
    def __init__(self, rows = None, columns = None, elements = None):
        self.rows = rows
        self.columns = columns
        self.elements = elements

        if [self.rows, self.columns, self.elements].count(None) > 1:
            raise TypeError("GridMaker required 2 values to when initalized from row, column or elements to calculate grid size")
        self.__calculateGrid()

    def getIndexByColumn(self, index):
        col_index = math.ceil(index / self.rows)
        row_index = index - ((math.ceil(index / self.rows) - 1) * self.rows)
        return(row_index, col_index)

    def getIndexByRow(self, index):
        row_index = math.ceil(index / self.columns)
        col_index = index - ((math.ceil(index / self.columns) - 1) * self.columns)
        return(row_index, col_index)    
    
    def __calculateGrid(self):
        if self.rows is None:
            self.rows = float(math.ceil(self.elements / self.columns))
        elif self.columns is None:
            self.columns = float(math.ceil(self.elements / self.rows))

    @property
    def cells(self):
        return float(self.rows * self.columns)

##################################
# Creates a grid for the QR code labels.
# --------------------------------
# Parameter:
#   rows: Number of rows in the grid.
#   columns: Number of columns in the grid.
#   elements: Number of elements in the grid.
class GridPosition(GridMaker):
    def __init__(self, 
                 rows=None, 
                 columns=None, 
                 elements=None, 
                 element_height=None,
                 element_width=None,
                 grid_start = (0,0),
                 grid_width=None,
                 grid_height=None):
        self.element_height = element_height
        self.element_width = element_width
        self.grid_width_start = float(grid_start[0])
        self.grid_height_start = float(grid_start[1])
        self.grid_width = grid_width
        self.grid_height = grid_height
        super().__init__(rows, columns, elements)

    @property
    def column_width(self):
        return self.grid_width / self.columns

    @property
    def row_height(self):
        return self.grid_height / self.rows
    
    def elementCoordinates(self, index, by_row = False):
        if by_row:
            row_index, col_index = self.getIndexByRow(index)
        else:
            row_index, col_index = self.getIndexByColumn(index)
        col_start = self.grid_width_start + ((self.column_width - self.element_width) / 2 ) + (self.column_width * (col_index - 1))
        row_start = self.grid_height_start + ((self.row_height - self.element_height) / 2 ) + (self.row_height * (row_index - 1))
        return ((col_start, row_start), (row_index, col_index))
