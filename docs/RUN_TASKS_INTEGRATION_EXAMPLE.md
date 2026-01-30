# Run Tasks Integration Example - Explanation

## What is `examples/run_tasks_integration.py`?

It's a **webhook server** that integrates with Terraform Cloud/Enterprise (TFC/TFE) run tasks. This is NOT a test file - it's a fully functional example server that you can deploy and customize.

---

## How It Works: The Complete Flow

### Step 1: You Start the Server
```bash
python examples/run_tasks_integration.py --port 8888
```

The server starts and waits for incoming webhooks from TFC/TFE.

### Step 2: Configure in TFC/TFE
You configure a run task in TFC/TFE pointing to your server:
- **URL**: `http://your-server:8888`
- **Stage**: When to run (pre-plan, post-plan, pre-apply, post-apply)
- **Enforcement**: Advisory (warn) or Mandatory (block)

### Step 3: Someone Triggers a Terraform Run
When a user clicks "Start Run" in TFC/TFE or pushes code:

```
User triggers run
    ↓
TFC/TFE prepares the run
    ↓
TFC/TFE sends webhook → http://your-server:8888
```

### Step 4: Your Server Receives the Webhook
The webhook payload contains:
```json
{
  "run_id": "run-abc123",
  "workspace_name": "prod-app",
  "organization_name": "my-company",
  "stage": "pre_plan",
  "access_token": "secret-token",
  "task_result_callback_url": "https://app.terraform.io/api/v2/task-results/xyz",
  ...
}
```

### Step 5: Your Server Processes It
```python
# Parse the incoming webhook
request = RunTaskRequest.model_validate(payload)

# YOUR CUSTOM VALIDATION LOGIC HERE
# Examples:
# - Check if resources have required tags
# - Validate naming conventions
# - Run security scans (Checkov, tfsec, etc.)
# - Check cost estimates
# - Verify compliance policies
# - Check for sensitive data in configs

result_status = "passed"  # or "failed"
result_message = "All checks passed!"
```

### Step 6: Your Server Sends Results Back
```python
client.run_tasks_integration.callback(
    callback_url=request.task_result_callback_url,
    access_token=request.access_token,
    options=TaskResultCallbackOptions(
        status="passed",  # or "failed"
        message="All checks passed!",
        url="https://your-dashboard.com/results",
        outcomes=[
            TaskResultOutcome(
                outcome_id="check-1",
                description="Security scan passed",
                body="No vulnerabilities found",
                tags={
                    "Status": [TaskResultTag(label="Passed", level="info")],
                    "Severity": [TaskResultTag(label="Low")]
                }
            )
        ]
    )
)
```

### Step 7: TFC/TFE Receives and Displays Results
In the TFC/TFE UI, users see:
- **Run Task Status**: Passed or Failed
- **Message**: Your custom message
- **Outcomes**: Detailed results with tags
- **Link**: To your detailed results page

If mandatory and failed → Run is blocked
If advisory and failed → Run continues with warning

---

## Real-World Use Cases

### Example 1: Cost Control
```python
# Check estimated costs
if estimated_cost > 10000:
    result_status = "failed"
    result_message = f"Cost ${estimated_cost} exceeds budget limit"
```

### Example 2: Production Safety
```python
# Require approval for production
if request.workspace_name.startswith("prod-"):
    result_status = "failed"
    result_message = "Production changes require manual approval"
```

### Example 3: Security Scanning
```python
# Run Checkov security scan
scan_results = run_checkov(request.configuration_version_download_url)
if scan_results.has_critical_issues:
    result_status = "failed"
    result_message = f"Found {len(scan_results.critical)} critical security issues"
```

### Example 4: Tagging Enforcement
```python
# Check if all resources have required tags
if not all_resources_have_tags(config, required_tags=["owner", "project"]):
    result_status = "failed"
    result_message = "All resources must have 'owner' and 'project' tags"
```

### Example 5: Compliance Checking
```python
# Check against compliance policies
if not meets_compliance_standards(config):
    result_status = "failed"
    result_message = "Configuration violates compliance policy XYZ-123"
```

