---
paths:
  - "infra/**/*.tf"
---

## Terraform

Terraform code is very important because it controls production systems. For this reason, it's critical that agents should never:

1. Modify production systems using CLI tools for cloud providers such as `gcloud`, `az`, etc unless explicitly asked
2. Be able to run terraform directly via `tofu apply`. Terraform must be designed to run only via `just apply`.
3. Justfile execution must be guarded against agent execution using `is-ai-agent`.

Instructions when writing terraform:

- Implement the requested behavior directly. Add a boolean, feature flag, or optional setting only when I explicitly request configurability or the feature needs to support multiple modes.
  If quota, permissions, or cost block deployment, report the blocker and use the existing plan and apply workflow. Don’t add a toggle as a precaution.
- All "bootstrap" secrets (i.e. vars required to run the terraform code) should be `export`ed in the Justfile. The Justfile is guarded so agents cannot run it, ensuring that required secrets are not available to agents ensures that terraform cannot be run by an agent.
- Don't add a `locals` for a variable only used a single time
- Don't add `output` resources unless specifically asked
- Use `~> 9.9.0` style provider version pinning
- Always assume you are using or can use the latest version of a terraform module. Never workaround a missing feature that has been added to a terraform module.
- Consult the terraform MCP when using an external module. Module surfaces change often.
- When creating a cloudflare worker, always set the `compatibility_date` to the current date.
- Uppercase all `TF_VAR_*`
- Put `locals` at the top of the file
- Reference Terraform-managed resources directly; add a data source only when a verified provider limitation requires it or the resource is managed elsewhere.
- Add a one line comment at the top of each `.tf`` file describing it's purpose.
- When using submodules, do not specify provider versions in the submodule. Let the root provider configuration specify the version.
- Name Terraform resources using consistent <application_or_system>_<purpose> identifiers that communicate business ownership and function independently of cloud providers, environments, or incidental implementation details
- Always add a `description` to any `variable` block.
- If an SSH key is required for a VM, encryption, or something else I'll generate it manually in 1P and provide a UUID to reference.
- Make infrastructure configuration changes in Terraform for the operator to apply. Use cloud CLIs, ssh, APIs, 1password, etc for read-only inspection and verification. Never make infrastructure changes directly.
- Prefer pre-built, well-supported terraform modules for configuration over complicated shell scripts. By way of example, using `system_file` or `system_folder` over custom shell commands when creating files.
- Prefer `terraform_data` with `remote-exec` over `local-exec` and `ssh` commands.
- Never rewrite host headers, or any other headers, unless specifically asked to when setting up a Cloudflare Tunnel.
- Don't worry about other users on the machine reading content. You can assume the data is safe during the terraform application process.
- All 1Password references should use item uuids since they change less often than titles. However, the name of the item should be added in a comment the 1p resource. The uuid can change if the item was moved out of a vault, so the name helps us locate the uuid if this occurs.
  - 1P uuids should never be a `variable` and should always be hardcoded.
  - 1P items should always use consistent tags so it's easy to understand which items are system- vs user-created.

Prefer ephemeral reads when the provider supports them directly. Keep a sensitive data source if using an ephemeral read would require custom scripts, extra resources, manual rotation tracking, or weaker drift detection. Add a one-line comment explaining the provider limitation or operational trade-off.

Here's an example of how to structure pulling data from 1p using ephemeral resources:

```terraform file="onepassword_secrets.tf"
# Required secrets read through the 1Password provider
#
# Custom fields require a named section (provider has no root field_map).
# R2 deployment state backend credentials stay out of TF, do not include them here.

ephemeral "onepassword_item" "application_server" {
  vault = var.OP_VAULT_UID
  uuid  = "uu2mxzr32hnwtfun3viom62ggq"
}

locals {
  onepassword_secrets = {
    application_server_ip = data.onepassword_item.application_server.url
  }
}
```


Most modules should have dedicated file to store various local variables to DRY up the codebase, make sure consistent string constants are used across the project, etc:

```terraform file="locals.tf"
locals {
  base_name              = "app-name"
  base_name_alphanumeric = replace(local.base_name, "/[^a-zA-Z0-9]/", "")

  # indicate the environment explicitly to make it clear when viewing resources
  # in the cloud provider this is not a test/staging resource, and to make it
  # easy to create an entire staging environment with a simple refactor in the future
  environment = "prod"
  name        = "${local.base_name}-${local.environment}"

  # configuration to store tf state for ability for multiple devs to deploy
  tfstate = {
    # resource group should be distinct from the resource group of the deployment
    resource_group = "${local.base_name}-tfstate"
    container      = "${local.base_name}-tfstate"
    key            = "${local.environment}.tfstate"
  }
}
```

### Comments

Clear comments are critical to documenting the various design and technical decisions that went into why infrastructure was structured in a particular way. Keep these rules in mind when writing terraform comments:

- Always document magic numbers or strings with a one-line comment and a link to the doc if applicable. For example, if an IP address references a range defined in a cloud provider's documentation, link to those docs and indicate why we are using it.
- Add `# sourced from ENV` for any `variable` sourced from the ENV.
- Notice the comment block at the top of the example block above describing the purpose of the file. All files should have this.
- Not all files require a longer description, but all should at least have a single comment line describing the purpose of the file.
- If a file requires a longer comment it should use the following format:

```terraform
# configure public application uploads and their CORS policy
#
# - host images have public read access and must stay separate from private screening downloads
# - bucket names are persistent storage identifiers; changing them requires migrating their contents

locals {
  # ...
```

Note the blank `#` if a file requires a longer explanation. Prefer bullets over longer sentences. If there's just a single bullet, write it as a sentence not a bullet.

### SSH Keys

- All SSH required exist in 1Password and are available through the 1P `SSH_AUTH_SOCK`
- The `SSH_AUTH_SOCK` value is not set to 1Password by default. `ssh` parses the local SSH config, which includes the 1Password socket, but Terraform does not. This is intentional and ensures terraform is only run from the Justfile.
- All SSH keys should be generated manually in 1Password and only the public keys should be read into the ENV via a Justfile `export`.
- Private keys should never make their way into terraform deployment state
- Parse effective OpenSSH client settings with `ssh -G … | jc --ssh-conf` and read the resulting JSON fields.

### File Structure

* `mise.toml` opentofu, environment variables, and other configuration required for terraform.
* `onepassword_secrets.tf` extracts secrets from 1Password that are required to run the terraform code. Secrets should be pulled from here, and not ENV.
* `providers.tf` defines the providers to use.
* `variables.tf` defines "global" variables, including those sourced from the ENV.
* `deployment_state.tf` stores the terraform state in a remote bucket. This should only exist in the root module.
* `Justfile` contains the commands to run the terraform code. Never run it directly.
* `locals.tf` most modules should have dedicated file to store various local variables to DRY up the codebase and make sure consistent string constants are used across the project.
