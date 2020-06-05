from .video_display import VideoDisplayWidget
from .slider import SliderWidget
from video_analysis_toolbox.utilities import TrackingError
from PyQt5 import QtCore


class DoubleThresholdWidget(VideoDisplayWidget):

    def __init__(self, videos, app, *args, **kwargs):
        super().__init__(videos, app=app, *args, **kwargs)
        # Add display for thresholding
        self.add_display('Contours', self.apply_thresholds, show='contours')
        self.add_display('Tracking', self.apply_thresholds, show='tracking')
        # Threshold sliders
        self.thresh1_widget = SliderWidget('Thresh 1', 0, 254, self.app.tracker.thresh1)
        self.thresh2_widget = SliderWidget('Thresh 2', 1, 255, self.app.tracker.thresh2)
        self.thresh1_widget.value_changed.connect(self.change_thresh1)
        self.thresh2_widget.value_changed.connect(self.change_thresh2)
        self.slider_widget.layout().addWidget(self.thresh1_widget)
        self.slider_widget.layout().addWidget(self.thresh2_widget)
        # Make videos checkable
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            item.setCheckState(QtCore.Qt.Checked)

    @property
    def thresholds(self):
        return self.thresh1_widget.value, self.thresh2_widget.value

    @property
    def selected_videos(self):
        selected = []
        for i, video in enumerate(self.videos):
            item = self.video_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(video.path)
        return selected

    @QtCore.pyqtSlot(int)
    def change_thresh1(self, val):
        """Called when thresh2 changes."""
        thresh1 = self.thresh2_widget.value
        if thresh1 >= val:
            self.thresh2_widget.set_value(val - 1)
        self._change_thresholds()

    @QtCore.pyqtSlot(int)
    def change_thresh2(self, val):
        """Called when thresh1 changes."""
        thresh2 = self.thresh1_widget.value
        if thresh2 <= val:
            self.thresh1_widget.set_value(val + 1)
        self._change_thresholds()

    def _change_thresholds(self):
        """Called whenever either threshold changes. Updates thresholds in parent tracker then updates the display."""
        thresh1, thresh2 = self.thresholds
        self.app.tracker.thresh1 = thresh1
        self.app.tracker.thresh2 = thresh2
        self.update_display_image()
        self.draw()

    def apply_thresholds(self, image, show='contours'):
        try:
            frame_info = self.app.tracker.apply_thresholds(image)
            if show == 'contours':
                return self.app.tracker.show_contours(image, **frame_info)
            elif show == 'tracking':
                return self.app.tracker.show_tracking(image, **frame_info)
        except TrackingError as e:
            self.app.statusBar().showMessage(str(e.message), 1000)  # show any error in the status bar
            return image
