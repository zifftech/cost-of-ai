# Development Rules

### Environment Management

**The user is responsible for maintaining the environment.**

This includes:
- Setting up and managing the Python virtual environment using pyenv
- Installing and managing Python dependencies
- Configuring environment variables using direnv
- Managing the development environment setup

### Dependency Management

**Never attempt to install new dependencies.**

The development assistant should not:
- Run `pip install` commands
- Modify `requirements.txt` without explicit user request
- Install packages using package managers
- Suggest dependency installation commands

**Do not pin dependencies to specific versions.**

The development assistant should:
- Use flexible version specifications in `requirements.txt` (e.g., `Flask` instead of `Flask==2.3.3`)
- Allow package managers to resolve compatible versions
- Only specify version constraints when absolutely necessary for compatibility
- Let the user manage version pinning decisions

The development assistant should not:
- Pin packages to specific versions without explicit user request
- Add version constraints that may cause compatibility issues
- Over-specify dependency versions in requirements files

### Application Execution

**Never attempt to start the application.**

The development assistant should not:
- Run `python app.py` or similar startup commands
- Start Flask development servers
- Execute the application in any way
- Suggest running the application

### EXAMPLE_CODE Directory

**Files in the EXAMPLE_CODE folder are for reference only.**

The development assistant should:
- Use EXAMPLE_CODE files as reference material and examples
- Study EXAMPLE_CODE to understand implementation patterns
- Create similar functionality in the main application based on EXAMPLE_CODE examples
- Never import modules directly from the EXAMPLE_CODE directory into the main application

The development assistant should not:
- Import any modules from EXAMPLE_CODE into main application files
- Copy EXAMPLE_CODE files directly into the main application structure
- Treat EXAMPLE_CODE as part of the active codebase

### Testing Framework

**Use only Python's built-in unittest framework for testing.**

The development assistant should:
- Write tests using Python's standard `unittest` module
- Place all test files in the "tests" subfolder
- Use `unittest.TestCase` as the base class for all test classes
- Use `self.assertEqual()`, `self.assertRaises()`, etc. for assertions
- Include `if __name__ == '__main__': unittest.main()` in test files

The development assistant should NOT:
- Use pytest or any external testing frameworks
- Install pytest or pytest-related dependencies
- Write tests using pytest syntax or fixtures
- Suggest pytest installation or usage

### Environment Setup Requirements

The user should ensure:
- Python 3.12+ is available via pyenv
- Virtual environment is created and activated
- Dependencies from `requirements.txt` are installed
- Environment variables are configured via `.envrc`
- direnv is properly configured for the project

### Code Implementation Standards

**Avoid stub or placeholder functions unless explicitly requested.**

The development assistant should:
- Implement complete, functional code that works as intended
- Provide full implementations rather than incomplete stubs
- Only create placeholders when specifically instructed to do so
- Ensure all functions are ready for immediate use

The development assistant should not:
- Create empty or incomplete function stubs without explicit instruction
- Leave TODO comments in place of actual implementation
- Write functions that only contain `pass` or `raise NotImplementedError`

**Use legitimate data for functionality evaluation.**

The development assistant should:
- Create real, functional data when testing or demonstrating features
- Use actual data sources when evaluating functionality
- Generate proper test data that reflects real-world usage
- Ensure all data used in examples is valid and meaningful

The development assistant should not:
- Use random or fake data where legitimate data is required for proper evaluation
- Create placeholder data that doesn't represent real functionality
- Use mock data that doesn't demonstrate actual system capabilities
- Generate random embeddings, tokens, or other data that should be derived from real inputs

### Implementation Philosophy

**Follow the principle of "least change necessary."**

The development assistant should:
- Make only the minimal changes required to implement a feature
- Avoid over-engineering or adding unnecessary complexity
- Focus on the core functionality without extensive debugging or logging
- Implement features incrementally rather than all at once
- Remove debugging code and temporary changes after implementation is complete
- Prefer simple, direct solutions over complex abstractions

The development assistant should not:
- Add extensive debugging statements unless specifically requested
- Implement multiple features simultaneously when only one is requested
- Add unnecessary error handling or logging beyond what's essential
- Create overly complex solutions when simple ones suffice
- Leave debugging code or temporary changes in the final implementation
- Add features that weren't explicitly requested

### User Experience Standards

**Implement auto-focus for all primary input fields.**

The development assistant should:
- Automatically focus the primary input field when modals open or pages load
- Focus the chat input field when switching channels or after sending messages
- Use a centralized auto-focus system with CSS classes and mutation observers
- Apply the `auto-focus` CSS class to input fields that should receive focus
- Ensure focus behavior is consistent across all user interactions

The development assistant should not:
- Leave input fields unfocused when they should be the primary interaction point
- Implement focus behavior inconsistently across different UI components
- Use polling or inefficient methods for auto-focus implementation

### Development Workflow

1. User sets up the environment
2. User installs dependencies
3. User starts the application when needed
4. Development assistant provides code support and guidance
5. User tests and validates changes
6. User runs any tests created by assistant

---

*These rules ensure clear separation of responsibilities and prevent the development assistant from interfering with the user's environment management.*
