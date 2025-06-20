(sec:configuration)=

# Configuration

The behavior of several components (such as {py:class}`~secbench.api.Bench` can
be changed at runtime thanks to either [toml](https://toml.io/en/)
configuration files or environment variables.

The environment variable `SECBENCH_USER_CONFIG` can point to a list of colon
separated paths to `.toml` configuration files.  The first entry in the
environment takes configuration over the others.

For example let's say you have:

```console
$ export SECBENCH_USER_CONFIG="a.toml:/home/user_a/b.to_ml"`
```
Then, configuration values will be first in file "a.toml"

## Rules

To summarize, for a given configuration key (e.g., `discovery.verbose`), the
value will be searched in the following order:
- Environment variable (if supported)
- Entry `<<hostname>>.discovery.verbose` in configuration files.
- Entry `discovery.verbose`

## List of Supported Options

In this section, we list the configuration options supported in *Secbench*.

(tab:secbench-config)=

:::{table} List of Secbench Configuration options
| Configuration Key | Environment Variable | Description |
|-------------------|----------------------|-------------|
|  | `SECBENCH_USER_CONFIG`  | List of colon separated `.toml` files to load |
| `discovery.verbose` | `SECBENCH_DISCOVERY_VERBOSE`  | Makes the device discovery more verbose (default: "false") |
| `scopenet`        | `SECBENCH_SCOPENET`  | IP address range where to look for scopes (e.g., "192.168.1.0/26") |
| `scanners.vxi11.scan_timeout`        |   | Timeout in seconds applied for scanning devices through network (default: 0.01) |
| `scanners.vxi11.scan_verbose`        |   | Lists devices found on the network during discovery |
| `scanners.pyvisa.backend` | `SECBENCH_SCANNERS_PYVISA_BACKEND` | Which backend is used for `pyvisa` |
:::
