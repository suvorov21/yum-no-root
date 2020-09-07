# Tool for non-root installation of packages with yum

## Requirements

Python3 > 3.6
Click - can be installed with `python3 -m pip install -r requirements.txt`

## Usage

Set of packages to install should be set in `packages_ini` var.

```bash
python3 install.py --prefix=/path/to/package/extraction/target/ --rpm_path=/path/to/store/rpms/
```
To enable the setup
```bash
source /path/to/package/extraction/target/enable.sh
```

To enable rh opt tools, e.g. devtools:
```bash
source /path/to/package/extraction/target/opt/rh/devtoolset-9/enable
```

## Logic

- `repoquery -R --resolve --recursive` to resolve all the dependencies
- `yumdownloader --destdir rpm_path` to download all rpms
- `rpm2cpio rpm_path/package.rpm | cpio -idmv` -- to extract the packages
- create enable.sh and cast default `enable` from absolute paths to prefix

The packages are unpacked into the tmp folder and then moved to `prefix` in order to solve the access rights issues as for some packages change the folder access rights to 'read only'.

## Disclaimer

The installation _may be_ corrupted as installation of basic packages not into the root path is not recommended. The best option is to ask admin to install all the packs you need. However, I successfully used this tool at various CentOS clusters to install all the packs I need with no further issues.