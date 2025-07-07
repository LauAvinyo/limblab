# Contributing to LimbLab

Thank you for your interest in contributing to LimbLab! This guide will help you get started with contributing to the project, whether you're a developer, scientist, or documentation writer.

## 🤝 How to Contribute

### 🐛 Report Bugs
Found a bug? Help us fix it by reporting it properly.

**Before reporting:**
1. Check if the issue has already been reported
2. Try to reproduce the issue with the latest version
3. Gather all relevant information

**What to include:**
- **Clear title:** Brief description of the issue
- **Detailed description:** What happened vs. what you expected
- **Steps to reproduce:** Exact steps to trigger the issue
- **Environment:** OS, Python version, LimbLab version
- **Error messages:** Complete error text and traceback
- **Data description:** Brief description of your data (if relevant)

**Example bug report:**
```
Title: Volume processing fails with large TIFF files

Description:
When processing TIFF files larger than 2GB, LimbLab crashes with a memory error.

Steps to reproduce:
1. Create experiment: limblab create-experiment test
2. Try to clean large volume: limblab clean-volume test large_file.tif DAPI
3. Observe memory error after 5 minutes

Environment:
- OS: macOS 14.0
- Python: 3.9.7
- LimbLab: 0.2.0
- File: 2.5GB TIFF, 2048x2048x512 pixels

Error:
MemoryError: Unable to allocate array of shape (2048, 2048, 512)
```

### 💡 Suggest Features
Have an idea for a new feature? We'd love to hear it!

**What to include:**
- **Clear description:** What the feature should do
- **Use case:** Why this feature is needed
- **Expected behavior:** How it should work
- **Alternatives considered:** Other approaches you've thought about
- **Mockups/sketches:** Visual examples if applicable

**Example feature request:**
```
Title: Batch processing for multiple experiments

Description:
Ability to process multiple experiments automatically without manual intervention.

Use case:
I have 50 experiments that need the same processing pipeline. Currently, I have to run each command manually for each experiment.

Expected behavior:
limblab batch-process experiments.txt --pipeline "clean,extract,stage,align"

This would:
1. Read experiment list from experiments.txt
2. Apply the specified pipeline to each experiment
3. Generate a summary report
4. Handle errors gracefully and continue with remaining experiments

Alternatives:
- Shell script automation (less user-friendly)
- Python script with API (requires programming knowledge)
```

### 📚 Improve Documentation
Good documentation is crucial for user adoption.

**Areas for improvement:**
- **Tutorials:** Step-by-step guides for common tasks
- **User guides:** Detailed explanations of features
- **API documentation:** Function descriptions and examples
- **Code comments:** Inline documentation for complex code
- **Examples:** Sample data and workflows

**Documentation standards:**
- Use clear, concise language
- Include code examples
- Add screenshots for visual steps
- Test all examples before submitting
- Follow the existing style and format

### 🔧 Contribute Code
Ready to write code? Here's how to get started.

#### Development Setup

**1. Fork the repository**
```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/limblab.git
cd limblab
```

**2. Set up development environment**
```bash
# Create virtual environment
python -m venv limblab_dev
source limblab_dev/bin/activate  # On Windows: limblab_dev\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
pip install -r requirements-dev.txt
```

**3. Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

**4. Make your changes**
- Write code following the style guide
- Add tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

**5. Submit a pull request**
```bash
git add .
git commit -m "Add feature: brief description"
git push origin feature/your-feature-name
```

#### Code Style Guide

**Python Code:**
```python
# Use descriptive variable names
experiment_path = Path("/path/to/experiment")
volume_data = load_volume(experiment_path)

# Add type hints
def process_volume(volume_path: Path, channel: str) -> np.ndarray:
    """Process volume data for analysis.
    
    Args:
        volume_path: Path to volume file
        channel: Channel name to process
        
    Returns:
        Processed volume data
        
    Raises:
        FileNotFoundError: If volume file doesn't exist
        ValueError: If channel name is invalid
    """
    if not volume_path.exists():
        raise FileNotFoundError(f"Volume file not found: {volume_path}")
    
    # Process the volume
    processed_data = apply_filters(load_data(volume_path))
    
    return processed_data
```

**Documentation:**
```markdown
# Feature Name

Brief description of the feature.

## Usage

```python
from limblab import feature_name

result = feature_name(parameter1, parameter2)
```

## Parameters

- `parameter1`: Description of parameter
- `parameter2`: Description of parameter

## Returns

Description of return value.

## Examples

```python
# Basic usage
result = feature_name("example", 42)

# Advanced usage
result = feature_name("example", 42, option=True)
```
```

#### Testing Guidelines

**Write tests for:**
- New functions and classes
- Edge cases and error conditions
- Integration between components
- Performance benchmarks

**Test structure:**
```python
import pytest
from pathlib import Path
from limblab import your_function

class TestYourFunction:
    """Test suite for your_function."""
    
    def test_basic_functionality(self):
        """Test basic functionality with valid inputs."""
        result = your_function("test_input")
        assert result is not None
        assert isinstance(result, expected_type)
    
    def test_error_handling(self):
        """Test error handling with invalid inputs."""
        with pytest.raises(ValueError):
            your_function("invalid_input")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with empty input
        result = your_function("")
        assert result == expected_empty_result
        
        # Test with very large input
        large_input = "x" * 10000
        result = your_function(large_input)
        assert result is not None
```

