"""
Command-line interface for validating QType YAML spec files.
"""

import sys
import logging
from typing import Any
from pydantic import ValidationError
from qtype.dsl import validate_spec
from qtype.ir import *

logger = logging.getLogger(__name__)


def validate_main(args: Any) -> None:
    """
    Validate a QType YAML spec file against the QTypeSpec schema and semantics.

    Args:
        args: Arguments passed from the command line or calling context.

    Exits:
        Exits with code 1 if validation fails.
    """
    try:
        spec = validate_spec(args)
        logger.info("✅ Schema validation successful.")
    except ValidationError as exc:
        logger.error("❌ Schema validation failed:\n%s", exc)
        sys.exit(1)

    try:
        validate_semantics(spec)
        logger.info("✅ Semantic validation successful.")
    except Exception as exc:
        logger.error("❌ Semantic validation failed:\n%s", exc)
        sys.exit(1)

    try:
        intermediate_representation = resolve_semantic_ir(spec)
        logger.info("✅ Semantic resolution successful.")
    except Exception as exc:
        logger.error("❌ Semantic resolution failed:\n%s", exc)
        sys.exit(1)
