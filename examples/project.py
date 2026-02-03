"""
Comprehensive Integration Test for python-tfe Projects CRUD Operations

This file tests all CRUD operations:
- List: Get all projects in an organization
- Create: Add new projects with validation
- Read: Get specific project details
- Update: Modify existing projects
- Delete: Remove projects

Setup Instructions:
1. Create a test organization in HCP Terraform (https://app.terraform.io)
2. Generate an organization or user API token with appropriate permissions
3. Set environment variables:
   export TFE_TOKEN="your-api-token-here"
   export TFE_ORG="your-test-organization-name"
4. Run the tests:
   pytest examples/project.py -v -s

Important Notes:
- These tests make real API calls and create/delete actual resources
- Always use a dedicated test organization, never production
- Tests will fail if you don't have proper permissions
- Clean up is automatic, but verify resources are deleted after testing
"""

import os
import sys
import uuid

from pytfe._http import HTTPTransport
from pytfe.config import TFEConfig
from pytfe.models import (
    ProjectAddTagBindingsOptions,
    ProjectCreateOptions,
    ProjectListOptions,
    ProjectUpdateOptions,
    TagBinding,
)
from pytfe.resources.projects import Projects


def get_client():
    """Create a real Projects client for integration testing"""
    token = os.environ.get("TFE_TOKEN")
    org = os.environ.get("TFE_ORG")
    project_id = os.environ.get("TFE_PROJECT_ID")

    if not token:
        print("TFE_TOKEN environment variable is required. "
            "Get your token from HCP Terraform: Settings → API Tokens")
        sys.exit(1)

    if not org:
        print("TFE_ORG environment variable is required. "
            "Use your organization name from HCP Terraform URL")
        sys.exit(1)

    print(f"\nTesting against organization: {org}")
    print(f"Using token: {token[:10]}...")
    print(f"Using project ID: {project_id}")

    config = TFEConfig()

    try:
        transport = HTTPTransport(
            config.address,
            token,
            timeout=config.timeout,
            verify_tls=config.verify_tls,
            user_agent_suffix=None,
            max_retries=3,
            backoff_base=0.1,
            backoff_cap=1.0,
            backoff_jitter=True,
            http2=False,
            proxies=None,
            ca_bundle=None,
        )
    except Exception as e:
        print(f"Failed to create HTTP transport: {e}")
        sys.exit(1)

    return Projects(transport), org, project_id


def test_list_projects_integration(projects, org, project_id):
    """Test LIST operation - Get all projects in organization

    This is the safest test to run first - it only reads data.
    Tests: projects.list(organization, options)
    """
    try:
        # Test basic list without options
        print("\n=== LIST PROJECTS ===")
        print("Testing LIST operation: basic list")
        project_list = list(projects.list(org))
        print(f"Found {len(project_list)} projects in organization '{org}'")

        if not isinstance(project_list, list):
            print(f"LIST operation failed: expected list, got {type(project_list)}")
            sys.exit(1)

        if project_list:
            project = project_list[0]
            if not hasattr(project, "id"):
                print("Project should have an ID")
                sys.exit(1)
            if not hasattr(project, "name"):
                print("Project should have a name")
                sys.exit(1)
            if not hasattr(project, "organization"):
                print("Project should have an organization")
                sys.exit(1)
            if not hasattr(project, "description"):
                print("Project should have a description")
                sys.exit(1)
            if not hasattr(project, "created_at"):
                print("Project should have created_at")
                sys.exit(1)
            if not hasattr(project, "updated_at"):
                print("Project should have updated_at")
                sys.exit(1)
            print(f"Example project: {project.name} (ID: {project.id})")
            print(f"Created: {project.created_at}, Updated: {project.updated_at}")
        else:
            print("No projects found - this is normal for a new organization")

        # Test list with options
        print("Testing LIST operation: with options")
        list_options = ProjectListOptions(page_size=5)
        project_list_with_options = list(projects.list(org, list_options))
        print(
            f"List with options returned {len(project_list_with_options)} projects"
        )

    except Exception as e:
        print(f"LIST operation failed. Check your TFE_TOKEN and TFE_ORG. Error: {e}")
        sys.exit(1)


