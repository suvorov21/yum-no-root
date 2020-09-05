import subprocess
import os

RPM_PATH = '/t2k/users/suvorov/rpm_test/'
PREFIX = '/t2k/users/suvorov/centos/'

def resolve(packages):
    """Scan for all possible dependencies."""
    rpms = packages
    for pack in rpms:
        result = subprocess.run(['repoquery', '-R', '--resolve',
                                 '--recursive', pack, "/dev/null"],
                                check=True, stdout=subprocess.PIPE)
        lines = result.stdout.split(b'\n')
        for line in lines:
            line = line.decode("utf-8")
            if line != '':
                print(line)
                packages = packages | {line}

    return packages

def download(packages):
    """Download rpms"""
    for pack in packages:
        result = subprocess.run(['yumdownloader', '--resolve', pack],
                                check=True, stdout=subprocess.PIPE
                               )
        print(result.stdout.decode("utf-8"))

def install(run=False):
    """Install the rpms in the PREFIX"""
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
        subprocess.run([''], check=True)

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
                    data = data.replace('=/opt/rh', f'={PREFIX}/opt/rh/')
                    file_w.seek(0)
                    file_w.write(data)
                    file_w.truncate()

if __name__ == "__main__":
    packages_ini = {'rh-python38-python-devel.x86_64', 'devtoolset-9.x86_64'}
    packs = resolve(packages_ini)
    download(packs)
    install()
    create_enable()
    cast_enable()
