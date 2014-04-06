# modified pkgbuild for ArkOS
# date: 28.2.14
# original from aur.archlinux.org
# changes:
# - updated depencies and build process
# - use patched retroshare-v0.5.5
# - add rswebui-plugin
# - allow to compile rs-nogui only

# header from aur.archlinux.org:
# Maintainer: stqn
# Contributor: JHeaton <jheaton at archlinux dot us>
# Contributor: Tristero <tristero at online dot de>
# Contributor: funkyou

# Set this to true to build and install retroshare-gui
# this is currently not possible because of missing .install and .desktop files
# get these files and add them to sources if you need rs-gui
_build_gui=false
# Set this to true to build and install retroshare-nogui
_build_nogui=true

# Set this to true to build and install the plugins
_build_linkscloud=false
_build_feedreader=false
_build_voip=false
# RSWebUI lets you control Retroshare form your Browser
# works with gui or nogui
_build_rswebui=true

### Nothing to be changed below this line ###

pkgname=retroshare
pkgver=0.5.5c
pkgrel=1
pkgdesc="Serverless encrypted instant messenger with filesharing, chatgroups, e-mail."
arch=('i686' 'x86_64' 'armv6h' 'armv7h')
url="http://retroshare.sourceforge.net/"
license=('LGPL' 'GPL')
# depencies of libretroshare
# qt4: for qmake
# git: for downloading source
makedepends=('qt4' 'git')
# libgcrypt is needed by libgnome-keyring
depends=('openssl' 'libupnp' 'libgnome-keyring' 'libxss' 'libgcrypt')

# install currently disabled, not needed for nogui-only build
#install="${pkgname}.install"

# download branch v0.5.5-mmi into folder retroshare
# todo: add .install and .desktop if gui enabled
source=(	'retroshare::git+https://github.com/electron128/retroshare#branch=v0.5.5-arkos'
		'rswebui::git+https://github.com/electron128/rswebui.git'
)

# no check for git repo
#sah256sums=('SKIP' 'SKIP')
# it has to be md5sums, don't know why
md5sums=('SKIP' 'SKIP')
# first: shasum of rev7068
#sha256sums=('772b0d7916137e81fc0f5ea14f0a8fa70d3d7acb701ca0b0c1c66018f2255650'
#			'4b50547648612e9091536205402a4da9ddea9c18c0f71e5d6cd30b2226f206d9'
#			'70be00968f2477e368f75393f193e76f366fff2dadab869c855e92048060cf29')

# Add missing dependencies if needed
[[ $_build_gui == true ]] && depends=(${depends[@]} 'qt4')
[[ $_build_nogui == true ]] && depends=(${depends[@]} 'libssh' 'protobuf')
# Plugins
[[ $_build_voip == true ]] && depends=(${depends[@]} 'speex')
[[ $_build_feedreader == true ]] && depends=(${depends[@]} 'curl' 'libxslt')
# rswebui needs qt4, because it has a settings dialog
[[ $_build_rswebui == true ]] && depends=(${depends[@]} 'qt4' 'wt' 'boost' 'graphicsmagick' 'pango')

# this fails because of sha256sums size mismatch
# Add source for rswebui
# download to retroshare/plugins/rswebui
#[[ $_build_rswebui == true ]] && source=(${source[@]} 'retroshare/plugins/rswebui::git+https://git.gitorious.org/rswebui/rswebui.git')
#[[ $_build_rswebui == true ]] && sha256sums=(${sha256sums[@]} 'SKIP')

_rssrcdir="retroshare"

