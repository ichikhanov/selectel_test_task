from cerberus import Validator
from utils import ValidationException


class CerberusValidator:
    def __init__(self):
        self.ticket_patch_validator = Validator(
            {
                "status": {
                    "type": "string",
                    "required": True,
                    "allowed": ["open", "responded", "closed", "waiting_for_response"],
                }
            }
        )
        self.ticket_post_validator = Validator(
            {
                "theme": {"type": "string", "required": True},
                "text": {"type": "string", "required": True},
                "email": {
                    "type": "string",
                    "required": True,
                    "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                },
                "status": {"type": "string", "required": True, "allowed": ["open"]},
            }
        )

        self.comment_post_validator = Validator(
            {
                "ticket_id": {"type": "integer", "required": True, "coerce": int},
                "email": {
                    "type": "string",
                    "required": True,
                    "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                },
                "text": {"type": "string", "required": True},
            }
        )

    def _validate(self, validator, object_to_validate):
        if not object_to_validate:
            raise ValidationException("Empty request data")
        request_data = validator.normalized(object_to_validate)
        if not validator.validate(object_to_validate) and validator.errors:
            raise ValidationException(validator.errors)
        return request_data

    def validate_ticket_patch_schema(self, object_to_validate):
        return self._validate(self.ticket_patch_validator, object_to_validate)

    def validate_ticket_post_schema(self, object_to_validate):
        return self._validate(self.ticket_post_validator, object_to_validate)

    def validate_comment_post_schema(self, object_to_validate):
        return self._validate(self.comment_post_validator, object_to_validate)
