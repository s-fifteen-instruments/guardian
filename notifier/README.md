`notifier` is used to notify the `watcher` service of generated keys in the epoch file volume.

This is useful in the case of testing with simulated keys (see the `qsim` service), and no other services exist to notify `watcher` to ingest these keys.
This service is generally deprecated with the current availability of other services, i.e. `csim` with the classical key generation and notifier, and `qkd` with the actual QKD software stack.

To update the dependencies:

1. Change the Dockerfile to reference the version-unbounded `requirements.txt` instead of `requirements.freeze.txt`.
   * Temporarily reassign `$TOP_DIR` to the current directory.
   * Remove the version pin on the `alpine` image, if necessary.
1. Build the image from within the `notifier` directory, i.e. `docker build -t notifier-tmp .`.
1. Run the image and print the new frozen dependencies, i.e. `docker run --rm --entrypoint "/bin/sh" notifier-tmp` then `pip freeze`.
