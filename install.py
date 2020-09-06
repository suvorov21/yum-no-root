import subprocess
import os

RPM_PATH = '/t2k/users/suvorov/rpm_v2/'
PREFIX = '/t2k/users/suvorov/centos_v2/'

def resolve(packages):
    """Scan for all possible dependencies."""
    rpms = packages
    for pack in rpms:
        result = subprocess.run(['repoquery', '-R', '--resolve',
                                 '--recursive', pack, "/dev/null"],
                                check=True, stdout=subprocess.PIPE
                                )
        lines = result.stdout.split(b'\n')
        for line in lines:
            line = line.decode("utf-8")
            if line != '':
                print(line)
                packages = packages | {line}

    return packages

def download(packages):
    """Download rpms."""
    for pack in packages:
        result = subprocess.run(['yumdownloader', '--resolve', pack],
                                check=True, stdout=subprocess.PIPE
                               )
        print(result.stdout.decode("utf-8"))

def install(run=False):
    """Install the rpms to the PREFIX."""
    os.chdir(PREFIX)
    subprocess.run(['mkdir', '-p', 'tmp_install'], check=False)
    with open('install.sh', 'w') as w_file:
        w_file.write('cd tmp_install\n')
        for file in os.listdir(RPM_PATH):
            if file.endswith('.rpm'):
                w_file.write(f'echo "Working on {file}"\n')
                w_file.write(f'rpm2cpio {RPM_PATH+file} | cpio -idmv\n')
                w_file.write('chmod -R 765 ./*\n')
                w_file.write(f'cp -r {PREFIX}/tmp_install/* {PREFIX}\n')
                w_file.write(f'rm -rf {PREFIX}/tmp_install/*\n')
    if run:
        res = subprocess.Popen("source install.sh",
                               shell=True,
                               executable="/bin/bash"
                               )
        res.wait()

def create_enable():
    """Create centOS installation script."""
    with open(PREFIX + 'enable.sh', 'w') as file:
        file.write(f'export PATH="{PREFIX}/usr/sbin:{PREFIX}/usr/bin:{PREFIX}/sbin:{PREFIX}/bin:$PATH"\n')
        file.write(f'export LD_LIBRARY_PATH="{PREFIX}/usr/lib64:{PREFIX}/lib64"')

def cast_enable():
    """Cast paths in enable paths from absolute to relative."""
    for root, dirs, files in os.walk(os.path.join(PREFIX, "opt/")):
        for file in files:
            if file == 'enable':
                print(root, dirs, file)
                with open(os.path.join(root, file), 'r+') as file_w:
                    data = file_w.read()
                    data = data.replace('=/opt/rh',
                                        f'={PREFIX}/opt/rh/'
                                        )
                    data = data.replace(':/opt/rh',
                                        f':{PREFIX}/opt/rh/'
                                        )
                    file_w.seek(0)
                    file_w.write(data)
                    file_w.truncate()

if __name__ == "__main__":
    packages_dev_latest = {'rh-python38-python-devel.x86_64',
                           'devtoolset-9.x86_64'
                           }

    packages_t2k = {'cmake3', 'epel-release', 'python-devel', 'wget',
                    'ncurses-devel', 'libX11-devel', 'libxml2-devel',
                    'libXpm-devel', 'libXft-devel', 'libXext-devel',
                    'libcurl-devel', 'mesa-dri-drivers', 'ed', 'imake',
                    'krb5-devel', 'tcsh', 'krb5-devel', 'openssl-devel',
                    'graphviz-devel', 'libXt-devel', 'motif-devel',
                    'freetype-devel', 'gmp-devel', 'gsl-devel',
                    'glut-devel', 'which', 'man-db'
                    }

    packages_devgroup = {'bison', 'byacc', 'cscope', 'ctags', 'cvs',
                         'diffstat', 'doxygen', 'flex', 'gcc',
                         'gcc-c++', 'gcc-gfortran', 'gettext', 'git',
                         'indent', 'intltool', 'libtool', 'patch',
                         'patchutils', 'rcs', 'redhat-rpm-config',
                         'rpm-build', 'subversion', 'swig', 'systemtap'
                         }

    packages_ini = packages_devgroup | packages_t2k | packages_dev_latest
    packs = resolve(packages_ini)
    download(packs)
    install(True)
    create_enable()
    cast_enable()
