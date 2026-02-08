# inbuilt
import os
import logging
import configparser
from datetime import datetime, timedelta


# external
import pandas as pd


class SystemCleanup:
    def __init__(self, config: configparser.ConfigParser, master_specs: pd.DataFrame) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting system cleanup process...")
        self.config = config
        self.master_specs = master_specs
        self.retention_days = int(config["DEFAULT"]["retention_policy_in_days"])
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

        self.outbound_dir = os.path.join(
            config["DEFAULT"]["file_hunt_path"],
            config["DEFAULT"]["outbound_directory_name"],
        )

    def run(self):
        self.logger.info("Removing old logs...")
        self.__remove_old_logs()
        self.logger.info("Removing old outputs...")
        self.__remove_old_outputs()

    def __remove_old_logs(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for f in os.listdir(self.final_log_dir):
            path = os.path.join(self.final_log_dir, f)
            if os.path.isfile(path):
                if datetime.fromtimestamp(os.path.getmtime(path)) < cutoff:
                    os.remove(path)
                    self.logger.warning(f"Removed old log file: {path}")
        for f in os.listdir(self.temp_log_dir):
            path = os.path.join(self.temp_log_dir, f)
            if os.path.isfile(path):
                os.remove(path)
                self.logger.warning(f"Removed old log file: {path}")

    def __remove_old_outputs(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        for f in os.listdir(self.outbound_dir):
            path = os.path.join(self.outbound_dir, f)
            if os.path.isfile(path):
                if datetime.fromtimestamp(os.path.getmtime(path)) < cutoff:
                    os.remove(path)
                    self.logger.warning(f"Removed old output file: {path}")

    def __enforce_delta_retention_for_all_tables(self):
        pass
