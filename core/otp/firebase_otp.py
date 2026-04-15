"""
Firebase Realtime Database OTP Handler.
Your phone app receives an SMS OTP and writes it to Firebase.
This handler listens on that path and reads it in real-time.

Setup:
  1. Create Firebase project at https://console.firebase.google.com
  2. Download service account JSON key
  3. In your phone app (or a simple Android app):
       FirebaseDatabase.getInstance().getReference("otp/device1").setValue("123456")
  4. Configure below in config.yaml:

     otp:
       default: firebase
       firebase:
         credentials_path: "config/firebase_credentials.json"
         database_url: "https://your-project.firebaseio.com"
         otp_path: "otp/device1"

HOW IT WORKS:
  Framework starts listener on Firebase path
  Phone receives SMS -> app writes OTP to Firebase
  Listener fires instantly (~200ms latency)
  Framework reads OTP and injects into field
  Framework clears the path for next use
"""
import time
import threading
from loguru import logger
from core.otp.base_otp import BaseOTPHandler


class FirebaseOTPHandler(BaseOTPHandler):
    """
    Listens to a Firebase Realtime DB path for OTP values.
    Free tier: 100 concurrent connections, 1GB storage, 10GB/month transfer.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.credentials_path = config.get("credentials_path", "config/firebase_credentials.json")
        self.database_url = config.get("database_url", "")
        self.otp_path = config.get("otp_path", "otp/device1")
        self._otp_received = None
        self._lock = threading.Event()
        self._db = None
        self._ref = None
        self._initialized = False

    def _initialize(self) -> None:
        """Lazy initialization — only connect when first needed."""
        if self._initialized:
            return
        try:
            import firebase_admin
            from firebase_admin import credentials, db

            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred, {"databaseURL": self.database_url})

            self._ref = db.reference(self.otp_path)
            self._initialized = True
            logger.success(f"[FirebaseOTP] Connected | Path: {self.otp_path}")
        except Exception as e:
            raise RuntimeError(
                f"[FirebaseOTP] Initialization failed: {e}\n"
                f"  Check: credentials_path={self.credentials_path}\n"
                f"  Check: database_url={self.database_url}"
            )

    def get_otp(self, timeout: int = 30) -> str:
        """
        Poll Firebase path until OTP appears or timeout expires.
        Uses polling (1s interval) — reliable without websocket complexity.
        """
        self._initialize()
        self._otp_received = None
        self._lock.clear()

        logger.info(f"[FirebaseOTP] Waiting for OTP on path '{self.otp_path}' (timeout={timeout}s)")

        start = time.time()
        while time.time() - start < timeout:
            try:
                value = self._ref.get()
                if value and str(value).strip():
                    otp = str(value).strip()
                    logger.success(f"[FirebaseOTP] OTP received: {otp}")
                    self.clear()   # immediately clear for next use
                    return otp
            except Exception as e:
                logger.warning(f"[FirebaseOTP] Poll error: {e}")
            time.sleep(1)

        raise TimeoutError(
            f"[FirebaseOTP] No OTP received within {timeout}s on path '{self.otp_path}'"
        )

    def clear(self) -> None:
        """Clear the OTP from Firebase path so next call gets a fresh value."""
        try:
            if self._ref:
                self._ref.set(None)
                logger.debug(f"[FirebaseOTP] Cleared path: {self.otp_path}")
        except Exception as e:
            logger.warning(f"[FirebaseOTP] Clear failed: {e}")