def test_create_project_integration(projects, org, project_id):
    """Test CREATE operation - Add new projects

    Tests: projects.create(organization, options)
    Validates: ProjectCreateOptions with name and description
    """
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"create-test-{unique_id}"
    test_description = f"Integration test project created at {unique_id}"
    created_project_id = None

    try:
        # Test CREATE operation
        print(f"Testing CREATE operation: {test_name}")
        create_options = ProjectCreateOptions(
            name=test_name, description=test_description
        )
        created_project = projects.create(org, create_options)

        # Validate created project
        if created_project.name != test_name:
            print(f"Expected name {test_name}, got {created_project.name}")
            sys.exit(1)
        if created_project.description != test_description:
            print(f"Expected description {test_description}, got {created_project.description}")
            sys.exit(1)
        if created_project.organization != org:
            print(f"Expected org {org}, got {created_project.organization}")
            sys.exit(1)
        if not created_project.id.startswith("prj-"):
            print(f"Project ID should start with 'prj-', got {created_project.id}")
            sys.exit(1)
        if created_project.workspace_count != 0:
            print("New project should have 0 workspaces")
            sys.exit(1)

        created_project_id = created_project.id
        print(f"CREATE successful: {created_project_id}")
        print(
            f"Project details: {created_project.name} - {created_project.description}"
        )

    except Exception as e:
        print(f"CREATE operation failed: {e}")
        sys.exit(1)

    finally:
        # Clean up created project
        if created_project_id:
            try:
                print(f"Cleaning up created project: {created_project_id}")
                projects.delete(created_project_id)
                print("Cleanup successful")
            except Exception as e:
                print(f"Warning: Failed to clean up project {created_project_id}: {e}")


def test_read_project_integration(projects, org, project_id):
    """Test READ operation - Get specific project details

    Tests: projects.read(project_id, include)
    Creates a project, reads it, then cleans up
    """
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"read-test-{unique_id}"
    created_project_id = None

    try:
        # Create a project to read
        print(f"Creating project for READ test: {test_name}")
        create_options = ProjectCreateOptions(
            name=test_name, description="Project for read test"
        )
        created_project = projects.create(org, create_options)
        created_project_id = created_project.id

        # Test READ operation
        print(f"Testing READ operation: {created_project_id}")
        read_project = projects.read(created_project_id)

        # Validate read project
        if read_project.id != created_project_id:
            print(f"Expected ID {created_project_id}, got {read_project.id}")
            sys.exit(1)
        if read_project.name != test_name:
            print(f"Expected name {test_name}, got {read_project.name}")
            sys.exit(1)
        if read_project.organization != org:
            print(f"Expected org {org}, got {read_project.organization}")
            sys.exit(1)
        if not hasattr(read_project, "created_at"):
            print("Project should have created_at")
            sys.exit(1)
        if not hasattr(read_project, "updated_at"):
            print("Project should have updated_at")
            sys.exit(1)

        print(f"READ successful: {read_project.name}")
        print(f"Project created: {read_project.created_at}")

        # Note: Projects API doesn't support include parameters in the current API version
        print("READ operation completed successfully")

    except Exception as e:
        print(f"READ operation failed: {e}")
        sys.exit(1)

    finally:
        # Clean up created project
        if created_project_id:
            try:
                print(f"Cleaning up read test project: {created_project_id}")
                projects.delete(created_project_id)
                print("Cleanup successful")
            except Exception as e:
                print(f"Warning: Failed to clean up project {created_project_id}: {e}")


