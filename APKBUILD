# Contributor: Zenmap Alpine contributors <maintainer1@gmail.com>
# Maintainer: Zenmap Alpine contributors <maintaier2@gmail.com>
pkgname=zenmap-alpine
pkgver=0.1.0
pkgrel=0
pkgdesc="Lightweight GTK3 graphical frontend for Nmap"
url="https://github.com/zenmap-alpine/zenmap-alpine"
arch="noarch"
license="MIT"
depends="python3 py3-gobject3 gtk+3.0 nmap"
source="zenmap-alpine.py
	zenmap-alpine.desktop
	LICENSE
	README.md"

build() {
	:
}

check() {
	python3 -m py_compile zenmap-alpine.py
}

package() {
	install -Dm755 "$srcdir"/zenmap-alpine.py \
		"$pkgdir"/usr/bin/zenmap-alpine

	install -Dm644 "$srcdir"/zenmap-alpine.desktop \
		"$pkgdir"/usr/share/applications/zenmap-alpine.desktop

	install -Dm644 "$srcdir"/LICENSE \
		"$pkgdir"/usr/share/licenses/zenmap-alpine/LICENSE

	install -Dm644 "$srcdir"/README.md \
		"$pkgdir"/usr/share/licenses/zenmap-alpine/README.md
}

sha512sums="
ab1a93a7cb48f3d3747ec8cf9d2f88bfc4e28767d4cf07f393d0569f0bf60aec9ea2d8494c70cfc702b6c8e9e2afd4930f446527412193444b5ca95df95f8cd4  zenmap-alpine.py
be17561b30f2f5e29dad98ec5302bea6b15b28e77fb7ae93b029ff464bce2f4cd293b5055dfa674a867d404c3d10a544437578f9456c624a2ecaf157f18c21f8  zenmap-alpine.desktop
98640a14716f703b56241ac4325563ea7fa9ea0a03db0ccca432a98a38e47438dd8f23e6e0c779cf1c09c6abbad0fae9d03250296adb42bd5817604d8c93f72e  LICENSE
ff2b51fe7eec8cd00dc111966a24f6f628be5e09c62196315c10a9dc35dfd1fdddc6e3dd12d690443c8df1db94efb3c6d6279ddfc999f4c5d44cfd78743c42f1  README.md
"
