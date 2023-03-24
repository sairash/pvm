from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from tqdm import tqdm
from pathlib import Path
import re, requests, sys, os, zipfile, shutil, atexit, time

urls = ["https://windows.php.net/downloads/releases/archives"]

links = {}
valid_hex = '0123456789ABCDEF'.__contains__ 
arguments = sys.argv


os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm'), exist_ok=True)
os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions'), exist_ok=True)
os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'), exist_ok=True)
os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup'), exist_ok=True)


if (os.path.exists(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')) == False):
    f = open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt'), "w")
    f.close()
lines = 0

if os.stat(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')).st_size != 0:
    with open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')) as f:
        lines = f.readlines()[0]


def exit_handler():
    print()
    printC("Thanks For Using ", '#FFFF00')
    printC("PVM - Made by Sairash. ", '#02c702', '' )
    printC("Git link ", '#0abc20', '' )
    printC("https://github.com/sairash/pvm", '#27a043')


atexit.register(exit_handler)


def clean_hex(data):
    return ''.join(filter(valid_hex, data.upper()))

def printC(text, color='#ffffff', end='\n'):
    hexint = int(clean_hex(color), 16)
    print("\x1B[38;2;{};{};{}m{}\x1B[0m".format(hexint>>16, hexint>>8&0xFF, hexint&0xFF, text),end=end)

def change_php_ini_file(old_version):
    print()
    print('Checking Your Previous INI files!')
    if os.path.exists(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup', old_version, 'php.ini')):
        print('Found Previous INI Files')
        shutil.copyfile(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup', old_version, 'php.ini'), os.path.join(Path.home(), "AppData", 'Roaming','pvm','php', 'php.ini'))
    else:
        print('Creating New INI Files')
        shutil.copyfile(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php', 'php.ini-development'), os.path.join(Path.home(), "AppData", 'Roaming','pvm','php', 'php.ini'))
    print()
    printC("PHP Ready For Use ", '#FFFF00')
    print('Try using "', end="")
    printC('php -v command', "#02c702", "")
    print('"')


def unzip(version, old_version):
    print("Unzipping: Version "+ version)
    shutil.rmtree(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php'))
    os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php'))
    with zipfile.ZipFile(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions/php-'+version+'.zip'), 'r') as zf:
        for member in tqdm(zf.infolist(), desc='php-'+version):
            try:
                zf.extract(member, os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'))
            except zipfile.error as e:
                pass

    f =open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt'), "w")
    f.write(version)
    f.close()
    change_php_ini_file(old_version)
    

def backup_ini_file(version):
    old_version = "0"
    if os.stat(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')).st_size != 0:
        f =open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt'), "r")
        old_version = f.read()
        f.close()
        os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup', old_version), exist_ok=True)
        # shutil.rmtree(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup', version))
        if(os.path.exists(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php', 'php.ini'))):
            shutil.copyfile(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php', 'php.ini'), os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'ini_backup', old_version, 'php.ini'))
    unzip(version, old_version)



def download():
    print("Downloading: Version "+ arguments[2])

    filesize = int(requests.head(links[arguments[2]]).headers["Content-Length"])
    os.path.join(Path.home(), "AppData", 'Roaming','pvm')
    os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions'), exist_ok=True)
    os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'), exist_ok=True)


    chunk_size = 1024

    with requests.get(links[arguments[2]], stream=True) as r, open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions/php-'+arguments[2]+'.zip'), "wb") as f, tqdm(
            unit="B",  # unit string to be displayed.
            unit_scale=True,  # let tqdm to determine the scale in kilo, mega..etc.
            unit_divisor=1024,  # is used when unit_scale is true
            total=filesize,  # the total iteration.
            file=sys.stdout,  # default goes to stderr, this is the display on console.
            desc='php-'+arguments[2]  # prefix to be displayed on progress bar.
    ) as progress:
        for chunk in r.iter_content(chunk_size=chunk_size):
            # download the file chunk by chunk
            datasize = f.write(chunk)
            # on each chunk update the progress bar.
            progress.update(datasize)


    backup_ini_file(arguments[2])


def scrape_site(print_data = True):
    print('Scanning for Php Version:')

    for url in urls:
        req = Request(url)
        html_page = urlopen(req)

        soup = BeautifulSoup(html_page, 'html.parser')

        for link in soup.find_all('a', href=lambda x: x and x.endswith('-x86.zip')):
            href = link.get('href')
            href_string_split = href.split('/').pop()
            if(href_string_split.startswith("php-devel-") or href_string_split.startswith("php-test-") or href_string_split.startswith("php-debug-")) == False:
                key = href_string_split.split('-')
                if key[2] != 'nts':
                    links[key[1]] = url+'/'+href_string_split


    f = open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt'), "w+")
    for link in links.keys():
        if print_data:
            print(link) if(link != lines) else printC('* '+link, '#90EE90')
        f.write(link+'\n')
    f.close()



def logic_before_scrape():
    if os.path.isfile(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt')) == False:
        f = open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt'), "w")
        f.close()
    if os.stat(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt')).st_size != 0:
        if (time.time() - os.path.getmtime(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt')))/ 3600 > 24 :
            scrape_site()
        else:
            f = open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'list.txt'), "r")
            for line in f.read().split("\n"):
                print(line) if(line != lines) else printC('* '+line, '#90EE90')
            f.close()
    else:
        scrape_site()
            

if len(arguments) < 2 :
    printC("Use 'pvm help'", '#FF0000')
    sys.exit()


if arguments[1] == 'help':
    printC("pvm list            -- See all of the available versions.", '#37df4a')
    printC("pvm list --force    -- Refresh Cache.", '#37df4a')
    printC("pvm help            -- Sell all the commands.", '#02c702')
    printC("pvm version         -- See the current version.", '#0abc20')
    printC("pvm show php        -- Show the working directory of pvm.", '#0abc20')
    printC("pvm show ini        -- Show the current php.ini file path.", '#0abc20')
    printC("pvm edit ini        -- Open the current ini file to edit.", '#0abc20')
    printC("pvm use [php_version]        -- What version of php You want to use.", '#27a043')

elif arguments[1] == 'list':
    if len(arguments) == 3:
        if arguments[2] == '--force':
            scrape_site()
    else:
        logic_before_scrape()

elif arguments[1] == 'show':
    print()
    if len(arguments) != 3:
        sys.exit()


    if arguments[2] == "php":
        print("Current Working File Path: ")
        print(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'))
    elif arguments[2] == "ini":
        print("Current INI File Path: ")
        print(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php', 'php.ini'))

elif arguments[1] == 'edit':
    print()

    if len(arguments) != 3:
        sys.exit()

    if arguments[2] == "ini":
        print("Opening INI File for edit: ")
        os.system('cmd /c "'+os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php', 'php.ini')+'"')

elif arguments[1] == 'version':
    if(lines != '1'):
        printC("Current version is PHP "+lines, '#90EE90')
    else:
        printC("You have not installed any versions from PVM!", '#FF0000')


elif arguments[1] == 'use':
    if len(arguments) != 3:
        sys.exit()

    if "php-"+arguments[2]+'.zip' in os.listdir(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions')):
      backup_ini_file(arguments[2])
      sys.exit()

    scrape_site(False)
    if arguments[2] not in links:
        printC("This version is not available, use 'pvm list' to get the list of 'valid' versions.", '#FF0000')
        sys.exit()

    
    download()