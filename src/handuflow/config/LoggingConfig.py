import os
import sys
import shutil
import logging
import configparser
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler


class LoggingConfig:
    """Databricks-safe logging configuration"""

    LOGGER_NAME = "handuflow"

    def __init__(self, run_id: str, config: configparser.ConfigParser):
        self.level = logging.INFO
        self.run_id = run_id
        self.retention_days = int(config["DEFAULT"]["log_retention_policy_in_days"])

        self.final_log_dir = os.path.join(
            config["DEFAULT"]["log_base_path"],
            config["DEFAULT"]["log_directory_name"],
        )
        temp = config["DEFAULT"]["temp_directory"]
        temp = temp.replace("/dbfs", "")
        self.temp_log_dir = os.path.join(
            temp,
            config["DEFAULT"]["log_directory_name"],
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(
            self.temp_log_dir, f"sdmf_log_{self.run_id}_{timestamp}.log"
        )

        os.makedirs(self.temp_log_dir, exist_ok=True)
        os.makedirs(self.final_log_dir, exist_ok=True)

        self.logger = logging.getLogger(self.LOGGER_NAME)

    def configure(self):
        self.logger.setLevel(self.level)

        # Do not propagate to Databricks root logger
        self.logger.propagate = False

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] - %(message)s"
        )

        # ---- Console handler (notebook output) ----
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.level)
        self.logger.addHandler(console_handler)

        # ---- File handler ----
        file_handler = TimedRotatingFileHandler(
            self.log_file,
            when="midnight",
            interval=1,
            backupCount=0,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.level)
        self.logger.addHandler(file_handler)

        # Silence noisy libs
        logging.getLogger("py4j").setLevel(logging.WARN)
        logging.getLogger("pyspark").setLevel(logging.WARN)
        logging.getLogger("org.apache.spark").setLevel(logging.WARN)

        self.cleanup_old_logs()


    def cleanup_old_logs(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for f in os.listdir(self.temp_log_dir):
            path = os.path.join(self.temp_log_dir, f)
            if os.path.isfile(path):
                if datetime.fromtimestamp(os.path.getmtime(path)) < cutoff:
                    os.remove(path)

    def move_logs_to_final_location(self):
        if not self.log_file or not os.path.exists(self.log_file):
            return

        # 🔑 CRITICAL: close handlers before moving
        for h in list(self.logger.handlers):
            h.flush()
            h.close()
            self.logger.removeHandler(h)

        dst = os.path.join(self.final_log_dir, os.path.basename(self.log_file))

        try:
            shutil.copy2(self.log_file, dst)
        except FileNotFoundError:
            # temp disk may already be gone on cluster shutdown
            pass

    def cleanup_final_logs(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for f in os.listdir(self.final_log_dir):
            path = os.path.join(self.final_log_dir, f)
            if os.path.isfile(path):
                if datetime.fromtimestamp(os.path.getmtime(path)) < cutoff:
                    os.remove(path)