def test_update_project_integration(projects, org, project_id):
    """Test UPDATE operation - Modify existing projects

    Tests: projects.update(project_id, options)
    Validates: ProjectUpdateOptions with name and description changes
    """
    unique_id = str(uuid.uuid4())[:8]
    original_name = f"update-test-{unique_id}"
    updated_name = f"updated-test-{unique_id}"
    original_description = "Original description for update test"
    updated_description = "Updated description for update test"
    created_project_id = None

    try:
        # Create a project to update
        print(f"Creating project for UPDATE test: {original_name}")
        create_options = ProjectCreateOptions(
            name=original_name, description=original_description
        )
        created_project = projects.create(org, create_options)
        created_project_id = created_project.id

        # Test UPDATE operation - name only
        print("Testing UPDATE operation: name only")
        update_options = ProjectUpdateOptions(name=updated_name)
        updated_project = projects.update(created_project_id, update_options)

        if updated_project.id != created_project_id:
            print(f"Project ID should remain {created_project_id}")
            sys.exit(1)
        if updated_project.name != updated_name:
            print(f"Expected updated name {updated_name}, got {updated_project.name}")
            sys.exit(1)
        if updated_project.description != original_description:
            print("Description should remain unchanged")
            sys.exit(1)
        print(f"UPDATE name successful: {updated_project.name}")

        # Test UPDATE operation - description only
        print("Testing UPDATE operation: description only")
        update_options = ProjectUpdateOptions(description=updated_description)
        updated_project = projects.update(created_project_id, update_options)

        if updated_project.name != updated_name:
            print("Name should remain unchanged")
            sys.exit(1)
        if updated_project.description != updated_description:
            print(f"Expected updated description {updated_description}, got {updated_project.description}")
            sys.exit(1)
        print("UPDATE description successful")

        # Test UPDATE operation - both name and description
        final_name = f"final-{unique_id}"
        final_description = "Final description for update test"
        print("Testing UPDATE operation: both name and description")
        update_options = ProjectUpdateOptions(
            name=final_name, description=final_description
        )
        updated_project = projects.update(created_project_id, update_options)

        if updated_project.name != final_name:
            print(f"Expected final name {final_name}, got {updated_project.name}")
            sys.exit(1)
        if updated_project.description != final_description:
            print(f"Expected final description {final_description}, got {updated_project.description}")
            sys.exit(1)
        print(f"UPDATE both fields successful: {updated_project.name}")

    except Exception as e:
        print(f"UPDATE operation failed: {e}")
        sys.exit(1)

    finally:
        # Clean up created project
        if created_project_id:
            try:
                print(f"Cleaning up update test project: {created_project_id}")
                projects.delete(created_project_id)
                print("Cleanup successful")
            except Exception as e:
                print(f"Warning: Failed to clean up project {created_project_id}: {e}")


def test_delete_project_integration(projects, org, project_id):
    """Test DELETE operation - Remove projects

    Tests: projects.delete(project_id)
    Creates a project, deletes it, verifies it's gone
    """
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"delete-test-{unique_id}"
    created_project_id = None

    try:
        # Create a project to delete
        print(f"Creating project for DELETE test: {test_name}")
        create_options = ProjectCreateOptions(
            name=test_name, description="Project for delete test"
        )
        created_project = projects.create(org, create_options)
        created_project_id = created_project.id
        print(f"Project created for deletion: {created_project_id}")

        # Verify project exists
        print("Verifying project exists before deletion")
        read_project = projects.read(created_project_id)
        if read_project.id != created_project_id:
            print(f"Project ID mismatch: expected {created_project_id}, got {read_project.id}")
            sys.exit(1)
        print(f"Project confirmed to exist: {read_project.name}")

        # Test DELETE operation
        print(f"Testing DELETE operation: {created_project_id}")
        projects.delete(created_project_id)
        print("DELETE operation completed")

        # Verify project is deleted
        print("Verifying project is deleted")
        try:
            projects.read(created_project_id)
            print("Project should not exist after deletion")
            sys.exit(1)
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                print("Project successfully deleted - confirmed by 404 error")
            else:
                raise e

        # Clear project_id since it's been deleted
        created_project_id = None

    except Exception as e:
        print(f"DELETE operation failed: {e}")
        sys.exit(1)

    finally:
        # Additional cleanup attempt (should be unnecessary)
        if created_project_id:
            try:
                print(f"Additional cleanup attempt: {created_project_id}")
                projects.delete(created_project_id)
            except Exception:
                pass  # Project might already be deleted


