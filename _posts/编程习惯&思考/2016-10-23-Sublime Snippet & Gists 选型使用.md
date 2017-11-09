---
layout:     post
title:      "Sublime Snippet & Gists 选型使用"
subtitle:	"使用sublime快速插入代码片段"
date:       2016-10-23 12:00:00
author:     "zhidaliao"
header-img: "img/post-bg-unix-linux.jpg"
tags:
    - 编程习惯 & 思考
    - sublime
---

## 背景
在编写代码的过程中，总会有一些代码忘记了怎么写，这个时候就要去 翻以前的代码 / 找印象笔记 / github找历史代码 / 谷歌搜索， 非常的麻烦，需要自己筛选再用上，效率非常低下。

在这个背景下， sublime 和 Github Gists 都推出了 snippet 功能：
- sublime 支持 编写 snippet 模板，然后在文本编辑的时候快速插入，对于前端代码和python会合适一些，因为类似于 Java 会用其他的IDE，这个时候就不能在 eclipse 中快速插入。
- Github Gists 支持在浏览器中上传片段，但是没有标签标注，会导致查找非常混乱， Gists 支持第三方IDE，比如 sublime/Jetbrain系列，支持快速上传和使用。

最后还是决定使用 sublime 统一管理，新建一个 仓库保存我的代码片段， 以文件夹作为标签区分， 在第三方IDE比如 eclipse中要使用代码片段， 就先在 sublime中快速插入然后粘贴过去，解决查找代码片段的首要问题

[我的仓库地址](https://github.com/liaozhida/snippet-hub)
```
├── docker
├── html
├── java
│   ├── file\ &\ Primitive\ Data\ Types\
│   ├── mq
│   ├── network
│   ├── quartz
│   ├── spring
│   └── time
├── js
├── markdown
├── maven
└── python
```



## 使用步骤

1. 安装(OSX + sublime text 2)
	
	```
	cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/User
	git clone yourHost
	```

2. 更新

	```
	cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/User/sublime-snippet
	git pull
	```

3. 使用

	开始编辑文件，注意sublime右下角的文件内容必须为(javascript、html、或其他在 sublime-snippet中 scope定义的文件类型)，输入快捷键,然后按tab键(或者回车)即可。

4. 如何定义一个snippet

	```
	文件名必须以.sublime-snippet结尾，该文件为kraken-route-get-render.sublime-snippet
	<snippet>
		<content><![CDATA[ //内容定义在下方，${1}代表鼠标停留的第一个文字，当按tab键将切换到第2个位置，就是${2}
		router.get('/${1}', ${2} function(req, res) {
			var _q = req.query || {};
			var _p = req.params || {};
			${4}
			res.render('${3}');
		});
		]]></content>
		<tabTrigger>rgr</tabTrigger> //定义的快捷键，请不要重复，定义的规则通常是文件名每个单词首字母
		<scope>source.js</scope> //如果是js,填写source.js 如果是html,填写text.html.basic
	</snippet>
	```

5. 当你也想添加自己的snippet的时候
	* 你可以在该项目的 [Issues](http://gitlab.umiit.cn/tool/sublime-snippet/issues) 中new issues,写清楚相关需求
	* 将该项目clone到本地，然后新建一个分支，分支名为[issues的编号-snippet的名称]，然后编写代码，将该分支推送到服务器
	* 等待合并到master中

## scope 列表

[Here is a list of scopes to use in Sublime Text 2 snippets](https://gist.github.com/tushortz/1288d593ca2bf1593182)

## 常见问题

- 定义了scope 为 xml 的 snippet, 然后在 xml格式的文本中输入关键字无效。 解决方案为： 先输入 `<` ，再按 `Tab`



## 参考文档
- [What You Can Do With Gists on Github?](https://www.labnol.org/internet/github-gist-tutorial/28499/)
- [snippets](http://sublimetext.info/docs/en/extensibility/snippets.html)
- [Quickly Insert Text & Code with Sublime Text Snippets](https://www.granneman.com/webdev/editors/sublime-text/top-features-of-sublime-text/quickly-insert-text-and-code-with-sublime-text-snippets/)
- [Sublime Text2 和 gist 打造自己的代码片断库](https://my.oschina.net/wycdavid/blog/200662)