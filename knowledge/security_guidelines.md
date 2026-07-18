# Security Guidelines

## Password management

Passwords must never be stored, logged or returned in plain text.

Before storing a password, the application must use a secure password hashing algorithm.

API responses must never include passwords, authentication tokens or secret credentials.

## Input validation

Usernames and email addresses must be validated before they are processed.

Passwords must satisfy the minimum length and complexity requirements defined by the project.

## Sensitive information

Sensitive data must not be exposed through logs, exceptions or API responses.

Authentication tokens and credentials must be stored outside the source code.