#!/usr/bin/env python3
"""
Flask Auth Service API - Data Validation Schemas.
This module defines Marshmallow schemas for request/response validation and serialization.
"""

from marshmallow import Schema, fields, validate, ValidationError


class RegisterSchema(Schema):
    """Schema for user registration."""
    username = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^[a-zA-Z0-9_-]{3,30}$',
            error="Username must be 3-30 characters, alphanumeric with underscores and hyphens."
        )
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, error="Password must be at least 8 characters long.")
    )
    email = fields.Email(required=False)


class LoginSchema(Schema):
    """Schema for user login."""
    identifier = fields.Str(
        required=True,
        error_messages={"required": "Either username or email is required."}
    )
    password = fields.Str(
        required=True,
        error_messages={"required": "Password is required."}
    )


class UserSchema(Schema):
    """Schema for user response."""
    username = fields.Str()
    role = fields.Str()
    email = fields.Email(allow_none=True)
    creation_method = fields.Str()
    created_at = fields.DateTime(format='iso')
    is_active = fields.Boolean()