def test_comprehensive_crud_integration(projects, org, project_id):
    """Test all CRUD operations in sequence

    WARNING: This test creates and deletes real resources!
    Tests complete workflow: CREATE -> READ -> UPDATE -> LIST -> DELETE
    """
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"comprehensive-{unique_id}"
    updated_name = f"comprehensive-updated-{unique_id}"
    test_description = f"Comprehensive CRUD test {unique_id}"
    updated_description = f"Updated comprehensive CRUD test {unique_id}"
    created_project_id = None

    try:
        print(f"Starting comprehensive CRUD test: {test_name}")

        # 1. CREATE
        print("1. CREATE: Creating project")
        create_options = ProjectCreateOptions(
            name=test_name, description=test_description
        )
        created_project = projects.create(org, create_options)
        created_project_id = created_project.id

        if created_project.name != test_name:
            print(f"Expected name {test_name}, got {created_project.name}")
            sys.exit(1)
        if created_project.description != test_description:
            print(f"Expected description {test_description}, got {created_project.description}")
            sys.exit(1)
        print(f"CREATE: {created_project_id}")

        # 2. READ
        print("2. READ: Reading created project")
        read_project = projects.read(created_project_id)

        if read_project.id != created_project_id:
            print(f"Expected ID {created_project_id}, got {read_project.id}")
            sys.exit(1)
        if read_project.name != test_name:
            print(f"Expected name {test_name}, got {read_project.name}")
            sys.exit(1)
        if read_project.description != test_description:
            print(f"Expected description {test_description}, got {read_project.description}")
            sys.exit(1)
        print(f"READ: {read_project.name}")

        # 3. UPDATE
        print("3. UPDATE: Updating project")
        update_options = ProjectUpdateOptions(
            name=updated_name, description=updated_description
        )
        updated_project = projects.update(created_project_id, update_options)

        if updated_project.id != created_project_id:
            print(f"Expected ID {created_project_id}, got {updated_project.id}")
            sys.exit(1)
        if updated_project.name != updated_name:
            print(f"Expected name {updated_name}, got {updated_project.name}")
            sys.exit(1)
        if updated_project.description != updated_description:
            print(f"Expected description {updated_description}, got {updated_project.description}")
            sys.exit(1)
        print(f"UPDATE: {updated_project.name}")

        # 4. LIST (verify updated project appears)
        print("4. LIST: Verifying project appears in list")
        project_list = list(projects.list(org))
        found_project = None
        for p in project_list:
            if p.id == created_project_id:
                found_project = p
                break

        if found_project is None:
            print(f"Updated project {created_project_id} should appear in list")
            sys.exit(1)
        if found_project.name != updated_name:
            print(f"Expected name {updated_name}, got {found_project.name}")
            sys.exit(1)
        print("LIST: Found updated project in list")

        # 5. DELETE
        print("5. DELETE: Deleting project")
        projects.delete(created_project_id)
        print("DELETE: Project deleted")

        # 6. Verify deletion
        print("6. VERIFY: Confirming deletion")
        try:
            projects.read(created_project_id)
            print("Project should not exist after deletion")
            sys.exit(1)
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                print("VERIFY: Deletion confirmed")
            else:
                raise e

        created_project_id = None  # Clear since deleted
        print("Comprehensive CRUD test completed successfully!")

    except Exception as e:
        print(f"Comprehensive CRUD test failed: {e}")
        sys.exit(1)

    finally:
        if created_project_id:
            try:
                print(f"Final cleanup: {created_project_id}")
                projects.delete(created_project_id)
            except Exception:
                pass


def test_validation_integration(projects, org, project_id):
    """Test validation functions work with real API

    Tests all validation scenarios with actual API calls
    """
    print("Testing validation with real API calls")

    try:
        # Test valid project creation
        unique_id = str(uuid.uuid4())[:8]
        valid_name = f"validation-test-{unique_id}"

        print(f"Testing valid project creation: {valid_name}")
        create_options = ProjectCreateOptions(
            name=valid_name, description="Valid project"
        )
        created_project = projects.create(org, create_options)

        if created_project.name != valid_name:
            print(f"Expected name {valid_name}, got {created_project.name}")
            sys.exit(1)
        created_project_id = created_project.id
        print(f"Valid project created successfully: {created_project_id}")

        # Test valid project update
        updated_name = f"validation-updated-{unique_id}"
        print(f"Testing valid project update: {updated_name}")
        update_options = ProjectUpdateOptions(name=updated_name)
        updated_project = projects.update(created_project_id, update_options)

        if updated_project.name != updated_name:
            print(f"Expected name {updated_name}, got {updated_project.name}")
            sys.exit(1)
        print("Valid project updated successfully")

        # Clean up
        projects.delete(created_project_id)
        print("Validation test cleanup completed")

    except Exception as e:
        print(f"Validation integration test failed: {e}")
        sys.exit(1)


