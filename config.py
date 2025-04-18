"""
Configuration Module

This module manages the configuration settings for the Shopee price tracker,
including loading configuration from the Excel file.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from excel_handler import ExcelHandler

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_LINK_COLUMN = "A"
DEFAULT_VAR1_COLUMN = "B"
DEFAULT_VAR2_COLUMN = "C"
DEFAULT_DISCOUNT_COLUMN = "D"


@dataclass
class Config:
    """Configuration class for the Shopee price tracker."""
    
    link_column: str
    var1_column: str
    var2_column: str
    discount_column: str
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return (
            f"Config(link_column={self.link_column}, "
            f"var1_column={self.var1_column}, var2_column={self.var2_column}, "
            f"discount_column={self.discount_column})"
        )


def parse_config_cell(value: str) -> Dict[str, str]:
    """
    Parse a configuration cell value.
    
    Format: key1=value1;key2=value2;...
    
    Args:
        value: The cell value
        
    Returns:
        Dict of configuration key-value pairs
    """
    if not value or not isinstance(value, str):
        return {}
    
    result = {}
    parts = value.split(';')
    
    for part in parts:
        if '=' not in part:
            continue
        
        key, val = part.split('=', 1)
        result[key.strip().lower()] = val.strip()
    
    return result


def load_config_from_excel(excel: ExcelHandler) -> Config:
    """
    Load configuration from the Excel file.
    
    The configuration is expected to be in the first row of the sheet.
    
    Args:
        excel: The ExcelHandler instance
        
    Returns:
        Configuration object
    """
    # Try to get configuration from the first row
    config_dict = {}
    
    # Check cells A1, B1, C1, etc. for configuration
    for col_idx in range(10):  # Check first 10 columns
        col_letter = excel.column_index_to_letter(col_idx)
        cell_value = excel.get_column_value(1, col_letter)
        
        if cell_value:
            parsed = parse_config_cell(cell_value)
            config_dict.update(parsed)
    
    # Extract configuration values with defaults
    link_col = config_dict.get('link_column', DEFAULT_LINK_COLUMN)
    var1_col = config_dict.get('var1_column', DEFAULT_VAR1_COLUMN)
    var2_col = config_dict.get('var2_column', DEFAULT_VAR2_COLUMN)
    discount_col = config_dict.get('discount_column', DEFAULT_DISCOUNT_COLUMN)
    
    return Config(
        link_column=link_col,
        var1_column=var1_col,
        var2_column=var2_col,
        discount_column=discount_col
    )
