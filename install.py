import subprocess
import os

import click

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

def download(packages, rpm_path):
    """Download rpms."""
    os.chdir(rpm_path)
    for pack in packages:
        result = subprocess.run(['yumdownloader', '--resolve', pack],
                                check=True, stdout=subprocess.PIPE
                               )
        print(result.stdout.decode("utf-8"))

def install(rpm_path, prefix, run=False):
    """Install the rpms to the PREFIX."""
    os.chdir(prefix)
    subprocess.run(['mkdir', '-p', 'tmp_install'], check=False)
    with open('install.sh', 'w') as w_file:
        w_file.write('cd tmp_install\n')
        for file in os.listdir(rpm_path):
            if file.endswith('.rpm'):
                w_file.write(f'echo "Working on {file}"\n')
                w_file.write(f'rpm2cpio {rpm_path+file} | cpio -idmv\n')
                w_file.write('chmod -R 765 ./*\n')
                w_file.write(f'cp -r {prefix}/tmp_install/* {prefix}\n')
                w_file.write(f'rm -rf {prefix}/tmp_install/*\n')
    if run:
        res = subprocess.Popen("source install.sh",
                               shell=True,
                               executable="/bin/bash"
                               )
        res.wait()

def create_enable(prefix):
    """Create centOS installation script."""
    with open(prefix + 'enable.sh', 'w') as file:
        file.write(f'export PATH="{prefix}/usr/sbin:{prefix}/usr/bin:{prefix}/sbin:{prefix}/bin:$PATH"\n')
        file.write(f'export LD_LIBRARY_PATH="{prefix}/usr/lib64:{prefix}/lib64"')

def cast_enable(prefix):
    """Cast paths in enable paths from absolute to relative."""
    for root, dirs, files in os.walk(os.path.join(prefix, "opt/")):
        for file in files:
            if file == 'enable':
                print(root, dirs, file)
                with open(os.path.join(root, file), 'r+') as file_w:
                    data = file_w.read()
                    data = data.replace('=/opt/rh',
                                        f'={prefix}/opt/rh/'
                                        )
                    data = data.replace(':/opt/rh',
                                        f':{prefix}/opt/rh/'
                                        )
                    file_w.seek(0)
                    file_w.write(data)
                    file_w.truncate()

@click.command()
@click.option('--prefix', default='~/')
@click.option('--rpm_path', default='~/')
def main(prefix, rpm_path):
    """Main sequence."""
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


    if prefix[-1] != '/':
        prefix += '/'

    if rpm_path[-1] != '/':
        rpm_path += '/'

    packages_ini = packages_devgroup | packages_t2k | packages_dev_latest
    packs = resolve(packages_ini)
    download(packs, rpm_path)
    install(rpm_path, prefix, True)
    create_enable(prefix)
    cast_enable(prefix)

if __name__ == "__main__":
    main()