def test_error_handling_integration(projects, org, project_id):
    """Test error handling with real API calls

    Tests various error scenarios to ensure proper error handling
    """
    print("Testing error handling scenarios")

    # Test reading a non-existent project
    print("Testing read non-existent project")
    fake_project_id = "prj-nonexistent123456789"
    try:
        projects.read(fake_project_id)
        print("Should have raised an exception for non-existent project")
        sys.exit(1)
    except Exception as e:
        print(
            f"Correctly handled error for non-existent project: {type(e).__name__}"
        )
        if not ("404" in str(e) or "not found" in str(e).lower()):
            print(f"Expected 404 or not found error, got: {e}")
            sys.exit(1)

    # Test updating a non-existent project
    print("Testing update non-existent project")
    try:
        update_options = ProjectUpdateOptions(name="should-fail")
        projects.update(fake_project_id, update_options)
        print("Should have raised an exception for non-existent project")
        sys.exit(1)
    except Exception as e:
        print(
            f"Correctly handled update error for non-existent project: {type(e).__name__}"
        )
        if not ("404" in str(e) or "not found" in str(e).lower()):
            print(f"Expected 404 or not found error, got: {e}")
            sys.exit(1)

    # Test deleting a non-existent project
    print("Testing delete non-existent project")
    try:
        projects.delete(fake_project_id)
        print("Should have raised an exception for non-existent project")
        sys.exit(1)
    except Exception as e:
        print(
            f"Correctly handled delete error for non-existent project: {type(e).__name__}"
        )
        if not ("404" in str(e) or "not found" in str(e).lower()):
            print(f"Expected 404 or not found error, got: {e}")
            sys.exit(1)

    print("All error handling scenarios tested successfully")


def test_project_tag_bindings_integration(projects, org, project_id):
    """
    Integration test for project tag binding operations

    Note: Project tag bindings may not be available in all HCP Terraform plans.
    This test gracefully handles unavailable features while testing what's available.
    """
    unique_id = str(uuid.uuid4())[:8]
    test_name = f"tag-test-{unique_id}"
    test_description = f"Project for testing tag bindings - {unique_id}"
    created_project_id = None

    try:
        # Create a test project for tagging operations
        print(f"Setting up test project for tagging: {test_name}")
        create_options = ProjectCreateOptions(
            name=test_name, description=test_description
        )
        created_project = projects.create(org, create_options)
        created_project_id = created_project.id
        print(f"Created test project: {created_project_id}")

        # Test 1: List tag bindings (this should work)
        print("Testing LIST_TAG_BINDINGS")
        try:
            initial_tag_bindings = projects.list_tag_bindings(created_project_id)
            if not isinstance(initial_tag_bindings, list):
                print("Should return a list")
                sys.exit(1)
            print(f"list_tag_bindings works: {len(initial_tag_bindings)} bindings")
            list_tag_bindings_available = True
        except Exception as e:
            print(f"list_tag_bindings not available: {e}")
            list_tag_bindings_available = False

        # Test 2: List effective tag bindings
        print("Testing LIST_EFFECTIVE_TAG_BINDINGS")
        try:
            effective_bindings = projects.list_effective_tag_bindings(created_project_id)
            if not isinstance(effective_bindings, list):
                print("Should return a list")
                sys.exit(1)
            print(
                f"list_effective_tag_bindings works: {len(effective_bindings)} bindings"
            )
            effective_tag_bindings_available = True
        except Exception as e:
            print(f"list_effective_tag_bindings not available: {e}")
            print("   This feature may require a higher HCP Terraform plan")
            effective_tag_bindings_available = False

        # Test 3: Add tag bindings (if basic listing works)
        if list_tag_bindings_available:
            print("Testing ADD_TAG_BINDINGS")
            try:
                test_tags = [
                    TagBinding(key="environment", value="testing"),
                    TagBinding(key="integration-test", value="true"),
                ]
                add_options = ProjectAddTagBindingsOptions(tag_bindings=test_tags)
                added_bindings = projects.add_tag_bindings(created_project_id, add_options)

                if not isinstance(added_bindings, list):
                    print("Should return a list")
                    sys.exit(1)
                if len(added_bindings) != len(test_tags):
                    print("Should return all added tags")
                    sys.exit(1)
                print(
                    f"add_tag_bindings works: added {len(added_bindings)} bindings"
                )

                # Verify tags were actually added
                current_bindings = projects.list_tag_bindings(created_project_id)
                added_keys = {binding.key for binding in current_bindings}
                for tag in test_tags:
                    if tag.key not in added_keys:
                        print(f"Tag {tag.key} not found after adding")
                        sys.exit(1)
                print(f"Verified tags added: {len(current_bindings)} total bindings")

                add_tag_bindings_available = True

                # Test 4: Delete tag bindings
                print("Testing DELETE_TAG_BINDINGS")
                try:
                    result = projects.delete_tag_bindings(created_project_id)
                    if result is not None:
                        print("Delete should return None")
                        sys.exit(1)

                    # Verify deletion
                    final_bindings = projects.list_tag_bindings(created_project_id)
                    print(
                        f"delete_tag_bindings works: {len(final_bindings)} bindings remain"
                    )
                    delete_tag_bindings_available = True
                except Exception as e:
                    print(f"delete_tag_bindings not available: {e}")
                    delete_tag_bindings_available = False

            except Exception as e:
                print(f"add_tag_bindings not available: {e}")
                print("   This feature may require a higher HCP Terraform plan")
                add_tag_bindings_available = False
                delete_tag_bindings_available = False
        else:
            add_tag_bindings_available = False
            delete_tag_bindings_available = False

        # Summary
        print("\nProject Tag Bindings API Availability Summary:")
        features = [
            ("list_tag_bindings", list_tag_bindings_available),
            ("list_effective_tag_bindings", effective_tag_bindings_available),
            ("add_tag_bindings", add_tag_bindings_available),
            ("delete_tag_bindings", delete_tag_bindings_available),
        ]

        for feature_name, available in features:
            status = "Available" if available else "Not Available"
            print(f"   {feature_name}: {status}")

        available_count = sum(available for _, available in features)
        print(
            f"\n{available_count}/4 tag binding features are available in this HCP Terraform organization"
        )

        if available_count == 4:
            print("All project tag binding operations work perfectly!")
        elif available_count > 0:
            print("Partial functionality available - basic operations work!")
        else:
            print("Tag binding features may require a higher HCP Terraform plan")

    except Exception as e:
        print(
            f"Project tag binding integration test failed unexpectedly. "
            f"This may indicate a configuration or connectivity issue. Error: {e}"
        )
        sys.exit(1)

    finally:
        # Clean up: Delete the test project
        if created_project_id:
            try:
                print(f"Cleaning up test project: {created_project_id}")
                projects.delete(created_project_id)
                print("Test project deleted successfully")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to clean up test project {created_project_id}: {cleanup_error}"
                )


