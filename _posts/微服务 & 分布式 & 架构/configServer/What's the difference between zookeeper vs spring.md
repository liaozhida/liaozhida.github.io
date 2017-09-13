What's the difference between zookeeper vs spring cloud config server?.md


With the Spring Cloud Config Server you have a central place to manage external properties for applications across all environments. The concepts on config server map identically to the Spring Environment and PropertySource abstractions, so they fit very well with Spring applications, but can be used with any application running in any language.

Zookeeper is more than just a Distributed Configuration Server, it's a centralized service used for an almost bewildering array of use cases, including configuration management, synchronizing data between services, leader election, message queues, and as a naming service.

If you want to focus on just the configuration management part, i should say, they're different implementations of the same concept.

With Spring Cloud Config Server, you have a config server backed by a (by default) git repository. Every time a new push happens to that git repository, the config server would be aware of the new configuration values. Clients of the config server can either pull the new config values from the server and reconfigure themselves or pursue an event driven approach by connecting to a cloud bus.

At its heart, Zookeeper provides a hierarchical namespace for storing information. Clients can insert new nodes in this hierarchy, change them, or query them. Furthermore, they can add watches to nodes to be told when they change.

When should one be used over the other?
In my opinion, Spring Cloud is very good fit for any application, especially if you're already using spring framework. Also, the repository based approach of config server feels more natural to me and is very flexible, you can easily store generic, application specific and environment based configuration values. And last but not least, Spring Cloud Zookeeper is available as part of spring cloud.



[What's the difference between zookeeper vs spring cloud config server?](https://stackoverflow.com/questions/34835884/whats-the-difference-between-zookeeper-vs-spring-cloud-config-server)

