from PyQt5 import QtWidgets, QtCore, QtGui


class SliderWidget(QtWidgets.QWidget):
    """Widget for a named slider with editable box showing the current value. The current value of the slider can be
    accessed via the value property.

    Parameters
    ----------
    name : str
        Name of the slider.
    minval : int
        Minimum value of the slider.
    maxval : int
        Maximum value of the slider.
    initval : int
        Initial value of the slider.
    """

    value_changed = QtCore.pyqtSignal(int)

    def __init__(self, name, minval, maxval, initval, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set attributes
        self._name = name
        self._min = minval
        self._max = maxval
        self._value = initval
        # Create widget
        self.setLayout(QtWidgets.QHBoxLayout())
        # Add name
        label = QtWidgets.QLabel(name)
        label.setFixedSize(60, 20)
        self.layout().addWidget(label)
        # Add slider
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(minval)
        self.slider.setMaximum(maxval)
        self.slider.setValue(initval)
        self.slider.valueChanged.connect(self.set_value)
        self.slider.setFixedHeight(20)
        self.layout().addWidget(self.slider)
        # Add value editor
        self.editor = QtWidgets.QLineEdit(str(initval))
        self.value_checker = QtGui.QIntValidator(minval, maxval)
        self.editor.setValidator(self.value_checker)
        self.editor.editingFinished.connect(self.editor_value_changed)
        self.editor.setFixedSize(60, 20)
        self.layout().addWidget(self.editor)

    @property
    def value(self):
        """Returns the current value of the slider."""
        return self._value

    def set_range(self, minval, maxval):
        """Updates the minimum and maximum values of the slider."""
        self.slider.setMinimum(minval)
        self.slider.setMaximum(maxval)
        self.value_checker.setRange(minval, maxval)
        self._value = max(min(self._value, maxval), minval)
        self.slider.setValue(self._value)

    @QtCore.pyqtSlot()
    def editor_value_changed(self):
        """Called whenever the value of the slider is changed via the editor."""
        val = int(self.editor.text())
        self.set_value(val)

    @QtCore.pyqtSlot(int)
    def set_value(self, val):
        """Called whenever the value of the slider changes (either the slider itself or in the value editor)."""
        self.slider.setValue(val)
        self.editor.setText(str(val))
        self._value = val
        self.value_changed.emit(self._value)
