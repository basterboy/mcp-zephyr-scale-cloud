# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-01-19

### 📚 Documentation Enhancement
- **Added comprehensive Table of Contents** - Full navigation with clickable anchor links for easy README navigation
- **Streamlined installation guide** - Focused on modern pipx approach with cross-platform support (macOS/Windows/Linux)
- **Added Poetry installation alternative** - Support for Poetry-based dependency management
- **Updated troubleshooting section** - Aligned with new installation methods, added pipx PATH resolution
- **Added architecture diagram** - Visual representation of MCP server architecture
- **Fixed all TOC anchor links** - Resolved GitHub markdown anchor generation issues with emoji headers

### 🔧 Installation Improvements
- **pipx as primary installation method** - Isolated package installation preventing conflicts
- **Cross-platform pipx setup** - Instructions for Homebrew, apt, scoop, and pip installation
- **Poetry workflow support** - Both project-level and global Poetry installation options
- **Enhanced PATH troubleshooting** - Specific solutions for pipx ensurepath issues

## [0.1.5] - 2025-09-05

### 📚 Documentation Overhaul
- **Comprehensive README restructure** - Complete reorganization for better user experience
- **Added Cursor integration guide** - Step-by-step setup instructions with configuration examples
- **Added Zephyr API token guide** - Detailed instructions for obtaining API tokens from JIRA
- **Added API overview section** - Comprehensive explanation of Zephyr Scale Cloud API capabilities
- **Improved installation section** - Reordered options with PyPI as primary recommendation
- **Enhanced configuration documentation** - Better organization of environment variables and options
- **Removed redundant sections** - Eliminated duplicate installation and configuration blocks
- **Streamlined content flow** - Logical progression from installation to usage

### 🔧 Technical Improvements  
- **Fixed PyPI publishing workflow** - Replaced deprecated `poetry publish --no-build` with `twine upload`
- **Updated GitHub Actions** - Migrated to latest artifact actions (v4) for better reliability

## [0.1.4] - 2025-09-05

### 🔧 Fixed
- Fixed PyPI publishing workflow - replaced deprecated `poetry publish --no-build` with `twine upload`
- Improved PyPI publishing reliability using standard twine approach

## [0.1.3] - 2025-09-05

### 🔧 Fixed
- Updated GitHub Actions workflow to use newer artifact actions (v4)
- Fixed deprecated actions/upload-artifact@v3 and actions/download-artifact@v3
- Updated actions/cache to v4

## [0.1.2] - 2025-09-05

### 🔧 Fixed
- Fixed GitHub Actions workflow syntax error
- Resolved PyPI publishing job configuration
- Temporarily disabled PyPI publishing until secrets are configured

## [0.1.1] - 2025-09-05

### 🔧 Fixed
- Fixed GitHub release workflow to properly include Python package files (.whl and .tar.gz)
- Added comprehensive installation instructions to README
- Improved release automation with better file handling

### 📚 Documentation
- Added multiple installation options (GitHub releases, PyPI, source)
- Added installation verification instructions
- Updated Quick Start guide

## [0.1.0] - 2025-09-05

### 🎉 Initial Release

This is the first release of the MCP Zephyr Scale Cloud server, providing comprehensive test management capabilities through the Model Context Protocol.

### ✨ Features

#### **🩺 API Health & Connectivity**
- Healthcheck tool for API connectivity and authentication verification

#### **⭐ Priority Management (4 tools)**
- `get_priorities` - Retrieve all priorities with project filtering
- `get_priority` - Get specific priority details by ID
- `create_priority` - Create new priorities with metadata
- `update_priority` - Update existing priority configurations

#### **📊 Status Management (4 tools)**
- `get_statuses` - Retrieve statuses with type and project filtering
- `get_status` - Get specific status details by ID
- `create_status` - Create new statuses with type specification
- `update_status` - Update existing status configurations

#### **📁 Folder Management (3 tools)**
- `get_folders` - Retrieve folders with type and project filtering
- `get_folder` - Get specific folder details by ID
- `create_folder` - Create hierarchical folder structures

#### **📋 Test Case Management (7 tools)**
- `get_test_case` - Get detailed test case information
- `get_test_cases` - Retrieve test cases with advanced pagination
- `create_test_case` - Create comprehensive test cases
- `update_test_case` - Update test cases with validation
- `get_test_case_versions` - Access version history
- `get_test_case_version` - Get specific test case versions
- `get_links` - Retrieve test case links

#### **📝 Test Steps & Scripts (4 tools)**
- `get_test_steps` - Retrieve test steps with pagination
- `create_test_steps` - Create test steps (APPEND/OVERWRITE modes)
- `get_test_script` - Retrieve test scripts
- `create_test_script` - Create/update scripts (plain text/BDD)

#### **🔗 Test Case Links (2 tools)**
- `create_issue_link` - Link test cases to Jira issues
- `create_web_link` - Add web links to test cases

### 🔧 Technical Features

#### **Architecture & Framework**
- Model Context Protocol (MCP) server implementation
- Schema-based HTTP client with type safety
- Comprehensive Pydantic data validation
- Advanced server lifespan management
- Structured logging with configurable levels

#### **Pagination & Performance**
- Stable offset-based pagination (switched from unreliable NextGen)
- Performance optimizations with max_results=1000 recommendations
- Comprehensive pagination guidance for AI assistants
- Environment variable fallback for project keys

#### **Data Validation & Error Handling**
- Type-safe API interactions with Pydantic schemas
- Comprehensive input validation with helpful error messages
- Graceful error handling with detailed feedback
- API response validation and schema enforcement

#### **Testing & Quality**
- **209 passing tests** with comprehensive coverage
- Unit tests for individual components
- Integration tests for end-to-end functionality
- Schema validation tests
- CI/CD pipeline with multiple Python versions (3.10-3.13)
- Code quality tools: Black, Ruff, isort, mypy

### 📦 Package Information

- **Total Tools**: 25 MCP tools for complete test management
- **Python Support**: 3.10, 3.11, 3.12, 3.13
- **Dependencies**: MCP 1.0+, httpx, Pydantic 2.11+, python-dotenv
- **License**: MIT License
- **Development Status**: Alpha (stable API, comprehensive features)

### 🚀 Getting Started

```bash
# Install the package
pip install mcp-zephyr-scale-cloud

# Or with Poetry
poetry add mcp-zephyr-scale-cloud

# Set up environment
cp env.template .env
# Edit .env with your Zephyr Scale API token

# Run the server
mcp-zephyr-scale-cloud
```

### 📚 Documentation

- Complete README with usage examples
- Comprehensive API tool documentation
- Environment variable configuration guide
- Performance optimization tips
- Architecture and project structure overview

### 🎯 What's Next

See the [README.md](README.md) for planned features including Test Cycles, Test Executions, Test Plans, Environments, and Automation Integration.

---

**Full Changelog**: https://github.com/basterboy/mcp-zephyr-scale-cloud/commits/v0.1.0
