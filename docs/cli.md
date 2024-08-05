# `limb`

**Usage**:

```console
$ limb [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `align`
* `clean-volume`
* `create-experiment`
* `extract-surface`
* `stage`
* `vis`

## `limb align`

**Usage**:

```console
$ limb align [OPTIONS] EXPERIMENT_FOLDER_PATH
```

**Arguments**:

* `EXPERIMENT_FOLDER_PATH`: Path to the experiment folder  [required]

**Options**:

* `--morph / --no-morph`: Automatically pick the isovalue for the surface  [default: no-morph]
* `--help`: Show this message and exit.

## `limb clean-volume`

**Usage**:

```console
$ limb clean-volume [OPTIONS] EXPERIMENT_FOLDER_PATH VOLUME_PATH CHANNEL_NAME
```

**Arguments**:

* `EXPERIMENT_FOLDER_PATH`: [required]
* `VOLUME_PATH`: [required]
* `CHANNEL_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `limb create-experiment`

**Usage**:

```console
$ limb create-experiment [OPTIONS] EXPERIMENT_NAME [EXPERIMENT_FOLDER_PATH]
```

**Arguments**:

* `EXPERIMENT_NAME`: [required]
* `[EXPERIMENT_FOLDER_PATH]`

**Options**:

* `--help`: Show this message and exit.

## `limb extract-surface`

**Usage**:

```console
$ limb extract-surface [OPTIONS] EXPERIMENT_FOLDER_PATH [ISOVALUE]
```

**Arguments**:

* `EXPERIMENT_FOLDER_PATH`: Path to the experiment folder  [required]
* `[ISOVALUE]`

**Options**:

* `--auto / --no-auto`: Automatically pick the isovalue for the surface  [default: no-auto]
* `--help`: Show this message and exit.

## `limb stage`

**Usage**:

```console
$ limb stage [OPTIONS] EXPERIMENT_FOLDER_PATH
```

**Arguments**:

* `EXPERIMENT_FOLDER_PATH`: Path to the experiment folder  [required]

**Options**:

* `--help`: Show this message and exit.

## `limb vis`

**Usage**:

```console
$ limb vis [OPTIONS] ALGORITHM:{isosurfaces|raycast|slab|slices|probe} EXPERIMENT_FOLDER_PATH CHANNELS...
```

**Arguments**:

* `ALGORITHM:{isosurfaces|raycast|slab|slices|probe}`: [required]
* `EXPERIMENT_FOLDER_PATH`: [required]
* `CHANNELS...`: [required]

**Options**:

* `--help`: Show this message and exit.
