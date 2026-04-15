"""
Abstract Base OTP Handler.
All OTP strategies implement this contract.
"""
from abc import ABC, abstractmethod


class BaseOTPHandler(ABC):
    """
    Contract for all OTP handlers.
    Implementations: FirebaseOTP, GmailIMAPOTP, MockOTP
    """

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def get_otp(self, timeout: int = 30) -> str:
        """
        Wait for and return the OTP code.
        Args:
            timeout: max seconds to wait for OTP
        Returns:
            OTP string e.g. "123456"
        Raises:
            TimeoutError if OTP not received within timeout
        """

    @abstractmethod
    def clear(self) -> None:
        """Clear/reset OTP state so next call gets a fresh OTP."""
