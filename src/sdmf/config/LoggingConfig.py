# inbuilt
import os
import sys
import shutil
import logging
import configparser
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

class LoggingConfig:
    """Configures global logging with console + rotating file handler and auto cleanup."""

    def __init__(self, run_id:str, config: configparser.ConfigParser):
        self.level = logging.INFO
        self.run_id = run_id
        self.retention_days = int(config['DEFAULT']['log_retention_policy_in_days'])
        self.final_log_dir = os.path.join(config['DEFAULT']['file_hunt_path'], config['DEFAULT']['log_directory_name'])
        self.temp_log_dir = os.path.join(config['DEFAULT']['temp_directory'], config['DEFAULT']['log_directory_name'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.temp_log_dir, f"sdmf_log_{self.run_id}_{timestamp}.log")
        os.makedirs(self.temp_log_dir, exist_ok=True)
        os.makedirs(self.final_log_dir, exist_ok=True)


    def configure(self):
        root = logging.getLogger()
        root.setLevel(self.level)
        if any(isinstance(h, logging.StreamHandler) for h in root.handlers):
            return
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))
        root.addHandler(console_handler)
        
        file_handler = TimedRotatingFileHandler(self.log_file, when="midnight", interval=1, backupCount=0, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s"))
        root.addHandler(file_handler)
        self.cleanup_old_logs()

    def cleanup_old_logs(self):
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        for filename in os.listdir(self.temp_log_dir):
            file_path = os.path.join(self.temp_log_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"Deleted old log file: {file_path}")
                    
    def move_logs_to_final_location(self):
        if not self.log_file:
            print("No log file defined, skipping move")
            return

        if not os.path.exists(self.log_file):
            print(f"Log file does not exist, skipping move: {self.log_file}")
            return

        final_dir = self.final_log_dir
        os.makedirs(final_dir, exist_ok=True)

        src = self.log_file
        dst = os.path.join(final_dir, os.path.basename(src))

        # Case 1: dbutils is available (Databricks)
        try:
            import dbutils  # type: ignore

            if dst.startswith("/dbfs"):
                dbutils.fs.cp(f"file:{src}", f"dbfs:{dst.replace('/dbfs', '')}")
                print(f"Log file moved to (DBFS): {dst}")
                return
        except Exception:
            # dbutils not available or failed → fall back to shutil
            pass

        # Case 2: local filesystem or /dbfs mount
        shutil.copyfile(src, dst)
        print(f"Log file moved to: {dst}")


    
    def cleanup_final_logs(self):
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        for filename in os.listdir(self.final_log_dir):
            file_path = os.path.join(self.final_log_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"Deleted old final log file: {file_path}")


