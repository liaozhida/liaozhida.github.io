## nodejs环境
	
nvm是管理nodejs的工具，可以在一台机器上安装多个不同版本的nodejs

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Install nvm](#install-nvm)
- [Config nvm](#config-nvm)
- [Install nodejs](#install-nodejs)
- [Config npm](#config-npm)
- [Install tool](#install-tool)
- [Commands Of nvm](#commands-of-nvm)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Install nvm
```	
brew install nvm
```

### Config nvm

```
mkdir ~/.nvm
echo 'export NVM_DIR=~/.nvm' >> ~/.zshrc
echo '. $(brew --prefix nvm)/nvm.sh' >> ~/.zshrc
```


### Install nodejs
目前系统统一nodejs版本为0.12.7，并设置为默认版本,请 ***必须*** 安装该版本
```
nvm install 0.12.7
nvm alias default 0.12.7
```

### Config npm
将以下代码复制粘贴到~/.npmrc中，如果没有该文件，请新建

```
always-auth=true
registry=http://m2.paraller.com/content/groups/npm/
_auth=
email=修改为你的email
```

### Install tool

+ grunt-cli grunt工具
+ supervisor 保持nodejs不间断运行 

```
npm install -g grunt-cli supervisor
```

### Commands Of nvm

+ nvm ls //查看目前机器已经安装的nodejs
+ nvm help //查看各个命令的使用方法
