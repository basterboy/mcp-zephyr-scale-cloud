# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.8] - 2025-10-08

### ✨ New Features: Test Plan Management

- **Test Plan Operations** - Create and retrieve test plans with comprehensive metadata
  - `get_test_plans` - Retrieve test plans with pagination support
  - `get_test_plan` - Get detailed test plan information by key
  - `create_test_plan` - Create new test plans with metadata and organizational support

- **Test Plan Link Management** - Connect test plans to other entities
  - `create_test_plan_issue_link` - Link test plans to Jira issues
  - `create_test_plan_web_link` - Add web links to test plans (description required)
  - `create_test_plan_test_cycle_link` - Link test plans to test cycles (unique bidirectional feature)

### 📦 Schema Additions

- **TestPlanInput** - Schema for creating test plans
- **TestPlan** - Main test plan entity schema
- **TestPlanList** - Paginated response for test plan lists
- **TestPlanTestCycleLinkInput** - Schema for linking test plans to test cycles
- **TestPlanLinks** - Comprehensive link management including test cycle links
- **WebLinkInputWithMandatoryDescription** - Web link schema with required description (test plan specific)

### 🔧 API Enhancements

- **6 new HTTP client methods** - Complete test plan API integration
- **3 new validation functions** - Test plan data validation
  - `validate_test_plan_key` - Validate test plan key format (PROJ-P123)
  - `validate_test_plan_input` - Validate test plan creation data
  - `validate_test_plan_test_cycle_link_input` - Validate test plan-to-cycle link data

### 📊 Total MCP Tools

- **38 tools** (increased from 32) - Comprehensive test management capabilities
- **6 test plan tools** - Create, retrieve, and link test plans
- **32 existing tools** - Test cases, test cycles, priorities, statuses, folders, steps, scripts

### 🎯 Key Features

- **Test plan organization** - Organize test artifacts with test plans
- **Unique test cycle linking** - Bidirectional link between test plans and test cycles
- **Mandatory web link descriptions** - Enhanced documentation for test plan web links
- **Offset-based pagination** - Efficient bulk data retrieval (up to 1000 records)
- **Custom fields support** - Flexible metadata with custom fields
- **Label support** - Tag test plans for better organization

### ⚠️ API Limitations

- **No update operation** - Zephyr Scale Cloud API does not provide PUT endpoint for test plans
  - Only GET and POST operations are available for test plans

### 🧪 Testing

- **11 new schema tests** - Comprehensive test plan schema validation
- **All tests passing** - Maintained test coverage for new functionality
- **Integration tests ready** - Test plan tools ready for end-to-end testing

## [0.1.7] - 2025-10-07

### ✨ New Features: Test Cycle Management

- **Test Cycle CRUD Operations** - Complete lifecycle management for test cycles
  - `get_test_cycles` - Retrieve test cycles with pagination and filtering
  - `get_test_cycle` - Get detailed test cycle information by key
  - `create_test_cycle` - Create new test cycles with comprehensive metadata
  - `update_test_cycle` - Update existing test cycles
  - `get_test_cycle_links` - Retrieve all links for a test cycle
  - `create_test_cycle_issue_link` - Link test cycles to Jira issues
  - `create_test_cycle_web_link` - Add web links to test cycles

### 📦 Schema Additions

- **TestCycleInput** - Schema for creating test cycles
- **TestCycle** - Main test cycle entity schema
- **TestCycleList** - Paginated response for test cycle lists
- **JiraProjectVersion** - Jira version integration schema
- **TestCycleLinkList** - Schema for managing test cycle links

### 🔧 API Enhancements

- **7 new HTTP client methods** - Complete test cycle API integration
- **4 new validation functions** - Test cycle data validation
  - `validate_test_cycle_key` - Validate test cycle key format (PROJ-R123)
  - `validate_test_cycle_input` - Validate test cycle creation data
  - `validate_test_cycle_update_input` - Validate test cycle updates
  - `validate_jira_version_id` - Validate Jira project version IDs

### 📊 Total MCP Tools

- **32 tools** (increased from 25) - Comprehensive test management capabilities
- **7 test cycle tools** - Full CRUD with link management
- **25 existing tools** - Test cases, priorities, statuses, folders, steps, scripts

### 🎯 Key Features

- **Offset-based pagination** - Efficient bulk data retrieval (up to 1000 records)
- **Jira version integration** - Link test cycles to specific Jira project versions
- **Planned date support** - Track start and end dates for test cycles
- **Link management** - Connect test cycles to Jira issues and web resources
- **Custom fields support** - Flexible metadata with custom fields
- **Environment variable fallback** - Automatic project key resolution

## [0.1.6] - 2025-09-08

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
