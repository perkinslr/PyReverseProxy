ReverseProxy/tlsheader.so: tlsheader.c
	gcc tlsheader.c -o ReverseProxy/tlsheader.so -fPIC -shared
