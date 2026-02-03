#!/usr/bin/env python3
"""Helper script to get workspace information for GitHub Secrets."""

import os
from pytfe import TFEClient, TFEConfig

def main():
    client = TFEClient(TFEConfig.from_env())
    org = os.getenv("TFE_ORG", "pythontfeoauthtesst")
    
    print(f"\n{'='*70}")
    print(f"Workspaces in organization: {org}")
    print(f"{'='*70}\n")
    
    try:
        workspaces = client.workspaces.list(org).data
        
        if not workspaces:
            print("⚠️  No workspaces found!")
            print("\n💡 You need to create at least one workspace in HCP Terraform:")
            print(f"   1. Go to: https://app.terraform.io/app/{org}/workspaces")
            print("   2. Click 'New workspace'")
            print("   3. Create a simple workspace (e.g., 'ci-test')")
            print("\nThen run this script again.")
            return
        
        print(f"Found {len(workspaces)} workspace(s):\n")
        
        for ws in workspaces:
            print(f"Workspace Name: {ws.attributes.name}")
            print(f"Workspace ID:   {ws.id}")
            print(f"Created:        {ws.attributes.created_at}")
            print("-" * 70)
        
        # Pick the first workspace as default
        default_ws = workspaces[0]
        
        print(f"\n{'='*70}")
        print("📋 Add these to your GitHub Secrets:")
        print(f"{'='*70}\n")
        print(f"TFE_WORKSPACE={default_ws.attributes.name}")
        print(f"TFE_WORKSPACE_ID={default_ws.id}")
        print(f"\n💡 Go to: https://github.com/KshitijaChoudhari/python-tfe/settings/secrets/actions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure TFE_TOKEN and TFE_ORG are set in your environment.")

if __name__ == "__main__":
    main()
