"""
Simple Project Integration Test - Read existing project

This script tests reading an existing project using TFE_PROJECT_ID environment variable.

Setup:
1. Set environment variables:
   export TFE_TOKEN="your-api-token"
   export TFE_ORG="your-organization"
   export TFE_PROJECT_ID="prj-xxxxx"  # Your existing project ID

2. Run: python project_simple.py
"""

import os
import sys

from pytfe._http import HTTPTransport
from pytfe.config import TFEConfig
from pytfe.resources.projects import Projects


def main():
    # Get environment variables
    token = os.environ.get("TFE_TOKEN")
    org = os.environ.get("TFE_ORG")
    project_id = os.environ.get("TFE_PROJECT_ID")

    if not token:
        print("Error: TFE_TOKEN environment variable not set")
        sys.exit(1)
    if not org:
        print("Error: TFE_ORG environment variable not set")
        sys.exit(1)
    if not project_id:
        print("Error: TFE_PROJECT_ID environment variable not set")
        sys.exit(1)

    print(f"\nTesting against organization: {org}")
    print(f"Using token: {token[:10]}...")
    print(f"Using project ID: {project_id}")

    # Create client
    config = TFEConfig()
    try:
        transport = HTTPTransport(
            config.address,
            token,
            timeout=config.timeout,
            verify_tls=config.verify_tls,
        )
        projects = Projects(transport)
    except Exception as e:
        print(f"Failed to create HTTP transport: {e}")
        sys.exit(1)

    # Test LIST operation
    print("\n=== LIST PROJECTS ===")
    try:
        project_list = list(projects.list(org))
        print(f"Found {len(project_list)} projects in organization '{org}'")
        
        for proj in project_list:
            print(f"  - {proj.name} (ID: {proj.id})")
            if proj.id == project_id:
                print(f"    ^ This is our test project!")
    except Exception as e:
        print(f"LIST operation failed: {e}")
        sys.exit(1)

    # Test READ operation
    print(f"\n=== READ PROJECT {project_id} ===")
    try:
        project = projects.read(project_id)
        print(f"Project Name: {project.name}")
        print(f"Project ID: {project.id}")
        print(f"Description: {project.description or 'None'}")
        print(f"Organization: {project.organization}")
        print(f"Workspace Count: {project.workspace_count}")
        print("READ operation successful")
    except Exception as e:
        print(f"READ operation failed: {e}")
        sys.exit(1)

    print("\n=== All Tests Passed ===")


if __name__ == "__main__":
    main()