### 🧪 Test New Features
Help us ensure quality by testing new features.

**Beta testing process:**
1. **Join beta program:** Contact the development team
2. **Install beta version:** Get access to pre-release versions
3. **Test thoroughly:** Use with your own data
4. **Report feedback:** Provide detailed feedback on usability
5. **Document issues:** Report bugs and suggest improvements

**Testing checklist:**
- [ ] Install and setup works correctly
- [ ] Basic functionality works as expected
- [ ] Error handling is appropriate
- [ ] Performance is acceptable
- [ ] Documentation is clear and accurate
- [ ] Integration with existing features works
- [ ] Edge cases are handled properly

### 🌟 Share Examples
Help other users by sharing your workflows and examples.

**What to share:**
- **Workflow scripts:** Automated analysis pipelines
- **Configuration files:** Custom parameter settings
- **Data examples:** Sample datasets for testing
- **Visualization examples:** Custom plotting scripts
- **Use cases:** Real-world applications

**Example contribution:**
```python
# Custom analysis workflow
import limblab
from pathlib import Path

def analyze_gene_expression(experiment_path: Path, gene_name: str):
    """Custom workflow for gene expression analysis."""
    
    # Process volume with custom parameters
    limblab.clean_volume(
        experiment_path, 
        f"{gene_name}.tif", 
        gene_name,
        gaussian_sigma=(8, 8, 8),
        frequency_cutoff=0.03
    )
    
    # Extract surface
    limblab.extract_surface(experiment_path, auto=True)
    
    # Stage limb
    limblab.stage_limb(experiment_path)
    
    # Create publication-quality visualization
    limblab.vis.isosurfaces(
        experiment_path, 
        gene_name,
        high_res=True,
        colormap='plasma'
    )
    
    return experiment_path
```

## 📋 Contribution Guidelines

### Before You Start

**1. Check existing issues**
- Search for similar issues or feature requests
- Check if your idea has already been discussed
- Avoid duplicating existing work

**2. Read the documentation**
- Understand the current functionality
- Review the codebase structure
- Check the development roadmap

**3. Join the community**
- Participate in discussions
- Ask questions if you're unsure
- Get feedback on your ideas

### Quality Standards

**Code contributions:**
- Follow the style guide
- Include comprehensive tests
- Update documentation
- Handle errors gracefully
- Consider performance implications

**Documentation contributions:**
- Use clear, concise language
- Include practical examples
- Test all code examples
- Follow the existing format
- Add appropriate cross-references

**Bug reports:**
- Provide complete information
- Include steps to reproduce
- Test with latest version
- Be respectful and constructive

### Review Process

**Pull request review:**
1. **Automated checks:** CI/CD pipeline runs tests
2. **Code review:** Team members review the code
3. **Documentation review:** Ensure docs are updated
4. **Testing:** Verify functionality works as expected
5. **Approval:** Changes are approved and merged

**Review criteria:**
- Code quality and style
- Test coverage and quality
- Documentation completeness
- Performance implications
- Security considerations

## 🏆 Recognition

### Contributor Credits
- **Code contributors:** Listed in release notes
- **Documentation contributors:** Acknowledged in docs
- **Bug reporters:** Credited in issue resolution
- **Testers:** Recognized in beta testing program

### Hall of Fame
- **Major contributors:** Special recognition for significant contributions
- **Long-term contributors:** Recognition for sustained involvement
- **Community leaders:** Acknowledgment for community building

### Co-authorship
- **Scientific contributions:** Co-authorship for major scientific contributions
- **Methodology papers:** Recognition in methodology publications
- **Case studies:** Acknowledgment in case study publications

## 🚀 Getting Started

### First Contribution
1. **Start small:** Fix a typo or add a simple example
2. **Follow the guide:** Use this guide for your first contribution
3. **Ask for help:** Don't hesitate to ask questions
4. **Be patient:** Reviews may take time

### Learning Resources
- **GitHub guides:** [GitHub Guides](https://guides.github.com/)
- **Python development:** [Python Development Guide](https://devguide.python.org/)
- **Open source:** [Open Source Guide](https://opensource.guide/)
- **Scientific software:** [Software Carpentry](https://software-carpentry.org/)

### Mentorship
- **New contributor program:** Get paired with experienced contributors
- **Office hours:** Regular sessions for questions and guidance
- **Workshops:** Hands-on contribution workshops
- **Documentation:** Comprehensive guides and tutorials

## 📞 Contact and Support

### Questions?
- **GitHub Discussions:** [https://github.com/lauavinyo/limblab/discussions](https://github.com/lauavinyo/limblab/discussions)
- **Email:** [laura.avino@embl.es](mailto:laura.avino@embl.es)
- **Issues:** [https://github.com/lauavinyo/limblab/issues](https://github.com/lauavinyo/limblab/issues)

### Getting Help
- **Documentation:** Check the user guide and tutorials
- **Examples:** Review existing examples and workflows
- **Community:** Ask questions in discussions
- **Direct contact:** Email for specific questions

---

*Thank you for contributing to LimbLab! Your contributions help make 3D limb analysis accessible to researchers worldwide.*