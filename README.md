## Changelog:

### 0.2.11 (2025-07-16)
- Added full config info to model initialization (lightning run script)
- Added model adjust option (lightning run script)

### 0.2.9 (2025-07-15)
- Minor changes to lightning run script that matches the delay-neural-operator code


### 0.2.8 (2025-07-14)
- Major (breaking) change: Removed OmegaConf dependency except for `MISSING` value
- Added toml save support for configuration files
- TODO: add toml load support

### 0.2.6 (2025-07-13)
- Major (breaking) change: Refactor-in-progress to use `dataclasses` for better performance and readability
- Major (breaking) change: Ignoring cluster-job-deployment; this will be reintroduced in a future release
- TODO: add support for schema validation

### 0.1.0 (2025-01-01)
- Initial release with slow, dictionary-to-class parsing
- Note-to-self: older qg package releases need to be pinned to this version for compatibility