mongo 性能瓶颈和调优.md


mongo URL 使用域名的方式，会造成查询缓慢


#### mongoose 连接超时参数

最近在项目中经常发生登录卡死的状况，由于是使用的passport单点登录，所以只能一步步排查，加日志。
最后发现是卡在一个mongodb查询那里，后来去官网查询后，发现查询超时时间默认是无限大的，所以导致我们看到的现象是http无返回，导致http超时了,因此nginx报502错误。
找到了mongoose文件的Connection部分，在下面可以看到有一些连接参数，其中就有socketTimeoutMS和connectTimeoutMS，点击进入mongodb官方文档，可以看到Server的参数中，socketTimeoutMS默认是无限大的，这在连接外网mongodb时可能导致一些问题，我们需要加上超时参数。


```
var options = {
    server: { 
      socketOptions: {
        autoReconnect: true,
        connectTimeoutMS: 10000,
        socketTimeoutMS: 10000,
      },
    },
  }

// Good way to make sure mongoose never stops trying to reconnect
mongoose.connect(uri, options);
```

socketTimeout和socket编程时的设置timeout是一个效果，闲置超时时间，Linux生效，window抛出异常


[mongoose 连接超时参数](https://blog.gaoqixhb.com/p/5844d3e0edf4c176ed21a956)