---

## What the Example Demonstrates

The example file shows you how to:

- **Receive webhooks** from TFC/TFE using a simple HTTP server
- **Parse `RunTaskRequest`** - the webhook payload from TFC/TFE
- **Access run information** - workspace, organization, stage, run ID
- **Add custom validation logic** - where you insert your checks
- **Create detailed outcomes** - with descriptions, tags, and links
- **Send results back** - using the `callback()` method
- **Handle errors gracefully** - proper error handling and responses

---

## Why This Example is Important

### Without Run Tasks Integration:
- Manual code reviews for every change
- Inconsistent policy enforcement
- Security issues discovered after deployment
- Cost overruns without warnings

### With Run Tasks Integration:
- Automated validation before apply
- Consistent policy enforcement
- Security issues caught early
- Cost controls built into workflow
- Detailed audit trail
- Custom business logic enforcement

---

## How to Use This Example

### 1. Basic Usage (Local Testing)
```bash
# Start the server
python examples/run_tasks_integration.py --port 8888

# In another terminal, test with mock data
python test_run_tasks_local.py
```

### 2. Deploy to Cloud (Real Usage)
```bash
# On your cloud server (EC2, Azure, GCP, etc.)
python examples/run_tasks_integration.py --port 8888

# Configure in TFC/TFE:
# URL: http://your-server-ip:8888
```

### 3. Customize the Logic
Edit the example file around line 54-67:
```python
# Replace this section with your custom checks
# Example: Check workspace naming
if not request.workspace_name.startswith(("dev-", "prod-", "staging-")):
    result_status = "failed"
    result_message = "Workspace must be prefixed with dev-, prod-, or staging-"
```

---

## Key Components Used

### 1. `RunTaskRequest`
Parses the incoming webhook from TFC/TFE:
- `run_id` - The Terraform run ID
- `workspace_name` - Which workspace
- `organization_name` - Which organization
- `stage` - When it's running (pre-plan, post-plan, etc.)
- `access_token` - Token for sending callback
- `task_result_callback_url` - Where to send results

### 2. `TaskResultCallbackOptions`
Defines the result to send back:
- `status` - "passed", "failed", "running"
- `message` - Short summary
- `url` - Link to detailed results (optional)
- `outcomes` - Detailed results list (optional)

### 3. `TaskResultOutcome`
Individual check result:
- `outcome_id` - Unique identifier
- `description` - What was checked
- `body` - Detailed explanation
- `url` - Link to more info
- `tags` - Categorization (Status, Severity, etc.)

### 4. `TaskResultTag`
Tag for categorization:
- `label` - Tag name (e.g., "Critical", "Passed")
- `level` - Severity (e.g., "error", "warning", "info")

### 5. `run_tasks_integration.callback()`
Sends results back to TFC/TFE:
- Uses the callback URL from the webhook
- Authenticates with the access token
- Sends structured result data

---

## Testing Strategy

### Level 1: Unit Tests
```bash
pytest tests/units/test_run_tasks_integration.py
```
Tests parsing and validation logic.

### Level 2: Local Integration
```bash
python test_run_tasks_local.py
```
Simulates complete flow with mock TFC/TFE server.

### Level 3: Cloud Deployment
Deploy to EC2/cloud and test with real webhooks.

### Level 4: Real HCP Terraform
Configure in actual TFC/TFE and trigger real runs.

---

## Summary

**What it is**: A working webhook server that integrates with TFC/TFE run tasks

**What it does**: Receives run information, validates it, sends results back

**Why it's important**: Enables automated policy enforcement and custom validation

**How to use it**: Deploy the server, configure in TFC/TFE, customize the validation logic

**Not a test**: It's a functional example you can deploy and use in production!

---

## Next Steps

1. Review the example code
2. Test locally with `test_run_tasks_local.py`
3. Customize validation logic for your needs
4. Deploy to cloud server
5. Configure in TFC/TFE
6. Monitor and iterate

**The example gives you everything you need to build your own run tasks integration!**