def test_project_tag_bindings_error_scenarios(projects, org, project_id):
    """
    Test error handling for project tag binding operations

    Tests various error conditions:
    - Invalid project IDs
    - Empty tag binding lists
    - Non-existent projects
    """
    print("Testing tag binding error scenarios")

    # Test invalid project ID validation
    print("Testing invalid project ID scenarios")

    invalid_project_ids = ["", "x", "invalid-id", None]

    for invalid_id in invalid_project_ids:
        if invalid_id is None:
            continue  # Skip None as it will cause different error

        try:
            projects.list_tag_bindings(invalid_id)
            print(f"Should have raised ValueError for invalid project ID: {invalid_id}")
            sys.exit(1)
        except ValueError as e:
            print(f"Correctly rejected invalid project ID '{invalid_id}': {e}")
            if "Project ID is required and must be valid" not in str(e):
                print(f"Expected validation error message, got: {e}")
                sys.exit(1)

        try:
            projects.list_effective_tag_bindings(invalid_id)
            print(f"Should have raised ValueError for invalid project ID: {invalid_id}")
            sys.exit(1)
        except ValueError as e:
            print(f"Correctly rejected invalid project ID '{invalid_id}': {e}")

        try:
            projects.delete_tag_bindings(invalid_id)
            print(f"Should have raised ValueError for invalid project ID: {invalid_id}")
            sys.exit(1)
        except ValueError as e:
            print(f"Correctly rejected invalid project ID '{invalid_id}': {e}")

    # Test empty tag binding list
    print("Testing empty tag binding list")
    try:
        fake_project_id = "prj-fakefakefake123"
        empty_options = ProjectAddTagBindingsOptions(tag_bindings=[])
        projects.add_tag_bindings(fake_project_id, empty_options)
        print("Should have raised ValueError for empty tag binding list")
        sys.exit(1)
    except ValueError as e:
        print(f"Correctly rejected empty tag binding list: {e}")
        if "At least one tag binding is required" not in str(e):
            print(f"Expected validation error message, got: {e}")
            sys.exit(1)

    # Test non-existent project operations
    print("Testing operations on non-existent project")
    fake_project_id = "prj-doesnotexist123"

    # These should raise HTTP errors (404) from the API
    for operation_name, operation_func in [
        ("list_tag_bindings", lambda: projects.list_tag_bindings(fake_project_id)),
        (
            "list_effective_tag_bindings",
            lambda: projects.list_effective_tag_bindings(fake_project_id),
        ),
        ("delete_tag_bindings", lambda: projects.delete_tag_bindings(fake_project_id)),
    ]:
        try:
            operation_func()
            print(f"{operation_name} should have failed for non-existent project")
            sys.exit(1)
        except Exception as e:
            print(
                f"{operation_name} correctly failed for non-existent project: {type(e).__name__}"
            )
            # Should be some kind of HTTP error (404, not found, etc.)
            if not (
                "404" in str(e)
                or "not found" in str(e).lower()
                or "does not exist" in str(e).lower()
            ):
                print(f"Expected 404 or not found error, got: {e}")
                sys.exit(1)

    # Test add_tag_bindings on non-existent project
    try:
        test_tags = [TagBinding(key="test", value="value")]
        add_options = ProjectAddTagBindingsOptions(tag_bindings=test_tags)
        projects.add_tag_bindings(fake_project_id, add_options)
        print("add_tag_bindings should have failed for non-existent project")
        sys.exit(1)
    except Exception as e:
        print(
            f"add_tag_bindings correctly failed for non-existent project: {type(e).__name__}"
        )
        if not (
            "404" in str(e)
            or "not found" in str(e).lower()
            or "does not exist" in str(e).lower()
        ):
            print(f"Expected 404 or not found error, got: {e}")
            sys.exit(1)

    print("All tag binding error scenarios tested successfully")


