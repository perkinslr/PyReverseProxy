all: preload.so ReverseProxy/tlsheader.so

ReverseProxy/tlsheader.so: tlsheader.c
	gcc tlsheader.c -o ReverseProxy/tlsheader.so -fPIC -shared

preload.so: preload.cpp
	clang++-10 -O3 -g --std=c++2a -stdlib=libc++ -fPIC -fimplicit-modules -fbuiltin-module-map -fmodule-map-file=/usr/include/c++/v1/module.modulemap -fmodule-map-file=$(PWD)/modules.map   -flto preload.cpp -o preload.so -shared


clean:
	rm preload.so ReverseProxy/tlsheader.so
