from ..utilities import KeyboardInteraction
import cv2
import numpy as np
from pathlib import Path
import warnings


class FrameErrorWarning(UserWarning):

    def __init__(self, *args):
        super().__init__(*args)


class Video(KeyboardInteraction):

    def __init__(self, name='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_number = 0
        self.name = name

    @classmethod
    def open(cls, path, convert_to_grayscale=True, import_frames=False, *args, **kwargs):
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path {path} does not exist.")
        if import_frames or (path.suffix == '.npy'):
            if path.suffix == '.npy':  # import numpy array
                video = _VideoArray.from_numpy(path, **kwargs)
            else:  # import frames from video
                video = _VideoArray.from_video(path, **kwargs)
        elif path.suffix == '.avi':
            try:  # open avi file (xvid or other compression)
                video = _VideoFile(path, convert_to_grayscale, *args, **kwargs)
                if video.fourcc == 'H264':
                    raise ValueError()
            except ValueError:  # open h264 compressed file
                video = _VideoFileH264(path, convert_to_grayscale, *args, **kwargs)
        else:
            raise ValueError(f"{path} is not a valid file type.")
        return video

    @property
    def frame_count(self):
        return 1

    @property
    def frame_rate(self):
        return 1.0

    @property
    def shape(self):
        return 0, 0

    def set_frame(self, f):
        self.frame_number = f

    def grab_frame(self, f):
        self.set_frame(f)

    def advance_frame(self):
        self.frame_number += 1

    def scroll(self, **kwargs):
        first_frame = kwargs.get('first_frame', 0)
        last_frame = kwargs.get('last_frame', self.frame_count)
        name = kwargs.get('name', self.name)
        display_function = kwargs.get('display_function', None)
        display_kwargs = kwargs.get('display_kwargs', dict())
        n_frames = last_frame - first_frame
        cv2.namedWindow(name)
        cv2.createTrackbar('frame', name, 0, n_frames - 1, lambda x: x)
        while True:
            frame_number = cv2.getTrackbarPos('frame', name) + first_frame
            frame = self.grab_frame(frame_number)
            if display_function is not None:
                frame = display_function(frame, **display_kwargs)
            cv2.imshow(name, frame)
            self.wait(1)
            if self.valid():
                break
        cv2.destroyWindow(name)
        return self.k

    def play(self, **kwargs):
        first_frame = kwargs.get('first_frame', 0)
        last_frame = kwargs.get('last_frame', self.frame_count)
        name = kwargs.get('name', self.name)
        frame_rate = kwargs.get('frame_rate', self.frame_rate)
        frame_time = max(1, int(1000. / frame_rate))
        display_function = kwargs.get('display_function', None)
        display_kwargs = kwargs.get('display_kwargs', dict())
        cv2.namedWindow(name)
        self.set_frame(first_frame)
        for f in range(first_frame, last_frame):
            frame = self.advance_frame()
            if display_function is not None:
                frame = display_function(frame, **display_kwargs)
            cv2.imshow(name, frame)
            self.wait(frame_time)
            if self.valid():
                break
        cv2.destroyWindow(name)
        return self.k

    def _return_range(self, first, last):
        self.frame_number = first
        frames = []
        self.set_frame(first)
        for f in range(first, last):
            frame = self.advance_frame()
            frames.append(frame)
        return frames

    def _return_frames(self, *args):
        frames = []
        for f in args:
            frame = self.grab_frame(f)
            frames.append(frame)
        return frames

    def return_frames(self, *args, as_object=False, **kwargs):
        if len(args) == 0:
            frames = self._return_range(0, self.frame_count)
        elif len(args) == 1:
            frames = [self.grab_frame(args[0])]
        elif len(args) == 2:
            frames = self._return_range(*args)
        else:
            frames = self._return_frames(*args)
        if as_object:
            return _VideoArray(frames, self.frame_rate, **kwargs)
        else:
            return np.array(frames)


class _VideoFile(Video):

    def __init__(self, path, convert_to_grayscale=True, *args, **kwargs):
        self.path = Path(path)
        self.cap = cv2.VideoCapture(str(self.path))
        self.convert_to_grayscale = convert_to_grayscale
        name = kwargs.get('name', self.path.name)
        super().__init__(name, *args, **kwargs)

    @property
    def frame_count(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def frame_rate(self) -> float:
        return self.cap.get(cv2.CAP_PROP_FPS)

    @property
    def shape(self) -> tuple:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fourcc(self) -> str:
        fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        return ''.join([chr((fourcc >> i) & 255) for i in range(0, 32, 8)])

    def set_frame(self, f):
        super().set_frame(f)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)

    def cvt_frame(self, frame):
        if self.convert_to_grayscale and (frame.ndim == 3):
            return frame[..., 0]
        else:
            return frame

    def grab_frame(self, f):
        self.set_frame(f)
        ret, frame = self.cap.read()
        if ret:
            return self.cvt_frame(frame)
        else:
            message = f'Frame #{f} does not exist!'
            warnings.warn(message, category=FrameErrorWarning)
            return np.zeros(self.shape[::-1], dtype='uint8')

    def advance_frame(self):
        ret, frame = self.cap.read()
        super().advance_frame()
        if ret:
            return self.cvt_frame(frame)
        else:
            message = f'Frame #{self.frame_number - 1} does not exist!'
            warnings.warn(message)
            return np.zeros(self.shape, dtype='uint8')


class _VideoFileH264(_VideoFile):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.fourcc == 'H264'
        self.n_error_frames = 19
        if self.convert_to_grayscale:
            self.error_frames = np.zeros((self.n_error_frames, self.shape[1], self.shape[0]), dtype='uint8')
        else:
            self.error_frames = np.zeros((self.n_error_frames, self.shape[1], self.shape[0], 3), dtype='uint8')
        while self.frame_number < self.n_error_frames:
            ret, frame = self.cap.read()
            self.error_frames[self.frame_number] = self.cvt_frame(frame)
            self.frame_number += 1
        self.set_frame(0)

    def set_frame(self, f):
        if f >= self.n_error_frames:
            super().set_frame(f)
        else:
            self.frame_number = f

    def grab_frame(self, f):
        if f >= self.n_error_frames:
            return super().grab_frame(f)
        else:
            self.set_frame(f)
            frame = self.error_frames[f]
            return frame

    def advance_frame(self):
        if self.frame_number >= self.n_error_frames:
            return super().advance_frame()
        else:
            frame = self.grab_frame(self.frame_number)
            self.frame_number += 1
            return frame


class _VideoArray(Video):

    def __init__(self, frames, frame_rate=24.0, **kwargs):
        self.frames = frames
        self._frame_rate = frame_rate
        super().__init__(**kwargs)

    @classmethod
    def from_video(cls, path, **kwargs):
        cap = cv2.VideoCapture(str(path))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = np.zeros((n, h, w), dtype='uint8')
        for i in range(n):
            ret, frame = cap.read()
            if ret:
                frame = frame[..., 0]
                frames[i] = frame
        return cls(frames, fps, **kwargs)

    @classmethod
    def from_numpy(cls, path, **kwargs):
        frames = np.load(path).astype('uint8')
        return cls(frames, **kwargs)

    @property
    def frame_count(self):
        return len(self.frames)

    @property
    def frame_rate(self):
        return self._frame_rate

    @property
    def shape(self):
        return self.frames.shape[2], self.frames.shape[1]

    def grab_frame(self, f):
        self.set_frame(f)
        try:
            frame = self.frames[self.frame_number]
            return frame
        except IndexError:
            raise ValueError('Frame #{} does not exist!'.format(self.frame_number))

    def advance_frame(self):
        try:
            frame = self.frames[self.frame_number]
            super().advance_frame()
            return frame
        except IndexError:
            raise ValueError('Frame #{} does not exist!'.format(self.frame_number))
