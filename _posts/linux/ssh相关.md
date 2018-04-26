ssh相关.md


- 自己生成公私钥
- 想控制哪部主机就将 公钥发送过去
- 代码管理可以创建 ~/.ssh/config   配置如下: 注意端口和用户
```
Host yea_git
IdentityFile ~/.ssh/zhida_mbp_personal
Hostname gitlab.***.com
Port 2222
User git
```
- 如果配置成功还是提示输入密码：`Enter passphrase for key` ,有两种办法
	- ssh-add ~/.ssh/privatekey
	- 创建公私钥的时候不要输入密码
- 传输公私钥的命令: `ssh-copy-id -i ~/.ssh/id_rsa.pub remote-host`

