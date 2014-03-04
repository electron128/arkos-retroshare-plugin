arkos-retroshare-plugin
=======================

Plugin for ArkOS to control retroshare-nogui.

status: it works but may has bugs

Installation
------------
	# get the PKGBUILD file
	git clone https://github.com/electron128/arkos-retroshare-plugin.git retroshare-pkgbuild
	# build the retroshare-nogui package
	cd retroshare-pkgbuild
	makepkg
	# install new package
	sudo pacman -U <name-of-package>

	# download arkos-retroshare-plugin
	cd genesis/plugins
	git clone https://github.com/electron128/arkos-retroshare-plugin.git retroshare
	# restart genesis

What is ArkOS?
--------------
*A project to help users self-host their websites, email, files and more.
Decentralize your web and reclaim your privacy rights while keeping the conveniences you need.*

https://arkos.io/

What is Retroshare?
-------------------
*Retroshare is a Open Source cross-platform, Friend-2-Friend and secure decentralised communication platform.*

http://retroshare.sourceforge.net/

How to compile retroshare-nogui on ArkOS/Archlinux
--------------------------------------------------
	# better upgrade the number of cpu cores in your VM

	# first update your system.
	# This is important, so packages which are installed later don't break the whole system
	sudo pacman -Syu

	# install a compiler
	sudo pacman -S base-devel

	# install more tools
	sudo pacman -S pkg-config subversion openssl libupnp libgnome-keyring libxss qt4 protobuf cmake

	# install git?
	sudo pacman -S git

	# install libgcrypt, this is needed by libgnome-keyring
	# update your system first!
	# else this package can break pacman
	# todo: discuss with rs devs if we can remove libgnome-keyring
	sudo pacman -S libgcrypt

	# need wget for downloading files?
	sudo pacman -S wget

	# download and compile libssh
	cd ~
	wget https://red.libssh.org/attachments/download/41/libssh-0.5.4.tar.gz
	tar zxvf libssh-0.5.4.tar.gz
	cd libssh-0.5.4/
	mkdir build/ && cd build/
	cmake -DWITH_STATIC_LIB=ON ..
	make -j2

	# get the retroshare sourcecode
	# a patched version of v0.5.5 is needed
	cd ~
	git clone https://github.com/electron128/retroshare

	# compile retroshare-nogui
	# on a raspberrypi this can take 4h
	# on a sinle core vm it is faster but still slow
	# adjust the -j parameter if you have more cpu cores available
	# todo: is make in rsctrl still needed???
	# probably not
	cd ~/retroshare-git/libbitdht/src && qmake-qt4 && make clean && make -j2 &&\
	cd ~/retroshare-git/openpgpsdk/src && qmake-qt4 && make clean && make -j2 &&\
	cd ~/retroshare-git/libretroshare/src && qmake-qt4 && make clean && make -j2 &&\
	cd ~/retroshare-git/rsctrl/src && make -j2 &&\
	cd ~/retroshare-git/retroshare-nogui/src && qmake-qt4 && make clean && make -j2

	# you should now have retrohare-nogui

How to compile rswebui on Archlinux/ArkOS
-----------------------------------------
	# rswebui is a experimental plugin to allow control of retroshare from your browser
	# https://gitorious.org/rswebui/rswebui

	# update your system
	sudo pacman -Syu

	# install depencies
	sudo pacman -S wt boost graphicsmagick pango

	# download rswebui sources
	cd ~/retroshare-git/plugins
	git clone https://git.gitorious.org/rswebui/rswebui.git

	# compile rswebui
	cd rswebui
	qmake-qt4
	make

	# copy the plugin to the extension folder
	# or symlink it
	# from: retroshare/plugins/rswebui/libWebUI.so.1.0.0
	# to:   /home/USER/.retroshare/extensions/libWebUI.so


