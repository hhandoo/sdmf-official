# inbuilt
import logging
import configparser

# external
from pyspark.sql import SparkSession
import pandas as pd

# internal
from handuflow.validation.Validator import Validator
from handuflow.validation.ValidationContext import ValidationContext
from handuflow.validation.validation_rules.ValidateMasterSpecs import ValidateMasterSpecs
from handuflow.validation.validation_rules.EnforceMasterSpecsStructure import (
    EnforceMasterSpecsStructure,
)
from handuflow.validation.validation_rules.ValidateFeedSpecsJSON import ValidateFeedSpecsJSON
from handuflow.validation.validation_rules.PrimaryKey import PrimaryKey
from handuflow.validation.validation_rules.ColumnExistsInSelection import (
    ColumnExistsInSelection,
)
from handuflow.validation.validation_rules.EnforceStandardChecks import EnforceStandardChecks
from handuflow.validation.validation_rules.StandardCheckStructureCheck import (
    StandardCheckStructureCheck,
)
from handuflow.validation.validation_rules.ComprehensiveChecksDependencyDatasetCheck import (
    ComprehensiveChecksDependencyDatasetCheck,
)
from handuflow.validation.validation_rules.PartitionKeysCheck import PartitionKeysCheck
from handuflow.validation.validation_rules.CompositeKeysCheck import CompositeKeysCheck
from handuflow.validation.validation_rules.VacuumHoursCheck import VacuumHoursCheck
from handuflow.exception.ValidationError import ValidationError


class SystemLaunchValidator:

    def __init__(
        self,
        file_hunt_path: str,
        spark: SparkSession,
        config: configparser.ConfigParser,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.spark = spark
        self.config = config

        self.context = ValidationContext(
            spark=spark,
            file_hunt_path=file_hunt_path,
            master_spec_name=self.config["FILES"]["master_spec_name"],
        )

    def __init_rules(self):
        self.rules = [
            ValidateMasterSpecs(),
            EnforceMasterSpecsStructure(),
            ValidateFeedSpecsJSON(),
            PrimaryKey(),
            ColumnExistsInSelection(),
            PartitionKeysCheck(),
            CompositeKeysCheck(),
            VacuumHoursCheck(),
            EnforceStandardChecks(),
            StandardCheckStructureCheck(),
            ComprehensiveChecksDependencyDatasetCheck(),
        ]

    def run(self):
        try:
            self.__init_rules()
            validator = Validator(self.rules, fail_fast=True)
            return validator.validate(self.context)
        except Exception as e:
            raise ValidationError(
                    "Something went wrong in system validation",
                    original_exception=e
                )

    def get_validated_master_specs(self) -> pd.DataFrame:
        opt_df = self.context.get_master_specs()
        opt_df = opt_df[opt_df["is_active"] == True]
        return opt_df
