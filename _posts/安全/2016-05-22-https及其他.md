


证书： 包含了公钥、颁发机构、域名等关键信息

#### 证书的制作：

- 生成采用des3算法保护的私钥，
```
openssl genrsa -des3 -out private-rsa.key 1024
```
Enter pass phrase 的含义是输入用来保护私钥文件的密码（密码不要超过6位）。

- 生成公钥证书
```
openssl req -new -x509 -key private-rsa.key -days 750 -out public-rsa.cer
```
该过程除了最开始时需要输入私钥文件的保护密码之外，其他需要的输入均可直接回车忽略，不影响正常使用。

- 生成PKCS12 格式Keystore (包含公私钥)
```
openssl pkcs12 -export -name test-alias -in public-rsa.cer -inkey private-rsa.key -out user-rsa.pfx
```

- 将public-rsa.cer 文件发送给融宝(公钥public-rsa.cer不需要商户替换)。

- 用户自己使用 user-rsa.pfx 进行需要私钥参与的运算操作。


[pfx证书与cer证书的区别](https://my.oschina.net/swingcoder/blog/673299)
[那些证书相关的玩意儿(SSL,X.509,PEM,DER,CRT,CER,KEY,CSR,P12等)](http://www.cnblogs.com/guogangj/p/4118605.html)



AES
DES


MD5
SHA

RSA
