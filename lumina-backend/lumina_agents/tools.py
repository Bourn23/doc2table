"""
Tool functions for AI agents in the Lumina system.

This module provides utility functions that agents can use to validate and process
Pydantic model code during schema generation and extraction workflows.

Tools:
    - verify_pydantic_model_code: Validates Python syntax and executability
    - validate_pydantic_model_structure: Checks for required fields in model
    - return_final_code_schema: Generates final schema output
"""

import ast
from agents import function_tool


@function_tool
def verify_pydantic_model_code(model_code: str) -> str:
    """
    Verifies that the provided Pydantic model code is syntactically valid Python.
    
    This function performs two validation steps:
    1. Compiles the code to catch syntax errors without executing it
    2. Executes the code in an isolated environment to verify it's runnable
    
    Args:
        model_code: The Pydantic model code string to verify. Should be complete
                   Python code including all necessary imports and class definitions.
    
    Returns:
        A success message if the code is valid, or a detailed error message
        explaining what went wrong.
    
    Example:
        >>> code = '''
        ... from pydantic import BaseModel, Field
        ... 
        ... class User(BaseModel):
        ...     name: str = Field(description="User's name")
        ...     age: int = Field(description="User's age", ge=0)
        ... '''
        >>> result = verify_pydantic_model_code(code)
        >>> print(result)
        ✅ Code is syntactically valid and executable.
    
    Note:
        The code is executed in an empty namespace to prevent side effects
        and ensure isolation from the current environment.
    """
    try:
        # Compile first to catch syntax errors without executing
        compile(model_code, '<string>', 'exec')
        
        # Execute in a sandboxed/empty dictionary to prevent side effects
        exec(model_code, {})
        
        return "✅ Code is syntactically valid and executable."
    except SyntaxError as e:
        return (
            f"❌ Syntax error in Pydantic model code.\n"
            f"   Line {e.lineno}: {e.msg}\n"
            f"   Text: {e.text.strip() if e.text else 'N/A'}\n"
            f"   Please check for missing colons, parentheses, or indentation issues."
        )
    except NameError as e:
        return (
            f"❌ Name error in Pydantic model code: {e}\n"
            f"   This usually means a missing import statement.\n"
            f"   Make sure all required types (BaseModel, Field, etc.) are imported."
        )
    except Exception as e:
        return (
            f"❌ Invalid Pydantic model code.\n"
            f"   Error type: {type(e).__name__}\n"
            f"   Error message: {str(e)}\n"
            f"   Please review the code for issues."
        )


@function_tool
def validate_pydantic_model_structure(model_code: str, required_fields: list[str]) -> str:
    """
    Validates that the generated Pydantic model code contains all required fields.
    
    This function parses the Python code into an Abstract Syntax Tree (AST) and
    checks that all specified field names are present in the model class definition.
    
    Args:
        model_code: The Pydantic model code to validate. Should contain at least
                   one class definition with annotated fields.
        required_fields: A list of field names that must be present in the model.
                        Field names should match exactly (case-sensitive).
    
    Returns:
        A success message listing the number of validated fields, or an error
        message detailing which fields are missing.
    
    Example:
        >>> code = '''
        ... from pydantic import BaseModel, Field
        ... 
        ... class Product(BaseModel):
        ...     name: str = Field(description="Product name")
        ...     price: float = Field(description="Product price")
        ...     in_stock: bool = Field(description="Availability")
        ... '''
        >>> required = ["name", "price", "in_stock"]
        >>> result = validate_pydantic_model_structure(code, required)
        >>> print(result)
        ✅ Validation successful. All 3 required fields are present.
    
    Note:
        This function only checks for the presence of fields, not their types
        or validation rules. It looks for annotated assignments (e.g., name: str).
    """
    if not required_fields:
        return "⚠️ No required fields specified. Validation skipped."
    
    try:
        # Parse the code into an Abstract Syntax Tree
        tree = ast.parse(model_code)
        
        # Find the class definition in the code
        class_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_found = True
                class_name = node.name
                
                # We found the class, now let's find the fields defined in it
                defined_fields = set()
                for body_item in node.body:
                    # Fields are defined as Annotated Assignments (e.g., name: str)
                    if isinstance(body_item, ast.AnnAssign):
                        if hasattr(body_item.target, 'id'):
                            defined_fields.add(body_item.target.id)
                
                # Check if all required fields are present
                missing_fields = set(required_fields) - defined_fields
                extra_fields = defined_fields - set(required_fields)
                
                if not missing_fields:
                    msg = f"✅ Validation successful. All {len(required_fields)} required fields are present in class '{class_name}'."
                    if extra_fields:
                        msg += f"\n   Additional fields found: {', '.join(sorted(extra_fields))}"
                    return msg
                else:
                    return (
                        f"❌ Validation failed for class '{class_name}'.\n"
                        f"   Missing required fields: {', '.join(sorted(missing_fields))}\n"
                        f"   Found fields: {', '.join(sorted(defined_fields)) if defined_fields else 'none'}\n"
                        f"   Please add the missing fields to the model."
                    )
        
        if not class_found:
            return (
                "❌ Validation failed. No class definition found in the code.\n"
                "   Make sure your code includes a Pydantic model class definition."
            )
        
        return "❌ Validation failed. Could not analyze class structure."

    except SyntaxError as e:
        return (
            f"❌ Cannot validate structure due to syntax error.\n"
            f"   Line {e.lineno}: {e.msg}\n"
            f"   Please fix syntax errors first using verify_pydantic_model_code."
        )
    except Exception as e:
        return (
            f"❌ Error during structural validation.\n"
            f"   Error type: {type(e).__name__}\n"
            f"   Error message: {str(e)}\n"
            f"   The code may have unexpected structure or formatting."
        )


@function_tool
def return_final_code_schema(model_name: str, model_code: str) -> dict:
    """
    Generates the final code schema for the Pydantic model.
    
    This function creates a standardized output format containing the model name
    and its complete code. It serves as the final step in the schema generation
    pipeline, packaging the validated model for use in extraction workflows.
    
    Args:
        model_name: The name of the Pydantic model class (e.g., "UserProfile").
                   Should match the class name in the model_code.
        model_code: The complete Pydantic model code, including all imports,
                   class definition, fields, and validators.
    
    Returns:
        A dictionary containing:
        - model_name: The name of the model
        - model_code: The complete Python code as a string
    
    Example:
        >>> model_name = "Product"
        >>> model_code = '''
        ... from pydantic import BaseModel, Field
        ... 
        ... class Product(BaseModel):
        ...     name: str = Field(description="Product name")
        ...     price: float = Field(description="Price in USD", ge=0)
        ... '''
        >>> schema = return_final_code_schema(model_name, model_code)
        >>> print(schema)
        {'model_name': 'Product', 'model_code': '...'}
    
    Note:
        This function does not perform validation. It should be called after
        verify_pydantic_model_code and validate_pydantic_model_structure have
        confirmed the code is valid.
    """
    return {
        "model_name": model_name,
        "model_code": model_code
    }
