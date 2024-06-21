from PySide6.QtWidgets import QWidget
from qfluentwidgets import MessageBox


def show_decision_message_box(
    parent: QWidget, title: str = None, content: str = None
) -> int:
    """
    Displays a message box with a custom title and text.

    Parameters:
    parent (QWidget): The parent widget for the message box.
    title (str): Title of the MessageBox.
    content (str): Text-content of the MessageBox.

    Returns:
    int: The result of the message box execution.
    """
    message_box = MessageBox(
        title=title,
        content=content,
        parent=parent,
    )

    message_box.yesButton.setText("Continue")
    message_box.cancelButton.setText("Cancel")

    return message_box.exec()
