---
owner: bob
description: Exoscale/OpenTofu troubleshooting for the maindi infra (IP allowlists, imports, safe applies).
---

# Exoscale / OpenTofu Cheat Sheet

All commands run from `product/060_app/infra/`.

## "My connection just hangs, no error"

This is almost always an IP-allowlist problem, not a real network fault.
Exoscale's security group and the Postgres `ip_filter` both silently drop
packets from IPs they don't recognize — no rejection, just a hang until
timeout. Applies to SSH (`make ssh`) and `psql` against the database alike.

```bash
make print-ip // Show this machine's current public IPv4/32.
```

Compare that against what's actually live on the security group (not
what's in `main.tf` — the file can say one thing while the deployed
resource says another, if `apply` hasn't run recently). If it's not
allowed, add a rule for it (see "Safe partial apply" below).

### Your IP changed — regain SSH access

`administrator_cidr` auto-detects via `curl icanhazip.com` on every
`tofu.sh` invocation — nothing to edit. Just re-apply the rule:

```bash
./tofu.sh plan -target='exoscale_security_group_rule.ssh' -out=maindi.tfplan
./tofu.sh show maindi.tfplan // Confirm: 1 to add, your new IP, nothing else.
./tofu.sh apply maindi.tfplan
rm -f maindi.tfplan
```

This adds a rule for the new IP without removing the old one (it was
never imported into state either) — old-IP rules accumulate harmlessly
until TASK-0250 cleans them up. Don't add your own IP to
`additional_administrator_cidrs` — that var is for *other* fixed admin
IPs, not your own already-dynamic one.

## Database (`ip_filter`) is stricter — VM-only by default

`main.tf`'s `exoscale_dbaas.postgres` only allows the app VM's own IP to
reach Postgres. Your laptop/dev machine can't connect directly, even if
its IP is in the SSH security group. To run `psql` against it: SSH into
the VM first (`make ssh`), then run `psql` from there — Docker is already
installed on the VM even if `psql` isn't:

```bash
docker run --rm -it postgres:16 psql "<connection URI>" // psql without installing anything on the VM.
```

## `tofu import` ID formats (provider-specific, easy to get wrong)

The error message usually tells you the exact expected format — read it,
don't guess twice:

```bash
./tofu.sh import exoscale_dbaas.postgres "maindi-v1-postgres@ch-dk-2" // DBaaS: name@zone
./tofu.sh import exoscale_compute_instance.app "<uuid>@ch-dk-2" // Compute instance: uuid@zone
./tofu.sh import exoscale_security_group.app "<uuid>" // Security group: uuid only, no zone
./tofu.sh import exoscale_security_group_rule.http "<sg_uuid>@<rule_uuid>" // SG rule: sg_uuid@rule_uuid
./tofu.sh import aws_s3_bucket.audio "<bucket-name>" // S3-compatible bucket: name only
```

## Safe partial plan/apply with `-target`

Use this whenever you want to change or add *one* resource without
touching everything else `plan` would otherwise show — e.g. adding one
security-group rule without recreating others that aren't fully imported
yet.

```bash
./tofu.sh plan -target='exoscale_security_group_rule.ssh' -out=maindi.tfplan // Scope the plan to one resource.
./tofu.sh show maindi.tfplan // Review before applying — always.
./tofu.sh apply maindi.tfplan // Apply exactly what was reviewed.
rm -f maindi.tfplan // Clean up the saved plan file after.
```

`-target` on a `for_each` resource needs the specific key:

```bash
./tofu.sh plan -target='exoscale_security_group_rule.ssh_additional["1.2.3.4/32"]' // Target one for_each instance.
```

## Read every plan before applying — no exceptions

`14 to add, 0 to change` looks harmless as a summary line. The dangerous
stuff hides in the body: search for `forces replacement` before ever
running `apply` — that phrase means Terraform intends to destroy and
recreate something, which for a VM or database is not a drill.

```bash
./tofu.sh show maindi.tfplan | grep -n "forces replacement" // Empty output = safe to proceed.
```

## Missing/incomplete state

If `plan` suddenly wants to create resources that already exist live,
local state is stale or missing — don't apply. Re-import the real
resources first (see above), and once state is correct, back it up
somewhere outside this single checkout:

```bash
cp terraform/terraform.tfstate ~/.config/maindi/tfstate_backups/terraform.tfstate.$(date +%Y%m%d_%H%M%S)
chmod 600 ~/.config/maindi/tfstate_backups/*
```
