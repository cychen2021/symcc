from dataclasses import dataclass, field
from typing import List, Optional, Union, Iterator
import re

@dataclass
class Node:
    """A node in the SMT-LIB2 expression tree.
    
    This class represents all types of nodes in SMT-LIB2 expressions:
    - Keywords (let, define-fun, assert, etc.)
    - Simple identifiers (function names like concat)
    - Literals (e.g., #x0001)
    - Complex identifiers (e.g., extract [7 7])
    
    Attributes:
        children: List of child nodes
        tag: A simple identifier or a complex identifier with indices
    """
    children: List['Node'] = field(default_factory=list)
    tag: str | tuple[str, int | str, ...]

    def add_child(self, child: 'Node') -> None:
        """Add a child node to this node."""
        self.children.append(child)

    def __str__(self) -> str:
        """String representation of the node."""
        if isinstance(self.tag, str):
            return self.tag
        # For complex identifiers with indices
        base, *indices = self.tag
        indices_str = ' '.join(str(i) for i in indices)
        return f"{base} [{indices_str}]"

    def __repr__(self) -> str:
        return self.__str__()
    
    def traverse_preorder(self) -> Iterator['Node']:
        """Traverse the tree in pre-order (root, left, right)."""
        yield self
        for child in self.children:
            yield from child.traverse_preorder()
    
    def traverse_postorder(self) -> Iterator['Node']:
        """Traverse the tree in post-order (left, right, root)."""
        for child in self.children:
            yield from child.traverse_postorder()
        yield self
    
    def is_leaf(self) -> bool:
        """Check if this node is a leaf node."""
        return len(self.children) == 0
    
    def depth(self) -> int:
        """Calculate the depth of this node in its subtree."""
        if self.is_leaf():
            return 0
        return 1 + max(child.depth() for child in self.children)
    
    @classmethod
    def create_complex(cls, base: str, *indices: Union[int, str]) -> 'Node':
        """Create a node with a complex identifier.
        
        Example:
            >>> node = Node.create_complex('extract', 7, 7)
            >>> str(node)  # 'extract [7 7]'
        """
        return cls(tag=(base, *indices))

    @classmethod
    def parse(cls, text: str) -> 'Node':
        """Parse an SMT-LIB2 expression into a Node tree.
        
        The text can be in one of these forms:
        - A literal or simple identifier: "x", "#x0001"
        - A compound expression: "(tag child1 child2 ...)"
        - A complex identifier: "((_ tag index1 index2 ...) child1 child2 ...)"
        
        Examples:
            >>> Node.parse("x")
            x
            >>> Node.parse("(concat x y)")
            concat
            >>> Node.parse("((_ extract 7 0) x)")
            extract [7 0]
        
        Args:
            text: The SMT-LIB2 expression to parse
            
        Returns:
            The root node of the parsed expression tree
            
        Raises:
            ValueError: If the input text is malformed
        """
        text = text.strip()
        
        # Handle literal or simple identifier
        if not text.startswith('('):
            return cls(tag=text)
        
        # Remove outer parentheses
        inner = text[1:-1].strip()
        if not inner:
            raise ValueError("Empty expression")
        
        # Split into tokens, handling nested parentheses
        tokens = cls._tokenize(inner)
        if not tokens:
            raise ValueError("Empty expression after tokenization")
        
        first_token = tokens[0]
        
        # Handle complex identifier with indices
        if first_token == '_':
            if len(tokens) < 3:
                raise ValueError("Invalid complex identifier")
            tag_parts = tokens[1:]  # Get the tag and indices
            # Find the first opening parenthesis after the complex identifier
            remaining = inner[inner.find(')', inner.find('_')):]
            remaining_tokens = cls._tokenize(remaining.strip())
            
            # Convert indices to int where possible
            indices = []
            for idx in tag_parts[1:]:
                try:
                    indices.append(int(idx))
                except ValueError:
                    indices.append(idx)
            
            node = cls(tag=(tag_parts[0], *indices))
            
            # Parse remaining children
            for child_expr in remaining_tokens:
                node.add_child(cls.parse(child_expr))
            
            return node
        
        # Handle simple expression
        node = cls(tag=first_token)
        for token in tokens[1:]:
            node.add_child(cls.parse(token))
        
        return node
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Split an SMT-LIB2 expression into tokens, preserving nested expressions.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of tokens, where nested expressions are kept as single tokens
        """
        tokens = []
        current = []
        depth = 0
        
        for char in text:
            if char == '(':
                depth += 1
                current.append(char)
            elif char == ')':
                depth -= 1
                current.append(char)
                if depth == 0:
                    tokens.append(''.join(current))
                    current = []
            elif char.isspace() and depth == 0:
                if current:
                    tokens.append(''.join(current))
                    current = []
            else:
                current.append(char)
        
        if current:
            tokens.append(''.join(current))
        
        return tokens
    
    def to_smt2(self, indent: int = 0) -> str:
        """Convert the tree to a formatted SMT-LIB2 string representation.
        
        Args:
            indent: Current indentation level
            
        Returns:
            A string in SMT-LIB2 format with proper indentation
        """
        spaces = '  ' * indent
        if self.is_leaf():
            return f"{spaces}{self}"
        
        result = [f"{spaces}{self}"]
        for child in self.children:
            result.append(child.to_smt2(indent + 1))
        return '\n'.join(result)
