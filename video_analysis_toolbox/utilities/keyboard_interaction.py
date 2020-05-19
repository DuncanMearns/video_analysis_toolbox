import cv2


class KeyboardInteraction:
    """Class for handling keyboard interaction

    Class Attributes
    ----------------
    enter : 13
        ASCII code for enter/carriage return key
    esc : 27
        ASCII code for escape key
    space : 32
        ASCII code for escape key"""

    enter_key = 13
    esc_key = 27
    space_key = 32

    def __init__(self, *args, **kwargs):
        self.k = None

    def wait(self, t=0):
        self.k = cv2.waitKey(t)

    def enter(self):
        return self.k == self.enter_key

    def space(self):
        return self.k == self.space_key

    def esc(self):
        return self.k == self.esc_key

    def valid(self):
        """Checks whether the enter, escape or space keys were pressed

        Parameters
        ----------
        k : int
            ASCII key code

        Returns
        -------
        bool
        """
        if self.k in (self.enter_key, self.esc_key, self.space_key):
            return True
        else:
            return False