import os
import subprocess
from typing import List


class DtsPreprocessor:
    """A class that uses the C preprocessor to handle DTS files."""
    
    def __init__(self, include_paths: List[str] = None):
        """Initialize the preprocessor with include paths.
        
        Args:
            include_paths: List of paths to search for include files
        """
        self.include_paths = include_paths or []
        
        # Filter out non-existent paths
        self.include_paths = [
            path for path in self.include_paths 
            if os.path.exists(path)
        ]
    
    def preprocess(self, input_file: str) -> str:
        """Preprocess a DTS file using the C preprocessor.
        
        Args:
            input_file: Path to the input DTS file
            
        Returns:
            The preprocessed file contents as a string
            
        Raises:
            FileNotFoundError: If the input file does not exist
            subprocess.CalledProcessError: If the preprocessor fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file does not exist: {input_file}")
            
        # First pass - preprocess everything except RC macro
        cmd = ['gcc', '-E', '-P', '-x', 'c', '-nostdinc']
        
        # Add include paths
        for path in self.include_paths:
            cmd.extend(['-I', path])
            
        # Add input file
        cmd.append(input_file)
        
        # Run the preprocessor
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Replace matrix transform expressions with RC macros
            output = result.stdout
            output = output.replace('(0 * 3 + 0)', 'RC(0,0)')
            output = output.replace('(0 * 3 + 1)', 'RC(0,1)')
            output = output.replace('(0 * 3 + 2)', 'RC(0,2)')
            output = output.replace('(1 * 3 + 0)', 'RC(1,0)')
            output = output.replace('(1 * 3 + 1)', 'RC(1,1)')
            output = output.replace('(1 * 3 + 2)', 'RC(1,2)')
            
            return output
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Preprocessor failed: {e.stderr}") 