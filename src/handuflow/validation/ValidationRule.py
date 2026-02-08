from abc import ABC, abstractmethod

from handuflow.validation.ValidationContext import ValidationContext

class ValidationRule(ABC):
    name: str

    @abstractmethod
    def validate(self, context: ValidationContext):
        """Raise ValidationError on failure"""
        pass