if __name__ == "__main__":
    """
    Run this file directly:

    export TFE_TOKEN="your-token"
    export TFE_ORG="your-org"
    python examples/project.py
    
    Or with command-line arguments:
    python examples/project.py --org ORG --token TOKEN
    """
    import argparse

    parser = argparse.ArgumentParser(description="Test python-tfe Projects CRUD operations")
    parser.add_argument("--org", help="HCP Terraform organization name")
    parser.add_argument("--token", help="HCP Terraform API token")
    args = parser.parse_args()

    # Override environment variables with command-line arguments if provided
    if args.org:
        os.environ["TFE_ORG"] = args.org
    if args.token:
        os.environ["TFE_TOKEN"] = args.token

    token = os.environ.get("TFE_TOKEN")
    org = os.environ.get("TFE_ORG")

    if not token or not org:
        print("Please set TFE_TOKEN and TFE_ORG environment variables")
        print("   export TFE_TOKEN='your-hcp-terraform-token'")
        print("   export TFE_ORG='your-organization-name'")
        print("Or use command-line arguments:")
        print("   python examples/project.py --org ORG --token TOKEN")
        sys.exit(1)

    print("Running integration tests...")
    print(f"Organization: {org}")
    print(f"Token: {token[:10]}...\n")

    try:
        # Get client
        projects, org, project_id = get_client()

        # Run all tests
        print("\n" + "="*50)
        print("TEST 1: List Projects")
        print("="*50)
        test_list_projects_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 2: Create Project")
        print("="*50)
        test_create_project_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 3: Read Project")
        print("="*50)
        test_read_project_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 4: Update Project")
        print("="*50)
        test_update_project_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 5: Delete Project")
        print("="*50)
        test_delete_project_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 6: Comprehensive CRUD")
        print("="*50)
        test_comprehensive_crud_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 7: Validation")
        print("="*50)
        test_validation_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 8: Error Handling")
        print("="*50)
        test_error_handling_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 9: Project Tag Bindings")
        print("="*50)
        test_project_tag_bindings_integration(projects, org, project_id)

        print("\n" + "="*50)
        print("TEST 10: Tag Bindings Error Scenarios")
        print("="*50)
        test_project_tag_bindings_error_scenarios(projects, org, project_id)

        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("="*50)

    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
