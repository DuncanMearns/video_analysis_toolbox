from ..utilities.keyboard_interaction import KeyboardInteraction
import cv2


class VideoPlayer(KeyboardInteraction):

    def __init__(self, name, frame_time=1):
        super().__init__()
        self.name = name
        self.frame_time = frame_time
        cv2.namedWindow(self.name)

    def __call__(self, *args, **kwargs):
        for arg in args:
            cv2.imshow(self.name, arg)
            self.wait(self.frame_time)
            if self.valid():
                self.close()
                return False
        return True

    def close(self):
        cv2.destroyWindow(self.name)
