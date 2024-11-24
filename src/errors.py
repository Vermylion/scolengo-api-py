from typing import Union


class ErrorCode:
    BLOCKED_ACCOUNT = 'BLOCKED_ACCOUNT'
    SKO_APP_NOT_SUBSCRIBED = 'SKO_APP_NOT_SUBSCRIBED'
    SUSPENDED_ACCOUNT = 'SUSPENDED_ACCOUNT'
    NULL = 'null'


class SkolengoErrorBody:
    """
    Represents the structure of a Skolengo error.
    """

    def __init__(self, status: str, code: Union[str, ErrorCode], title: str, detail: str):
        """
        :param status: Status code of the error.
        :param code: Error code.
        :param title: Identifier of the error type (e.g., PRONOTE_RESOURCES_NOT_READY).
        :param detail: Details about the error.
        """
        self.status = status
        self.code = code
        self.title = title
        self.detail = detail


class SkolengoError(Exception, SkolengoErrorBody):
    
    def __init__(self, error: SkolengoErrorBody):
        """
        Initializes a SkolengoError instance.

        :param error: An instance of SkolengoErrorBody.
        """

        print(error)

        self.name = error.get('title', 'Unknown Name')
        self.title = error.get('title', 'Unknown Title')

        self.status = error.get('status', 'Unknown Status')
        self.code = error.get('id', 'Unknown Code')  # Use 'id' to populate 'code'
        self.detail = error.get('detail', 'No Detail Provided')

        super().__init__(f"{self.title}: {self.detail}")

    
