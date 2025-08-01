## Changelog:
- See next-to-top version for stable release (latest is always WIP/unstable)

### 0.2.20 (2025-08-01)
- Add copy function for models

### 0.2.17 (2025-07-17)
- Add load from file for models

### 0.2.15 (2025-07-16)
- Changed GPUs to only include "free" GPUs; temporarily available due to cluster.
- Added missing pynvml dependency
- Added memory limit for GPU selection

### 0.2.12 (2025-07-16)
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