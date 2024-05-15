# webster-unabridged-dict

Scripts to convert Random House Webster's Unabridged Dictionary to [DICT](https://en.wikipedia.org/wiki/DICT#DICT_file_format) and [slob](https://github.com/itkach/slob) formats.

## Installation
Conversion script depends on `pychm` and `beautifulsoup4`.

```sh
sudo make install
```

Then add following to dictd config file (usually `/etc/dict/dictd.conf`) and restart dictd.

```
database webster-unabridged {
  data  /usr/local/share/dict/webster-unabridged.dict
  index /usr/local/share/dict/webster-unabridged.index
}
```

### slob

Aard2 format.

Building requires [slob](https://github.com/itkach/slob) library.

```sh
make slob
```
