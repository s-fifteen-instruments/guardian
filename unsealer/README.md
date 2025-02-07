'unsealer' currently depends on a base alpine package, that in turn installs docker.
This allows the unsealing script to monitor the health of the vault via the Docker API, and preemptively unseal the vault upon start/restart.

However, Alpine packages are **not** guaranteed to be maintained indefinitely, and may be dropped/superseded over its lifetime [1]. This also means its packages, and hence the corresponding python dependencies, cannot be reliably pinned.

The 'requirements.freeze.txt' should be updated anyway to reflect the last observed successful build and deploy. These frozen requirements should not be directly used, until the version pinning issue is resolved.

[1]: <https://gitlab.alpinelinux.org/alpine/abuild/-/issues/9996#note_87135>