build() {
	local _srcdir="${srcdir}/$_rssrcdir"
	local _qmake='qmake-qt4'

	msg "Compiling OpenPGP-SDK..."
	cd "${_srcdir}/openpgpsdk/src"
	$_qmake
	make

	msg "Compiling libbitdht..."
	cd "${_srcdir}/libbitdht/src"
	$_qmake
	make

	msg "Compiling libretroshare..."
	cd "${_srcdir}/libretroshare/src"
	$_qmake
	make

	if [[ "$_build_gui" == "true" ]] ; then
		msg "Compiling retroshare-gui..."
		cd "${_srcdir}/retroshare-gui/src"
		$_qmake
		make
	fi

	if [[ $_build_nogui == "true" ]] ; then
		msg "Compiling retroshare-nogui..."
		# not needed anymore, this is now doen by nogui-itself
		#cd "${_srcdir}/rsctrl/src"
		#make
		cd "${_srcdir}/retroshare-nogui/src"
		#sed -i 's/pkg-config --atleast-version 0.5.4 libssh/pkg-config --atleast-version 0.5 libssh/' retroshare-nogui.pro
		$_qmake
		make
	fi

	if [[ "$_build_voip" == "true" ]] ; then
		msg "Compiling VOIP plugin..."
		cd "${_srcdir}/plugins/VOIP"
		#sed -i 's/lessThan.*/true {/' VOIP.pro
		$_qmake
		make
	fi

	if [[ "$_build_feedreader" == "true" ]] ; then
		msg "Compiling FeedReader plugin..."
		cd "${_srcdir}/plugins/FeedReader"
		$_qmake
		make
	fi

	if [[ "$_build_linkscloud" == "true" ]] ; then
		msg "Compiling LinksCloud plugin..."
		cd "${_srcdir}/plugins/LinksCloud"
		$_qmake
		make
	fi

	if [[ $_build_rswebui == "true" ]] ; then
		msg "Compiling RSWebUI plugin..."
		mv "${srcdir}/rswebui" "${_srcdir}/plugins"
		cd "${_srcdir}/plugins/rswebui"
		$_qmake
		make
	fi
}

package() {
	local _srcdir="${srcdir}/$_rssrcdir"

	# --- Install Files ---

	msg "Installing files to fakeroot-environment..."

	if [[ "$_build_gui" == "true" ]] ; then
		install -D -m 755 \
			"${_srcdir}/retroshare-gui/src/RetroShare" \
			"${pkgdir}/usr/bin/${pkgname}"
	fi

	if [[ "$_build_nogui" == "true" ]] ; then
		install -D -m 755 \
			"${_srcdir}/retroshare-nogui/src/retroshare-nogui" \
			"${pkgdir}/usr/bin/${pkgname}-nogui"
	fi

	# Plugins
	if [[ "$_build_linkscloud" == "true" ]] ; then
		install -D -m 755 \
			"${_srcdir}/plugins/LinksCloud/libLinksCloud.so" \
			"${pkgdir}/usr/lib/retroshare/extensions/libLinksCloud.so"
	fi
	if [[ "$_build_voip" == "true" ]] ; then
		install -D -m 755 \
			"${_srcdir}/plugins/VOIP/libVOIP.so" \
			"${pkgdir}/usr/lib/retroshare/extensions/libVOIP.so"
	fi
	if [[ "$_build_feedreader" == "true" ]] ; then
		install -D -m 755 \
			"${_srcdir}/plugins/FeedReader/libFeedReader.so" \
			"${pkgdir}/usr/lib/retroshare/extensions/libFeedReader.so"
	fi
	if [[ "$_build_rswebui" == "true" ]] ; then
		install -D -m 755 \
				"${_srcdir}/plugins/rswebui/libWebUI.so.1.0.0" \
				"${pkgdir}/usr/lib/retroshare/extensions/libWebUI.so"
	fi

	if [[ "$_build_gui" == "true" ]] ; then
		# Icons
		install -D -m 644 \
			"${_srcdir}/retroshare-gui/src/gui/images/retrosharelogo2.png" \
			"${pkgdir}/usr/share/pixmaps/retroshare.png"

		# Desktop File
		install -D -m 644 \
			"${srcdir}/${pkgname}.desktop" \
			"${pkgdir}/usr/share/applications/${pkgname}.desktop"

		# Skins
		cp -r "${_srcdir}/retroshare-gui/src/qss" "${pkgdir}/usr/share/RetroShare/"
		#find "${pkgdir}/usr/share/RetroShare/" -depth -type d -name ".svn" -exec rm -r {} \;
	fi

	# bdboot (needed to bootstrap the DHT)
	install -D -m 644 \
		"${_srcdir}/libbitdht/src/bitdht/bdboot.txt" \
		"${pkgdir}/usr/share/RetroShare/bdboot.txt"
}
