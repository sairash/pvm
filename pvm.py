from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from tqdm import tqdm
from pathlib import Path
import re, requests, sys, os, zipfile, shutil, atexit

urls = ["https://windows.php.net/downloads/releases/archives"]
# urls = []

links = {}
valid_hex = '0123456789ABCDEF'.__contains__ 
arguments = sys.argv


os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm'), exist_ok=True)
os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions'), exist_ok=True)
os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'), exist_ok=True)


if (os.path.exists(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')) == False):
    f = open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt'), "w")
    f.write("1")
    f.close()
lines = 0

with open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt')) as f:
    lines = f.readlines()[0]


def exit_handler():
    print()
    printC("Thanks For Using ", '#FFFF00')
    printC("PVM - Made by Sairash. ", '#02c702', '' )
    printC("Git link ", '#0abc20', '' )
    printC("https://git.sairashgautam.com.np/", '#27a043')


atexit.register(exit_handler)


def clean_hex(data):
    return ''.join(filter(valid_hex, data.upper()))

def printC(text, color='#ffffff', end='\n'):
    hexint = int(clean_hex(color), 16)
    print("\x1B[38;2;{};{};{}m{}\x1B[0m".format(hexint>>16, hexint>>8&0xFF, hexint&0xFF, text),end=end)


def unzip():
    print("Unzipping: Version "+ arguments[2])
    shutil.rmtree(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php'))
    os.makedirs(os.path.join(Path.home(), "AppData", 'Roaming','pvm','php'))
    with zipfile.ZipFile(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions/php-'+arguments[2]+'.zip'), 'r') as zf:
        for member in tqdm(zf.infolist(), desc='php-'+arguments[2]):
            try:
                zf.extract(member, os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'php'))
            except zipfile.error as e:
                pass

    f =open(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'info.txt'), "w")
    f.write(arguments[2])
    f.close()


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

    unzip()


def scrape_site():
    print('Scanning for Php Version:')
    for url in urls:
        req = Request(url)
        html_page = urlopen(req)

        soup = BeautifulSoup(html_page, 'html.parser')

        for link in soup.find_all('a', href=lambda x: x and x.endswith('-x86.zip')):
            href = link.get('href')
            href_string_split = href.split('/').pop()
            if(href_string_split.startswith("php-devel-") or href_string_split.startswith("php-test-") or href_string_split.startswith("php-debug-")):
                return
            else:
                key = href_string_split.split('-')
                if key[2] != 'nts':
                    links[key[1]] = url+'/'+href_string_split



if len(arguments) < 2 :
    printC("Use 'pvm help'", '#FF0000')
    sys.exit()


if arguments[1] == 'help':
    printC("pvm list     -- See all of the available versions.", '#37df4a')
    printC("pvm help     -- Sell all the commands.", '#02c702')
    printC("pvm version  -- See the current version.", '#0abc20')
    printC("pvm use 18.0 -- What version of php You want to use.", '#27a043')

elif arguments[1] == 'list':
    scrape_site()
    for link in links.keys():
        print(link) if(link != lines) else printC('* '+link, '#90EE90')

elif arguments[1] == 'version':
    if(lines != '1'):
        printC("Current version is PHP "+lines, '#90EE90')
    else:
        printC("You have not installed any versions from PVM!", '#FF0000')


elif arguments[1] == 'use':
    if len(arguments) != 3:
        sys.exit()

    if "php-"+arguments[2]+'.zip' in os.listdir(os.path.join(Path.home(), "AppData", 'Roaming','pvm', 'versions')):
      unzip()
      sys.exit()

    scrape_site()
    if arguments[2] not in links:
        printC("This version is not available, use 'pvm list' to get the list of 'valid' versions.", '#FF0000')
        sys.exit()

      
    download()



