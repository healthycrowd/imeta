import jsonschema.exceptions


class ValidationError(Exception):
    pass


ValidationErrors = (ValidationError, jsonschema.exceptions.ValidationError)
