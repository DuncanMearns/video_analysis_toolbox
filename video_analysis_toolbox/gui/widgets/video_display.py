from .slider import SliderWidget
from video_analysis_toolbox.video import FrameErrorWarning
from PyQt5 import QtWidgets, QtCore
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import warnings


class VideoDisplayWidget(QtWidgets.QWidget):

    def __init__(self, videos, app: QtWidgets.QMainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

        # -----
        # SETUP
        # -----

        # Set videos and initialize frame number
        self.videos = videos
        self.current_video = self.videos[0]
        self.frame_number = 0

        # Set layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # -------
        # DISPLAY
        # -------

        # Create display widget for showing images
        self.display_widget = self.add_widget(1, 0, layout=QtWidgets.QVBoxLayout)

        # Initialize display attributes
        self.display_methods = []
        self.display_image = None

        # Create combobox for switching between images
        self.box_widget = QtWidgets.QComboBox()
        self.add_display('Input image', self.input_image)
        self.display_index = 0
        self.display_function = self.input_image
        self.display_kwargs = {}
        self.box_widget.currentIndexChanged.connect(self.change_display_image)
        self.box_widget.setFixedSize(120, 25)
        self.display_widget.layout().addWidget(self.box_widget, alignment=QtCore.Qt.AlignRight)

        # Create figure widget
        self.figure = plt.figure(facecolor='0.95')
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        self.ax.axis('off')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(500, 500)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy().MinimumExpanding, QtWidgets.QSizePolicy().MinimumExpanding)
        self.display_widget.layout().addWidget(self.canvas)

        # Initialize the display
        self.update_display_image()  # initializes the display image
        self.image_ = self.ax.imshow(self.display_image,
                                     origin='upper',
                                     cmap='Greys_r',
                                     vmin=0, vmax=255)

        # -------
        # SLIDERS
        # -------

        # Create slider widget for adjusting e.g. frame, thresholds etc.
        self.slider_widget = self.add_widget(0, 0, layout=QtWidgets.QVBoxLayout)
        self.slider_widget.layout().setSpacing(0)
        # Frame slider
        self.frame_slider = SliderWidget('Frame', 0, self.current_video.frame_count - 1, 0)
        self.frame_slider.value_changed.connect(self.change_frame)
        self.slider_widget.layout().addWidget(self.frame_slider)

        # ------
        # VIDEOS
        # ------

        # Create video widget for switching between videos
        self.video_widget = self.add_widget(0, 1, rowspan=2)
        self.video_widget.setMinimumWidth(150)
        self.video_widget.setMaximumWidth(200)
        self.video_list = QtWidgets.QListWidget()
        self.video_widget.layout().addWidget(self.video_list)
        # Add videos to list
        self.video_list.addItems([video.name for video in self.videos])
        self.video_list.itemSelectionChanged.connect(self.switch_video)
        self.video_list.setCurrentRow(0)

    def add_widget(self, i, j, widget=QtWidgets.QWidget, layout: QtWidgets.QLayout = QtWidgets.QGridLayout,
                   rowspan=1, colspan=1):
        """Adds a new widget to the grid.

        Parameters
        ----------
        i, j : int
            Row number, column number.
        widget : QtWidgets.QWidget type
            The type of widget to add.
        layout : QtWidgets.QLayout type
            The layout type to use.
        rowspan, colspan : int
            Number of rows in grid widget should span, number of columns in grid widget should span.

        Returns
        -------
        QtWidgets.QWidget
            The newly created widget.
        """
        w = widget()
        w.setLayout(layout())
        self.layout.addWidget(w, i, j, rowspan, colspan)
        return w

    def add_display(self, name, func, **kwargs):
        self.box_widget.addItem(name)
        self.display_methods.append((func, kwargs))

    def draw(self):
        """Redraws the display image in the GUI."""
        self.image_.set_data(self.display_image)
        self.canvas.draw()
        self.canvas.flush_events()

    @QtCore.pyqtSlot()
    def switch_video(self):
        """Switches between videos."""
        selected_video_index = self.video_list.currentRow()  # get the currently selected row of the video list
        self.current_video = self.videos[selected_video_index]  # set the new video
        self.frame_slider.set_range(0, self.current_video.frame_count)  # reset frame slider range to fit new video
        self.frame_slider.set_value(0)  # go to first frame of video

    @QtCore.pyqtSlot(int)
    def change_display_image(self, i):
        """Changes the image to be displayed (e.g. contours, tracking etc.)."""
        self.display_function, self.display_kwargs = self.display_methods[i]
        self.update_display_image()
        self.draw()

    @QtCore.pyqtSlot(int)
    def change_frame(self, frame):
        """Called when the frame changes."""
        self.frame_number = frame
        self.update_display_image()
        self.draw()

    @staticmethod
    def input_image(image, **kwargs):
        return image

    def update_display_image(self):
        with warnings.catch_warnings(record=True) as w:  # catch frame warnings so that GUI does not crash
            warnings.simplefilter("always")
            image = self.current_video.grab_frame(self.frame_number)  # grab the current frame
            w = list(filter(lambda i: issubclass(i.category, FrameErrorWarning), w))
            if len(w):
                self.app.statusBar().showMessage(str(w[0].message), 1000)  # show any warning in the status bar
            else:
                self.display_image = self.display_function(image, **self.display_kwargs)


class CheckableVideoWidget(VideoDisplayWidget):

    def __init__(self, videos, app, *args, **kwargs):
        super().__init__(videos, app, *args, **kwargs)
        # Make videos checkable
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    @property
    def selected_videos(self):
        selected = []
        for i, video in enumerate(self.videos):
            item = self.video_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(video.path)
        return selected
