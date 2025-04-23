"""DTS parser for converting DTS to keymap configuration."""

from typing import Dict, List, Optional, Union, Any
import re

class DtsNode:
    """Represents a DTS node."""
    
    def __init__(self, name: str):
        """Initialize node.
        
        Args:
            name: Node name
        """
        self.name = name
        self.properties: Dict[str, DtsProperty] = {}
        self.children: Dict[str, DtsNode] = {}
        self.labels: Dict[str, str] = {}


class DtsProperty:
    """Represents a DTS property."""
    
    def __init__(self, name: str, value: Any, type: str):
        """Initialize property.
        
        Args:
            name: Property name
            value: Property value
            type: Property type (string, array, reference, integer, boolean)
        """
        self.name = name
        self.value = value
        self.type = type


class DtsRoot:
    """Represents the root of a DTS AST."""
    
    def __init__(self):
        """Initialize root."""
        self.root = DtsNode("/")


class DtsParser:
    """Parser for DTS content."""
    
    def __init__(self):
        """Initialize parser."""
        self.tokens: List[str] = []
        self.pos = 0
        self.labels: Dict[str, DtsNode] = {}
        
    def parse(self, content: str) -> DtsRoot:
        """Parse DTS content.
        
        Args:
            content: DTS content string
            
        Returns:
            DtsRoot instance
        """
        # Remove comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        
        # Tokenize
        self.tokens = self._tokenize(content)
        self.pos = 0
        
        # Create root
        root = DtsRoot()
        
        # Parse root node
        self._parse_node_body(root.root)
        
        return root
        
    def _tokenize(self, content: str) -> List[str]:
        """Tokenize DTS content.
        
        Args:
            content: DTS content string
            
        Returns:
            List of tokens
        """
        # Split on whitespace, but keep strings and arrays intact
        tokens = []
        current = ""
        in_string = False
        in_array = False
        
        for char in content:
            if char == '"' and not in_array:
                in_string = not in_string
                current += char
            elif char == '<' and not in_string:
                if in_array:
                    current += char
                else:
                    if current.strip():
                        tokens.extend(current.strip().split())
                    current = char
                    in_array = True
            elif char == '>' and not in_string:
                if in_array:
                    current += char
                    tokens.append(current)
                    current = ""
                    in_array = False
                else:
                    current += char
            elif char in '{};=:' and not (in_string or in_array):
                if current.strip():
                    tokens.extend(current.strip().split())
                tokens.append(char)
                current = ""
            else:
                current += char
                
        if current.strip():
            tokens.extend(current.strip().split())
            
        return [t for t in tokens if t.strip()]
        
    def _parse_node_body(self, node: DtsNode) -> None:
        """Parse node body.
        
        Args:
            node: Node to parse body for
        """
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            
            if token == '}':
                self.pos += 1
                return
                
            if token == ';':
                self.pos += 1
                continue
                
            # Handle labels
            if (self.pos + 1 < len(self.tokens) and 
                self.tokens[self.pos + 1] == ':'):
                label = token
                self.pos += 2  # Skip label and colon
                if self.pos >= len(self.tokens):
                    raise ValueError("Unexpected end of input after label")
                token = self.tokens[self.pos]
                
                # Create node with label
                name = token
                child = DtsNode(name)
                child.labels[label] = name
                node.children[name] = child
                
                # Skip to opening brace
                self.pos += 1
                if (self.pos >= len(self.tokens) or 
                    self.tokens[self.pos] != '{'):
                    raise ValueError("Expected '{' after labeled node")
                self.pos += 1
                
                # Parse node body
                self._parse_node_body(child)
                continue
                
            # Handle property assignments
            if (self.pos + 1 < len(self.tokens) and 
                self.tokens[self.pos + 1] == '='):
                name = token
                self.pos += 2  # Skip name and =
                if self.pos >= len(self.tokens):
                    raise ValueError("Unexpected end of input after =")
                    
                value = self.tokens[self.pos]
                self.pos += 1
                
                # Create property
                if value.startswith('"') and value.endswith('"'):
                    prop = DtsProperty(name, value[1:-1], "string")
                elif value.startswith('<') and value.endswith('>'):
                    prop = DtsProperty(name, value, "array")
                elif value.startswith('&'):
                    prop = DtsProperty(name, value[1:], "reference")
                elif value.lower() in ('true', 'false'):
                    prop = DtsProperty(
                        name, 
                        value.lower() == 'true', 
                        "boolean"
                    )
                else:
                    try:
                        prop = DtsProperty(name, int(value), "integer")
                    except ValueError:
                        prop = DtsProperty(name, value, "string")
                        
                node.properties[name] = prop
                
                # Skip semicolon
                if (self.pos < len(self.tokens) and 
                    self.tokens[self.pos] == ';'):
                    self.pos += 1
                    
            # Handle child nodes
            elif (self.pos + 1 < len(self.tokens) and 
                  self.tokens[self.pos + 1] == '{'):
                name = token
                child = DtsNode(name)
                node.children[name] = child
                
                self.pos += 2  # Skip name and {
                self._parse_node_body(child)
                
            else:
                self.pos += 1 