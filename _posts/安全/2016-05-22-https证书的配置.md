`参考网站:https://aotu.io/notes/2016/08/16/nginx-https/ `

### https证书的配置

#### 生成Key文件

书申请者私钥文件，和证书里面的公钥配对使用，
在 HTTPS 『握手』通讯过程需要使用私钥去解密客戶端发來的经过证书公钥加密的随机数信息，是 HTTPS 加密通讯过程非常重要的文件，在配置 HTTPS 的時候要用到

#### 生成CSR文件

CSR :Cerificate Signing Request，证书签署请求文件，里面包含申请者的 DN（Distinguished Name，标识名）和**公钥**信息，在第三方证书颁发机构签署证书的时候需要提供。
证书颁发机构拿到 CSR 后使用其根证书私钥对证书进行加密并生成 CRT 证书文件，里面包含**证书加密信息以及申请者的 DN 及公钥信息**

#### 生成crt文件

前往亚狐的网站，查看证书信息，找到

- SSL证书文件Server Certificate
- 中级证书文件Intermediate Certificate
- 根证书文件Root Certificate

复制在同一个文件中，以 domain.crt文件命名

扩展：
>
>我们一般常见的证书链分为两种：
>
>二级证书：直接由 受信任的根证书颁发机构 颁发的证书（CRT 文件），由于这种情况下一旦 Root CA 证书遭到破坏或者泄露，提供这个 Certificate Authority 的机构之前颁发的证书就全部失去安全性了，需要全部换掉，对这个 CA 也是毁灭性打击，现在主流的商业 CA 都提供三级证书。
>三级证书：由 受信任的根证书颁发机构 下的 中级证书颁发机构 颁发的证书，这样 ROOT CA 就可以离线放在一个物理隔离的安全的地方，即使这个 CA 的中级证书被破坏或者泄露，虽然后果也很严重，但根证书还在，可以再生成一个中级证书重新颁发证书，而且这种情况对 HTTPS 的性能和证书安装过程也没有太大影响，这种方式也基本成为主流做法。
>


 

#### 使用 OpenSSl命令可以在系统当前目录生成 example.key 和 example.csr 文件：
```
openssl req -new -newkey rsa:2048 -sha256 -nodes -out example_com.csr -keyout example_com.key -subj "/C=CN/ST=ShenZhen/L=ShenZhen/O=Example Inc./OU=Web Security/CN=example.com"

```

下面是上述命令相关字段含义：

- C：Country ，单位所在国家，为两位数的国家缩写，如： CN 就是中国
- ST 字段： State/Province ，单位所在州或省
- L 字段： Locality ，单位所在城市 / 或县区
- O 字段： Organization ，此网站的单位名称;
- OU 字段： Organization Unit，下属部门名称;也常常用于显示其他证书相关信息，如证书类型，证书产品名称或身份验证类型或验证内容等;
- CN 字段： Common Name ，网站的域名;

生成 csr 文件后，提供给 CA 机构，签署成功后，就会得到一個 example.crt 证书文件，SSL 证书文件获得后，就可以在 Nginx 配置文件里配置 HTTPS 了。