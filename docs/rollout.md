# Rollout

This is sprint 8 in [alpha_build.md](alpha_build.md). Local UAT is in [uat.md](uat.md). Discovery places the API on Azure Container Apps, an empty section table on Azure Database for PostgreSQL, and the model name in Key Vault. The page extracts, the chunks, and Ollama stay on this machine. That cloud copy does not answer policy questions. It shows that the shape still fits.

UAT recorded two misses (A5 and A4/A10). This file still records the Azure attempt, as a learning step.

## What this machine already proved

The API image runs under Docker Compose. `POST /ask` on `http://localhost:8000` returns a signpost, a cited answer, or a ticket. That is the running system.

## What Azure would have held

| Azure piece | Role |
|---|---|
| Resource group | Folder for the deployment |
| Container Apps | The API image, port 8000 |
| PostgreSQL, empty `sections` | Three ids, no chunks |
| Key Vault | Model names, not page text |
| Container Registry | A place Azure can pull the image from |

PostgreSQL and a registry are the parts that bill. Key Vault is a small charge of the same kind.

## Constraint for this attempt

No bill. PostgreSQL, Key Vault, and Azure Container Registry were skipped. Docker Hub was skipped as well, so there was no public place to store the image.

The reduced path was: one resource group, one Container Apps environment with `--logs-destination none`, then one app from an image. Without an image registry, the last step could not run.

## What was done, 6 October 2026

1. `az login`
2. `az group create --name deskline-rg --location uksouth`
3. `az containerapp env create --name deskline-env --resource-group deskline-rg --location uksouth --logs-destination none`

The environment command first registered the `Microsoft.App` provider. That wait is normal. It then printed the JSON for `deskline-env`.

No API image was pushed. No Container App was created. `https://…/docs` was not opened on Azure.

## What was stopped

The resource group was deleted after that JSON, so the environment would not stay. Deleting a Container Apps environment can take 10–20 minutes. `az group show` reports `Deleting` until the group is gone. `az group exists --name deskline-rg` returning `false` means it has finished.

`az logout` ended the CLI session on this PC.

## Result

The Azure shape was started as far as a resource group and an empty Container Apps environment. The API container was not placed on Azure. Local Compose remains the place a question is answered.