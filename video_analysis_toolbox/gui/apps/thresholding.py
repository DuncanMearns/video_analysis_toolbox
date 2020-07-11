from .userapp import UserApplicationWindow
from ..widgets import DoubleThresholdWidget
from ...video import Video


class SetThresholdsApp(UserApplicationWindow):
    """Application for setting thresholds for tracking.

    Parameters
    ----------
    tracker : Tracker
        A Tracker object.
    videos : list
        List of paths to video files.
    """

    def __init__(self, videos, tracker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.videos = [Video.open(video) for video in videos]
        self.tracker = tracker
        # Set name
        self.setWindowTitle('Set thresholds')
        # Resize window
        self.resize(800, 800)
        # Threshold widget
        self.threshold_widget = DoubleThresholdWidget(self.videos, app=self)
        self.centralWidget().layout().insertWidget(0, self.threshold_widget)

    @property
    def output(self):
        selected_videos = self.threshold_widget.selected_videos
        thresholds = (self.tracker.thresh1, self.tracker.thresh2)
        return selected_videos, thresholds

    @classmethod
    def start(cls, videos: list, tracker):
        return super().start(videos, tracker)
