DESTDIR = /usr/local/share/dict
CONFIG_FILE = /etc/dict/dictd.conf
DICTNAME = webster-unabridged
DICTNAME_FULL = "Random House Webster's Unabridged Dictionary"
DICTSOURCE = ${DICTNAME}.chm

IPFS_PROVIDER = https://cloudflare-ipfs.com

define CONFIG
database ${DICTNAME} {
  data  ${DESTDIR}/${DICTNAME}.dict
  index ${DESTDIR}/${DICTNAME}.index
}
endef
export CONFIG

${DICTNAME}.index ${DICTNAME}.dict: ${DICTSOURCE} convert.py
	python3 convert.py ${DICTSOURCE} | dictfmt --utf8 --allchars -s ${DICTNAME_FULL} -j ${DICTNAME}

${DICTSOURCE} download:
	curl -o ${DICTSOURCE} "${IPFS_PROVIDER}/ipfs/bafykbzacecko7s2t2lv6mhlaj5b4dvkiranpfqjxwu5jnbookbdy7xr2dm3d4"

install: ${DICTNAME}.index ${DICTNAME}.dict
	mkdir -p ${DESTDIR}
	cp -f ${DICTNAME}.dict ${DICTNAME}.index ${DESTDIR}
	@echo "Don't forget to add following to dictd config (usually ${CONFIG_FILE}) and to restart dictd."
	@echo "$$CONFIG"

uninstall:
	rm -f ${DESTDIR}/${DICTNAME}.index ${DESTDIR}/${DICTNAME}.dict

clean:
	rm -f ${DICTNAME}.dict ${DICTNAME}.index
